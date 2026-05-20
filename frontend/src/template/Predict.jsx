import React, { useState } from "react";
import SpaceBackgroundOverlay from "../components/SpaceBackgroundOverlay";

export default function Predict({ ticker, info, predict }) {
  const [zoomed, setZoomed] = useState(false);

  if (!predict) {
    return null;
  }

  // Sentiment analysis sentences
  const sentimentSentences = {
    sell: [
      "Strong downward momentum detected. Consider liquidating your position to minimize losses.",
      "Market signals suggest a significant decline ahead. It's advisable to exit this investment.",
      "Technical indicators point to deteriorating conditions. Selling now could protect your capital.",
      "Bearish patterns emerging. This is a critical moment to divest before further depreciation."
    ],
    buy: [
      "Positive indicators show steady growth potential. This is a good opportunity to invest.",
      "Market fundamentals support upward movement. Consider building a position at current levels.",
      "Bullish signals suggest appreciation ahead. Now is an opportune time to accumulate shares.",
      "Technical analysis indicates strength. Adding to your portfolio could yield good returns."
    ],
    "strong buy": [
      "Exceptional buy signals across all indicators. This is a prime opportunity to maximize gains.",
      "Compelling fundamentals with explosive growth potential. Aggressive buying is recommended.",
      "All technical and fundamental indicators align bullishly. This demands immediate action.",
      "Outstanding opportunity with high profit potential. Consider increasing your position significantly."
    ],
    hold: [
      "Current valuations are fair. Maintain your position and monitor for better entry/exit points.",
      "Mixed signals suggest stability. Holding your shares is the prudent strategy.",
      "Market conditions are neutral. There's no compelling reason to change your current stance.",
      "The stock is consolidating. Keep your holdings while waiting for clearer directional signals."
    ],
    neutral: [
      "Market data is inconclusive. Wait for more clarity before making investment decisions.",
      "No strong directional bias detected. Consider gathering more information before acting.",
      "Indicators are mixed and conflicting. Patience is recommended until trends become clearer.",
      "Current conditions lack conviction. Hold steady and reassess when market signals strengthen."
    ]
  };

  // Get sentiment label from predict object
  const sentimentLabel = predict?.label ? predict.label.toLowerCase() : 'neutral';
  const sentences = sentimentSentences[sentimentLabel] || sentimentSentences.neutral;

  // Get a random sentence (optional: you can cycle through them)
  const getRandomSentence = (index = 0) => sentences[index % sentences.length];

  const imgSrc =
    typeof predict === 'string'
      ? (predict.startsWith('data:') ? predict : `data:image/png;base64,${predict}`)
      : predict.image
        ? (predict.image.startsWith('data:') ? predict.image : `data:image/png;base64,${predict.image}`)
        : '';

  return (
    <>
      <SpaceBackgroundOverlay />
      <div className="relative z-10 min-h-screen p-4 md:p-8 bg-[#050b0f]/35 text-slate-200">
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
          {/* Sentiment Analysis Section */}
          <div className="mb-8 bg-slate-900/50 border border-cyan-900/30 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="w-3 h-3 rounded-full bg-amber-500 animate-pulse"></span>
              <h3 className="text-sm font-black text-amber-500 tracking-[0.15em] uppercase">
                AI Sentiment Analysis
              </h3>
            </div>
            
            <div className="mb-6 pb-4 border-b border-cyan-900/20">
              <div className={`inline-block px-4 py-2 rounded-lg font-bold text-lg uppercase tracking-wider ${
                sentimentLabel === 'strong buy' ? 'bg-green-900/40 text-green-400 border border-green-700' :
                sentimentLabel === 'buy' ? 'bg-emerald-900/40 text-emerald-400 border border-emerald-700' :
                sentimentLabel === 'hold' ? 'bg-blue-900/40 text-blue-400 border border-blue-700' :
                sentimentLabel === 'sell' ? 'bg-red-900/40 text-red-400 border border-red-700' :
                'bg-slate-700/40 text-slate-300 border border-slate-600'
              }`}>
                {sentimentLabel}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {sentences.map((sentence, index) => (
                <div key={index} className="flex gap-3 items-start bg-black/30 p-4 rounded border border-cyan-900/20 hover:border-cyan-900/50 transition-all">
                  <span className="text-cyan-500 font-bold flex-shrink-0 text-lg">{index + 1}</span>
                  <p className="text-slate-300 text-sm leading-relaxed">{sentence}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Chart Section */}
          <div>
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
    </>
  );
}
