

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── Technical indicators ──────────────────────────────────────
from ta.momentum   import RSIIndicator, StochasticOscillator
from ta.trend      import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume     import OnBalanceVolumeIndicator

# ── Yahoo Finance ─────────────────────────────────────────────
import yfinance as yf

# ── ML ────────────────────────────────────────────────────────
from sklearn.ensemble        import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing   import StandardScaler
from sklearn.pipeline        import Pipeline
from sklearn.metrics         import classification_report, roc_auc_score
import joblib


# ══════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════

FORWARD_DAYS  = 5      # predict N trading days ahead
BUY_THRESHOLD = 0.015  # price must rise > 1.5% → label = BUY

STRONG_BUY = 0.65
BUY_PROB   = 0.55
NEUTRAL    = 0.45

TRAIN_RATIO = 0.80


# ══════════════════════════════════════════════════════════════
# STEP 1 — DOWNLOAD PRICE DATA
# ══════════════════════════════════════════════════════════════

def download_price(ticker: str, period: str = "5y") -> pd.DataFrame:
    print(f"\n📥  Price data  [{ticker}  {period}] …")
    df = yf.download(ticker, period=period, auto_adjust=True, progress=False)

    if df.empty:
        raise ValueError(
            f"No price data for '{ticker}'.\n"
            f"  NSE → RELIANCE.NS  TCS.NS  INFY.NS\n"
            f"  BSE → RELIANCE.BO"
        )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.dropna(inplace=True)
    print(f"   ✅  {len(df)} days  ({df.index[0].date()} → {df.index[-1].date()})")
    return df


# ══════════════════════════════════════════════════════════════
# STEP 2 — DOWNLOAD & COMPUTE FUNDAMENTALS
# ══════════════════════════════════════════════════════════════

def download_fundamentals(ticker: str, price_index: pd.DatetimeIndex) -> pd.DataFrame:
    """
    Pull quarterly financials from yfinance, compute ratios,
    then forward-fill onto the daily price index.

    Ratios computed:
        roe, roce, roic, gross_profit_margin, eps
        pb, peg, price_to_fcf, fcf_yield
        ocf_to_net_income, capex_to_ocf
        debttoequity, interest_coverage
        current_ratio, quick_ratio, cash_position
    """
    print(f"   📊  Fetching fundamentals …")

    tk   = yf.Ticker(ticker)
    info = tk.info  # live snapshot

    # ── Helper: safe get from info dict ──────────────────────
    def g(key, default=np.nan):
        val = info.get(key, default)
        return val if val not in (None, "N/A", "") else default

    # ── 1. Snapshot ratios (available directly from info) ────
    snap = {
        "pb"              : g("priceToBook"),
        "peg"             : g("pegRatio"),
        "roe"             : g("returnOnEquity"),
        "debttoequity"    : g("debtToEquity"),
        "current_ratio"   : g("currentRatio"),
        "quick_ratio"     : g("quickRatio"),
        "eps"             : g("trailingEps"),
        "gross_profit_margin": g("grossMargins"),
    }

    # ── 2. Cash-flow based ratios from quarterly statements ──
    try:
        cf  = tk.quarterly_cashflow      # columns = quarter-end dates
        inc = tk.quarterly_income_stmt
        bal = tk.quarterly_balance_sheet

        def latest(df_stmt, *keys):
            """Return latest quarter value for the first matching key."""
            for k in keys:
                matches = [c for c in df_stmt.index if k.lower() in c.lower()]
                if matches:
                    row = df_stmt.loc[matches[0]]
                    val = row.iloc[0]   # most recent quarter
                    return float(val) if pd.notna(val) else np.nan
            return np.nan

        ocf    = latest(cf,  "Operating Cash Flow", "Cash From Operations")
        capex  = latest(cf,  "Capital Expenditure", "Purchase Of PPE")
        net_inc= latest(inc, "Net Income")
        ebit   = latest(inc, "EBIT", "Operating Income")
        int_exp= latest(inc, "Interest Expense")
        rev    = latest(inc, "Total Revenue")
        cogs   = latest(inc, "Cost Of Revenue", "Cost Of Goods Sold")
        total_assets = latest(bal, "Total Assets")
        total_equity = latest(bal, "Stockholders Equity", "Total Equity")
        total_debt   = latest(bal, "Total Debt", "Long Term Debt")
        cash_pos     = latest(bal, "Cash And Cash Equivalents", "Cash")
        inv          = latest(bal, "Inventory")
        curr_assets  = latest(bal, "Current Assets")
        curr_liab    = latest(bal, "Current Liabilities")

        # capex from yfinance is usually negative — make positive
        capex = abs(capex) if pd.notna(capex) else np.nan
        fcf   = (ocf - capex) if (pd.notna(ocf) and pd.notna(capex)) else np.nan

        mktcap = g("marketCap")

        snap["ocf_to_net_income"] = (ocf / net_inc
                                     if pd.notna(ocf) and pd.notna(net_inc)
                                        and net_inc != 0 else np.nan)

        snap["capex_to_ocf"]      = (capex / ocf
                                     if pd.notna(capex) and pd.notna(ocf)
                                        and ocf != 0 else np.nan)

        snap["price_to_fcf"]      = (mktcap / (fcf * 4)   # annualise quarterly FCF
                                     if pd.notna(fcf) and pd.notna(mktcap)
                                        and fcf > 0 else np.nan)

        snap["fcf_yield"]         = ((fcf * 4) / mktcap
                                     if pd.notna(fcf) and pd.notna(mktcap)
                                        and mktcap > 0 else np.nan)

        snap["interest_coverage"] = (ebit / abs(int_exp)
                                     if pd.notna(ebit) and pd.notna(int_exp)
                                        and int_exp != 0 else np.nan)

        snap["roce"]              = (ebit / (total_assets - curr_liab)
                                     if pd.notna(ebit) and pd.notna(total_assets)
                                        and pd.notna(curr_liab)
                                        and (total_assets - curr_liab) != 0
                                     else np.nan)

        snap["roic"]              = (net_inc / (total_equity + total_debt)
                                     if pd.notna(net_inc) and pd.notna(total_equity)
                                        and pd.notna(total_debt)
                                        and (total_equity + total_debt) != 0
                                     else np.nan)

        snap["cash_position"]     = cash_pos if pd.notna(cash_pos) else np.nan

        if pd.notna(rev) and pd.notna(cogs) and rev != 0:
            snap["gross_profit_margin"] = (rev - cogs) / rev

    except Exception as e:
        print(f"   ⚠️  Statement parsing failed ({e}). Using snapshot ratios only.")

    # ── 3. Forward-fill onto daily index ─────────────────────
    # All fundamental values are "as of today" snapshots — we
    # broadcast them to every row in the daily price index.
    fund_df = pd.DataFrame(snap, index=[price_index[-1]])
    fund_df = fund_df.reindex(price_index).bfill().ffill()

    available = [k for k in snap if pd.notna(snap[k])]
    print(f"   ✅  {len(available)}/{len(FUND_COLS)} fundamental ratios fetched: "
          f"{', '.join(available)}")
    return fund_df


# Fundamental columns we expect
FUND_COLS = [
    "roe", "roce", "roic", "gross_profit_margin", "eps",
    "pb", "peg", "price_to_fcf", "fcf_yield",
    "ocf_to_net_income", "capex_to_ocf",
    "debttoequity", "interest_coverage",
    "current_ratio", "quick_ratio", "cash_position",
]


# ══════════════════════════════════════════════════════════════
# STEP 3 — TECHNICAL FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════

def build_technical(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c  = df["Close"].squeeze()
    h  = df["High"].squeeze()
    l  = df["Low"].squeeze()
    v  = df["Volume"].squeeze()
    o  = df["Open"].squeeze()

    # ── Returns ───────────────────────────────────────────────
    df["ret_1d"]  = c.pct_change(1)
    df["ret_5d"]  = c.pct_change(5)
    df["ret_20d"] = c.pct_change(20)
    df["log_ret"] = np.log(c / c.shift(1))

    # ── Moving Averages ───────────────────────────────────────
    for w in [5, 10, 20, 50, 200]:
        df[f"sma_{w}"] = SMAIndicator(c, window=w).sma_indicator()
        df[f"ema_{w}"] = EMAIndicator(c, window=w).ema_indicator()

    df["sma_5_20"]     = df["sma_5"]  / df["sma_20"]
    df["sma_20_50"]    = df["sma_20"] / df["sma_50"]
    df["price_sma50"]  = c / df["sma_50"]
    df["price_sma200"] = c / df["sma_200"]
    df["golden_cross"] = (df["sma_50"] > df["sma_200"]).astype(int)

    # ── RSI ───────────────────────────────────────────────────
    df["rsi_14"]    = RSIIndicator(c, window=14).rsi()
    df["rsi_7"]     = RSIIndicator(c, window=7).rsi()
    df["rsi_slope"] = df["rsi_14"].diff(3)

    # ── MACD ──────────────────────────────────────────────────
    _macd           = MACD(c)
    df["macd"]      = _macd.macd()
    df["macd_sig"]  = _macd.macd_signal()
    df["macd_diff"] = _macd.macd_diff()
    df["macd_cross"]= ((df["macd_diff"] > 0) &
                       (df["macd_diff"].shift(1) <= 0)).astype(int)

    # ── Bollinger Bands ───────────────────────────────────────
    bb              = BollingerBands(c, window=20, window_dev=2)
    df["bb_upper"]  = bb.bollinger_hband()
    df["bb_lower"]  = bb.bollinger_lband()
    df["bb_width"]  = bb.bollinger_wband()
    df["bb_pct"]    = bb.bollinger_pband()
    df["bb_squeeze"]= (df["bb_width"] <
                       df["bb_width"].rolling(20).quantile(0.20)).astype(int)

    # ── Stochastic ────────────────────────────────────────────
    stoch           = StochasticOscillator(h, l, c)
    df["stoch_k"]   = stoch.stoch()
    df["stoch_d"]   = stoch.stoch_signal()

    # ── ATR & Volatility ──────────────────────────────────────
    df["atr_14"] = AverageTrueRange(h, l, c, window=14).average_true_range()
    df["vol_20"] = df["log_ret"].rolling(20).std() * np.sqrt(252)

    # ── Volume ────────────────────────────────────────────────
    df["obv"]       = OnBalanceVolumeIndicator(c, v).on_balance_volume()
    df["vol_ma20"]  = v.rolling(20).mean()
    df["vol_ratio"] = v / df["vol_ma20"]

    # ── Target label ─────────────────────────────────────────
    df["future_ret"] = c.shift(-FORWARD_DAYS) / c - 1
    df["signal"]     = (df["future_ret"] > BUY_THRESHOLD).astype(int)

    # ── Safety: remove inf before dropna ─────────────────────
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    return df


# ══════════════════════════════════════════════════════════════
# FINAL 35-FEATURE LIST
# ══════════════════════════════════════════════════════════════

TECH_COLS = [
    # Trend
    "sma_5_20", "sma_20_50", "price_sma50", "price_sma200", "golden_cross",
    # Momentum
    "rsi_7", "rsi_14", "rsi_slope",
    "macd", "macd_diff", "macd_cross",
    "stoch_k", "stoch_d",
    "ret_1d", "ret_5d", "ret_20d", "log_ret",
    # Volatility
    "bb_pct", "bb_width", "bb_squeeze",
    "atr_14", "vol_20",
    # Volume
    "vol_ratio", "obv",
]

FEATURES = TECH_COLS + FUND_COLS   # 24 technical + 16 fundamental = 40 total
# (some fundamental cols may be NaN for certain tickers → imputed to median)


# ══════════════════════════════════════════════════════════════
# STEP 4 — MERGE TECHNICAL + FUNDAMENTAL
# ══════════════════════════════════════════════════════════════

def build_dataset(ticker: str, period: str = "5y") -> pd.DataFrame:

    # Price + technicals
    raw  = download_price(ticker, period)
    tech = build_technical(raw)

    # Fundamentals (broadcast to daily index)
    fund = download_fundamentals(ticker, tech.index)

    # Merge
    df = tech.join(fund[FUND_COLS], how="left")

    # Forward-fill any gaps (quarterly → daily)
    df[FUND_COLS] = df[FUND_COLS].ffill().bfill()

    # Impute remaining NaNs with column median (fallback)
    for col in FUND_COLS:
        if df[col].isna().any():
            df[col].fillna(df[col].median(), inplace=True)

    # Final safety net
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    X_check = df[FEATURES]
    for col in FEATURES:
        if df[col].isna().any():
            df[col].fillna(df[col].median(), inplace=True)

    buy_pct = df["signal"].mean()
    print(f"\n   Dataset  : {len(df)} rows  ×  {len(FEATURES)} features")
    print(f"   BUY labels : {buy_pct:.1%}   HOLD/SELL : {1-buy_pct:.1%}")
    return df


# ══════════════════════════════════════════════════════════════
# STEP 5 — TRAIN
# ══════════════════════════════════════════════════════════════

def train(df: pd.DataFrame):
    X = np.nan_to_num(df[FEATURES].values, nan=0.0, posinf=0.0, neginf=0.0)
    y = df["signal"].values

    split    = int(len(X) * TRAIN_RATIO)
    X_tr, X_te = X[:split], X[split:]
    y_tr, y_te = y[:split], y[split:]

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators    = 500,
            max_depth       = 8,
            min_samples_leaf= 15,
            max_features    = "sqrt",
            class_weight    = "balanced",
            random_state    = 42,
            n_jobs          = -1,
        )),
    ])

    print("\n🔄  Time-series cross-validation (5-fold) …")
    tscv   = TimeSeriesSplit(n_splits=5)
    cv_auc = cross_val_score(model, X_tr, y_tr, cv=tscv, scoring="roc_auc")
    print(f"   CV ROC-AUC : {cv_auc.mean():.3f} ± {cv_auc.std():.3f}")

    model.fit(X_tr, y_tr)

    y_prob = model.predict_proba(X_te)[:, 1]
    y_pred = model.predict(X_te)
    auc    = roc_auc_score(y_te, y_prob)

    print(f"\n📊  Test ROC-AUC : {auc:.3f}")
    print(classification_report(y_te, y_pred,
                                 target_names=["HOLD/SELL", "BUY"],
                                 digits=3))
    return model, y_prob, df.iloc[split:]


# ══════════════════════════════════════════════════════════════
# STEP 6 — PREDICT (LATEST BAR)
# ══════════════════════════════════════════════════════════════

def predict(model, df: pd.DataFrame, ticker: str) -> dict:
    X_latest = np.nan_to_num(
        df[FEATURES].iloc[-1:].values,
        nan=0.0, posinf=0.0, neginf=0.0
    )
    prob = model.predict_proba(X_latest)[0][1]
    last = df.iloc[-1]

    if   prob >= STRONG_BUY : label = "🟢  STRONG BUY"
    elif prob >= BUY_PROB   : label = "🔵  BUY"
    elif prob >= NEUTRAL    : label = "🟡  NEUTRAL"
    else                    : label = "🔴  SELL / HOLD"

    sep = "═" * 56
    print(f"\n{sep}")
    print(f"  SIGNAL  →  {ticker}")
    print(sep)
    print(f"  Date              : {df.index[-1].date()}")
    print(f"  Close (₹)         : {last['Close']:.2f}")
    print(f"  Signal            : {label}")
    print(f"  Buy Probability   : {prob:.1%}")
    print(sep)
    print("  TECHNICAL")
    print(f"  RSI(14)           : {last['rsi_14']:.1f}"
          + ("  ⚠ Overbought" if last["rsi_14"]>70
             else "  ↓ Oversold" if last["rsi_14"]<30 else ""))
    print(f"  MACD diff         : {last['macd_diff']:.4f}"
          + ("  ↑ Bullish" if last["macd_diff"]>0 else "  ↓ Bearish"))
    print(f"  BB %B             : {last['bb_pct']:.2f}"
          + ("  (near upper)" if last["bb_pct"]>0.8
             else "  (near lower)" if last["bb_pct"]<0.2 else ""))
    print(f"  Volume ratio      : {last['vol_ratio']:.2f}x"
          + ("  🔥 Spike" if last["vol_ratio"]>2 else ""))
    print(f"  Golden cross      : {'✅ Yes' if last['golden_cross'] else '❌ No'}")
    print(f"  Annl. volatility  : {last['vol_20']:.1%}")
    print(sep)
    print("  FUNDAMENTAL")
    def fv(col, fmt=".2f", suffix=""):
        v = last.get(col, np.nan)
        return f"{v:{fmt}}{suffix}" if pd.notna(v) else "N/A"
    print(f"  ROE               : {fv('roe','.1%')}")
    print(f"  ROCE              : {fv('roce','.1%')}")
    print(f"  ROIC              : {fv('roic','.1%')}")
    print(f"  Gross Margin      : {fv('gross_profit_margin','.1%')}")
    print(f"  EPS               : {fv('eps','.2f')}")
    print(f"  P/B               : {fv('pb','.2f')}x")
    print(f"  PEG               : {fv('peg','.2f')}")
    print(f"  Price/FCF         : {fv('price_to_fcf','.1f')}x")
    print(f"  FCF Yield         : {fv('fcf_yield','.1%')}")
    print(f"  OCF/Net Income    : {fv('ocf_to_net_income','.2f')}  (>1 = quality)")
    print(f"  CapEx/OCF         : {fv('capex_to_ocf','.2f')}  (<0.5 = efficient)")
    print(f"  Debt/Equity       : {fv('debttoequity','.2f')}")
    print(f"  Interest Coverage : {fv('interest_coverage','.1f')}x")
    print(f"  Current Ratio     : {fv('current_ratio','.2f')}")
    print(f"  Quick Ratio       : {fv('quick_ratio','.2f')}")
    print(f"  Cash Position     : ₹{fv('cash_position',',.0f')}")
    print(sep)

    return {
        "ticker": ticker, "date": df.index[-1].date(),
        "close": float(last["Close"]), "label": label, "prob": prob,
        "rsi": float(last["rsi_14"]), "macd_diff": float(last["macd_diff"]),
        "bb_pct": float(last["bb_pct"]), "vol_ratio": float(last["vol_ratio"]),
        "roe": last.get("roe", np.nan), "pb": last.get("pb", np.nan),
        "fcf_yield": last.get("fcf_yield", np.nan),
    }


# ══════════════════════════════════════════════════════════════
# STEP 7 — DASHBOARD
# ══════════════════════════════════════════════════════════════

def plot(df: pd.DataFrame, test_df: pd.DataFrame,
         y_prob: np.ndarray, result: dict, model):

    DARK   = "#0d1117"
    PANEL  = "#161b22"
    BORDER = "#30363d"
    ACCENT = "#00d4aa"
    YELLOW = "#ffd166"
    RED    = "#ff4d6d"
    PURPLE = "#7c6cfc"
    TEXT   = "#e6edf3"
    MUTED  = "#8b949e"

    plt.rcParams.update({
        "text.color"     : TEXT,
        "axes.labelcolor": TEXT,
        "xtick.color"    : MUTED,
        "ytick.color"    : MUTED,
        "axes.edgecolor" : BORDER,
    })

    fig = plt.figure(figsize=(20, 24), facecolor=DARK)
    gs  = gridspec.GridSpec(5, 2, figure=fig, hspace=0.50, wspace=0.35)
    win = df.tail(150)

    # ── 1  Price + BB ─────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor(PANEL)
    ax1.plot(win.index, win["Close"],  color=TEXT,   lw=1.2, label="Close")
    ax1.plot(win.index, win["sma_20"], color=ACCENT, lw=0.9, ls="--", label="SMA 20")
    ax1.plot(win.index, win["sma_50"], color=YELLOW, lw=0.9, ls="--", label="SMA 50")
    ax1.fill_between(win.index, win["bb_upper"], win["bb_lower"],
                     alpha=0.07, color=ACCENT)
    buys = test_df[test_df.index.isin(win.index) & (test_df["signal"] == 1)]
    ax1.scatter(buys.index, buys["Close"], marker="^", color=ACCENT,
                s=55, zorder=5, label="BUY label")
    ax1.set_title(f"{result['ticker']}  —  Price & Bollinger Bands",
                  color=TEXT, fontsize=12, pad=8)
    ax1.legend(facecolor=PANEL, labelcolor=TEXT, fontsize=8, loc="upper left")
    for sp in ax1.spines.values(): sp.set_color(BORDER)

    # ── 2  RSI ────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(PANEL)
    ax2.plot(win.index, win["rsi_14"], color=YELLOW, lw=1.2)
    ax2.axhline(70, color=RED,   lw=0.8, ls="--", alpha=0.7)
    ax2.axhline(30, color=ACCENT,lw=0.8, ls="--", alpha=0.7)
    ax2.fill_between(win.index, win["rsi_14"], 70,
                     where=win["rsi_14"]>=70, alpha=0.12, color=RED)
    ax2.fill_between(win.index, win["rsi_14"], 30,
                     where=win["rsi_14"]<=30, alpha=0.12, color=ACCENT)
    ax2.set_ylim(0, 100)
    ax2.set_title("RSI (14)", color=TEXT, fontsize=11)
    for sp in ax2.spines.values(): sp.set_color(BORDER)

    # ── 3  MACD ───────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor(PANEL)
    ax3.plot(win.index, win["macd"],    color=ACCENT, lw=1.1, label="MACD")
    ax3.plot(win.index, win["macd_sig"],color=YELLOW, lw=0.9, label="Signal")
    bar_c = [ACCENT if v >= 0 else RED for v in win["macd_diff"]]
    ax3.bar(win.index, win["macd_diff"], color=bar_c, alpha=0.45, width=0.8)
    ax3.axhline(0, color=MUTED, lw=0.5, ls=":")
    ax3.set_title("MACD", color=TEXT, fontsize=11)
    ax3.legend(facecolor=PANEL, labelcolor=TEXT, fontsize=8)
    for sp in ax3.spines.values(): sp.set_color(BORDER)

    # ── 4  Buy probability ────────────────────────────────────
    ax4 = fig.add_subplot(gs[2, :])
    ax4.set_facecolor(PANEL)
    ax4.plot(test_df.index, y_prob, color=ACCENT, lw=1.1, label="Buy probability")
    ax4.axhline(BUY_PROB,   color=YELLOW, lw=0.9, ls="--", label=f"Buy > {BUY_PROB}")
    ax4.axhline(STRONG_BUY, color=ACCENT, lw=0.9, ls="--", label=f"Strong buy > {STRONG_BUY}")
    ax4.fill_between(test_df.index, y_prob, BUY_PROB,
                     where=y_prob >= BUY_PROB, alpha=0.14, color=ACCENT)
    ax4.fill_between(test_df.index, y_prob, BUY_PROB,
                     where=y_prob <  BUY_PROB, alpha=0.06, color=RED)
    ax4.set_ylim(0, 1)
    ax4.set_title("Model Buy Probability — Test Window (holdout 20%)",
                  color=TEXT, fontsize=11)
    ax4.legend(facecolor=PANEL, labelcolor=TEXT, fontsize=8)
    for sp in ax4.spines.values(): sp.set_color(BORDER)

    # ── 5  Feature importance ─────────────────────────────────
    ax5 = fig.add_subplot(gs[3, 0])
    ax5.set_facecolor(PANEL)
    rf  = model.named_steps["rf"]
    imp = pd.Series(rf.feature_importances_, index=FEATURES).nlargest(20)
    # Colour-code: purple = fundamental, teal = technical
    colors = [PURPLE if f in FUND_COLS else ACCENT for f in imp.index[::-1]]
    ax5.barh(imp.index[::-1], imp.values[::-1], color=colors, alpha=0.85)
    ax5.set_title("Top 20 Feature Importances\n(teal=technical  purple=fundamental)",
                  color=TEXT, fontsize=10)
    ax5.set_xlabel("Importance", color=TEXT)
    for sp in ax5.spines.values(): sp.set_color(BORDER)

    # ── 6  Fundamental scorecard ──────────────────────────────
    ax6 = fig.add_subplot(gs[3, 1])
    ax6.set_facecolor(PANEL)
    ax6.axis("off")
    last = df.iloc[-1]

    def fval(col, fmt=".2f"):
        v = last.get(col, np.nan)
        return f"{v:{fmt}}" if pd.notna(v) else "N/A"

    metrics_display = [
        ("ROE",            fval("roe",".1%")),
        ("ROCE",           fval("roce",".1%")),
        ("ROIC",           fval("roic",".1%")),
        ("Gross Margin",   fval("gross_profit_margin",".1%")),
        ("P/B",            fval("pb",".2f") + "x"),
        ("PEG",            fval("peg",".2f")),
        ("Price/FCF",      fval("price_to_fcf",".1f") + "x"),
        ("FCF Yield",      fval("fcf_yield",".1%")),
        ("OCF/Net Income", fval("ocf_to_net_income",".2f")),
        ("CapEx/OCF",      fval("capex_to_ocf",".2f")),
        ("Debt/Equity",    fval("debttoequity",".2f")),
        ("Int. Coverage",  fval("interest_coverage",".1f") + "x"),
        ("Current Ratio",  fval("current_ratio",".2f")),
        ("Quick Ratio",    fval("quick_ratio",".2f")),
    ]

    ax6.text(0.02, 0.98, "Fundamental Scorecard",
             color=TEXT, fontsize=11, fontweight="bold",
             va="top", transform=ax6.transAxes)

    row_h = 0.063
    for i, (name, val) in enumerate(metrics_display):
        y = 0.90 - i * row_h
        ax6.text(0.02, y, name, color=MUTED, fontsize=9,
                 transform=ax6.transAxes, va="top", fontfamily="monospace")
        ax6.text(0.70, y, val,  color=ACCENT, fontsize=9, fontweight="bold",
                 transform=ax6.transAxes, va="top", fontfamily="monospace")

    for sp in ax6.spines.values(): sp.set_color(BORDER)

    # ── 7  Signal gauge ───────────────────────────────────────
    ax7 = fig.add_subplot(gs[4, :])
    ax7.set_facecolor(PANEL)
    ax7.set_xlim(0, 1); ax7.set_ylim(0, 1); ax7.axis("off")

    prob  = result["prob"]
    color = ACCENT if prob >= BUY_PROB else (YELLOW if prob >= NEUTRAL else RED)

    theta  = np.linspace(np.pi, 0, 200)
    ax7.plot(0.5 + 0.28*np.cos(theta), 0.55 + 0.28*np.sin(theta),
             color=BORDER, lw=22, solid_capstyle="round")
    end_t  = np.pi - prob * np.pi
    theta2 = np.linspace(np.pi, end_t, 200)
    ax7.plot(0.5 + 0.28*np.cos(theta2), 0.55 + 0.28*np.sin(theta2),
             color=color, lw=22, solid_capstyle="round")

    ax7.text(0.5, 0.65, f"{prob:.0%}", ha="center", va="center",
             fontsize=52, fontweight="bold", color=color, fontfamily="monospace")
    ax7.text(0.5, 0.38, result["label"], ha="center", fontsize=16, color=TEXT)
    ax7.text(0.5, 0.22,
             f"{result['ticker']}  ·  ₹{result['close']:.2f}  ·  {result['date']}",
             ha="center", fontsize=10, color=MUTED)
    ax7.set_title("Today's Signal", color=TEXT, fontsize=11, pad=6)
    for sp in ax7.spines.values(): sp.set_color(BORDER)

    fig.suptitle(
        f"Indian Stock ML Predictor v2  ·  {result['ticker']}  ·  "
        f"Random Forest  ·  {len(FEATURES)} features",
        color=TEXT, fontsize=14, fontweight="bold", y=0.995,
    )

    return fig


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
from .supabase_client import get_supabase_client
import base64
import joblib

def main(ticker: str = "RELIANCE.NS", period: str = "5y"):

    print(f"\n{'═'*56}")
    print(f"  Indian Stock ML Predictor v2  |  {ticker}")
    print(f"{'═'*56}")

    supabase = get_supabase_client()
    fname = f"{ticker.replace('.','_')}_rf_v2.pkl"
    image_name = f"{ticker.replace('.', '_')}_plot.png"
    json_name = f"{ticker.replace('.', '_')}_result.json"
    
    if supabase:
        try:
            import json
            
            # Ensure 'predict' bucket exists
            buckets = supabase.storage.list_buckets()
            # Handle both object attribute and dictionary representations
            bucket_names = [b.name if hasattr(b, 'name') else b.get('name') for b in buckets]
            if "predict" not in bucket_names:
                supabase.storage.create_bucket("predict")
                print("✅ Created new 'predict' storage bucket.")
                
            # Check if JSON result exists in storage
            files = supabase.storage.from_("predict").list()
            if isinstance(files, list):
                file_names = [f["name"] for f in files]
                if json_name in file_names:
                    print(f"✅ Found {json_name} in Supabase Storage!")
                    json_bytes = supabase.storage.from_("predict").download(json_name)
                    cached_result = json.loads(json_bytes.decode("utf-8"))
                    return cached_result
        except Exception as e:
            print("Supabase check error:", e)

    # 1. Build dataset (price + technicals + fundamentals)
    print("\n⚙️   Building dataset …")
    df = build_dataset(ticker, period)

    # 2. Train
    model, y_prob, test_df = train(df)

    # 3. Latest prediction
    result = predict(model, df, ticker)

    # 4. Save model
    joblib.dump(model, fname)
    print(f"\n💾  Model saved → {fname}")

    # 5. Dashboard
    fig=plot(df, test_df, y_prob, result, model)
    img_base64 = fig_to_base64(fig)
    
    final_result = {
        "image": img_base64,
        "ticker": result["ticker"],
        "prob": result["prob"],
        "label": result["label"]
    }
    
    if supabase:
        try:
            import json
            # Save to storage bucket instead of table
            json_bytes = json.dumps(final_result).encode('utf-8')
            supabase.storage.from_("predict").upload(json_name, json_bytes, {"content-type": "application/json", "upsert": "true"})
            print(f"✅ Saved prediction data to Supabase Storage as {json_name}")
            
            with open(fname, "rb") as f:
                supabase.storage.from_("predict").upload(fname, f.read(), {"upsert": "true"})
            img_bytes_raw = base64.b64decode(img_base64)
            supabase.storage.from_("predict").upload(image_name, img_bytes_raw, {"content-type": "image/png", "upsert": "true"})
            print("✅ Saved model and image to Supabase Storage (bucket 'predict')")
        except Exception as e:
            print("Supabase upload error:", e)

    return final_result


import io
import base64
import json

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor="#0d1117")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)
    return img_base64


import nest_asyncio
import uvicorn
from fastapi import APIRouter, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
from typing import Annotated
import yfinance as yf
import pandas as pd

nest_asyncio.apply()

router = APIRouter()
PORT = 8007

@lru_cache(maxsize=50)
def predict_dict(ticker: str):
    symbol = ticker.upper()
    if "." not in symbol:
        symbol = f"{symbol}.NS"
    return main(symbol, "5y")

@router.get("/analysis")
def get_analysis(ticker: Annotated[str, Query(..., description="Ticker symbol e.g. RELIANCE or RELIANCE.NS")]):
    return predict_dict(ticker)

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
    uvicorn.run("stocks.predict:app", host="127.0.0.1", port=PORT, reload=True)




