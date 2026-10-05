import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export const ErrorBanner: React.FC<{
  message: string;
  onRetry?: () => void;
  className?: string;
}> = ({ message, onRetry, className = '' }) => {
  return (
    <div
      className={`p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-200 text-xs font-mono flex items-center justify-between gap-3 ${className}`}
    >
      <div className="flex items-center space-x-2.5">
        <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
        <span>{message}</span>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-3 py-1 bg-rose-900/40 hover:bg-rose-800/40 text-rose-300 font-bold rounded-lg border border-rose-500/30 transition flex items-center space-x-1.5 shrink-0"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Retry</span>
        </button>
      )}
    </div>
  );
};
