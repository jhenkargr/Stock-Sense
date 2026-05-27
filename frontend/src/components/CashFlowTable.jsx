import { useState, useEffect } from "react";

const REQUEST_BASE =
  (import.meta.env.VITE_REQUEST_URL || "http://localhost:8006").startsWith("http")
    ? import.meta.env.VITE_REQUEST_URL || "http://localhost:8006"
    : `http://${import.meta.env.VITE_REQUEST_URL || "localhost:8006"}`;

const HIGHLIGHT_ROWS = ["Free Cash Flow", "Operating Cash Flow"];

function fmt(val) {
  if (val == null) return "—";
  const abs = Math.abs(val);
  const sign = val >= 0 ? "+" : "-";
  if (abs >= 100000) return `${sign}₹${(abs / 100000).toFixed(2)}L Cr`;
  return `${sign}₹${abs.toLocaleString("en-IN", { minimumFractionDigits: 2 })} Cr`;
}

function colorClass(val) {
  if (val == null) return "";
  return val >= 0 ? "text-emerald-400" : "text-orange-400";
}

export default function CashFlowTable({ ticker }) {
  const [cf, setCf] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const symbol = typeof ticker === "string" ? ticker : ticker?.symbol;
    if (symbol) fetchData(symbol);
  }, [ticker]);

  async function fetchData(symbol) {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${REQUEST_BASE}/cashflow/stocks?ticker=${symbol}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setCf({ symbol: symbol, currency: "INR", data: json });
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const years = cf && cf.data && Object.keys(cf.data).length > 0
    ? Object.keys(Object.values(cf.data)[0] || {})
    : [];

  return (
    <div className="min-h-screen p-6 font-sans text-slate-300"
      style={{
        background: `
          linear-gradient(rgba(0,180,180,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0,180,180,0.03) 1px, transparent 1px),
          #050d12`,
        backgroundSize: "40px 40px",
        fontFamily: "'Rajdhani', sans-serif"
      }}>

      <style>{`@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@500;600;700&family=Orbitron:wght@700;900&display=swap');`}</style>

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-3 mb-4 px-4 py-3 border border-cyan-500/20 bg-cyan-500/5">
          <span className="w-2 h-2 bg-cyan-400 animate-ping rounded-full" />
          <span className="text-cyan-400 text-xs tracking-widest" style={{ fontFamily: "'Share Tech Mono', monospace" }}>
            FETCHING DATA...
          </span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-4 px-4 py-3 border border-orange-500/30 bg-orange-500/5 text-orange-400 text-xs tracking-widest"
          style={{ fontFamily: "'Share Tech Mono', monospace" }}>
          ⚠ ERROR — {error}
        </div>
      )}



      {/* Table Panel */}
      {cf && (
        <div className="relative border border-cyan-500/[0.12] bg-[rgba(0,20,30,0.75)] overflow-hidden">
          {/* top glow line */}
          <div className="absolute top-0 left-0 right-0 h-px"
            style={{ background: "linear-gradient(90deg,transparent,rgba(0,200,200,0.5),transparent)" }} />

          {/* Panel label */}
          <div className="flex items-center gap-2 px-4 py-2 border-b border-cyan-500/10 bg-cyan-500/[0.07]"
            style={{ fontFamily: "'Orbitron', monospace" }}>
            <span className="w-2 h-2 bg-cyan-400 flex-shrink-0"
              style={{ clipPath: "polygon(50% 0%,100% 50%,50% 100%,0% 50%)", boxShadow: "0 0 8px #00c8c8" }} />
            <span className="text-[9px] font-bold tracking-[3px] text-cyan-400">
              CASH FLOW STATEMENT — ANNUAL
            </span>
          </div>

          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-cyan-500/20">
                <th className="text-left px-4 py-2 text-[10px] tracking-widest text-cyan-500/55 uppercase"
                  style={{ fontFamily: "'Share Tech Mono', monospace" }}>Line Item</th>
                {years.map(y => (
                  <th key={y} className="text-right px-4 py-2 text-[10px] tracking-widest text-cyan-500/55 uppercase whitespace-nowrap"
                    style={{ fontFamily: "'Share Tech Mono', monospace" }}>{y}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(cf.data).map(([label, vals]) => {
                const isHL = HIGHLIGHT_ROWS.includes(label);
                return (
                  <tr key={label}
                    className={`border-b border-cyan-500/[0.06] transition-colors hover:bg-cyan-500/[0.04] ${isHL ? "bg-cyan-500/[0.04]" : ""}`}>
                    <td className={`px-4 py-3 text-sm font-semibold tracking-wide ${isHL ? "text-cyan-400" : "text-slate-300"}`}
                      style={{ fontFamily: "'Rajdhani', sans-serif" }}>
                      {label}
                    </td>
                    {years.map(y => (
                      <td key={y}
                        className={`px-4 py-3 text-right text-xs ${isHL && vals[y] == null ? "text-cyan-400" : colorClass(vals[y])}`}
                        style={{ fontFamily: "'Share Tech Mono', monospace" }}>
                        {fmt(vals[y])}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Empty state */}
      {!cf && !loading && (
        <div className="text-center py-16 text-cyan-500/30 text-xs tracking-widest"
          style={{ fontFamily: "'Share Tech Mono', monospace" }}>
          NO DATA — AWAITING TICKER SIGNAL
        </div>
      )}
    </div>
  );
}