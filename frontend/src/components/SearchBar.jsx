import React, { useState, useEffect, useRef } from 'react';
import LoadingIndicator from './Loadingindicator';
import StockAnalyzer from '../template/StockAnalyzer';


const SearchBar = () => {
  const [ticker, setTicker] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [predict, setPredict] = useState(null)
  const [info, setInfo] = useState(null);
  const [error, setError] = useState(null);
  const [stocks, setStocks] = useState([]);
  const [stocksLoading, setStocksLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [activeIdx, setActiveIdx] = useState(-1);
  const dropdownRef = useRef(null);

  // Load all NSE stocks from backend on mount



  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setSuggestions([]);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleChange = (e) => {
    const val = e.target.value.toUpperCase();
    setTicker(val);
    setActiveIdx(-1);

    if (val.length < 1) {
      setSuggestions([]);
      return;
    }

    // Symbol match (starts with) ranked above name match (contains)
    const q = val.toUpperCase();
    const bySymbol = stocks.filter((s) => s.symbol?.startsWith(q));
    const byName = stocks.filter((s) => !s.symbol?.startsWith(q) && s.name?.toUpperCase().includes(q));
    setSuggestions([...bySymbol, ...byName].slice(0, 8));
  };

  const handleSelect = (stock) => {
    // Append .NS suffix for yfinance
    const sym = stock.symbol;
    setTicker(stock.symbol);   // show clean symbol in input
    setSuggestions([]);
    setActiveIdx(-1);
    search(sym);               // search with .NS
  };

  const handleKeyDown = (e) => {
    if (!suggestions.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIdx((prev) => Math.min(prev + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIdx((prev) => Math.max(prev - 1, 0));
    } else if (e.key === "Enter" && activeIdx >= 0) {
      e.preventDefault();
      handleSelect(suggestions[activeIdx]);
    } else if (e.key === "Escape") {
      setSuggestions([]);
    }
  };

  const search = async (sym = ticker) => {
    // Auto-append .NS if user typed raw symbol and submitted mansym
    setLoading(true);
    setIsSearching(true);
    setError(null);
    setSuggestions([]);
    try {
      const [res, res2, res3] = await Promise.all([
        fetch(`http://localhost:8003/stocks?ticker=${sym}`),
        fetch(`http://localhost:8003/live?ticker=${sym}`),
        fetch(`http://localhost:8007/analysis?ticker=${sym}`)
      ]);

      if (!res.ok || !res2.ok || !res3.ok) throw new Error("Server error");

      const [data, data2, data3] = await Promise.all([res.json(), res2.json(), res3.json()]);

      setResult(data);
      setInfo(data2);
      setPredict(data3);
      console.log(data3)

    } catch (err) {
      console.error(err.message);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    search(ticker);
  };

  const QUICK_PICKS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "WIPRO", "SBIN"];

  return (
    <div className={`transition-all duration-700 ease-in-out ${isSearching ? 'mt-4 mb-10' : 'mb-24'}`}>
      <form onSubmit={handleSubmit} className="max-w-2xl mx-auto relative group" ref={dropdownRef}>
        <div className="flex items-stretch border border-cyan-900/50 bg-black/80 rounded overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.5)] focus-within:border-cyan-500/50 transition-all duration-300">
          <div className="px-6 py-5 flex items-center justify-center bg-cyan-950/10 border-r border-cyan-900/50">
            <span className="text-[11px] font-black text-cyan-500 tracking-[0.2em] uppercase">TICKER ›</span>
          </div>
          <input
            type="text"
            value={ticker}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={stocksLoading ? "LOADING STOCKS..." : "SEARCH NSE STOCK..."}
            disabled={stocksLoading}
            className="flex-1 bg-transparent px-8 py-5 outline-none text-cyan-100 placeholder:text-cyan-900/50 font-bold tracking-[0.2em] uppercase disabled:opacity-40"
          />
          <button
            type="submit"
            disabled={loading || stocksLoading}
            className="bg-cyan-400 hover:bg-cyan-300 disabled:bg-cyan-950 text-black px-12 font-black tracking-[0.2em] uppercase transition-all flex items-center gap-2 relative overflow-hidden"
          >
            <span className="relative z-10">{loading ? 'BUSY' : 'ANALYSE'}</span>
            {loading && <div className="absolute inset-0 bg-cyan-500/20" />}
          </button>
        </div>

        {/* Autocomplete Dropdown */}
        {suggestions.length > 0 && (
          <ul className="absolute top-full left-0 right-0 z-50 border border-cyan-900/50 bg-black/95 rounded mt-1 overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.8)] max-h-72 overflow-y-auto">
            {suggestions.map((stock, i) => (
              <li
                key={stock.symbol}
                onMouseDown={() => handleSelect(stock)}
                onMouseEnter={() => setActiveIdx(i)}
                className={`flex items-center gap-4 px-6 py-3 cursor-pointer transition-colors border-b border-cyan-950/50 last:border-b-0
                  ${i === activeIdx ? 'bg-cyan-950/60' : 'hover:bg-cyan-950/30'}`}
              >
                <span className="text-[11px] font-black text-cyan-400 tracking-[0.15em] min-w-[100px]">
                  {stock.symbol}
                </span>
                <span className="text-[12px] text-cyan-700 tracking-wider truncate">
                  {stock.name}
                </span>
                <span className="ml-auto text-[10px] text-cyan-900 tracking-widest">
                  NSE
                </span>
              </li>
            ))}
          </ul>
        )}

        {/* Quick pick chips */}
        {!isSearching && (
          <div className="flex justify-center gap-4 mt-6 animate-in fade-in duration-1000 delay-500">
            {QUICK_PICKS.map((sym) => (
              <button
                key={sym}
                type="button"
                onClick={() => {
                  setTicker(sym);
                  search(sym + ".NS");
                }}
                className="text-[10px] border border-cyan-950/50 px-4 py-1.5 text-cyan-900 hover:border-cyan-500 hover:text-cyan-400 transition-all tracking-[0.2em] font-black rounded"
              >
                {sym}
              </button>
            ))}
          </div>
        )}
      </form>

      {/* Loading */}
      {loading && <LoadingIndicator />}

      {/* Error */}
      {error && (
        <p className="text-center text-red-500 mt-4 tracking-widest text-sm">{error}</p>
      )}

      {/* Result */}
      {result && !loading && (
        <div>
          <StockAnalyzer stock={ticker} ticker={result} info={info} predict={predict} />
        </div>
      )}


    </div>
  );
};

export default SearchBar;