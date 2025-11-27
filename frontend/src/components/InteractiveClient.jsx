import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const InteractiveClient = ({ currentAlgo, onResponse }) => {
  const [ripples, setRipples] = useState([]);
  const [lastStatus, setLastStatus] = useState(null);
  const [lastLatency, setLastLatency] = useState(null);

  const handleClick = async (e) => {
    // Create ripple
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const id = Date.now();
    setRipples((prev) => [...prev, { x, y, id }]);
    setTimeout(() => setRipples((prev) => prev.filter((r) => r.id !== id)), 500);

    // Make request
    const start = performance.now();
    try {
      const res = await axios.get(`http://localhost:8000/api/image/200/200?algo=${currentAlgo}`);
      const end = performance.now();
      const latency = (end - start).toFixed(0);
      
      setLastStatus(res.status);
      setLastLatency(latency);
      onResponse(res.status, latency);
    } catch (err) {
      const end = performance.now();
      const latency = (end - start).toFixed(0);
      const status = err.response ? err.response.status : 'ERR';
      
      setLastStatus(status);
      setLastLatency(latency);
      onResponse(status, latency);
    }
  };

  const getStatusColor = (status) => {
    if (status === 200) return 'text-green-400';
    if (status === 429) return 'text-red-400';
    return 'text-yellow-400';
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h2 className="text-xl font-bold mb-4">Interactive Client</h2>
      <div 
        onClick={handleClick}
        className="w-full h-64 bg-gray-700 rounded-lg flex items-center justify-center cursor-pointer hover:bg-gray-600 transition-colors relative overflow-hidden group select-none"
      >
        <span className="text-gray-400 group-hover:text-white transition-colors z-10">Click to Spam API</span>
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
                position: 'absolute',
                width: 100,
                height: 100,
                borderRadius: '50%',
                backgroundColor: 'white',
                transform: 'translate(-50%, -50%)',
                pointerEvents: 'none'
              }}
            />
          ))}
        </AnimatePresence>
      </div>
      <div className="mt-4 flex justify-between items-center text-sm text-gray-400">
        <span>Status: <span className={`font-bold ${getStatusColor(lastStatus)}`}>{lastStatus || '-'}</span></span>
        <span>Latency: <span className="font-bold text-white">{lastLatency || '-'}</span> ms</span>
      </div>
    </div>
  );
};

export default InteractiveClient;
