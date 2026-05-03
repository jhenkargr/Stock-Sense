import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  Activity, 
  TrendingUp, 
  BarChart3, 
  PieChart, 
  Cpu, 
  Globe, 
  ArrowUpRight, 
  ArrowDownRight,
  Info,
  Clock,
  ShieldCheck,
  AlertCircle,
  Zap
} from 'lucide-react';

// --- CONFIGURATION ---
const apiKey = ""; // Gemini API Key (handled by environment)
const VERSION = "V2.4";

const App = () => {
  const [ticker, setTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stockData, setStockData] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString('en-GB'));
  const [isSearching, setIsSearching] = useState(false);

  // Update clock
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString('en-GB'));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const analyzeStock = async (queryTicker) => {
    if (!queryTicker) return;
    setLoading(true);
    setIsSearching(true);
    setError(null);
    
    const prompt = `Analyze stock "${queryTicker.toUpperCase()}". 
    Provide JSON: { 
      "companyName": string, 
      "sector": string, 
      "price": number, 
      "priceChange": number, 
      "grossProfitMargin": string, 
      "eps": number, 
      "peRatio": number, 
      "pbRatio": number, 
      "marketCap": string, 
      "dividendYield": string, 
      "aiInsight": string (2 sentences max)
    }`;

    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { responseMimeType: "application/json" }
        })
      });

      if (!response.ok) throw new Error("Connection Failure");
      
      const result = await response.json();
      const data = JSON.parse(result.candidates[0].content.parts[0].text);
      setStockData(data);
    } catch (err) {
      setError("ANALYSIS FAILED: TICKER UNREACHABLE");
      setIsSearching(false);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    analyzeStock(ticker);
  };

  return (
    <div className="min-h-screen bg-[#050b0f] text-[#e0f2fe] font-mono selection:bg-cyan-500 selection:text-black overflow-x-hidden">
      
      {/* Visual Overlay: Grid & Scanlines (Removed animate-pulse) */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute inset-0 opacity-[0.15]" 
             style={{ backgroundImage: 'linear-gradient(#0ea5e9 1px, transparent 1px), linear-gradient(90deg, #0ea5e9 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
        </div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#050b0f]/50 to-[#050b0f]"></div>
        <div className="absolute inset-0 pointer-events-none opacity-[0.03]"
             style={{ backgroundImage: 'repeating-linear-gradient(0deg, #fff, #fff 1px, transparent 1px, transparent 2px)', backgroundSize: '100% 3px' }}>
        </div>
      </div>

      {/* Header */}
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
            {currentTime}
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        
        {/* Landing Hero Section */}
        {!isSearching && (
          <div className="text-center mt-20 mb-16 animate-in fade-in slide-in-from-bottom-6 duration-1000">
            <h2 className="text-7xl md:text-[100px] font-black tracking-tighter mb-4 leading-none uppercase">
              ANALYSE ANY <span className="text-cyan-400 drop-shadow-[0_0_20px_rgba(34,211,238,0.4)]">STOCK</span>
            </h2>
            <p className="text-cyan-800 tracking-[0.5em] text-[11px] uppercase font-black">
              // REAL-TIME FUNDAMENTALS · RATIOS · AI INSIGHTS
            </p>
          </div>
        )}

        {/* Search Bar - Precisely styled like image */}
        <div className={`transition-all duration-700 ease-in-out ${isSearching ? 'mt-4 mb-10' : 'mb-24'}`}>
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto relative group">
            <div className="flex items-stretch border border-cyan-900/50 bg-black/80 rounded overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.5)] focus-within:border-cyan-500/50 transition-all duration-300">
              <div className="px-6 py-5 flex items-center justify-center bg-cyan-950/10 border-r border-cyan-900/50">
                <span className="text-[11px] font-black text-cyan-500 tracking-[0.2em] uppercase">TICKER ›</span>
              </div>
              <input 
                type="text" 
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="E.G. AAPL, TSLA, MSFT"
                className="flex-1 bg-transparent px-8 py-5 outline-none text-cyan-100 placeholder:text-cyan-900/50 font-bold tracking-[0.2em] uppercase"
              />
              <button 
                type="submit"
                disabled={loading}
                className="bg-cyan-400 hover:bg-cyan-300 disabled:bg-cyan-950 text-black px-12 font-black tracking-[0.2em] uppercase transition-all flex items-center gap-2 group relative overflow-hidden"
              >
                <span className="relative z-10">{loading ? "BUSY" : "ANALYSE"}</span>
                {loading && <div className="absolute inset-0 bg-cyan-500/20"></div>}
              </button>
            </div>

            {/* Suggestions Overlay */}
            {!isSearching && (
              <div className="flex justify-center gap-4 mt-6 animate-in fade-in duration-1000 delay-500">
                {['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'NVDA', 'AMZN'].map(sym => (
                  <button 
                    key={sym}
                    onClick={() => { setTicker(sym); analyzeStock(sym); }}
                    className="text-[10px] border border-cyan-950/50 px-4 py-1.5 text-cyan-900 hover:border-cyan-500 hover:text-cyan-400 transition-all tracking-[0.2em] font-black rounded"
                  >
                    {sym}
                  </button>
                ))}
              </div>
            )}
          </form>
        </div>

        {/* Loading Indicator */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-6 animate-in fade-in duration-300">
            <div className="relative">
              <div className="w-16 h-16 border-[1px] border-cyan-900 rounded-full"></div>
              <div className="absolute inset-0 border-t-2 border-cyan-400 rounded-full animate-spin"></div>
              <Zap className="absolute inset-0 m-auto w-6 h-6 text-cyan-500" />
            </div>
            <p className="text-cyan-600 tracking-[0.4em] text-[10px] font-black uppercase">
              DECRYPTING SECTOR DATA...
            </p>
          </div>
        )}

        {/* Analysis Results View */}
        {stockData && !loading && (
          <div className="animate-in fade-in slide-in-from-bottom-12 duration-1000 space-y-8">
            
            {/* Main Header Display */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 p-10 border border-cyan-900/30 bg-black/40 backdrop-blur-xl rounded-2xl relative overflow-hidden group">
                <div className="absolute -right-20 -top-20 w-64 h-64 bg-cyan-500/5 blur-[100px] rounded-full"></div>
                <div className="flex flex-col h-full justify-between relative z-10">
                  <div>
                    <div className="flex items-center gap-4 mb-4">
                      <span className="bg-cyan-400 text-black px-3 py-1 text-[11px] font-black rounded tracking-widest uppercase shadow-[0_0_15px_rgba(34,211,238,0.3)]">{ticker}</span>
                      <div className="h-[1px] w-8 bg-cyan-900/50"></div>
                      <span className="text-cyan-700 text-[10px] tracking-[0.3em] uppercase font-black">{stockData.sector}</span>
                    </div>
                    <h3 className="text-5xl font-black tracking-tighter uppercase mb-2">{stockData.companyName}</h3>
                  </div>
                  <div className="mt-12 flex items-end gap-10">
                    <div>
                      <span className="text-[10px] text-cyan-800 uppercase block mb-2 tracking-[0.3em] font-black">Market Value</span>
                      <span className="text-6xl font-black tabular-nums">${stockData.price.toLocaleString()}</span>
                    </div>
                    <div className={`mb-2 px-4 py-2 rounded-lg text-sm font-black flex items-center gap-2 border ${stockData.priceChange >= 0 ? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-400' : 'border-red-500/20 bg-red-500/5 text-red-400'}`}>
                      {stockData.priceChange >= 0 ? <TrendingUp className="w-4 h-4" /> : <Activity className="w-4 h-4" />}
                      {Math.abs(stockData.priceChange)}%
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Insight Sidebar */}
              <div className="p-8 border border-cyan-500/20 bg-cyan-500/5 backdrop-blur-xl rounded-2xl flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-6">
                    <Cpu className="w-5 h-5 text-cyan-400" />
                    <span className="text-[10px] font-black text-cyan-400 tracking-[0.3em] uppercase">NEURAL INSIGHT</span>
                  </div>
                  <p className="text-sm leading-relaxed text-cyan-100 font-medium italic opacity-80">
                    "{stockData.aiInsight}"
                  </p>
                </div>
                <div className="mt-8 pt-6 border-t border-cyan-500/10">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[9px] text-cyan-800 font-black uppercase tracking-[0.2em]">Confidence Index</span>
                    <span className="text-[9px] text-cyan-400 font-black uppercase">94.2%</span>
                  </div>
                  <div className="w-full h-1 bg-cyan-950 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-400 w-[94%] shadow-[0_0_8px_#22d3ee]"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Technical Data Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
              <MetricBox label="Profit Margin" value={stockData.grossProfitMargin} icon={<BarChart3 />} />
              <MetricBox label="EPS Trailing" value={stockData.eps} icon={<TrendingUp />} />
              <MetricBox label="P/E Ratio" value={stockData.peRatio} icon={<Activity />} />
              <MetricBox label="P/B Ratio" value={stockData.pbRatio} icon={<PieChart />} />
              <MetricBox label="Market Cap" value={stockData.marketCap} icon={<Globe />} />
              <MetricBox label="Dividend" value={stockData.dividendYield} icon={<ArrowUpRight />} />
              <MetricBox label="System Sync" value="ACTIVE" success icon={<ShieldCheck />} />
              <MetricBox label="Data Uplink" value="LIVE" icon={<Clock />} />
            </div>

            {/* Action Bar */}
            <div className="flex justify-center mt-12">
              <button 
                onClick={() => { setStockData(null); setIsSearching(false); setTicker(""); }}
                className="text-[10px] font-black text-cyan-800 hover:text-cyan-400 tracking-[0.5em] uppercase border border-cyan-900/30 px-8 py-3 rounded-full hover:border-cyan-500/50 transition-all"
              >
                // RESET SCANNER
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="max-w-md mx-auto p-6 border border-red-900/50 bg-red-950/10 text-red-400 rounded-lg flex gap-4 items-center animate-shake">
            <AlertCircle className="w-6 h-6 flex-shrink-0" />
            <p className="text-[11px] font-black tracking-widest uppercase">{error}</p>
          </div>
        )}
      </main>

      {/* Footer Disclaimer */}
      <footer className="fixed bottom-0 left-0 right-0 z-50 p-8 pointer-events-none">
        <div className="max-w-6xl mx-auto flex justify-center opacity-30">
          <p className="text-[10px] text-cyan-800 tracking-[0.4em] uppercase font-black text-center whitespace-nowrap">
            STOCKSENSE // FOR EDUCATIONAL PURPOSES ONLY · NOT FINANCIAL ADVICE · DATA IS SIMULATED
          </p>
        </div>
      </footer>
    </div>
  );
};

const MetricBox = ({ label, value, icon, success }) => (
  <div className="p-6 border border-cyan-900/20 bg-black/30 backdrop-blur-md rounded-xl hover:border-cyan-500/40 transition-all group overflow-hidden relative">
    <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-30 transition-opacity">
      {React.cloneElement(icon, { className: "w-8 h-8" })}
    </div>
    <div className="flex items-center gap-3 mb-4 text-cyan-900 group-hover:text-cyan-500 transition-colors">
      <div className="p-1.5 bg-cyan-950/20 rounded">
        {React.cloneElement(icon, { className: "w-3 h-3" })}
      </div>
      <span className="text-[9px] font-black tracking-[0.2em] uppercase">{label}</span>
    </div>
    <div className={`text-2xl font-black tracking-tight ${success ? 'text-emerald-400' : 'text-cyan-100'} group-hover:translate-x-1 transition-transform`}>
      {value}
    </div>
  </div>
);

export default App;