/*import { useClock } from '../hooks/useClock'

export default function Header() {
  const time = useClock()

  return (
    <header className="border-b border-[#0d2235] py-5 relative z-10">
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        {/* Logo *}
        <div className="flex items-baseline gap-3">
          <span className="font-display text-xl font-black tracking-[4px] text-accent text-glow-accent">
            STOCKSENSE
          </span>
          <span className="font-mono text-[10px] text-muted tracking-[3px]">
            // MARKET ANALYSER v2.4
          </span>
        </div>

        {/* Right side *}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-accent2 shadow-[0_0_8px_#00ff9d] animate-pulse_dot" />
            <span className="font-mono text-[11px] text-accent2 tracking-[2px]">MARKET OPEN</span>
          </div>
          <span className="font-mono text-xs text-muted tracking-[2px]">{time}</span>
        </div>
      </div>
    </header>
  )
}*/
import { useClock } from '../hooks/useClock'
import React from 'react';

const VERSION = "V2.4";

const Header = () => {
  const time = useClock()
  return (
    <header className="relative z-50 border-b border-cyan-950/30 bg-black/40 backdrop-blur-md px-8 py-5 flex justify-between items-center">
      <div className="flex items-center gap-5">
        <h1 className="text-2xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 drop-shadow-[0_0_12px_rgba(34,211,238,0.6)]">
          STOCKSENSE
        </h1>
        <span className="text-[10px] text-cyan-800 tracking-[0.3em] mt-1 uppercase font-bold opacity-60">
          // MARKET ANALYSER {VERSION}
        </span>
      </div>

      <div className="flex items-center gap-8 text-[11px] tracking-[0.2em] font-bold">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_#10b981]"></span>
          <span className="text-emerald-400">MARKET OPEN</span>
        </div>
        <div className="text-cyan-500 tabular-nums">
          {time}
        </div>
      </div>
    </header>
  );
};

export default Header;
