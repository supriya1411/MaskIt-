import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from 'recharts';
import { BarChart3, Activity, RefreshCw, ArrowRight } from 'lucide-react';
import { useDashboardStore } from '../stores/dashboardStore';
import { useThemeStore } from '../stores/themeStore';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorBanner } from '../components/common/ErrorBanner';

export const AnalyticsPage: React.FC = () => {
  const { timeline, signals, risk, overview, isLoading, error, fetchAll } = useDashboardStore();
  const { theme } = useThemeStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchAll();
  }, []);

  const hasData = (signals && signals.length > 0 && signals.some((s) => s.count > 0)) || (timeline && timeline.length > 0);

  const formattedTimeline = timeline.map((t) => ({
    time: new Date(t.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    probes: t.probes_count,
    masked: t.masked_count,
    risk: t.avg_risk,
  }));

  const riskPieData = risk
    ? [
        { name: 'Low Risk (<35)', value: risk.low_count, color: '#16A34A' },
        { name: 'Medium (35-60)', value: risk.medium_count, color: '#2563EB' },
        { name: 'High (60-80)', value: risk.high_count, color: '#D97706' },
        { name: 'Critical (>80)', value: risk.critical_count, color: '#DC2626' },
      ].filter((d) => d.value > 0)
    : [];

  const tooltipBg = theme === 'dark' ? '#0F172A' : '#FFFFFF';
  const tooltipBorder = theme === 'dark' ? '#334155' : '#E2E8F0';
  const gridStroke = theme === 'dark' ? '#334155' : '#E2E8F0';

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <span>Fingerprint Analytics</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Aggregated telemetry and risk scoring queried directly from the backend
          </p>
        </div>

        <button
          onClick={() => fetchAll()}
          className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-750 transition-colors flex items-center space-x-2 text-xs font-medium"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {error && <ErrorBanner message={error} onRetry={fetchAll} />}

      {isLoading ? (
        <LoadingSkeleton rows={3} height="h-64" />
      ) : !hasData ? (
        <EmptyState
          icon={<Activity className="w-10 h-10 text-slate-400" />}
          title="No Telemetry Data Available Yet"
          description="Execute a browser scan or visit a protected website to populate fingerprint telemetry."
          actionText="Run Browser Scan"
          onAction={() => navigate('/scan')}
        />
      ) : (
        <div className="space-y-6">
          {/* Chart 1: Probes vs Masked Timeline */}
          <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div>
                <h3 className="font-semibold text-sm text-slate-900 dark:text-white">
                  Interception Activity (Probes vs Masked)
                </h3>
                <p className="text-xs text-slate-500">Real-time volume over time</p>
              </div>
              <span className="text-xs font-medium text-slate-500">Timeline</span>
            </div>

            <div className="h-72 w-full text-xs">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formattedTimeline}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
                  <XAxis dataKey="time" stroke="#94A3B8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: tooltipBg,
                      borderColor: tooltipBorder,
                      color: theme === 'dark' ? '#F8FAFC' : '#0F172A',
                      borderRadius: '0.5rem',
                      fontSize: '12px',
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="probes" stroke="#64748B" strokeWidth={2} name="Probes Detected" dot={{ r: 2 }} />
                  <Line type="monotone" dataKey="masked" stroke="#2563EB" strokeWidth={2.5} name="Signals Masked" dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Grid: Signals Breakdown & Risk Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Chart 2: Signal Distribution */}
            <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <h3 className="font-semibold text-sm text-slate-900 dark:text-white">
                Probes by Signal Vector
              </h3>

              <div className="h-64 w-full text-xs">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={signals} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} horizontal={false} />
                    <XAxis type="number" stroke="#94A3B8" fontSize={11} tickLine={false} />
                    <YAxis dataKey="signal" type="category" stroke="#94A3B8" fontSize={10} width={90} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: tooltipBg,
                        borderColor: tooltipBorder,
                        color: theme === 'dark' ? '#F8FAFC' : '#0F172A',
                        borderRadius: '0.5rem',
                        fontSize: '12px',
                      }}
                    />
                    <Bar dataKey="count" fill="#2563EB" radius={[0, 4, 4, 0]} name="Probe Count" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 3: Risk Score Distribution */}
            <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <h3 className="font-semibold text-sm text-slate-900 dark:text-white">
                Risk Distribution
              </h3>

              <div className="h-64 w-full flex items-center justify-center text-xs">
                {riskPieData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={riskPieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={80}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {riskPieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: tooltipBg,
                          borderColor: tooltipBorder,
                          color: theme === 'dark' ? '#F8FAFC' : '#0F172A',
                          borderRadius: '0.5rem',
                          fontSize: '12px',
                        }}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-xs text-slate-500">No risk categorization events recorded yet.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
