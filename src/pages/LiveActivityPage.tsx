import React, { useEffect, useState } from 'react';
import { Radio, Shield, Clock, ArrowRight, Trash2 } from 'lucide-react';
import { dashboardWs, LiveDashboardEvent } from '../services/websocket';
import { api } from '../services/api';

export const LiveActivityPage: React.FC = () => {
  const [events, setEvents] = useState<LiveDashboardEvent[]>([]);
  const [wsStatus, setWsStatus] = useState<'CONNECTING' | 'CONNECTED' | 'DISCONNECTED'>('CONNECTING');

  useEffect(() => {
    // Initial fetch of recent stored events from backend PostgreSQL
    api.getEvents(25)
      .then((data) => {
        setEvents(data.map((d) => ({
          event: d.event_type,
          domain: d.domain,
          signal: d.signal_type || 'GENERIC',
          action: d.action || 'MASKED',
          risk_before: d.risk_before || d.risk_score,
          risk_after: d.risk_after || d.risk_score,
          timestamp: d.timestamp,
        })));
      })
      .catch(() => {});

    const unsubscribeWs = dashboardWs.addEventListener((ev) => {
      if (ev.event !== 'CONNECTED' && ev.event !== 'PONG') {
        setEvents((prev) => [ev, ...prev].slice(0, 50));
      }
    });

    const unsubscribeStatus = dashboardWs.addStatusListener((status) => {
      setWsStatus(status);
    });

    return () => {
      unsubscribeWs();
      unsubscribeStatus();
    };
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center space-x-2">
            <Radio className="w-5 h-5 text-blue-600" />
            <span>Live Protection Feed</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time fingerprint probe interception via WebSocket (<code>/ws/dashboard</code>)
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <span
            className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full font-medium ${
              wsStatus === 'CONNECTED'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                : 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
            }`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${wsStatus === 'CONNECTED' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
            <span>{wsStatus === 'CONNECTED' ? 'Connected' : 'Connecting'}</span>
          </span>

          {events.length > 0 && (
            <button
              onClick={() => setEvents([])}
              className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded"
              title="Clear list"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Compact Real-Time Feed List */}
      <div className="rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 font-medium">
          <span>Recent Interceptions ({events.length})</span>
          <span>Auto-updating stream</span>
        </div>

        {events.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500 space-y-1">
            <Shield className="w-8 h-8 text-slate-300 dark:text-slate-700 mx-auto mb-2" />
            <p className="font-semibold text-slate-700 dark:text-slate-300">Waiting for live probe activity...</p>
            <p className="text-slate-400">Fingerprint queries from protected sites will appear here in real-time.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
            {events.map((ev, i) => (
              <div
                key={ev.timestamp ? `${ev.timestamp}-${i}` : i}
                className="p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-slate-400 text-[11px] tabular-nums">
                    {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : 'Just now'}
                  </span>
                  <span className="font-semibold text-slate-900 dark:text-white">
                    {ev.domain || 'Domain'}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900 text-[11px] font-medium">
                    {ev.signal || 'Signal'}
                  </span>
                </div>

                <div className="flex items-center space-x-3 text-xs">
                  <span className="inline-flex items-center px-2 py-0.5 rounded font-medium bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 text-[11px]">
                    {ev.action || 'MASKED'}
                  </span>

                  {ev.risk_before !== undefined && ev.risk_after !== undefined && (
                    <span className="text-slate-500 tabular-nums">
                      {ev.risk_before} → <span className="font-semibold text-blue-600 dark:text-blue-400">{ev.risk_after}</span>
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
