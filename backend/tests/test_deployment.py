"""Deployment boundaries: read-only storage, exact CORS, provider-free health/demo."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.engine import make_url

from app.config import Settings
from app.database import make_engine
from app.main import create_app
from app.search_provider import SearchProvider


@pytest.mark.asyncio
async def test_readonly_database_rejects_writes(database):
    path = make_url(database[1].database_url).database.replace('\\', '/')
    # URI protection must work even when the OS user owns the file.
    engine = make_engine(f'sqlite+aiosqlite:///file:{path}?mode=ro&immutable=1&uri=true')
    try:
        async with engine.connect() as connection:
            assert (await connection.execute(text('SELECT count(*) FROM listings'))).scalar() == 300
            with pytest.raises(DBAPIError, match='readonly'):
                await connection.execute(text('CREATE TABLE forbidden (id INTEGER)'))
    finally:
        await engine.dispose()


def test_allowed_origins_health_and_demo(database, monkeypatch):
    monkeypatch.setenv('ALLOWED_ORIGINS', '["https://stayscape.example"]')
    settings = Settings(_env_file=None, database_url=database[1].database_url, search_demo_mode=True)
    async def no_provider(*args):
        raise AssertionError('Health/demo must not interpret with a provider')
    monkeypatch.setattr(SearchProvider, 'interpret', no_provider)
    with TestClient(create_app(settings)) as client:
        health = client.get('/api/health', headers={'Origin': 'https://stayscape.example'})
        assert health.status_code == 200
        assert health.headers['access-control-allow-origin'] == 'https://stayscape.example'
        denied = client.get('/api/health', headers={'Origin': 'https://not-allowed.example'})
        assert 'access-control-allow-origin' not in denied.headers
        queries = client.get('/api/search/examples').json()['queries']
        response = client.post('/api/search', json={'query': queries[0], 'demo': True})
        assert response.status_code == 200
        assert response.json()['source'] == 'demo'
