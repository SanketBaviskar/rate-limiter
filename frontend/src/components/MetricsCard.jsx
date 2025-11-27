import React from "react";
import { motion } from "framer-motion";

const MetricsCard = ({ title, value, label, color }) => {
	return (
		<motion.div
			initial={{ opacity: 0, y: 20 }}
			animate={{ opacity: 1, y: 0 }}
			className="bg-neutral-900 rounded-xl p-6 border border-neutral-800 shadow-lg"
		>
			<h3 className="text-neutral-500 text-sm font-medium uppercase tracking-wider mb-4">
				{title}
			</h3>
			<div className="flex items-end justify-between">
				<span className={`text-4xl font-bold ${color}`}>{value}</span>
				<span className={`${color} text-sm`}>{label}</span>
			</div>
		</motion.div>
	);
};

export default MetricsCard;
