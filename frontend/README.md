# STOCKSENSE — React + Tailwind Stock Analyser

A dark terminal-style stock analysis dashboard built with **React 18**, **Tailwind CSS v3**, and **Chart.js**.

## 🚀 Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Start development server
npm run dev

# 3. Open in browser
# → http://localhost:5173
```

## 🏗 Build for Production

```bash
npm run build
npm run preview
```

---

## 📁 Project Structure

```
stocksense/
├── index.html
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── package.json
└── src/
    ├── main.jsx              # React entry point
    ├── App.jsx               # Root component + state management
    ├── index.css             # Global styles (Tailwind + scanlines + scrollbar)
    │
    ├── data/
    │   └── stocks.js         # Stock database + unknown stock generator
    │
    ├── hooks/
    │   └── useClock.js       # Live clock hook
    │
    └── components/
        ├── Header.jsx            # Top nav with logo + live clock
        ├── SearchBar.jsx         # Ticker input + quick picks
        ├── LoadingSpinner.jsx    # Animated loading state
        ├── ResultsDashboard.jsx  # Assembles all result panels
        ├── StockHeader.jsx       # Price + rating bar
        ├── KpiGrid.jsx           # 6 KPI cards with animated bars
        ├── AISummary.jsx         # AI analysis text panel
        ├── PriceChart.jsx        # Chart.js 52-week sparkline
        ├── FundamentalsTable.jsx # Metrics table with tags
        ├── HealthScorecard.jsx   # Canvas arc gauges
        └── AnalystSentiment.jsx  # Animated sentiment bars
```

---

## 🎨 Tech Stack

| Tool | Purpose |
|------|---------|
| React 18 | UI framework |
| Tailwind CSS v3 | Utility styling |
| Chart.js 4 + react-chartjs-2 | Price sparkline chart |
| Vite 5 | Build tool / dev server |
| Google Fonts | Orbitron · Rajdhani · Share Tech Mono |

---

## 📊 Supported Tickers (pre-loaded data)

`AAPL` · `TSLA` · `MSFT` · `GOOGL` · `NVDA` · `AMZN`

Any other ticker will return simulated data with estimated metrics.

---

## 🔌 Connecting Real Data

To replace simulated data with live market data, update `src/data/stocks.js` to fetch from:
- [Alpha Vantage](https://www.alphavantage.co/) (free tier available)
- [Polygon.io](https://polygon.io/)
- [Yahoo Finance API](https://finance.yahoo.com/)
- [Financial Modeling Prep](https://financialmodelingprep.com/)

---

> ⚠️ **Disclaimer**: This app is for educational purposes only. Data is simulated and does not constitute financial advice.
