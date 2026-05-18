import React, { useState } from "react";
import CashFlowTable from "../components/CashFlowTable";
import Simplifier from "../components/Simplifier";
import CompanyOverview from "../components/CompanyOverview";


export default function StockAnalyzer({ ticker, stock, info }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);
  return (
    <div className="min-h-screen p-4 md:p-8 bg-[#020b12] text-slate-200 ">
      <div className="max-w-6xl mx-auto space-y-8 pb-[190px]">


        {/* Header */}
        <div className="bg-slate-900/40 border-l-4 border-cyan-500 p-8 flex flex-col md:flex-row justify-between">

          <div>
            <h1 className="text-6xl font-black tracking-tighter text-cyan-400">
              {typeof stock === 'string' ? stock : stock?.symbol}
            </h1>

            <div className="flex gap-2 mt-2 text-slate-400 text-sm">
              <span>{typeof stock === 'string' ? info?.name || stock : stock?.name}</span>
              <span>•</span>


              <span>{info.sector}</span>
            </div>
          </div>

          <div className="mt-6 md:mt-0 text-right">
            <div className="text-5xl font-bold text-green-400">{'\u20B9'}{info.live}</div>

            <div className="flex justify-end gap-2 mt-1 text-green-400 text-sm">
              <span>▲</span>
              <span style={{ color: info.rise > 0 ? "green" : "red" }}>
                {info.rise > 0 ? "+" : ""}{info.rise} {info.percent} 1Day
              </span>
            </div>
          </div>

          <div className="text-right mt-4">
            <div className="text-xs text-slate-500 mb-1 uppercase">
              AI Rating
            </div>

            <button className="border-2 border-green-400 text-green-400 px-8 py-2 font-bold hover:bg-green-400/10">
              BUY
            </button>
          </div>
        </div>

        {/* Company Overview (from port 8002) */}
        <div>
          <CompanyOverview symbol={typeof stock === 'string' ? stock : stock?.symbol} />
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {ticker.map((metric, index) => (
            <div key={index} className="relative bg-black/70 border border-cyan-900/40 rounded-lg p-5 hover:border-cyan-500/40 transition-all duration-300">

              {/* Top Right — Comment Badge + Info Icon */}
              <div className="absolute top-3 right-3 flex items-center gap-2">

                {/* Comment Badge */}
                {metric.comment && (
                  <span className={`text-[9px] font-black tracking-[0.15em] uppercase px-2 py-1 rounded border ${metric.comment === "good"
                    ? "bg-green-500/10 text-green-400 border-green-500/30"
                    : "bg-red-500/10 text-red-400 border-red-500/30"
                    }`}>
                    {metric.comment === "good" ? "✓ HEALTHY" : "✗ WEAK"}
                  </span>
                )}

                {/* Info Icon */}
                <button
                  className="w-5 h-5 rounded-full border border-cyan-700 text-cyan-600 hover:border-cyan-400 hover:text-cyan-400 transition-all flex items-center justify-center text-[10px] font-black"
                  onMouseEnter={() => setHoveredIndex(index)}
                  onMouseLeave={() => setHoveredIndex(null)}
                >
                  i

                  {/* Tooltip */}
                  {hoveredIndex === index && (
                    <div className="absolute top-7 right-0 z-50 w-56 bg-black border border-cyan-800 rounded-lg p-3 text-left shadow-xl pointer-events-none">
                      <p className="text-cyan-400 font-black text-[10px] tracking-widest uppercase mb-1">
                        {metric.full_form}
                      </p>
                      <p className="text-cyan-600 text-[10px] leading-relaxed">
                        {metric.info}
                      </p>
                    </div>
                  )}
                </button>

              </div>

              {/* Title */}
              <p className="text-[11px] font-black tracking-[0.2em] uppercase text-cyan-600 mb-3 pr-24">
                {metric.key.replace(/_/g, " ")}
              </p>

              {/* Value */}
              <p className="text-2xl font-black text-cyan-100 tracking-wider">
                {metric.value ?? "N/A"}
              </p>

              {/* Note */}
              {metric.note && (
                <p className="text-[11px] text-cyan-700 mt-2 tracking-wide">
                  {metric.note}
                </p>
              )}

            </div>
          ))}
        </div>

        <div>
          <CashFlowTable ticker={stock} />
        </div>

        {/* Simplifier (AI analysis panel) */}
        <div>
          <Simplifier symbol={typeof stock === 'string' ? stock : stock?.symbol} />
        </div>

      </div>
    </div>
  );
}


function Metric({ title, value, color, width, note }) {
  return (
    <div className="bg-slate-900/60 p-6 border border-white/10">
      <div className="text-xs text-slate-500 uppercase mb-4">{title}</div>

      <div className="text-4xl font-bold mb-4">{value}</div>

      <div className="h-[2px] bg-white/10 relative mb-2">
        <div className={`${color} h-full`} style={{ width }}></div>
      </div>

      <div className="text-xs text-slate-500">{note}</div>
    </div>
  );
}