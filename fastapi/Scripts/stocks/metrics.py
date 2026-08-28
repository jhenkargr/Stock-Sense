import yfinance as yf


def fmt(value, percent=False):
    if value is None:
        return "N/A"
    return f"{value:.2f}%" if percent else f"{value:.2f}"

def safe_get(df, key):
        try:
            return df.loc[key].iloc[0]
        except:
            return None

def fundamental(stock):
    a=stock.info
    bal = stock.balance_sheet
    inc = stock.financials
    
    equity_row = bal.loc["Stockholders Equity"]  # or whatever name appears in index
    avg_equity = (equity_row.iloc[0] + equity_row.iloc[1]) / 2
    net_profit = inc.loc["Net Income"].iloc[0]
    
    net_profit = inc.loc["Net Income"].iloc[0]
    tax        = inc.loc["Tax Provision"].iloc[0]
    interest   = inc.loc["Interest Expense"].iloc[0]
    ebit = net_profit + tax + interest

    net_income = inc.loc["Net Income"]
    latest  = net_income.iloc[0]   # most recent year
    base    = net_income.iloc[-2]
    n_years = len(net_income) - 2  # number of years between
    cagr = (latest / base) ** (1 / n_years) - 1
    print(f"Profit Growth CAGR: {cagr*100:.2f}%")
    
    gross_profit_margin=a['grossMargins']
    eps=a['trailingEps']
    total_equity = a['bookValue'] * a['sharesOutstanding']
    roe = (net_profit / avg_equity)
    capital_employed = total_equity + a["totalDebt"]
    roce = (ebit / capital_employed) * 100
    pb=a['priceToBook']
    
    peg=a['trailingPE']/(cagr*100)
    debttoequity=a['totalDebt']/total_equity
    print('gross_profit_margin',gross_profit_margin ,"\n",'eps',eps,'\n','roe',roe,'\n','roce',roce,'\n','pb',pb,'\n','PEG Ratio',peg,'\n','DebtToEquity',debttoequity)

    a=stock.info
    info = stock.info
    inc = stock.financials

    total_equity = a['bookValue'] * a['sharesOutstanding']
    
    tax      = inc.loc["Tax Provision"].iloc[0]
    pbt      = inc.loc["Pretax Income"].iloc[0]

    net_profit = inc.loc["Net Income"].iloc[0]
    tax        = inc.loc["Tax Provision"].iloc[0]
    interest   = inc.loc["Interest Expense"].iloc[0]
    ebit = net_profit + tax + interest
    
    tax_rate = tax / pbt
    total_debt = info["totalDebt"]
    nopat    = ebit * (1 - tax_rate)
    
    cash = a["totalCash"]
    
    invested_capital = total_equity + total_debt - cash
    roic = nopat / invested_capital
    print(f"ROIC : {roic * 100:.2f}%")
    
    interest   = abs(inc.loc["Interest Expense"].iloc[0])
    
    rd = interest / total_debt
    
    tax_rate = 0.25
    rd_after_tax = rd * (1 - tax_rate)
    
    rf   = 0.07
    beta = 1.0
    erp  = 0.08
    re   = rf + (beta * erp)
    print(f"Cost of Equity (Re)       : {re*100:.2f}%")
    
    # ── WACC = Cost of Capital ───────────────────────────
    total_equity  = info["bookValue"] * info["sharesOutstanding"]
    total_capital = total_equity + total_debt
    we = total_equity / total_capital
    wd = total_debt   / total_capital
    
    wacc = (we * re) + (wd * rd_after_tax)
    print(f"Cost of Capital (WACC)    : {wacc*100:.2f}%")

    info = stock.info
    
    income_stmt = stock.income_stmt
    
    interest_expense = abs(safe_get(income_stmt, "Interest Expense"))
    total_debt = info["totalDebt"]
    
    
    rd = interest_expense / total_debt
    print(f"Interest Expense  : {interest_expense:.2f}")
    cost_of_debt=rd*100
    print(f"Cost of Debt (Rd) : {cost_of_debt:.2f}%")
    interestcoverage = ebit/interest_expense
    print(interestcoverage)

    balance_sheet = stock.balance_sheet
    
    current_assets   = safe_get(balance_sheet, 'Current Assets')
    current_liab     = safe_get(balance_sheet, 'Current Liabilities')
    inventory        = safe_get(balance_sheet, 'Inventory') or 0
    
    CurrentRatio = current_assets / current_liab
    QuickRatio   = (current_assets - inventory) / current_liab
    print(CurrentRatio)
    print(QuickRatio)

    return [
        {"key": "gross_profit_margin",    "value": fmt(gross_profit_margin, percent=True),
         "full_form": "Gross Profit Margin",
         "info": "gross_profit_margin = Net Income / Revenue",
         "comment": "good" if (gross_profit_margin is not None and gross_profit_margin > 30) else "bad",
         "note": "Higher potential profitability" if (gross_profit_margin is not None and gross_profit_margin > 30) else "Lower profitability"},
    
        {"key": "eps",                    "value": fmt(eps),
         "full_form": "Earnings Per Share",
         "info": "eps = Net Income / Shares Outstanding",
         "comment": "good" if (eps is not None and eps > 0) else "bad",
         "note": "The higher the EPS, the higher will be the company's profitability per share"},
    
        {"key": "roe",                    "value": fmt(roe, percent=True),
         "full_form": "Return On Equity",
         "info": "roe = (Net Income / Shareholders Equity) × 100",
         "comment": "good" if (roe is not None and roe > 15) else "bad",
         "note": "Strong returns for investors" if (roe is not None and roe > 15) else "Weak returns for investors"},
    
        {"key": "roce",                   "value": fmt(roce, percent=True),
         "full_form": "Return On Capital Employed",
         "info": "roce = (EBIT / Capital Employed) × 100",
         "comment": "good" if (roce is not None and cost_of_debt is not None and roce > cost_of_debt) else "bad",
         "note": "Debt is helping the company generate higher returns" if (roce is not None and cost_of_debt is not None and roce > cost_of_debt) else "The company pays more interest than the return it generates"},
    
        {"key": "pb",                     "value": fmt(pb),
         "full_form": "Price To Book Ratio",
         "info": "pb = Stock Price / Book Value Per Share",
         "comment": "good" if (pb is not None and pb > 1.3) else "bad",
         "note": "Investors expect strong future growth" if (pb is not None and pb > 1.3) else "The stock may be undervalued"},
    
        {"key": "peg",                    "value": fmt(peg),
         "full_form": "Price Earnings To Growth Ratio",
         "info": "peg = P/E Ratio / EPS Growth Rate",
         "comment": "good" if (peg is not None and peg < 1) else "bad",
         "note": "The company's growth rate is high relative to its price" if (peg is not None and peg < 1) else "Growth is not strong enough to justify the price"},
    
        {"key": "debttoequity",           "value": fmt(debttoequity),
         "full_form": "Debt To Equity Ratio",
         "info": "debttoequity = Total Debt / Total Shareholders Equity",
         "comment": "good" if (debttoequity is not None and debttoequity < 1) else "bad",
         "note": "Lower financial risk" if (debttoequity is not None and debttoequity < 1) else "Financial risk is High"},
    
        {"key": "roic",                   "value": fmt(roic, percent=True),
         "full_form": "Return On Invested Capital",
         "info": "roic = (NOPAT / Invested Capital) × 100",
         "comment": "good" if (roic is not None and roic > 15) else "bad",
         "note": "Company generates high returns from its investments" if (roic is not None and roic > 15) else "Company generates low returns from its investments"},
    
        {"key": "cost_of_debt",           "value": fmt(cost_of_debt, percent=True),
         "full_form": "Cost Of Debt",
         "info": "cost_of_debt = (Interest Expense / Total Debt) × 100",
         "comment": "good" if (cost_of_debt is not None and cost_of_debt < 8) else "bad",
         "note": "Company has good credit rating" if (cost_of_debt is not None and cost_of_debt < 8) else "More profit goes toward interest payments"},
    
        
    
        {"key": "interest_coverage",      "value": fmt(interestcoverage),
         "full_form": "Interest Coverage Ratio",
         "info": "interest_coverage = EBIT / Interest Expense",
         "comment": "good" if (interestcoverage is not None and interestcoverage > 4) else "bad",
         "note": "Company is comfortable handling its debt - Good for Investor" if (interestcoverage is not None and interestcoverage > 4) else "Higher chance of financial distress"},
    
        {"key": "current_ratio",          "value": fmt(CurrentRatio),
         "full_form": "Current Ratio",
         "info": "current_ratio = Current Assets / Current Liabilities",
         "comment": "good" if (CurrentRatio is not None and 1.5 < CurrentRatio < 3) else "bad",
         "note": "Company can easily pay short-term debts" if (CurrentRatio is not None and 1.5 < CurrentRatio < 3) else "Current liabilities are higher than assets"},
    
        {"key": "quick_ratio",            "value": fmt(QuickRatio),
         "full_form": "Quick Ratio",
         "info": "quick_ratio = (Current Assets − Inventory) / Current Liabilities",
         "comment": "good" if (QuickRatio is not None and QuickRatio > 0.8) else "bad",
         "note": "Company has enough liquid assets" if (QuickRatio is not None and QuickRatio > 0.8) else "Company might struggle to meet short-term obligations quickly"},
    
    
    ]
    


import nest_asyncio
import uvicorn
from fastapi import FastAPI, HTTPException , Query, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
from typing import Annotated
import yfinance as yf
import requests
import threading
import time


router = APIRouter()
app=FastAPI()
PORT = 8003







# ── Routes ──────────────────────────────────────────

@lru_cache(maxsize=1)
def getvalues(ticker):
    try:
        symbol = ticker.upper()
        if "." not in symbol:
            symbol = f"{symbol}.NS"
        stock = yf.Ticker(symbol)
        result=fundamental(stock)
        return result
    
    except Exception as e:
        print(f"NSE fetch error: {e}")
        return []

@router.get("/stocks")
def get_stocks(ticker: Annotated[str, Query(..., description="Ticker symbol e.g. RELIANCE or RELIANCE.NS")]):
    return getvalues(ticker)

@router.get("/live")
def rowone(ticker: Annotated[str, Query(..., description="Ticker symbol e.g. RELIANCE or RELIANCE.NS")]):
    symbol = ticker.upper()
    if "." not in symbol:
        symbol = f"{symbol}.NS"

    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        live = stock.fast_info["last_price"]
        previous_close = info.get("previousClose")
        if previous_close in (None, 0):
            raise HTTPException(status_code=502, detail="previousClose is unavailable for this ticker")

        result = {
            "live": fmt(live),
            "rise": fmt(live - previous_close),
            "percent": fmt((live - previous_close) / previous_close * 100, percent=True),
            "sector": info.get("sector", "N/A"),
        }
        return result
    

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Unable to fetch live data for {symbol}: {e}") from e


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



    
