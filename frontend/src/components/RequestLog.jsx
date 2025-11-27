import React, { useEffect, useRef } from "react";

const RequestLog = ({ logs }) => {
	const scrollRef = useRef(null);

	useEffect(() => {
		if (scrollRef.current) {
			scrollRef.current.scrollTop = 0;
		}
	}, [logs]);

	return (
		<div className="bg-neutral-900 rounded-xl p-6 border border-neutral-800 flex flex-col h-[400px] shadow-2xl">
			<h2 className="text-xl font-bold mb-4 text-neutral-200">
				Request Log
			</h2>
			<div
				ref={scrollRef}
				className="flex-1 overflow-y-auto font-mono text-xs space-y-1 p-2 bg-neutral-950 rounded border border-neutral-800 text-neutral-300"
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
