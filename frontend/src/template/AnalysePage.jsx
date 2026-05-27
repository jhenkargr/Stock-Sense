import React, { useState } from "react";
import SearchBar from "../components/SearchBarAnalyse";
import LoadingIndicator from "../components/Loadingindicator";
import StockAnalyzer from "./StockAnalyzer";

const REQUEST_BASE =
	(import.meta.env.VITE_REQUEST_URL || "http://localhost:8006").startsWith("http")
		? import.meta.env.VITE_REQUEST_URL || "http://localhost:8006"
		: `http://${import.meta.env.VITE_REQUEST_URL || "localhost:8006"}`;

export default function AnalysePage() {
	const [ticker, setTicker] = useState(null);
	const [result, setResult] = useState(null);
	const [info, setInfo] = useState(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	const handleSearch = async (sym) => {
		setLoading(true);
		setError(null);

		try {
			const [res, res2] = await Promise.all([
				fetch(`${REQUEST_BASE}/metrics/stocks?ticker=${sym}`),
				fetch(`${REQUEST_BASE}/metrics/live?ticker=${sym}`),
			]);

			if (!res.ok || !res2.ok) {
				throw new Error("Server error");
			}

			const [data, data2] = await Promise.all([res.json(), res2.json()]);

			setTicker(sym);
			setResult(data);
			setInfo(data2);
		} catch (err) {
			console.error(err.message);
			setError(err.message);
			setResult(null);
		} finally {
			setLoading(false);
		}
	};

	return (
		<main className="relative z-10 max-w-7xl mx-auto px-6 py-14 md:py-20">
			<div className="relative z-50 pb-6">
				<SearchBar onSearch={handleSearch} />
			</div>

			<div className="relative z-10 mt-12 md:mt-16">
				{loading && <LoadingIndicator />}
				{error && (
					<p className="text-center text-red-500 mt-4 tracking-widest text-sm">
						{error}
					</p>
				)}
				{result && !loading && (
					<div>
						<StockAnalyzer stock={ticker} ticker={result} info={info} />
					</div>
				)}
			</div>
		</main>
	);
}
