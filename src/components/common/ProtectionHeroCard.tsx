import React from 'react';
import { ShieldCheck, ArrowRight, Activity, Shield } from 'lucide-react';

interface ProtectionHeroCardProps {
  riskBefore: number;
  riskAfter: number;
  consistency: number;
  isActive: boolean;
  onScanClick?: () => void;
  onProtectClick?: () => void;
}

export const ProtectionHeroCard: React.FC<ProtectionHeroCardProps> = ({
  riskBefore,
  riskAfter,
  consistency,
  isActive,
  onScanClick,
  onProtectClick,
}) => {
  const riskReduction = Math.max(0, Math.round(riskBefore - riskAfter));
  const hasData = riskBefore > 0 || riskAfter > 0;

  return (
    <div className="rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 md:p-8 shadow-sm space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        {/* Left: Status & Description */}
        <div className="space-y-3 max-w-xl">
          <div className="flex items-center space-x-2.5">
            <span className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
              isActive
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-emerald-500' : 'bg-slate-400'}`} />
              <span>{isActive ? 'Protection Active' : 'Protection Paused'}</span>
            </span>
          </div>

          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-white flex items-center space-x-2">
            <span>Browser Signal Virtualization</span>
          </h2>

          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            Real-time browser fingerprint virtualization active. Hardware concurrency, WebGL renderer,
            and Canvas rasterization are dynamically sanitized into consistent population cohorts.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            {onProtectClick && (
              <button
                onClick={onProtectClick}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium shadow-sm transition-colors flex items-center space-x-1.5"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Protect Domain</span>
              </button>
            )}
            {onScanClick && (
              <button
                onClick={onScanClick}
                className="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-200 text-xs font-medium transition-colors flex items-center space-x-1.5"
              >
                <Activity className="w-4 h-4 text-blue-600" />
                <span>Re-scan Signals</span>
              </button>
            )}
          </div>
        </div>

        {/* Right: Risk Comparison */}
        <div className="w-full lg:w-80 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 p-4 space-y-3.5">
          <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-750 pb-2">
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
              Entropy & Risk Impact
            </span>
            {hasData && (
              <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded">
                -{riskReduction} pts
              </span>
            )}
          </div>

          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Unprotected Risk:</span>
              <span className="font-semibold text-rose-600 tabular-nums">{riskBefore} / 100</span>
            </div>
            <div className="h-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div
                style={{ width: `${Math.min(100, Math.max(5, riskBefore))}%` }}
                className="h-full bg-rose-500 rounded-full transition-all duration-500"
              />
            </div>
          </div>

          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Protected Risk:</span>
              <span className="font-semibold text-emerald-600 tabular-nums">{riskAfter} / 100</span>
            </div>
            <div className="h-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div
                style={{ width: `${Math.min(100, Math.max(5, riskAfter))}%` }}
                className="h-full bg-blue-600 rounded-full transition-all duration-500"
              />
            </div>
          </div>

          <div className="space-y-1 text-xs pt-1">
            <div className="flex justify-between">
              <span className="text-slate-500">Consistency:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200 tabular-nums">{consistency}%</span>
            </div>
            <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div
                style={{ width: `${Math.min(100, Math.max(5, consistency))}%` }}
                className="h-full bg-emerald-500 rounded-full transition-all duration-500"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
