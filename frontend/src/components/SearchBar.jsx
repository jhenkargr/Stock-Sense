import React, { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import SpaceBackgroundOverlay from "./SpaceBackgroundOverlay";

const QUICK_TICKERS = [
  { symbol: "RELIANCE", name: "Reliance Industries" },
  { symbol: "TCS", name: "Tata Consultancy Services" },
  { symbol: "HDFCBANK", name: "HDFC Bank" },
  { symbol: "INFY", name: "Infosys" },
  { symbol: "SBIN", name: "State Bank of India" },
];

const SearchBar = ({ onSearch }) => {
  const [ticker, setTicker] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [activeIdx, setActiveIdx] = useState(-1);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [suggestionsLocked, setSuggestionsLocked] = useState(false);

  const dropdownRef = useRef(null);
  const inputRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target)
      ) {
        setSuggestions([]);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Fetch suggestions from port 8009
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
      const res = await fetch(
        `http://localhost:8009/stocks/suggest?q=${query}`
      );

      if (res.ok) {
        const data = await res.json();

        const result = Array.isArray(data)
          ? data
          : data.suggestions || [];

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

  // Handle typing
  const handleChange = async (e) => {
    const value = e.target.value.toUpperCase();

    setTicker(value);
    setActiveIdx(-1);
    setSuggestionsLocked(false);

    await fetchSuggestions(value);
  };

  // Handle stock selection
  const handleSelect = async (stock) => {
    const sym = stock.symbol || stock;

    setTicker(sym);
    setActiveIdx(-1);
    setSuggestionsLocked(true);
    setSuggestions([]);

    // Trigger search
    if (onSearch) {
      onSearch(sym);
    }

    // Keep focus on input
    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  };

  // Keyboard navigation
  const handleKeyDown = async (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();

      setActiveIdx((prev) =>
        Math.min(prev + 1, suggestions.length - 1)
      );
    }

    else if (e.key === "ArrowUp") {
      e.preventDefault();

      setActiveIdx((prev) =>
        Math.max(prev - 1, 0)
      );
    }

    else if (e.key === "Enter") {
      e.preventDefault();

      // Select highlighted suggestion
      if (activeIdx >= 0 && suggestions[activeIdx]) {
        handleSelect(suggestions[activeIdx]);
      }

      // Search current ticker
      else if (ticker && onSearch) {
        onSearch(ticker);
        setSuggestionsLocked(true);
        setSuggestions([]);
      }
    }

    else if (e.key === "Escape") {
      setSuggestions([]);
    }
  };

  // Submit button
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!ticker) return;

    if (onSearch) {
      onSearch(ticker);
    }

    setSuggestionsLocked(true);
    setSuggestions([]);

    inputRef.current?.focus();
  };

  // Refetch on focus
  const handleFocus = async () => {
    if (!suggestionsLocked && ticker.length > 0) {
      await fetchSuggestions(ticker);
    }
  };

  return (
    <div className="relative isolate max-w-2xl mx-auto group">
      <SpaceBackgroundOverlay />
      <section className="relative z-10 mb-6 text-center max-w-2xl mx-auto">
        <p className="text-[11px] md:text-xs tracking-[0.5em] uppercase font-black text-cyan-500/80 mb-3">
          Detailed Stock Analyser
        </p>
        <h2 className="text-4xl md:text-5xl font-black tracking-tighter leading-none uppercase text-white max-w-none">
          Search a stock to inspect the full report
        </h2>
        <p className="mt-4 text-sm md:text-base text-cyan-100/70 tracking-wide">
          Enter a ticker below to load live data, company overview, AI simplifier output, and fundamentals.
        </p>
      </section>

      <form
        onSubmit={handleSubmit}
        ref={dropdownRef}
        className="relative z-10"
      >
        <div className="flex items-stretch border border-cyan-900/50 bg-black/80 rounded overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.5)] focus-within:border-cyan-500/50 transition-all duration-300">

        {/* Left Label */}
        <div className="px-6 py-5 flex items-center justify-center bg-cyan-950/10 border-r border-cyan-900/50">
          <span className="text-[11px] font-black text-cyan-500 tracking-[0.2em] uppercase">
            TICKER ›
          </span>
        </div>

        {/* Input */}
        <input
          ref={inputRef}
          type="text"
          value={ticker}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          placeholder={
            suggestionsLoading
              ? "LOADING..."
              : "SEARCH NSE STOCK..."
          }
          className="flex-1 bg-transparent px-8 py-5 outline-none text-cyan-100 placeholder:text-cyan-900/50 font-bold tracking-[0.2em] uppercase"
        />

        {/* Button */}
        <button
          type="submit"
          disabled={suggestionsLoading || !ticker}
          className="bg-cyan-400 hover:bg-cyan-300 disabled:bg-cyan-950 text-black px-12 font-black tracking-[0.2em] uppercase transition-all"
        >
          ANALYSE
        </button>
        </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <ul className="absolute top-full left-0 right-0 z-50 border border-cyan-900/50 bg-black/95 rounded mt-1 overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.8)] max-h-72 overflow-y-auto">

          {suggestions.map((stock, i) => (
            <li
              key={stock.symbol || stock}
            >
              <button
                type="button"
                onMouseDown={() => handleSelect(stock)}
                onMouseEnter={() => setActiveIdx(i)}
                className={`flex w-full items-center gap-4 px-6 py-3 text-left cursor-pointer transition-colors border-b border-cyan-950/50 last:border-b-0
                ${
                  i === activeIdx
                    ? "bg-cyan-950/60"
                    : "hover:bg-cyan-950/30"
                }`}
              >
                <span className="text-[11px] font-black text-cyan-400 tracking-[0.15em] min-w-[100px]">
                  {stock.symbol || stock}
                </span>

                <span className="text-[12px] text-cyan-700 tracking-wider truncate">
                  {stock.name || ""}
                </span>

                <span className="ml-auto text-[10px] text-cyan-900 tracking-widest">
                  NSE
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
        <span className="text-[11px] font-black text-cyan-500/70 tracking-[0.2em] uppercase">
          QUICK SEARCH:
        </span>

        {QUICK_TICKERS.map((stock) => (
          <button
            key={stock.symbol}
            type="button"
            onClick={() => handleSelect(stock)}
            className="rounded-full border border-cyan-900/60 bg-cyan-950/20 px-4 py-2 text-[11px] font-black tracking-[0.18em] uppercase text-cyan-100 transition-all hover:border-cyan-400/70 hover:bg-cyan-950/50 hover:text-white"
          >
            {stock.symbol}
          </button>
        ))}
      </div>
      </form>
    </div>
  );
};

SearchBar.propTypes = {
  onSearch: PropTypes.func,
};

export default SearchBar;