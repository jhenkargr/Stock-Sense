
import { useClock } from '../hooks/useClock'
import { Link } from 'react-router-dom'
import React, { useEffect, useState } from 'react';

const VERSION = "V2.4";

const Header = () => {
  const time = useClock()
  const [marketStatus, setMarketStatus] = useState("Closed")

  useEffect(() => {
    const fetchMarketStatus = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8010/api/nse-status")

        if (!response.ok) {
          return
        }

        const data = await response.json()
        setMarketStatus(data?.["Capital Market"] || "Closed")
      } catch {
        setMarketStatus("Closed")
      }
    }

    fetchMarketStatus()
  }, [])

  const isMarketOpen = marketStatus.toLowerCase() === "open"

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-cyan-950/30 bg-black/40 backdrop-blur-md px-8 py-5 flex justify-between items-center">
      <div className="flex items-center gap-5">
        <Link
          to="/"
          className="text-2xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 drop-shadow-[0_0_12px_rgba(34,211,238,0.6)] transition-opacity hover:opacity-80"
        >
          STOCKSENSE
        </Link>
        <span className="text-[10px] text-cyan-800 tracking-[0.3em] mt-1 uppercase font-bold opacity-60">
          {`// MARKET ANALYSER ${VERSION}`}
        </span>
      </div>

      <div className="flex items-center gap-8 text-[11px] tracking-[0.2em] font-bold">
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full shadow-[0_0_10px_#10b981] ${
              isMarketOpen ? "bg-emerald-500" : "bg-red-500"
            }`}
          ></span>
          <span className={isMarketOpen ? "text-emerald-400" : "text-red-400"}>
            MARKET {isMarketOpen ? "OPENED" : "CLOSED"}
          </span>
        </div>
        <div className="text-cyan-500 tabular-nums">
          {time}
        </div>
      </div>
    </header>
  );
};

export default Header;
