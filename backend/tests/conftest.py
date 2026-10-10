import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.database import make_engine, session_factory
from app.dataset import Catalog
from app.generator import GenerationOptions, generate
from app.main import create_app
from app.seeding import seed_database


@pytest.fixture(scope="session")
def catalog():
    return Catalog(Settings(_env_file=None))


@pytest.fixture(scope="session")
def dataset(catalog):
    return generate(catalog, GenerationOptions(count=300, seed=42))


@pytest.fixture
async def database(tmp_path, dataset, catalog):
    url = f"sqlite+aiosqlite:///{(tmp_path / 'test.db').as_posix()}"
    engine = make_engine(url)
    await seed_database(engine, dataset, catalog)
    yield engine, Settings(_env_file=None, database_url=url)
    await engine.dispose()


@pytest.fixture
async def session(database):
    async with session_factory(database[0])() as session:
        yield session


@pytest.fixture
def client(database):
    with TestClient(create_app(database[1])) as client:
        yield client
