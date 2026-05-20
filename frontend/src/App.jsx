/*import { useState, useCallback } from 'react'
import Header from './components/Header'
import SearchBar from './components/SearchBar'
import LoadingSpinner from './components/LoadingSpinner'
import ResultsDashboard from './components/ResultsDashboard'
import { STOCK_DB, generateUnknown } from './data/stocks'

export default function App() {
  const [state, setState] = useState('idle') // 'idle' | 'loading' | 'results'
  const [ticker, setTicker] = useState('')
  const [data, setData] = useState(null)

  const handleSearch = useCallback((raw) => {
    setState('loading')
    setTicker(raw)

    setTimeout(() => {
      const result = STOCK_DB[raw] || generateUnknown(raw)
      setData(result)
      setState('results')
      // Scroll to results smoothly
      requestAnimationFrame(() => {
        document.getElementById('results-anchor')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      })
    }, 1200)
  }, [])

  return (
    <div className="bg-bg min-h-screen scanlines relative">
      {/* Background grid *//*}
      <div className="fixed inset-0 bg-grid pointer-events-none z-0" />

      <div className="relative z-10">
        <Header />

        <main className="max-w-7xl mx-auto px-6">
          <SearchBar onSearch={handleSearch} />

          <div id="results-anchor" />

          {state === 'loading' && <LoadingSpinner />}
          {state === 'results' && data && (
            <ResultsDashboard ticker={ticker} data={data} />
          )}
        </main>

        <footer className="border-t border-[#0d2235] py-5 text-center relative z-10">
          <p className="font-mono text-[10px] text-muted tracking-[2px]">
            STOCKSENSE // FOR EDUCATIONAL PURPOSES ONLY · NOT FINANCIAL ADVICE · DATA IS SIMULATED
          </p>
        </footer>
      </div>
    </div>
  )
}*/

import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import BackgroundOverlay from "./components/BackgroundOverlay";
import StockAnalyzer from "./template/StockAnalyzer";
import Predict from "./template/Predict";
import Home from "./template/Home"
import Header from "./components/Header";
import Footer from "./components/Footer";
import SearchBar from "./components/SearchBar";
import LoadingIndicator from "./components/Loadingindicator";

function AnalysePage() {
  const [ticker, setTicker] = useState(null);
  const [result, setResult] = useState(null);
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (sym) => {
    setLoading(true);
    setError(null);
    try {
      const [res, res2] = await Promise.all([
        fetch(`http://localhost:8003/stocks?ticker=${sym}`),
        fetch(`http://localhost:8003/live?ticker=${sym}`)
      ]);

      if (!res.ok || !res2.ok) throw new Error("Server error");

      const [data, data2] = await Promise.all([res.json(), res2.json()]);

      setTicker(sym);
      setResult(data);
      setInfo(data2);
    } catch (err) {
      console.error(err.message);
      setError(err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative z-10 max-w-7xl mx-auto px-6 py-14 md:py-20">
      <SearchBar onSearch={handleSearch} />

      <div className="mt-12 md:mt-16">
        {loading && <LoadingIndicator />}
        {error && <p className="text-center text-red-500 mt-4 tracking-widest text-sm">{error}</p>}
        {result && !loading && (
          <div>
            <StockAnalyzer stock={ticker} ticker={result} info={info} />
          </div>
        )}
      </div>
    </main>
  );
}

function PredictPage() {
  const [ticker, setTicker] = useState(null);
  const [info, setInfo] = useState(null);
  const [predict, setPredict] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (sym) => {
    setLoading(true);
    setError(null);
    try {
      const [res, res2] = await Promise.all([
        fetch(`http://localhost:8003/live?ticker=${sym}`),
        fetch(`http://localhost:8007/analysis?ticker=${sym}`)
      ]);

      if (!res.ok || !res2.ok) throw new Error("Server error");

      const [data, data2] = await Promise.all([res.json(), res2.json()]);

      setTicker(sym);
      setInfo(data);
      setPredict(data2);
    } catch (err) {
      console.error(err.message);
      setError(err.message);
      setPredict(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative z-10 max-w-7xl mx-auto px-6 py-14 md:py-20">
      <section className="text-center max-w-3xl mx-auto mt-8 md:mt-14 mb-12">
        <p className="text-[11px] md:text-xs tracking-[0.5em] uppercase font-black text-cyan-500/80 mb-4">
          AI Based Stock Predictor
        </p>
        <h2 className="text-4xl md:text-6xl font-black tracking-tighter leading-none uppercase text-white">
          Run prediction analysis for any ticker
        </h2>
        <p className="mt-5 text-sm md:text-base text-cyan-100/70 tracking-wide">
          Enter a ticker to get AI-powered price forecasts and prediction charts.
        </p>
      </section>
      <SearchBar onSearch={handleSearch} />

      <div className="mt-12 md:mt-16">
        {loading && <LoadingIndicator />}
        {error && <p className="text-center text-red-500 mt-4 tracking-widest text-sm">{error}</p>}
        {predict && !loading && (
          <div>
            <Predict ticker={ticker} info={info} predict={predict} />
          </div>
        )}
      </div>
    </main>
  );
}



function App() {
  return (
    <Router>
     <BackgroundOverlay/>
     <div>
      <Header/>
     </div>
      <div className="pt-24 md:pt-28"> {/* prevents content from hiding behind fixed Navbar */}

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analyse" element={<AnalysePage />} />
          <Route path="/predict" element={<PredictPage />} />
        
          {/* You can add more routes later like: */}
          {/* <Route path="/simplify" element={<SimplifyDocs />} /> */}
          {/* <Route path="/templates" element={<Templates />} /> */}
          {/* <Route path="/lawyers" element={<FindLawyers />} /> */}
        </Routes>
      </div>
      <div>
        <Footer/>
      </div>
      
    </Router>
  );
}

export default App;
