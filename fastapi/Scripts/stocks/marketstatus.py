import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

router = APIRouter()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "Connection": "keep-alive",
}

from datetime import datetime, timezone, timedelta

def get_ist_schedule_status():
    """Fallback market status calculated from NSE normal trading hours (Mon-Fri 09:15 - 15:30 IST)."""
    ist = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist)
    weekday = now_ist.weekday()  # 0 = Monday, 4 = Friday
    time_minutes = now_ist.hour * 60 + now_ist.minute
    is_open = (0 <= weekday <= 4) and (555 <= time_minutes <= 930)
    status_str = "Open" if is_open else "Closed"
    return {
        "Capital Market": status_str,
        "Currency": status_str,
        "Commodity": status_str,
        "Debt": status_str,
    }

@router.get("/api/nse-status")
def nse_status():
    try:
        session = requests.Session()

        # Visit home page first to get cookies
        session.get(
            "https://www.nseindia.com",
            headers=HEADERS,
            timeout=10
        )

        response = session.get(
            "https://www.nseindia.com/api/marketStatus",
            headers=HEADERS,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        # Filter only entries containing both 'market' and 'marketStatus' keys
        result = {
            item["market"]: item["marketStatus"]
            for item in data.get("marketState", [])
            if isinstance(item, dict) and "market" in item and "marketStatus" in item
        }

        if result and "Capital Market" in result:
            return result

        raise ValueError("Missing 'Capital Market' in NSE marketState response")

    except Exception as e:
        import traceback
        traceback.print_exc()
        fallback_data = get_ist_schedule_status()
        fallback_data["source"] = "schedule_fallback"
        fallback_data["error"] = str(e)
        return fallback_data
PORT = 8010

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
    uvicorn.run("stocks.marketstatus:app", host="127.0.0.1", port=PORT, reload=True)