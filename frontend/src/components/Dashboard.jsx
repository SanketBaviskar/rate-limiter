import React, { useState, useEffect } from "react";
import axios from "axios";
import MetricsCard from "./MetricsCard";
import AlgoSelector from "./AlgoSelector";
import InteractiveClient from "./InteractiveClient";
import RequestLog from "./RequestLog";

let API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
if (API_URL && !API_URL.startsWith("http")) {
	API_URL = `https://${API_URL}`;
}

const Dashboard = () => {
	const [metrics, setMetrics] = useState({
		globalMetrics: { totalRequests: 0, total429s: 0, activeIPs: 0 },
		algorithmData: {},
	});
	const [currentAlgo, setCurrentAlgo] = useState("fixed_window");
	const [logs, setLogs] = useState([]);

	useEffect(() => {
		const fetchMetrics = async () => {
			try {
				const res = await axios.get(`${API_URL}/api/monitor`);
				setMetrics(res.data);
			} catch (err) {
				console.error("Failed to fetch metrics", err);
			}
		};

		fetchMetrics();
		const interval = setInterval(fetchMetrics, 1000);
		return () => clearInterval(interval);
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
						<p className="text-neutral-400 mt-2">
							Visualize and test advanced rate limiting algorithms
						</p>
					</div>
					<AlgoSelector
						currentAlgo={currentAlgo}
						setAlgo={(algo) => {
							setCurrentAlgo(algo);
							addLog(`Switched to ${algo}`, "info");
						}}
					/>
				</header>

				<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
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
				</div>

				<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
					<InteractiveClient
						currentAlgo={currentAlgo}
						onResponse={handleResponse}
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
					</div>
				</div>
			</div>
		</div>
	);
};

export default Dashboard;
