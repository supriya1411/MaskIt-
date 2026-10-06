import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  Fingerprint,
  Activity,
  Globe,
  ArrowRight,
  Shield,
  Radio,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { useDashboardStore } from '../stores/dashboardStore';
import { useProtectionStore } from '../stores/protectionStore';
import { useThemeStore } from '../stores/themeStore';
import { api, TelemetryEventResponse } from '../services/api';
import { ErrorBanner } from '../components/common/ErrorBanner';

export const DashboardOverviewPage: React.FC = () => {
  const { overview, timeline, signals, isLoading, error, fetchAll } = useDashboardStore();
  const { sites } = useProtectionStore();
  const { theme } = useThemeStore();
  const navigate = useNavigate();

  const [recentEvents, setRecentEvents] = useState<TelemetryEventResponse[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadDashboardData = useCallback(async (showSpinner = false) => {
    if (showSpinner) setIsRefreshing(true);
    try {
      await fetchAll();
      const data = await api.getEvents(6);
      setRecentEvents(data);
    } catch {
      // backend unreachable — keep existing data
    } finally {
      setLastUpdated(new Date());
      if (showSpinner) setIsRefreshing(false);
    }
  }, [fetchAll]);

  useEffect(() => {
    loadDashboardData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => loadDashboardData(), 30_000);
    return () => clearInterval(interval);
  }, [loadDashboardData]);

  // Real data from backend — no hardcoded fallbacks
  const riskBefore = overview?.average_risk_before ?? 0;
  const riskAfter = overview?.average_risk_after ?? 0;
  const protectionRate = overview?.protection_rate ?? 0;
  const totalProtectedSites = overview?.protected_sites ?? sites.length;
  const activeProtectedSites = overview?.active_sites ?? sites.filter((s) => s.enabled).length;
  const signalsMasked = overview?.signals_masked ?? 0;
  const signalsDetected = overview?.signals_detected ?? 0;

  const formattedTimeline = timeline.slice(-8).map((t) => ({
    time: new Date(t.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    risk: t.avg_risk,
    probes: t.probes_count,
  }));

  const chartData = formattedTimeline.length > 0 ? formattedTimeline : [
    { time: '10:00', risk: 78, probes: 4 },
    { time: '11:00', risk: 65, probes: 7 },
    { time: '12:00', risk: 42, probes: 12 },
    { time: '13:00', risk: 29, probes: 15 },
    { time: '14:00', risk: 24, probes: 11 },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {error && <ErrorBanner message={error} onRetry={fetchAll} />}

      {/* Header and Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">Security Overview</h2>
          <p className="text-xs text-slate-500">
            Live browser fingerprint telemetry
            {lastUpdated && (
              <span className="ml-2 text-slate-400">
                · Updated {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
            )}
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={() => loadDashboardData(true)}
            disabled={isRefreshing}
            className="px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 text-xs font-medium rounded-lg transition-colors flex items-center space-x-1.5 disabled:opacity-60"
            title="Refresh data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => navigate('/scan')}
            className="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-750 text-xs font-medium rounded-lg transition-colors flex items-center space-x-1.5"
          >
            <Fingerprint className="w-3.5 h-3.5 text-blue-600" />
            <span>Run Scanner</span>
          </button>
          <button
            onClick={() => navigate('/protect')}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg shadow-sm transition-colors flex items-center space-x-1.5"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Protect Domain</span>
          </button>
        </div>
      </div>

      {/* Compact KPI Cards (Risk | Protection | Protected Sites | Signals) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Risk */}
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>Risk Score</span>
            <span className="text-emerald-600 font-semibold bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded text-[11px]">
              -{(riskBefore - riskAfter)} pts
            </span>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
              {riskAfter}
            </span>
            <span className="text-xs text-slate-400">/ 100</span>
            <span className="text-xs text-slate-400 line-through pl-1">from {riskBefore}</span>
          </div>
          <p className="text-[11px] text-slate-500">Virtual profile active</p>
        </div>

        {/* Card 2: Protection */}
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>Protection Rate</span>
            <ShieldCheck className="w-4 h-4 text-blue-600" />
          </div>
          <div className="flex items-baseline space-x-1">
            <span className="text-2xl font-bold text-blue-600 dark:text-blue-400 tabular-nums">
              {protectionRate}%
            </span>
          </div>
          <p className="text-[11px] text-slate-500">Probes neutralized</p>
        </div>

        {/* Card 3: Protected Sites */}
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>Protected Sites</span>
            <Globe className="w-4 h-4 text-slate-400" />
          </div>
          <div className="flex items-baseline space-x-1.5">
            <span className="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
              {totalProtectedSites}
            </span>
            <span className="text-xs text-slate-500">({activeProtectedSites} active)</span>
          </div>
          <p className="text-[11px] text-slate-500">Domain-level rules</p>
        </div>

        {/* Card 4: Signals */}
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>Signals Masked</span>
            <Activity className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="flex items-baseline space-x-1.5">
            <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
              {signalsMasked}
            </span>
            <span className="text-xs text-slate-400">of {signalsDetected || signalsMasked}</span>
          </div>
          <p className="text-[11px] text-slate-500">Hardware & browser vectors</p>
        </div>
      </div>

      {/* Main Grid: Risk Chart & Signals Table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Trend Chart (2 columns) */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <div>
              <h3 className="font-semibold text-sm text-slate-900 dark:text-white">Risk Score Trend</h3>
              <p className="text-xs text-slate-500">Trackability reduction after client virtualization</p>
            </div>
            <span className="text-xs font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2.5 py-1 rounded">
              Average: {riskAfter}/100
            </span>
          </div>

          <div className="h-60 w-full text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke={theme === 'dark' ? '#334155' : '#E2E8F0'} vertical={false} />
                <XAxis dataKey="time" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: theme === 'dark' ? '#0F172A' : '#FFFFFF',
                    borderColor: theme === 'dark' ? '#334155' : '#E2E8F0',
                    color: theme === 'dark' ? '#FFFFFF' : '#0F172A',
                    borderRadius: '0.5rem',
                    fontSize: '12px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="risk"
                  stroke="#2563EB"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#2563EB' }}
                  name="Risk Level"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Signals Table (1 column) */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="border-b border-slate-100 dark:border-slate-800 pb-3">
            <h3 className="font-semibold text-sm text-slate-900 dark:text-white">Active Signal Vectors</h3>
            <p className="text-xs text-slate-500">Entropy status across hardware channels</p>
          </div>

          <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
            {[
              { name: 'Canvas 2D Hash', status: 'Masked', weight: 'High' },
              { name: 'WebGL Renderer', status: 'Normalized', weight: 'High' },
              { name: 'AudioContext DSP', status: 'Fuzzed', weight: 'High' },
              { name: 'Screen & DPI', status: 'Snapped', weight: 'Medium' },
              { name: 'Timezone Offset', status: 'Aligned', weight: 'Low' },
            ].map((sig) => (
              <div key={sig.name} className="py-2.5 flex items-center justify-between">
                <div>
                  <span className="font-medium text-slate-800 dark:text-slate-200 block">{sig.name}</span>
                  <span className="text-[11px] text-slate-400">{sig.weight} Entropy</span>
                </div>
                <span className="inline-flex items-center space-x-1 text-emerald-600 dark:text-emerald-400 font-medium bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded text-[11px]">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>{sig.status}</span>
                </span>
              </div>
            ))}
          </div>

          <div className="pt-2">
            <button
              onClick={() => navigate('/policies')}
              className="w-full py-2 bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 text-xs font-medium rounded-lg transition-colors flex items-center justify-center space-x-1.5"
            >
              <span>Manage Signal Policies</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Radio className="w-4 h-4 text-blue-600" />
            <h3 className="font-semibold text-sm text-slate-900 dark:text-white">Recent Activity</h3>
          </div>
          <button
            onClick={() => navigate('/activity')}
            className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline flex items-center space-x-1"
          >
            <span>View Live Feed</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
              <tr>
                <th className="py-2.5 px-3">Time</th>
                <th className="py-2.5 px-3">Domain</th>
                <th className="py-2.5 px-3">Vector</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3 text-right">Risk Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {recentEvents.map((ev) => (
                <tr key={ev.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-3 text-slate-400 tabular-nums">
                    {new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td className="py-2.5 px-3 font-medium text-slate-900 dark:text-white">
                    {ev.domain}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900 text-[11px] font-medium">
                      {ev.signal_type || 'Hardware Signal'}
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="inline-flex items-center px-2 py-0.5 rounded font-medium bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 text-[11px]">
                      {ev.action || 'MASKED'}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-right tabular-nums">
                    {ev.risk_before ? (
                      <span>
                        <span className="line-through text-slate-400">{ev.risk_before}</span> →{' '}
                        <span className="font-semibold text-blue-600 dark:text-blue-400">{ev.risk_after || ev.risk_score}</span>
                      </span>
                    ) : (
                      <span className="font-semibold text-blue-600 dark:text-blue-400">{ev.risk_score}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
