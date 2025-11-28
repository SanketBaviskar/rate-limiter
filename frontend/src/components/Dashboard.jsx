import React, { useState, useEffect } from "react";
import axios from "axios";
import MetricsCard from "./MetricsCard";
import AlgoSelector from "./AlgoSelector";
import InteractiveClient from "./InteractiveClient";
import RequestLog from "./RequestLog";
import TrafficVisualizer from "./TrafficVisualizer";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const Dashboard = () => {
	const [metrics, setMetrics] = useState({
		globalMetrics: { totalRequests: 0, total429s: 0, activeIPs: 0 },
		algorithmData: {},
	});
	const [currentAlgo, setCurrentAlgo] = useState("fixed_window");
	const [logs, setLogs] = useState([]);
	const [redisStatus, setRedisStatus] = useState("Checking...");
	const [currentTime, setCurrentTime] = useState(new Date());
	const [triggerVisualizer, setTriggerVisualizer] = useState(0);
	const [resetTrigger, setResetTrigger] = useState(0);

	const fetchMetrics = async () => {
		try {
			const res = await axios.get(`${API_URL}/api/monitor`);
			setMetrics(res.data);
		} catch (err) {
			console.error("Failed to fetch metrics", err);
		}
	};

	const fetchHealth = async () => {
		try {
			const res = await axios.get(`${API_URL}/api/health`);
			const isFake = res.data.redis.is_fakeredis;
			setRedisStatus(
				isFake ? "FakeRedis (Local)" : "Real Redis (Shared)"
			);
		} catch (err) {
			setRedisStatus("Error connecting");
		}
	};

	useEffect(() => {
		fetchMetrics();
		fetchHealth();

		const timer = setInterval(() => setCurrentTime(new Date()), 1000);
		return () => clearInterval(timer);
	}, []);

	const addLog = (msg, type) => {
		const time = new Date().toLocaleTimeString();
		let color = "text-gray-400";
		if (type === "success") color = "text-green-400";
		if (type === "error") color = "text-red-400";
		if (type === "warning") color = "text-yellow-400";
		if (type === "info") color = "text-blue-400";

		setLogs((prev) => [{ time, msg, color }, ...prev].slice(0, 50));
	};

	const handleResponse = (status, latency) => {
		fetchMetrics(); // Update metrics after every request
		if (status === 200) {
			addLog(`[${currentAlgo}] 200 OK (${latency}ms)`, "success");
		} else if (status === 429) {
			addLog(
				`[${currentAlgo}] 429 Too Many Requests (${latency}ms)`,
				"error"
			);
		} else {
			addLog(`[${currentAlgo}] ${status} (${latency}ms)`, "warning");
		}
	};

	return (
		<div className="min-h-screen bg-neutral-950 text-white p-8 font-sans">
			<div className="max-w-6xl mx-auto">
				<header className="mb-8 flex flex-col md:flex-row justify-between items-center gap-4">
					<div>
						<h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-neutral-200 to-neutral-500">
							Rate Limiter Dashboard
						</h1>
						<div className="flex gap-4 items-center mt-2">
							<p className="text-neutral-400">
								Visualize and test advanced rate limiting
								algorithms
							</p>
							<span
								className={`text-xs px-2 py-1 rounded border ${
									redisStatus.includes("Real")
										? "bg-green-900/30 border-green-800 text-green-400"
										: redisStatus.includes("Fake")
										? "bg-yellow-900/30 border-yellow-800 text-yellow-400"
										: "bg-red-900/30 border-red-800 text-red-400"
								}`}
							>
								{redisStatus}
							</span>
						</div>
					</div>
					<AlgoSelector
						currentAlgo={currentAlgo}
						setAlgo={(algo) => {
							setCurrentAlgo(algo);
							addLog(`Switched to ${algo}`, "info");
						}}
					/>
				</header>

				<div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
					<MetricsCard
						title="Total Requests"
						value={metrics.globalMetrics.totalRequests}
						label="Global"
						color="text-white"
					/>
					<MetricsCard
						title="Total 429s"
						value={metrics.globalMetrics.total429s}
						label="Blocked"
						color="text-red-400"
					/>
					<MetricsCard
						title="Active IPs"
						value={metrics.globalMetrics.activeIPs}
						label="Tracking"
						color="text-blue-400"
					/>
					<MetricsCard
						title="System Time"
						value={currentTime.toLocaleTimeString()}
						color="text-emerald-400"
					/>
				</div>

				<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
					<InteractiveClient
						currentAlgo={currentAlgo}
						onResponse={handleResponse}
						onRequest={() => setTriggerVisualizer(Date.now())}
						resetTrigger={resetTrigger}
					/>
					<div className="flex flex-col gap-4">
						<RequestLog logs={logs} />
						<div className="flex gap-4">
							<button
								onClick={() => setLogs([])}
								className="flex-1 py-2 rounded font-semibold text-sm bg-neutral-800 hover:bg-neutral-700 text-neutral-300 border border-neutral-700 transition-colors"
							>
								Clear Logs
							</button>
							<button
								onClick={async () => {
									try {
										await axios.post(
											`${API_URL}/api/reset`
										);
										addLog(
											"System Reset: All stats cleared",
											"warning"
										);
										fetchMetrics(); // Refresh metrics after reset
										setResetTrigger((prev) => prev + 1); // Trigger client reset
									} catch (err) {
										console.error("Failed to reset:", err);
										addLog(
											"Failed to reset system",
											"error"
										);
									}
								}}
								className="flex-1 py-2 rounded font-semibold text-sm bg-rose-900/30 text-rose-400 border border-rose-900 hover:bg-rose-900/50 transition-colors"
							>
								Reset System
							</button>
						</div>
						<TrafficVisualizer trigger={triggerVisualizer} />
					</div>
				</div>

				<footer className="mt-12 pt-8 border-t border-neutral-800 text-center text-neutral-500 text-sm">
					<div className="flex flex-col md:flex-row justify-between items-center gap-4">
						<div>
							<p>
								© 2025 Distributed Rate Limiter System. All
								rights reserved.
							</p>
							<p className="mt-1">
								Released under the{" "}
								<span className="text-neutral-300">
									MIT License
								</span>
								.
							</p>
						</div>

						<div className="flex flex-col items-center md:items-end">
							<p>
								Designed & Developed by{" "}
								<span className="text-white font-semibold">
									Sanket Baviskar
								</span>
							</p>
							<a
								href="mailto:sanket@example.com"
								className="mt-1 hover:text-blue-400 transition-colors flex items-center gap-2"
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									className="h-4 w-4"
									viewBox="0 0 20 20"
									fill="currentColor"
								>
									<path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
									<path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
								</svg>
								Contact Me
							</a>
						</div>
					</div>
				</footer>
			</div>
		</div>
	);
};

export default Dashboard;
