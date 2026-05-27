import React, { useState } from "react";
import SearchBar from "../components/SearchBarPredict";
import LoadingIndicator from "../components/Loadingindicator";
import Predict from "./Predict";

const REQUEST_BASE =
  (import.meta.env.VITE_REQUEST_URL || "http://localhost:8006").startsWith("http")
    ? import.meta.env.VITE_REQUEST_URL || "http://localhost:8006"
    : `http://${import.meta.env.VITE_REQUEST_URL || "localhost:8006"}`;

export default function PredictPage() {
  const [ticker, setTicker] = useState(null);
  const [info, setInfo] = useState(null);
  const [predict, setPredict] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (sym) => {
    setLoading(true);
    setError(null);

    try {
      const [res, res2] = await Promise.all([
        fetch(`${REQUEST_BASE}/metrics/live?ticker=${sym}`),
        fetch(`${REQUEST_BASE}/predict/analysis?ticker=${sym}`),
      ]);

      if (!res.ok || !res2.ok) {
        throw new Error("Server error");
      }

      const [data, data2] = await Promise.all([res.json(), res2.json()]);

      setTicker(sym);
      setInfo(data);
      setPredict(data2);
    } catch (err) {
      console.error(err.message);
      setError(err.message);
      setPredict(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative z-10 max-w-7xl mx-auto px-6 py-14 md:py-20">
      <div className="relative z-50 pb-6">
        <section className="text-center max-w-3xl mx-auto mt-8 md:mt-14 mb-12">
          <p className="text-[11px] md:text-xs tracking-[0.5em] uppercase font-black text-cyan-500/80 mb-4">
            AI Based Stock Predictor
          </p>
          <h2 className="text-4xl md:text-6xl font-black tracking-tighter leading-none uppercase text-white">
            Run prediction analysis for any ticker
          </h2>
          <p className="mt-5 text-sm md:text-base text-cyan-100/70 tracking-wide">
            Enter a ticker to get AI-powered price forecasts and prediction charts.
          </p>
        </section>

        <SearchBar onSearch={handleSearch} />
      </div>

      <div className="mt-12 md:mt-16">
        {loading && <LoadingIndicator />}
        {error && (
          <p className="text-center text-red-500 mt-4 tracking-widest text-sm">
            {error}
          </p>
        )}
        {predict && !loading && (
          <div>
            <Predict ticker={ticker} info={info} predict={predict} />
          </div>
        )}
      </div>
    </main>
  );
}
