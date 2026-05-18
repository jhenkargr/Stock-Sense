import React from "react";
import { Link } from "react-router-dom";

const launcherCards = [
    {
        title: "AI Based Stock Predictor",
        description: "Open the prediction flow and explore the forecast engine for a ticker.",
        to: "/predict",
        accent: "from-cyan-400/30 to-blue-500/20",
        border: "border-cyan-500/30",
        button: "Start Predicting",
    },
    {
        title: "Detailed Stock Analyser",
        description: "Jump straight to the search bar and inspect full company insights.",
        to: "/analyse",
        accent: "from-emerald-400/20 to-cyan-500/20",
        border: "border-emerald-500/30",
        button: "Open Search Bar",
    },
];

export default function Home() {
    return (
        <main className="relative z-10 max-w-7xl mx-auto px-6 py-14 pb-40 md:py-20 md:pb-48 lg:pb-56">
            <section className="text-center max-w-4xl mx-auto mt-10 md:mt-16 animate-in fade-in slide-in-from-bottom-6 duration-1000">
                <p className="text-[11px] md:text-xs tracking-[0.5em] uppercase font-black text-cyan-500/80 mb-4">
                    REAL-TIME MARKET INTELLIGENCE
                </p>
                <h2 className="text-5xl md:text-7xl lg:text-[88px] font-black tracking-tighter leading-none uppercase text-white">
                    Decode the{" "}
                    <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-emerald-400 drop-shadow-[0_0_24px_rgba(34,211,238,0.35)]">
                        Market
                    </span>
                </h2>
                <p className="mt-6 text-sm md:text-base text-cyan-100/70 max-w-2xl mx-auto tracking-wide">
                    Harness AI-powered predictions and deep-dive fundamentals analysis. Pick your workflow: forecast tomorrow's movement or dissect today's opportunities.
                </p>
            </section>

            <section className="mt-14 grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 max-w-5xl mx-auto">
                {launcherCards.map((card) => (
                    <Link
                        key={card.title}
                        to={card.to}
                        className={`group relative overflow-hidden rounded-2xl border ${card.border} bg-black/50 backdrop-blur-md p-6 md:p-8 shadow-[0_0_40px_rgba(0,0,0,0.35)] transition-all duration-300 hover:-translate-y-1 hover:border-cyan-400/50`}
                    >
                        <div className={`absolute inset-0 bg-gradient-to-br ${card.accent} opacity-80`} />
                        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.12),transparent_45%)]" />
                        <div className="relative z-10 flex h-full flex-col justify-between gap-8">
                            <div>
                                <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-black/30 px-3 py-1 text-[10px] font-black tracking-[0.25em] uppercase text-cyan-200/90">
                                    {card.title === "AI Based Stock Predictor" ? "Predict" : "Analyse"}
                                </div>
                                <h3 className="text-3xl md:text-4xl font-black tracking-tight text-white uppercase">
                                    {card.title}
                                </h3>
                                <p className="mt-4 text-sm md:text-base text-cyan-50/75 leading-relaxed max-w-md">
                                    {card.description}
                                </p>
                            </div>

                            <div className="flex items-center justify-between gap-4">
                                <span className="text-[11px] font-black tracking-[0.3em] uppercase text-cyan-100/60">
                                    {card.to.replace("/", "") || "home"}
                                </span>
                                <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-[11px] font-black tracking-[0.22em] uppercase text-white transition-all group-hover:border-cyan-300/40 group-hover:bg-cyan-400/10">
                                    {card.button}
                                    <span aria-hidden="true">→</span>
                                </span>
                            </div>
                        </div>
                    </Link>
                ))}
            </section>
        </main>
    );
}