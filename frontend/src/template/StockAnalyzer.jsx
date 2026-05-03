import React, { useState } from "react";
import CashFlowTable from "../components/CashFlowTable";


export default function StockAnalyzer({ ticker, stock, info, predict }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const [zoomed, setZoomed] = useState(false);
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

        {/* Prediction Chart */}
        {predict && (() => {
          const imgSrc =
            typeof predict === 'string'
              ? (predict.startsWith('data:') ? predict : `data:image/png;base64,${predict}`)
              : predict.image
                ? (predict.image.startsWith('data:') ? predict.image : `data:image/png;base64,${predict.image}`)
                : '';
          return (
            <>
              <div className="w-full mt-10">
                <div className="px-2 py-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                    <h3 className="text-[11px] font-black text-cyan-500 tracking-[0.25em] uppercase">
                      Prediction Forecast
                    </h3>
                  </div>
                  <button
                    onClick={() => setZoomed(true)}
                    className="flex items-center gap-2 text-[10px] font-black tracking-[0.15em] uppercase text-cyan-600 border border-cyan-900/50 px-3 py-1.5 rounded hover:border-cyan-500 hover:text-cyan-400 transition-all"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16zM11 8v6M8 11h6" />
                    </svg>
                    Zoom
                  </button>
                </div>
                <div className="flex justify-center items-center">
                  <img
                    src={imgSrc}
                    alt="Stock price prediction chart"
                    onClick={() => setZoomed(true)}
                    style={{ mixBlendMode: 'lighten' }}
                    className="w-full h-auto cursor-zoom-in"
                  />
                </div>
              </div>

              {/* Zoom Overlay */}
              {zoomed && (
                <div
                  className="fixed inset-0 z-[9999] bg-black/95 flex items-center justify-center p-6"
                  onClick={() => setZoomed(false)}
                  onKeyDown={(e) => e.key === 'Escape' && setZoomed(false)}
                  tabIndex={0}
                  ref={(el) => el && el.focus()}
                >
                  <button
                    onClick={(e) => { e.stopPropagation(); setZoomed(false); }}
                    className="absolute top-6 right-6 text-cyan-400 hover:text-cyan-300 transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                  <img
                    src={imgSrc}
                    alt="Stock price prediction chart — zoomed"
                    onClick={(e) => e.stopPropagation()}
                    style={{ mixBlendMode: 'lighten' }}
                    className="max-w-[95vw] max-h-[90vh] object-contain rounded-lg"
                  />
                </div>
              )}
            </>
          );
        })()}

        {/* AI Analysis */}
        <div className="border border-cyan-900 bg-slate-900/30 p-8">

          <div className="inline-block bg-cyan-500 text-black px-4 py-1 text-xs font-bold mb-6">
            AI ANALYSIS
          </div>

          <p className="leading-relaxed text-slate-300 text-lg pb-90">
            <strong className="text-white">Apple Inc.</strong> remains a
            fundamentally dominant company with an exceptional gross profit
            margin of <span className="text-green-400">43.2%</span>. The P/E
            ratio of <span className="text-yellow-400">28.4x</span> is slightly
            elevated but justified given consistent EPS growth and an
            extraordinary ROE of <span className="text-green-400">147%</span>.
          </p>

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