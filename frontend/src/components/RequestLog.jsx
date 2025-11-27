import React, { useEffect, useRef } from 'react';

const RequestLog = ({ logs }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [logs]);

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 flex flex-col h-[400px]">
      <h2 className="text-xl font-bold mb-4">Request Log</h2>
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto font-mono text-xs space-y-1 p-2 bg-gray-900 rounded border border-gray-700"
      >
        {logs.map((log, i) => (
          <div key={i} className={log.color}>
            [{log.time}] {log.msg}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RequestLog;
