import React from 'react';

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
