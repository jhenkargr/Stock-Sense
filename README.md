<div align="center">


# 📈 StockSense

<p align="center">
  <img src="https://img.shields.io/badge/React-18-cyan?style=for-the-badge&logo=react" alt="React 18" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-emerald?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Tailwind--CSS-v3-blue?style=for-the-badge&logo=tailwind-css" alt="Tailwind CSS v3" />
  <img src="https://img.shields.io/badge/Scikit--Learn-Random%20Forest-orange?style=for-the-badge&logo=scikit-learn" alt="Scikit-Learn" />
  <img src="https://img.shields.io/badge/Supabase-Caching-green?style=for-the-badge&logo=supabase" alt="Supabase" />
</p>

<p align="center">
  <a href="#introduction">Introduction</a> &nbsp;·&nbsp;
  <a href="#features">Features</a> &nbsp;·&nbsp;
  <a href="#architecture">Architecture</a> &nbsp;·&nbsp;
  <a href="#getting-started">Get Started</a> &nbsp;·&nbsp;
  <a href="#contribute">Contribute</a>
</p>
</div>

---

## <a id="introduction"></a>🧩 What is StockSense?

**StockSense** is a premium, AI-powered stock analysis and forecast platform designed for the Indian Stock Market (NSE). Featuring a modern dark terminal-style interface with rich micro-animations, glassmorphism, and 3D backgrounds, it bridges the gap between deep quantitative analytics and natural language insights. 

<p align="center">
  <img src="path/to/stocksense_dashboard_hero.png" alt="StockSense Main Dashboard Banner" width="100%" />
</p>

The platform downloads daily historical prices and quarterly fundamental statements directly to train custom machine learning models on-the-fly and generates comprehensive financial reports. By utilizing a high-performance **FastAPI microservices gateway** and a **React 18 single-page application**, StockSense empowers retail investors with professional-grade institutional research tools.

---

## <a id="features"></a>✨ Features

<table width="100%">
  <tr>
    <td width="50%" valign="top">
      <h3>🔍 Detailed Stock Analyzer</h3>
      <p align="center">
        <img src="path/to/stock_analyzer_screenshot.png" alt="Detailed Stock Analyzer Screen" width="100%"/>
      </p>
      <ul>
        <li><strong>Live Market Telemetry:</strong> Instant feeds for stock price, daily variations, percentage swings, and exchange sectors (via <code>yfinance</code>).</li>
        <li><strong>12 Crucial KPI Metrics:</strong> Calculations for margins, margins health scorecards, ratios, and valuation coefficients.</li>
        <li><strong>Health Assessments:</strong> Automatic checkmarks and health indicators highlighting whether metrics are <code>✓ HEALTHY</code> or <code>✗ WEAK</code> based on industry thresholds.</li>
        <li><strong>Interactive Tooltips:</strong> Deep-dives detailing full forms and mathematical formulas explaining each metric to the user.</li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <h3>📄 Annual Report Simplifier</h3>
      <p align="center">
        <img src="path/to/report_simplifier_screenshot.png" alt="Annual Report Simplifier Screen" width="100%"/>
      </p>
      <ul>
        <li><strong>Automated PDF Extraction:</strong> Fetches complete Annual Reports from Screener.in on-demand and extracts text layouts.</li>
        <li><strong>AI Financial Parsing:</strong> Employs a sequential, rate-limited processing framework to handle massive PDFs without hitting API limits.</li>
        <li><strong>Hierarchical LLM Merge:</strong> Splits, compresses, and merges text using advanced LLM candidates via the Nvidia API.</li>
        <li><strong>Command-A Formatting Pass:</strong> Cleans and structures raw analyses into structured Markdown sections using Cohere.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>📊 Cash Flow Statement Analysis</h3>
      <p align="center">
        <img src="path/to/cash_flow_screenshot.png" alt="Cash Flow Statement Analysis Screen" width="100%"/>
      </p>
      <ul>
        <li><strong>Scaled Visual Reporting:</strong> Pulls annual cash flow parameters scaled specifically in <strong>₹ Crores</strong> (representing Indian standard scale).</li>
        <li><strong>Complete Cash Parameters:</strong> Tracks Operating Cash Flow, Capital Expenditures (CapEx), Free Cash Flow (FCF), PPE investments, Debt Issued vs Repaid, Stock Issuance, and End Cash Positions.</li>
        <li><strong>Tabular Trend Tracking:</strong> Displays YoY trends in clean, dark-mode tables mapped by reporting years.</li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <h3>🔮 AI-Based Stock Predictor</h3>
      <p align="center">
        <img src="path/to/stock_predictor_screenshot.png" alt="AI-Based Stock Predictor Screen" width="100%"/>
      </p>
      <ul>
        <li><strong>40-Feature Classification Engine:</strong> Combines 24 technical indicators (Trend, Momentum, Volatility, Volume) and 16 fundamental ratios.</li>
        <li><strong>Random Forest Classifier:</strong> A custom Scikit-Learn pipeline (500 estimators, depth 8, balanced class weights) trained with a 5-fold Time-Series cross-validation split.</li>
        <li><strong>Visual Dashboard Generator:</strong> Creates a professional 20x24 inch Matplotlib report plotting Price & Bollinger Bands, RSI, MACD, and a custom today's Signal Gauge.</li>
      </ul>
    </td>
  </tr>
</table>

---

## <a id="architecture"></a>🏗️ Architecture

StockSense is built upon a high-concurrency, asynchronous microservices architecture that splits heavy ML training and web scraping into dedicated API processes managed by a central gateway.

<p align="center">
  <img src="./stocksense_architecture.png" alt="StockSense Microservices Architecture Flowchart" width="100%" />
</p>



---

## 📁 Project Structure

```
stocksense-react/
├── fastapi/                   # Python FastAPI Backend Services
│   ├── Scripts/               # Core Scripts & Models
│   │   ├── stocks/            # Main FastAPI microservice source
│   │   │   ├── main.py        # Microservices Gateway Router (Port 8006)
│   │   │   ├── cashflow.py    # Cashflow Parser Service (Port 8001)
│   │   │   ├── simplifier.py  # Annual Report Parser (Port 8002)
│   │   │   ├── metrics.py     # Live KPI & Telemetry Service (Port 8003)
│   │   │   ├── predict.py     # Random Forest ML Training & Plotting (Port 8007)
│   │   │   ├── suggestions.py # Autocomplete Suggestion Service (Port 8009)
│   │   │   ├── marketstatus.py# NSE India live status client (Port 8010)
│   │   │   └── supabase_client.py # Cloud Storage integration
│   │   └── requirements.txt   # Python Dependencies
│   └── README.md              # Backend Specific Doc
│
├── frontend/                  # React 18 SPA Frontend
│   ├── src/
│   │   ├── App.jsx            # Routing & Layout Root
│   │   ├── index.css          # Custom styling with Scanline animations
│   │   ├── components/        # Reusable UI Widgets (3D backgrounds, tables)
│   │   │   ├── ThreeDBackground.jsx     # Three.js Space Simulation
│   │   │   ├── CashFlowTable.jsx        # Data rendering table
│   │   │   └── Simplifier.jsx           # Markdown compiler
│   │   └── template/          # Core Page Layouts
│   │       ├── Home.jsx       # Landing Page Dashboard
│   │       ├── AnalysePage.jsx# Detailed analysis panel
│   │       └── PredictPage.jsx# Prediction execution panel
│   ├── package.json           # Node configuration
│   └── tailwind.config.js     # Tailwind CSS configuration
│
└── Backend/                   # [DEPRECATED / IGNORED] Express server
```

---

## <a id="getting-started"></a>🚀 Getting Started

### Prerequisites
Ensure you have the following installed on your workspace:
*   [Node.js (v18+)](https://nodejs.org/) & `npm`
*   [Python (v3.8+)](https://www.python.org/) & `pip`
*   A valid [Supabase](https://supabase.com) Project URL and Anon API key
*   API keys for Nvidia API (or Cohere) to run AI features

---

### 1️⃣ Frontend Setup

1.  Navigate into the `frontend` folder:
    ```bash
    cd frontend
    ```
2.  Install required Node modules:
    ```bash
    npm install
    ```
3.  Create a `.env` file in the `frontend/` directory and configure the gateway URL:
    ```env
    VITE_REQUEST_URL=http://localhost:8006
    ```
4.  Launch the Vite development server:
    ```bash
    npm run dev
    ```
    *Open `http://localhost:5173` in your browser.*

---

### 2️⃣ FastAPI Service Setup

1.  Navigate to the `fastapi/` folder:
    ```bash
    cd fastapi
    ```
2.  Activate your Python virtual environment (if not already active):
    ```bash
    # Windows
    Scripts\activate
    
    # macOS/Linux
    source bin/activate
    ```
3.  Install standard requirements:
    ```bash
    pip install -r Scripts/requirements.txt
    ```
4.  Create a `.env` file inside `fastapi/Scripts/stocks/` with the following variables:
    ```env
    # LLM Integrations
    NVIDIA_API_KEY=your_nvidia_api_key
    COHERE_API_KEY=your_cohere_api_key

    # Screener.in (Required to fetch PDF reports)
    mail=your_screener_email
    password=your_screener_password

    # Supabase (Storage caching)
    PROJECT_URL=https://your-project-id.supabase.co
    PUBLIC_URL=your-supabase-anon-or-service-key
    ```
5.  Start the entire backend stack via the microservices gateway:
    ```bash
    python -m stocks.main
    ```
    *This runs the gateway on Port 8006 and spins up ports 8001, 8002, 8003, 8007, 8009, and 8010 in the background.*

---

## 📡 API Reference

### FastAPI Service

| Service | Port | Endpoint | Methods | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Cashflow Service** | `8001` | `/cashflow/stocks` | `GET` | Mapped annual Cashflow metrics in ₹ Crores. |
| **Report Simplifier** | `8002` | `/simplify/` | `GET` | Downloads report PDF, extracts pages, and returns LLM-cleaned markdown summary. |
| **Live Metrics Service**| `8003` | `/metrics/stocks` | `GET` | Mapped analysis calculations for 12 financial KPIs. |
| | | `/metrics/live` | `GET` | Dynamic stock value, daily variations, percentage metrics. |
| **ML Forecast Service** | `8007` | `/predict/analysis`| `GET` | Trains ML Classifier, performs time-series CV, generates plot, and returns final base64 string chart + prediction signal. |
| **Autocomplete Service**| `8009` | `/suggestion/stocks/suggest` | `GET` | Returns NSE symbol search list (falls back to Yahoo). |
| **NSE Market Status** | `8010` | `/marketstatus/api/nse-status` | `GET` | Check NSE market status (open/closed). |

---

## 🗺️ Roadmap & Future Milestones

| Phase | Milestone | Description | Status |
| :--- | :--- | :--- | :---: |
| **Phase 1** | 📊 Multi-Model Predictions | Integrate LSTM, XGBoost, and Prophet models for comparison. | ⏳ Planned |
| **Phase 2** | 📈 Advanced Technical Charts | Embed interactive TradingView-style charting for live indicator overlays. | ⏳ Planned |
| **Phase 3** | 💼 Portfolio Simulations | Enable backtesting on mock portfolios with custom transaction logs. | ⏳ Planned |
| **Phase 4** | 🧠 Semantic Vector Search (RAG) | Query multiple annual reports using AI embeddings and pgvector search. | ⏳ Planned |

---

## <a id="contribute"></a>🤝 Contribution

We welcome contributions to make **StockSense** even better! Here is how you can get started:

1. **Fork the Repository**  
   Click the **Fork** button at the top-right of this repository page to create a copy in your GitHub account.

2. **Clone your Fork**  
   ```bash
   git clone https://github.com/your-username/stocksense-react.git
   cd stocksense-react
   ```

3. **Create a Feature Branch**  
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **Make & Commit Changes**  
   Please follow the design style of the project and ensure your code is clean:
   ```bash
   git commit -m "feat: add support for dynamic portfolio tracking"
   ```

5. **Push to GitHub**  
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Submit a Pull Request**  
   Go to the original repository on GitHub and open a Pull Request. Describe your changes clearly in the PR description.

### 📝 Contribution Guidelines
* **Code Styling:** Keep the dark terminal-style aesthetic intact when making UI modifications.
* **Testing:** Ensure the FastAPI gateway (`python -m stocks.main`) starts up cleanly without throwing dependency errors.
* **Documentation:** If you add new microservice endpoints, update the API Reference table in this README.

---

> ⚠️ **Disclaimer:** StockSense is an educational software application designed to demonstrate data engineering and ML concepts. It does not constitute financial advice. Always consult a certified financial advisor before making actual stock investments.

