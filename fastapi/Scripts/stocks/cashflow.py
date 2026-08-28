
import uvicorn
from fastapi import APIRouter, FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
from typing import Annotated
import yfinance as yf
import pandas as pd



router = APIRouter()
PORT = 8001

@lru_cache(maxsize=50)
def cashflow_dict(ticker_symbol: str):
    ticker = yf.Ticker(ticker_symbol+".NS")
    cf = ticker.cashflow

    if cf is None or cf.empty:
        raise HTTPException(status_code=404, detail=f"No cash flow data found for {ticker_symbol}")

    items = {
        "Operating Cash Flow" : "Operating Cash Flow",
        "Capital Expenditure" : "Capital Expenditure",
        "Free Cash Flow"      : "Free Cash Flow",
        "PPE"                 : "Purchase Of PPE",
        "Investment Purchase" : "Purchase Of Investment",
        "Net Stock Issuance"  : "Net Issuance Payments Of Debt",
        "Cash Dividends Paid" : "Payment Of Dividends",
        "Debt Issued": "Long Term Debt Issuance",
        "Debt Repaid": "Long Term Debt Payments",
        "Stock Issuance": "Common Stock Issuance",
        "Cash Position": "End Cash Position"
    }

    result = {}
    for label, key in items.items():
        if key in cf.index:
            yearly = cf.loc[key] / 1e7
            result[label] = {
                col.strftime("%Y"): round(val, 2) if not pd.isna(val) else None
                for col, val in yearly.items()
            }
        else:
            result[label] = {}

    return result

@router.get("/stocks")
def get_stocks(
    ticker: Annotated[str, Query(description="Ticker symbol e.g. RELIANCE.NS")],
):
    return cashflow_dict(ticker.upper())

def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app

app = create_app()


if __name__ == "__main__":
    print(f"Docs at http://127.0.0.1:{PORT}/docs")
    uvicorn.run("stocks.cashflow:app", host="127.0.0.1", port=PORT, reload=True)



