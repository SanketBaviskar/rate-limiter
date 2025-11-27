import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";

let API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
if (API_URL && !API_URL.startsWith("http")) {
	// If it looks like a Render internal hostname (no dots, just alphanumeric+hyphens)
	if (!API_URL.includes(".")) {
		API_URL = `https://${API_URL}.onrender.com`;
	} else {
		API_URL = `https://${API_URL}`;
	}
}
API_URL = API_URL.replace(/\/$/, "");

const InteractiveClient = ({ currentAlgo, onResponse }) => {
	const [ripples, setRipples] = useState([]);
	const [lastStatus, setLastStatus] = useState(null);
	const [lastLatency, setLastLatency] = useState(null);

	// Auto-test state
	const [rps, setRps] = useState(1);
	const [totalRequests, setTotalRequests] = useState(10);
	const [isTesting, setIsTesting] = useState(false);
	const [progress, setProgress] = useState(0);

	// Config state
	const [limit, setLimit] = useState(10);
	const [window, setWindow] = useState(60);

	const updateConfig = async () => {
		try {
			await axios.post(`${API_URL}/api/config`, { limit, window });
			alert(`Config Updated: Limit=${limit}, Window=${window}s`);
		} catch (err) {
			console.error("Failed to update config:", err);
			alert("Failed to update config");
		}
	};

	const sendRequest = async () => {
		const start = performance.now();
		try {
			const res = await axios.get(
				`${API_URL}/api/image/200/200?algo=${currentAlgo}`
			);
			const end = performance.now();
			const latency = (end - start).toFixed(0);

			setLastStatus(res.status);
			setLastLatency(latency);
			onResponse(res.status, latency);
		} catch (err) {
			const end = performance.now();
			const latency = (end - start).toFixed(0);
			const status = err.response ? err.response.status : "ERR";

			setLastStatus(status);
			setLastLatency(latency);
			onResponse(status, latency);
		}
	};

	const handleClick = (e) => {
		// Create ripple
		const rect = e.currentTarget.getBoundingClientRect();
		const x = e.clientX - rect.left;
		const y = e.clientY - rect.top;
		const id = Date.now();
		setRipples((prev) => [...prev, { x, y, id }]);
		setTimeout(
			() => setRipples((prev) => prev.filter((r) => r.id !== id)),
			500
		);

		sendRequest();
	};

	const startAutoTest = async () => {
		if (isTesting) return;
		setIsTesting(true);
		setProgress(0);

		const intervalMs = 1000 / rps;
		let sent = 0;

		const interval = setInterval(() => {
			if (sent >= totalRequests) {
				clearInterval(interval);
				setIsTesting(false);
				return;
			}

			sendRequest();
			sent++;
			setProgress((sent / totalRequests) * 100);
		}, intervalMs);
	};

	const getStatusColor = (status) => {
		if (status === 200) return "text-emerald-400";
		if (status === 429) return "text-rose-400";
		return "text-amber-400";
	};

	return (
		<div className="bg-neutral-900 rounded-xl p-6 border border-neutral-800 shadow-2xl">
			<h2 className="text-xl font-bold mb-4 text-neutral-200">
				Interactive Client
			</h2>

			{/* Configuration Area */}
			<div className="bg-neutral-950 rounded-lg p-4 border border-neutral-800 mb-6">
				<h3 className="text-sm font-semibold text-neutral-300 mb-3">
					Rate Limit Configuration
				</h3>
				<div className="flex gap-4 mb-4">
					<div className="flex-1">
						<label className="block text-xs text-neutral-500 mb-1">
							Limit (Capacity)
						</label>
						<input
							type="number"
							min="1"
							value={limit}
							onChange={(e) => setLimit(Number(e.target.value))}
							className="w-full bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-neutral-500 transition-colors"
						/>
					</div>
					<div className="flex-1">
						<label className="block text-xs text-neutral-500 mb-1">
							Window (Seconds)
						</label>
						<input
							type="number"
							min="1"
							value={window}
							onChange={(e) => setWindow(Number(e.target.value))}
							className="w-full bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-neutral-500 transition-colors"
						/>
					</div>
				</div>
				<button
					onClick={updateConfig}
					className="w-full py-2 rounded font-semibold text-sm bg-neutral-800 hover:bg-neutral-700 text-neutral-200 border border-neutral-700 transition-all hover:border-neutral-500"
				>
					Update Configuration
				</button>
				{(currentAlgo === "token_bucket" ||
					currentAlgo === "leaky_bucket") && (
					<p className="text-xs text-neutral-500 mt-2 text-center">
						{currentAlgo === "leaky_bucket"
							? "Leak Rate"
							: "Refill Rate"}
						: {(limit / window).toFixed(2)}{" "}
						{currentAlgo === "leaky_bucket"
							? "reqs/sec"
							: "tokens/sec"}
					</p>
				)}
			</div>

			{/* Manual Click Area */}
			<div
				onClick={handleClick}
				className="w-full h-48 bg-neutral-800 rounded-lg flex items-center justify-center cursor-pointer hover:bg-neutral-700 transition-colors relative overflow-hidden group select-none mb-6 border border-neutral-700"
			>
				<span className="text-neutral-400 group-hover:text-white transition-colors z-10 font-medium">
					Click to Spam API
				</span>
				<AnimatePresence>
					{ripples.map((ripple) => (
						<motion.span
							key={ripple.id}
							initial={{ scale: 0, opacity: 0.5 }}
							animate={{ scale: 4, opacity: 0 }}
							exit={{ opacity: 0 }}
							transition={{ duration: 0.5 }}
							style={{
								left: ripple.x,
								top: ripple.y,
								position: "absolute",
								width: 100,
								height: 100,
								borderRadius: "50%",
								backgroundColor: "white",
								transform: "translate(-50%, -50%)",
								pointerEvents: "none",
							}}
						/>
					))}
				</AnimatePresence>
			</div>

			{/* Auto Test Controls */}
			<div className="bg-neutral-950 rounded-lg p-4 border border-neutral-800">
				<h3 className="text-sm font-semibold text-neutral-300 mb-3">
					Automatic Test
				</h3>
				<div className="flex gap-4 mb-4">
					<div className="flex-1">
						<label className="block text-xs text-neutral-500 mb-1">
							Requests / Sec
						</label>
						<input
							type="number"
							min="1"
							max="100"
							value={rps}
							onChange={(e) => setRps(Number(e.target.value))}
							className="w-full bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-neutral-500 transition-colors"
						/>
					</div>
					<div className="flex-1">
						<label className="block text-xs text-neutral-500 mb-1">
							Total Requests
						</label>
						<input
							type="number"
							min="1"
							max="1000"
							value={totalRequests}
							onChange={(e) =>
								setTotalRequests(Number(e.target.value))
							}
							className="w-full bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-neutral-500 transition-colors"
						/>
					</div>
				</div>

				<div className="flex gap-2">
					<button
						onClick={startAutoTest}
						disabled={isTesting}
						className={`flex-1 py-2 rounded font-semibold text-sm transition-colors border ${
							isTesting
								? "bg-neutral-800 text-neutral-500 border-neutral-700 cursor-not-allowed"
								: "bg-neutral-200 text-neutral-900 hover:bg-white border-transparent"
						}`}
					>
						{isTesting
							? `Testing... ${Math.round(progress)}%`
							: "Start Auto Test"}
					</button>

					<button
						onClick={async () => {
							try {
								await axios.post(`${API_URL}/api/reset`);
								alert("Stats and Limits Reset!");
							} catch (err) {
								console.error("Failed to reset:", err);
								alert("Failed to reset stats");
							}
						}}
						disabled={isTesting}
						className={`px-4 py-2 rounded font-semibold text-sm transition-colors border ${
							isTesting
								? "bg-neutral-800 text-neutral-500 border-neutral-700 cursor-not-allowed"
								: "bg-rose-900/30 text-rose-400 border-rose-900 hover:bg-rose-900/50"
						}`}
					>
						Reset
					</button>
				</div>

				{isTesting && (
					<div className="w-full bg-neutral-800 h-1 mt-3 rounded-full overflow-hidden">
						<div
							className="bg-neutral-200 h-full transition-all duration-200"
							style={{ width: `${progress}%` }}
						/>
					</div>
				)}
			</div>

			<div className="mt-4 flex justify-between items-center text-sm text-neutral-400">
				<span>
					Status:{" "}
					<span className={`font-bold ${getStatusColor(lastStatus)}`}>
						{lastStatus || "-"}
					</span>
				</span>
				<span>
					Latency:{" "}
					<span className="font-bold text-white">
						{lastLatency || "-"}
					</span>{" "}
					ms
				</span>
			</div>
		</div>
	);
};

export default InteractiveClient;
