import React from 'react';

const AlgoSelector = ({ currentAlgo, setAlgo }) => {
  return (
    <div className="flex space-x-4">
      <select 
        value={currentAlgo}
        onChange={(e) => setAlgo(e.target.value)}
        className="bg-gray-800 border border-gray-700 rounded px-4 py-2 focus:outline-none focus:border-blue-500 text-white"
      >
        <option value="fixed_window">Fixed Window</option>
        <option value="sliding_window_log">Sliding Window Log</option>
        <option value="sliding_window_counter">Sliding Window Counter</option>
        <option value="token_bucket">Token Bucket</option>
        <option value="leaky_bucket">Leaky Bucket</option>
      </select>
    </div>
  );
};

export default AlgoSelector;
