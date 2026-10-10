"""Measure local ASGI process RSS; no provider calls or database mutations."""
import asyncio
import ctypes
import json
import os
import sys
from pathlib import Path

# Run from repository root using the backend virtual environment.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
import httpx
from app.config import Settings
from app.main import create_app


def rss_mb():
    if sys.platform == 'win32':
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('faults', wintypes.DWORD)] + [(name, ctypes.c_size_t) for name in ['peak', 'rss', 'quota_peak', 'quota', 'pool_peak', 'pool', 'pagefile', 'pagefile_peak']]
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        handle = ctypes.windll.kernel32.GetCurrentProcess
        handle.restype = wintypes.HANDLE
        memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
        memory_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        if not memory_info(handle(), ctypes.byref(counters), counters.cb):
            raise OSError('Cannot measure process memory')
        return round(counters.rss / 1024**2, 1)
    # Linux RSS includes resident pages, not just the on-disk model size.
    status = Path('/proc/self/status').read_text()
    return round(int(next(line.split()[1] for line in status.splitlines() if line.startswith('VmRSS:'))) / 1024, 1)


async def main():
    settings = Settings(search_demo_mode=True, search_api_key='')
    app = create_app(settings)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://local') as client:
            (await client.get('/api/health')).raise_for_status()
            readings = {'platform': sys.platform, 'pid': os.getpid(), 'startup_rss_mib': rss_mb(), 'searches': []}
            for query in ['quiet Manhattan under $250 with wifi', 'romantic Brooklyn under $300', 'family Queens under $350 for 4 guests']:
                response = await client.post('/api/search', json={'query': query})
                response.raise_for_status()
                readings['searches'].append({'ranking': response.json()['ranking'], 'rss_mib': rss_mb()})
            print(json.dumps(readings, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
