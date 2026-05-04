import nest_asyncio
import uvicorn
import requests
import time
import threading

from fastapi import APIRouter, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

nest_asyncio.apply()

router = APIRouter()

# ──────────────────────────────────────────────
# NSE Session
# ──────────────────────────────────────────────
_session      = None
_session_time = None


def get_nse_session():
    global _session, _session_time
    now = time.time()
    if _session and _session_time and (now - _session_time) < 180:
        return _session

    print("🔄 Creating NSE session...")
    s = requests.Session()
    s.headers.update({
        'User-Agent'     : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept'         : '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer'        : 'https://www.nseindia.com/',
    })
    try:
        s.get('https://www.nseindia.com/', timeout=10)
        time.sleep(1)
        print("✅ NSE session ready")
    except Exception as e:
        print(f"⚠️ NSE warmup failed: {e}")

    _session      = s
    _session_time = now
    return _session


def search_nse(query: str):
    session = get_nse_session()
    url     = f"https://www.nseindia.com/api/search/autocomplete?q={query}"
    try:
        resp = session.get(url, timeout=10)
        print(f"  NSE '{query}' → {resp.status_code}")

        if resp.status_code in (401, 403):
            global _session, _session_time
            _session      = None
            _session_time = None
            session       = get_nse_session()
            resp          = session.get(url, timeout=10)

        if resp.status_code == 200:
            data    = resp.json()
            results = []
            for item in data.get('symbols', []):
                symbol = item.get('symbol', '')
                name   = item.get('symbol_info', '')
                if symbol:
                    results.append({'symbol': symbol, 'name': name})
            return results
        return []

    except Exception as e:
        print(f"  ❌ NSE error: {e}")
        return []


def search_yahoo(query: str):
    url    = "https://query1.finance.yahoo.com/v1/finance/search"
    params = {
        'q'          : query,
        'region'     : 'IN',
        'quotesCount': 10,
        'newsCount'  : 0,
    }
    try:
        resp = requests.get(
            url, params=params,
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=5
        )
        data    = resp.json()
        results = []
        for item in data.get('quotes', []):
            symbol   = item.get('symbol', '')
            name     = item.get('shortname', '') or item.get('longname', '')
            exchange = item.get('exchange', '')
            if exchange in ('NSI', 'BSE', 'NSE'):
                results.append({
                    'symbol'  : symbol.replace('.NS', '').replace('.BO', ''),
                    'name'    : name,
                    'exchange': 'NSE' if exchange == 'NSI' else exchange,
                })
        return results
    except Exception as e:
        print(f"  ❌ Yahoo error: {e}")
        return []


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@router.get('/health')
def health():
    return {
        'status'        : 'ok',
        'session_active': _session is not None,
    }


@router.get('/stocks/suggest')
def suggest(q: str = Query(..., min_length=1)):
    q       = q.strip()
    results = search_nse(q)

    if not results:
        print("  ⚠️ NSE failed → Yahoo Finance...")
        results = search_yahoo(q)

    return {
        'query'      : q,
        'count'      : len(results),
        'suggestions': results,
    }


PORT = 8009

def create_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app

app = create_app()

if __name__ == "__main__":
    print(f"Docs at http://127.0.0.1:{PORT}/docs")
    uvicorn.run("stocks.suggestions:app", host="127.0.0.1", port=PORT, reload=True)