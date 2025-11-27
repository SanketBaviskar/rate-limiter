import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MetricsCard from './MetricsCard';
import AlgoSelector from './AlgoSelector';
import InteractiveClient from './InteractiveClient';
import RequestLog from './RequestLog';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    globalMetrics: { totalRequests: 0, total429s: 0, activeIPs: 0 },
    algorithmData: {}
  });
  const [currentAlgo, setCurrentAlgo] = useState('fixed_window');
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/monitor');
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
    let color = 'text-gray-400';
    if (type === 'success') color = 'text-green-400';
    if (type === 'error') color = 'text-red-400';
    if (type === 'warning') color = 'text-yellow-400';
    if (type === 'info') color = 'text-blue-400';

    setLogs(prev => [{ time, msg, color }, ...prev].slice(0, 50));
  };

  const handleResponse = (status, latency) => {
    if (status === 200) {
      addLog(`[${currentAlgo}] 200 OK (${latency}ms)`, 'success');
    } else if (status === 429) {
      addLog(`[${currentAlgo}] 429 Too Many Requests (${latency}ms)`, 'error');
    } else {
      addLog(`[${currentAlgo}] ${status} (${latency}ms)`, 'warning');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
              Rate Limiter Dashboard
            </h1>
            <p className="text-gray-400 mt-2">Visualize and test advanced rate limiting algorithms</p>
          </div>
          <AlgoSelector currentAlgo={currentAlgo} setAlgo={(algo) => {
            setCurrentAlgo(algo);
            addLog(`Switched to ${algo}`, 'info');
          }} />
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
          <InteractiveClient currentAlgo={currentAlgo} onResponse={handleResponse} />
          <RequestLog logs={logs} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
