import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Globe,
  ShieldCheck,
  Activity,
  Layers,
  BarChart2,
  RefreshCw,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { useProtectionStore } from '../stores/protectionStore';
import { useThemeStore } from '../stores/themeStore';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorBanner } from '../components/common/ErrorBanner';

export const SiteDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { activeSiteAnalytics, isLoading, error, fetchSiteAnalytics } = useProtectionStore();
  const { theme } = useThemeStore();

  useEffect(() => {
    if (id) {
      fetchSiteAnalytics(id);
    }
  }, [id]);

  const signalChartData = activeSiteAnalytics
    ? [
        { name: 'Canvas', probes: activeSiteAnalytics.canvas_events },
        { name: 'WebGL', probes: activeSiteAnalytics.webgl_events },
        { name: 'Navigator', probes: activeSiteAnalytics.navigator_events },
        { name: 'Screen', probes: activeSiteAnalytics.screen_events },
        { name: 'Timezone', probes: activeSiteAnalytics.timezone_events },
        { name: 'Media', probes: activeSiteAnalytics.media_devices_events },
        { name: 'Audio', probes: activeSiteAnalytics.audio_events },
      ]
    : [];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Back button */}
      <button
        onClick={() => navigate('/sites')}
        className="inline-flex items-center space-x-1.5 text-xs font-medium text-slate-500 hover:text-blue-600 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Protected Sites</span>
      </button>

      {error && <ErrorBanner message={error} onRetry={() => id && fetchSiteAnalytics(id)} />}

      {isLoading || !activeSiteAnalytics ? (
        <LoadingSkeleton rows={4} height="h-28" />
      ) : (
        <div className="space-y-6">
          {/* Header Card */}
          <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-950 flex items-center justify-center text-blue-600 dark:text-blue-400">
                  <Globe className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-xl font-bold text-slate-900 dark:text-white">{activeSiteAnalytics.domain}</h2>
                    <span
                      className={`text-[11px] font-medium px-2 py-0.5 rounded ${
                        activeSiteAnalytics.enabled
                          ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                          : 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
                      }`}
                    >
                      {activeSiteAnalytics.enabled ? 'Active' : 'Paused'}
                    </span>
                  </div>
                  <span className="text-xs text-slate-500">
                    Rule ID: {activeSiteAnalytics.site_id}
                  </span>
                </div>
              </div>

              <button
                onClick={() => id && fetchSiteAnalytics(id)}
                className="p-2 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-750 rounded-lg text-slate-600 dark:text-slate-300 transition-colors shrink-0"
                title="Refresh Analytics"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>

            {/* Quick Metrics Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-2">
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800">
                <span className="text-[11px] text-slate-500 uppercase block mb-0.5">Total Events</span>
                <span className="text-xl font-bold text-slate-900 dark:text-white tabular-nums">{activeSiteAnalytics.events}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800">
                <span className="text-[11px] text-slate-500 uppercase block mb-0.5">Fingerprint Probes</span>
                <span className="text-xl font-bold text-blue-600 dark:text-blue-400 tabular-nums">{activeSiteAnalytics.fingerprint_probes}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800">
                <span className="text-[11px] text-slate-500 uppercase block mb-0.5">Signals Masked</span>
                <span className="text-xl font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">{activeSiteAnalytics.signals_masked}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800">
                <span className="text-[11px] text-slate-500 uppercase block mb-0.5">Consistency Index</span>
                <span className="text-xl font-bold text-slate-700 dark:text-slate-300 tabular-nums">{activeSiteAnalytics.consistency_score}%</span>
              </div>
            </div>
          </div>

          {/* Recharts Bar Chart: Signal Breakdown */}
          <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
              Signal Interception Frequency by Vector
            </h3>

            <div className="h-64 w-full pt-2 text-xs">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={signalChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={theme === 'dark' ? '#334155' : '#E2E8F0'} vertical={false} />
                  <XAxis dataKey="name" stroke="#94A3B8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: theme === 'dark' ? '#0F172A' : '#FFFFFF',
                      borderColor: theme === 'dark' ? '#334155' : '#E2E8F0',
                      color: theme === 'dark' ? '#FFFFFF' : '#0F172A',
                      borderRadius: '0.5rem',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="probes" fill="#2563EB" radius={[4, 4, 0, 0]} name="Probes Masked" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
