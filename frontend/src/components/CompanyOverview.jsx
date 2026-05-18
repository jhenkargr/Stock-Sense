import React, { useEffect, useState } from 'react';
import Groq from 'groq-sdk';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function CompanyOverview({ symbol }) {
  const [overview, setOverview] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const groqApiKey = import.meta.env.VITE_GROQ_API_KEY;

  const sym = typeof symbol === 'string'
    ? symbol
    : symbol?.symbol;

  useEffect(() => {
    if (!sym) return;

    const fetchOverview = async () => {
      try {
        setLoading(true);
        setError(null);

        if (!groqApiKey) {
          throw new Error('Missing VITE_GROQ_API_KEY in .env');
        }

        const groq = new Groq({ 
          apiKey: groqApiKey,
          dangerouslyAllowBrowser: true  // required for client-side usage
        });

        const completion = await groq.chat.completions.create({
          model: 'llama-3.3-70b-versatile',
          temperature: 0.4,
          max_tokens: 800,
          messages: [
            {
              role: 'system',
              content: 'You are a professional equity research analyst.'
            },
            {
              role: 'user',
              content: `
Give a professional Company Overview for ${sym} stock.

Format:
- What the company does
- Key business segments
- Main products/services
- Markets and geographies
- Industry position

Keep it professional and concise.
              `
            }
          ]
        });

        const content = completion.choices?.[0]?.message?.content || '';
        setOverview(content);

      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchOverview();
  }, [sym, groqApiKey]);

  if (loading) {
    return (
      <div className="border border-cyan-500/20 bg-black/30 rounded-lg p-6">
        <div className="flex items-center justify-center h-24">
          <div className="animate-spin rounded-full h-10 w-10 border-2 border-cyan-900 border-t-cyan-400 mr-4"></div>
          <div className="text-cyan-400 font-bold">
            Loading Company Overview...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="border border-red-500/20 bg-black/30 rounded-lg p-6">
        <div className="text-red-400">{error}</div>
      </div>
    );
  }

  return (
    <div className="border border-cyan-500/20 bg-black/30 backdrop-blur-sm rounded-lg overflow-hidden">

      {/* Header */}
      <div className="border-b border-cyan-500/10 px-6 py-4 bg-gradient-to-r from-cyan-500/5 to-blue-500/5">
        <h2 className="text-lg font-semibold text-cyan-300 uppercase tracking-wider">
          Company Overview
        </h2>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="text-cyan-100/80 leading-8 text-sm">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{overview}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}