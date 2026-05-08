// src/components/Logs/LogPanel.tsx
import React from 'react';
import { LogEntry } from './LogEntry';
import { LogFilter } from './LogFilter';

export const LogPanel: React.FC = () => {
  // placeholder: in real app this would consume a Zustand store of logs
  const logs = [] as const; // mock empty array
  return (
    <section className="flex flex-col h-full bg-gray-900 text-gray-100 font-mono text-sm">
      {/* Filter bar */}
      <LogFilter />
      {/* Log list */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1" data-testid="log-list">
        {logs.map((log, i) => (
          <LogEntry key={i} {...log} />
        ))}
      </div>
    </section>
  );
};

// src/components/Logs/LogEntry.tsx
import React from 'react';

type LogType = 'INFO' | 'TOOL_CALL' | 'TOOL_RESULT' | 'ERROR' | 'MEMORY_UPDATE' | 'AGENT_STEP';

export interface LogProps {
  timestamp: string; // ISO string
  type: LogType;
  message: string;
}

export const LogEntry: React.FC<LogProps> = ({ timestamp, type, message }) => {
  const colorMap: Record<LogType, string> = {
    INFO: 'text-green-400',
    TOOL_CALL: 'text-cyan-400',
    TOOL_RESULT: 'text-purple-400',
    ERROR: 'text-red-400',
    MEMORY_UPDATE: 'text-yellow-400',
    AGENT_STEP: 'text-blue-400',
  };
  return (
    <div className="flex items-start space-x-2">
      <span className="text-gray-500 w-20">{timestamp}</span>
      <span className={colorMap[type] + ' font-bold'}>{type}</span>
      <span className="flex-1 truncate">{message}</span>
    </div>
  );
};

// src/components/Logs/LogFilter.tsx
import React from 'react';

export const LogFilter: React.FC = () => {
  // placeholder for UI controls (checkboxes / dropdown) to toggle log types
  return (
    <div className="flex items-center space-x-2 px-2 py-1 bg-gray-800 border-b border-gray-700">
      <span className="text-gray-400 text-xs">Filter:</span>
      {/* Example checkboxes */}
      {['INFO', 'TOOL_CALL', 'TOOL_RESULT', 'ERROR', 'MEMORY_UPDATE', 'AGENT_STEP'].map((type) => (
        <label key={type} className="inline-flex items-center space-x-1 text-xs text-gray-300">
          <input type="checkbox" defaultChecked className="form-checkbox h-3 w-3" />
          <span>{type}</span>
        </label>
      ))}
    </div>
  );
};
