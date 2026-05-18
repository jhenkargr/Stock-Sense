import React, { useState } from "react";

export default function Predict({ ticker, info, predict }) {
  const [zoomed, setZoomed] = useState(false);

  if (!predict) {
    return null;
  }

  const imgSrc =
    typeof predict === 'string'
      ? (predict.startsWith('data:') ? predict : `data:image/png;base64,${predict}`)
      : predict.image
        ? (predict.image.startsWith('data:') ? predict.image : `data:image/png;base64,${predict.image}`)
        : '';

  return (
    <div className="min-h-screen p-4 md:p-8 bg-[#020b12] text-slate-200">
      <div className="max-w-6xl mx-auto space-y-8 pb-[190px]">
        {/* Header */}
        <div className="bg-slate-900/40 border-l-4 border-cyan-500 p-8 flex flex-col md:flex-row justify-between">
          <div>
            <h1 className="text-6xl font-black tracking-tighter text-cyan-400">
              {typeof ticker === 'string' ? ticker : ticker?.symbol}
            </h1>
            <div className="flex gap-2 mt-2 text-slate-400 text-sm">
              <span>{info?.name || ticker}</span>
              <span>•</span>
              <span>{info?.sector}</span>
            </div>
          </div>

          <div className="mt-6 md:mt-0 text-right">
            <div className="text-5xl font-bold text-green-400">{'\u20B9'}{info?.live}</div>
            <div className="flex justify-end gap-2 mt-1 text-green-400 text-sm">
              <span>▲</span>
              <span style={{ color: info?.rise > 0 ? "green" : "red" }}>
                {info?.rise > 0 ? "+" : ""}{info?.rise} {info?.percent} 1Day
              </span>
            </div>
          </div>
        </div>

        {/* Prediction Chart */}
        <div className="w-full mt-10">
          <div className="px-2 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
              <h3 className="text-[11px] font-black text-cyan-500 tracking-[0.25em] uppercase">
                AI Prediction Forecast
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
          <div className="flex justify-center items-center border border-cyan-900/30 rounded-lg p-6 bg-black/40">
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
      </div>
    </div>
  );
}
