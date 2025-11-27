import React from "react";

const AlgoSelector = ({ currentAlgo, setAlgo }) => {
	return (
		<div className="flex space-x-4">
			<select
				value={currentAlgo}
				onChange={(e) => setAlgo(e.target.value)}
				className="bg-neutral-900 border border-neutral-800 rounded px-4 py-2 focus:outline-none focus:border-neutral-500 text-neutral-200 transition-colors hover:border-neutral-600"
			>
				<option value="fixed_window">Fixed Window</option>
				<option value="sliding_window_log">Sliding Window Log</option>
				<option value="sliding_window_counter">
					Sliding Window Counter
				</option>
				<option value="token_bucket">Token Bucket</option>
				<option value="leaky_bucket">Leaky Bucket</option>
			</select>
		</div>
	);
};

export default AlgoSelector;
