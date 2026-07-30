import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

router = APIRouter()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
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

        return {
            item["market"]: item["marketStatus"]
            for item in data["marketState"]
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
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