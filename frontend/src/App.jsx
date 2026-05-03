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

import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import BackgroundOverlay from "./components/BackgroundOverlay";
import StockAnalyzer from "./template/StockAnalyzer";
import Home from "./template/Home"
import Header from "./Components/Header";
import Footer from "./Components/Footer";



function App() {
  return (
    <Router>
     <BackgroundOverlay/>
     <div>
      <Header/>
     </div>
      <div > {/* prevents content from hiding behind fixed Navbar */}

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analyse" element={<StockAnalyzer/>}/>
        
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
