import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function Simplifier({ symbol }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!symbol) return;

    const fetchData = async () => {
      try {
        setLoading(true);

        const response = await fetch(
          `http://127.0.0.1:8002/?symbol=${symbol}`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch analysis");
        }

        const result = await response.json();

        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [symbol]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-cyan-400 text-xl font-bold animate-pulse">
          Loading Analysis...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="bg-red-500/10 border border-red-500 p-6 rounded-lg">
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="min-h-screen bg-[#050816] text-white px-4 py-8">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="mb-8 border border-cyan-500/20 rounded-xl p-8 bg-white/5 backdrop-blur">
          <h1 className="text-4xl font-black text-cyan-400 mb-2">
            Equity Research Report
          </h1>

          <p className="text-cyan-200/70 uppercase tracking-[0.3em] text-sm">
            Comprehensive Stock Analysis
          </p>
        </div>

        {/* Markdown Report */}
        <div className="bg-white/5 border border-cyan-500/10 rounded-2xl p-8 overflow-hidden">

          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({ children }) => (
                <h1 className="text-4xl font-black text-cyan-400 mb-8">
                  {children}
                </h1>
              ),

              h2: ({ children }) => (
                <h2 className="text-2xl font-bold text-cyan-300 mt-10 mb-5 border-b border-cyan-500/20 pb-3">
                  {children}
                </h2>
              ),

              h3: ({ children }) => (
                <h3 className="text-xl font-semibold text-cyan-200 mt-6 mb-3">
                  {children}
                </h3>
              ),

              p: ({ children }) => (
                <p className="text-gray-300 leading-8 mb-4">
                  {children}
                </p>
              ),

              ul: ({ children }) => (
                <ul className="list-disc ml-6 space-y-2 mb-6 text-gray-300">
                  {children}
                </ul>
              ),

              ol: ({ children }) => (
                <ol className="list-decimal ml-6 space-y-2 mb-6 text-gray-300">
                  {children}
                </ol>
              ),

              li: ({ children }) => (
                <li className="leading-7">{children}</li>
              ),

              strong: ({ children }) => (
                <strong className="text-cyan-300 font-semibold">
                  {children}
                </strong>
              ),

              table: ({ children }) => (
                <div className="overflow-x-auto my-6">
                  <table className="w-full border-collapse border border-cyan-500/20">
                    {children}
                  </table>
                </div>
              ),

              thead: ({ children }) => (
                <thead className="bg-cyan-500/10">
                  {children}
                </thead>
              ),

              th: ({ children }) => (
                <th className="border border-cyan-500/20 px-4 py-3 text-left text-cyan-300">
                  {children}
                </th>
              ),

              td: ({ children }) => (
                <td className="border border-cyan-500/10 px-4 py-3 text-gray-300">
                  {children}
                </td>
              ),

              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-cyan-400 pl-4 italic text-cyan-100 my-4">
                  {children}
                </blockquote>
              ),
            }}
          >
            {data.analysis}
          </ReactMarkdown>

        </div>
      </div>
    </div>
  );
}