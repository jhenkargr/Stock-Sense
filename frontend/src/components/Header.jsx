
import { useClock } from '../hooks/useClock'
import { Link } from 'react-router-dom'
import React, { useEffect, useState } from 'react';

const rawUrl = import.meta.env.VITE_REQUEST_URL || "http://localhost:8006";
const REQUEST_BASE = rawUrl.startsWith("http")
  ? rawUrl
  : rawUrl.includes("localhost") || rawUrl.includes("127.0.0.1")
  ? `http://${rawUrl}`
  : `https://${rawUrl}`;

const VERSION = "V2.4";

// Calculate market status based on NSE trading hours (Mon-Fri 09:15 - 15:30 IST)
const getIstMarketStatus = () => {
  const now = new Date();
  // Get time in IST (UTC + 5:30)
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const ist = new Date(utc + 5.5 * 3600000);
  const day = ist.getDay(); // 0 = Sunday, 6 = Saturday
  const minutes = ist.getHours() * 60 + ist.getMinutes();
  const isOpen = day >= 1 && day <= 5 && minutes >= 555 && minutes <= 930;
  return isOpen ? "Open" : "Closed";
};

const Header = () => {
  const time = useClock();
  const [marketStatus, setMarketStatus] = useState(getIstMarketStatus);

  useEffect(() => {
    const fetchMarketStatus = async () => {
      try {
        const response = await fetch(`${REQUEST_BASE}/marketstatus/api/nse-status`);

        if (response.ok) {
          const data = await response.json();
          if (data && data["Capital Market"]) {
            setMarketStatus(data["Capital Market"]);
            return;
          }
        }
        setMarketStatus(getIstMarketStatus());
      } catch {
        setMarketStatus(getIstMarketStatus());
      }
    };

    fetchMarketStatus();
    const interval = setInterval(fetchMarketStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  const isMarketOpen = marketStatus.toLowerCase() === "open";

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
