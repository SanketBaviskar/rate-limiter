import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

const TrafficVisualizer = ({ trigger }) => {
	const [packets, setPackets] = useState([]);
	const packetIdCounter = useRef(0);

	useEffect(() => {
		if (trigger) {
			const id = packetIdCounter.current++;
			setPackets((prev) => [...prev, id]);

			// Remove packet after animation duration (e.g., 1s)
			setTimeout(() => {
				setPackets((prev) => prev.filter((p) => p !== id));
			}, 1000);
		}
	}, [trigger]);

	return (
		<div className="w-full bg-neutral-900 rounded-xl p-6 border border-neutral-800 shadow-lg flex items-center justify-between relative overflow-hidden">
			{/* Client Side */}
			<div className="flex flex-col items-center z-10">
				<div className="w-16 h-16 bg-neutral-800 rounded-lg flex items-center justify-center border border-neutral-700 shadow-inner">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						className="h-8 w-8 text-blue-400"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth={2}
							d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
						/>
					</svg>
				</div>
				<span className="text-xs text-neutral-400 mt-2 font-mono">
					CLIENT
				</span>
			</div>

			{/* Connection Line */}
			<div className="flex-1 h-0.5 bg-neutral-800 mx-4 relative">
				<AnimatePresence>
					{packets.map((id) => (
						<motion.div
							key={id}
							initial={{ left: "0%", opacity: 0, scale: 0.5 }}
							animate={{
								left: "100%",
								opacity: [0, 1, 1, 0],
								scale: 1,
							}}
							transition={{ duration: 0.8, ease: "easeInOut" }}
							className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-blue-400 rounded-full shadow-[0_0_20px_rgba(96,165,250,1)] z-20"
						/>
					))}
				</AnimatePresence>
			</div>

			{/* Server Side */}
			<div className="flex flex-col items-center z-10">
				<div className="w-16 h-16 bg-neutral-800 rounded-lg flex items-center justify-center border border-neutral-700 shadow-inner">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						className="h-8 w-8 text-emerald-400"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth={2}
							d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"
						/>
					</svg>
				</div>
				<span className="text-xs text-neutral-400 mt-2 font-mono">
					SERVER
				</span>
			</div>
		</div>
	);
};

export default TrafficVisualizer;
