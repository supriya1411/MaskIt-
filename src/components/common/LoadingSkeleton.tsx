import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export const LoadingSkeleton: React.FC<{ rows?: number; height?: string }> = ({
  rows = 3,
  height = 'h-16',
}) => {
  return (
    <div className="space-y-3 w-full animate-pulse">
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className={`w-full ${height} rounded-xl bg-slate-900/60 border border-slate-800/60`}
        />
      ))}
    </div>
  );
};

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

export const EmptyState: React.FC<{
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
}> = ({ icon, title, description, actionText, onAction }) => {
  return (
    <div className="p-10 rounded-2xl glass-card text-center flex flex-col items-center justify-center space-y-3">
      {icon && <div className="text-slate-500 mb-1">{icon}</div>}
      <h3 className="text-sm font-bold text-slate-200 font-mono uppercase tracking-wider">{title}</h3>
      <p className="text-xs text-slate-400 max-w-md">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="mt-2 px-4 py-2 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 rounded-xl text-xs font-bold transition font-mono"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};
