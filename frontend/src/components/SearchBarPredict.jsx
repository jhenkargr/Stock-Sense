import React, { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";

const QUICK_TICKERS = [
  { symbol: "RELIANCE", name: "Reliance Industries" },
  { symbol: "TCS", name: "Tata Consultancy Services" },
  { symbol: "HDFCBANK", name: "HDFC Bank" },
  { symbol: "INFY", name: "Infosys" },
  { symbol: "SBIN", name: "State Bank of India" },
];

const REQUEST_BASE =
  (import.meta.env.VITE_REQUEST_URL || "http://localhost:8006").startsWith("http")
    ? import.meta.env.VITE_REQUEST_URL || "http://localhost:8006"
    : `http://${import.meta.env.VITE_REQUEST_URL || "localhost:8006"}`;

const SearchBarPredict = ({ onSearch }) => {
  const [ticker, setTicker] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [activeIdx, setActiveIdx] = useState(-1);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [suggestionsLocked, setSuggestionsLocked] = useState(false);

  const dropdownRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setSuggestions([]);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const fetchSuggestions = async (query) => {
    if (suggestionsLocked) {
      setSuggestions([]);
      return;
    }
    if (!query || query.trim().length === 0) {
      setSuggestions([]);
      return;
    }

    setSuggestionsLoading(true);
    try {
      const res = await fetch(`${REQUEST_BASE}/suggestion/stocks/suggest?q=${query}`);
      if (res.ok) {
        const data = await res.json();
        const result = Array.isArray(data) ? data : data.suggestions || [];
        setSuggestions(result);
      } else {
        setSuggestions([]);
      }
    } catch (err) {
      console.error("Suggestions fetch error:", err);
      setSuggestions([]);
    } finally {
      setSuggestionsLoading(false);
    }
  };

  const handleChange = async (e) => {
    const value = e.target.value.toUpperCase();
    setTicker(value);
    setActiveIdx(-1);
    setSuggestionsLocked(false);
    await fetchSuggestions(value);
  };

  const handleSelect = async (stock) => {
    const sym = stock.symbol || stock;
    setTicker(sym);
    setActiveIdx(-1);
    setSuggestionsLocked(true);
    setSuggestions([]);
    if (onSearch) onSearch(sym);
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleKeyDown = async (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIdx((prev) => Math.min(prev + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIdx((prev) => Math.max(prev - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (activeIdx >= 0 && suggestions[activeIdx]) {
        handleSelect(suggestions[activeIdx]);
      } else if (ticker && onSearch) {
        onSearch(ticker);
        setSuggestionsLocked(true);
        setSuggestions([]);
      }
    } else if (e.key === "Escape") {
      setSuggestions([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!ticker) return;
    if (onSearch) onSearch(ticker);
    setSuggestionsLocked(true);
    setSuggestions([]);
    inputRef.current?.focus();
  };

  const handleFocus = async () => {
    if (!suggestionsLocked && ticker.length > 0) await fetchSuggestions(ticker);
  };

  return (
    <div className="relative isolate max-w-2xl mx-auto group">
      <form onSubmit={handleSubmit} ref={dropdownRef} className="relative z-10">
        <div className="flex items-stretch border border-cyan-900/50 bg-black/80 rounded overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.5)] focus-within:border-cyan-500/50 transition-all duration-300">
          <div className="px-6 py-5 flex items-center justify-center bg-cyan-950/10 border-r border-cyan-900/50">
            <span className="text-[11px] font-black text-cyan-500 tracking-[0.2em] uppercase">TICKER ›</span>
          </div>

          <input
            ref={inputRef}
            type="text"
            value={ticker}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onFocus={handleFocus}
            placeholder={suggestionsLoading ? "LOADING..." : "SEARCH NSE STOCK..."}
            className="flex-1 bg-transparent px-8 py-5 outline-none text-cyan-100 placeholder:text-cyan-900/50 font-bold tracking-[0.2em] uppercase"
          />

          <button type="submit" disabled={suggestionsLoading || !ticker} className="bg-cyan-400 hover:bg-cyan-300 disabled:bg-cyan-950 text-black px-12 font-black tracking-[0.2em] uppercase transition-all">ANALYSE</button>
        </div>

        {suggestions.length > 0 && (
          <ul className="absolute top-full left-0 right-0 z-50 border border-cyan-900/50 bg-black/95 rounded mt-1 overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.8)] max-h-72 overflow-y-auto">
            {suggestions.map((stock, i) => (
              <li key={stock.symbol || stock}>
                <button type="button" onMouseDown={() => handleSelect(stock)} onMouseEnter={() => setActiveIdx(i)} className={`flex w-full items-center gap-4 px-6 py-3 text-left cursor-pointer transition-colors border-b border-cyan-950/50 last:border-b-0 ${i === activeIdx ? "bg-cyan-950/60" : "hover:bg-cyan-950/30"}`}>
                  <span className="text-[11px] font-black text-cyan-400 tracking-[0.15em] min-w-[100px]">{stock.symbol || stock}</span>
                  <span className="text-[12px] text-cyan-700 tracking-wider truncate">{stock.name || ""}</span>
                  <span className="ml-auto text-[10px] text-cyan-900 tracking-widest">NSE</span>
                </button>
              </li>
            ))}
          </ul>
        )}

        <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
          <span className="text-[11px] font-black text-cyan-500/70 tracking-[0.2em] uppercase">QUICK SEARCH:</span>
          {QUICK_TICKERS.map((stock) => (
            <button key={stock.symbol} type="button" onClick={() => handleSelect(stock)} className="rounded-full border border-cyan-900/60 bg-cyan-950/20 px-4 py-2 text-[11px] font-black tracking-[0.18em] uppercase text-cyan-100 transition-all hover:border-cyan-400/70 hover:bg-cyan-950/50 hover:text-white">{stock.symbol}</button>
          ))}
        </div>
      </form>
    </div>
  );
};

SearchBarPredict.propTypes = {
  onSearch: PropTypes.func,
};

export default SearchBarPredict;
