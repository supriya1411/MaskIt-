import React, { useEffect, useState, useRef } from 'react';
import { Radio, Shield, Clock, ArrowRight, Trash2, Zap, Play, Square } from 'lucide-react';
import { dashboardWs, LiveDashboardEvent } from '../services/websocket';
import { api } from '../services/api';

export const LiveActivityPage: React.FC = () => {
  const [events, setEvents] = useState<LiveDashboardEvent[]>([]);
  const [wsStatus, setWsStatus] = useState<'CONNECTING' | 'CONNECTED' | 'DISCONNECTED'>('CONNECTING');
  const [isSimulating, setIsSimulating] = useState(false);
  const simIntervalRef = useRef<any>(null);

  useEffect(() => {
    // Initial fetch of recent stored events from backend
    api.getEvents(25)
      .then((data) => {
        if (data && data.length > 0) {
          setEvents(data.map((d) => ({
            event: d.event_type,
            domain: d.domain,
            signal: d.signal_type || 'GENERIC',
            action: d.action || 'MASKED',
            risk_before: d.risk_before || d.risk_score,
            risk_after: d.risk_after || d.risk_score,
            timestamp: d.timestamp,
          })));
        }
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
      if (simIntervalRef.current) clearInterval(simIntervalRef.current);
    };
  }, []);

  const triggerSingleProbe = async () => {
    const domains = ['youtube.com', 'tiktok.com', 'google.com', 'amazon.com', 'reddit.com'];
    const signals = ['CANVAS_HASH', 'WEBGL_GPU', 'AUDIO_DSP', 'HARDWARE_CPU', 'SCREEN_METRIC', 'FONT_ENUM'];
    const domain = domains[Math.floor(Math.random() * domains.length)];
    const signal = signals[Math.floor(Math.random() * signals.length)];

    const payload = {
      event_type: 'FINGERPRINT_PROBE',
      domain,
      signal_type: signal,
      action: 'MASKED',
      source: 'DASHBOARD',
      risk_before: 72 + Math.floor(Math.random() * 20),
      risk_after: 16 + Math.floor(Math.random() * 12),
    };

    try {
      await api.logEvent(payload);
    } catch (e) {
      // Fallback local emission if backend is offline
      const localEv: LiveDashboardEvent = {
        event: 'PROBE_INTERCEPTED',
        domain,
        signal,
        action: 'NOISE_INJECTED',
        risk_before: 88,
        risk_after: 22,
        timestamp: new Date().toISOString(),
      };
      setEvents((prev) => [localEv, ...prev].slice(0, 50));
    }
  };

  const toggleAutoStream = () => {
    if (isSimulating) {
      if (simIntervalRef.current) clearInterval(simIntervalRef.current);
      setIsSimulating(false);
    } else {
      setIsSimulating(true);
      triggerSingleProbe();
      simIntervalRef.current = setInterval(() => {
        triggerSingleProbe();
      }, 2500);
    }
  };

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

        <div className="flex items-center space-x-2.5 text-xs">
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

          <button
            onClick={triggerSingleProbe}
            className="px-2.5 py-1 bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-900 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-100 transition-colors font-medium flex items-center space-x-1 cursor-pointer"
            title="Simulate a real-time probe"
          >
            <Zap className="w-3.5 h-3.5 text-blue-600" />
            <span>+ Test Probe</span>
          </button>

          <button
            onClick={toggleAutoStream}
            className={`px-2.5 py-1 rounded-lg border font-medium flex items-center space-x-1 transition-colors cursor-pointer ${
              isSimulating
                ? 'bg-rose-50 dark:bg-rose-950/60 border-rose-300 dark:border-rose-800 text-rose-700 dark:text-rose-300'
                : 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-300 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300'
            }`}
          >
            {isSimulating ? <Square className="w-3 h-3 text-rose-600 fill-current" /> : <Play className="w-3 h-3 text-emerald-600 fill-current" />}
            <span>{isSimulating ? 'Stop Stream' : 'Live Stream'}</span>
          </button>

          {events.length > 0 && (
            <button
              onClick={() => setEvents([])}
              className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded cursor-pointer"
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
          <span className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Live WebSocket auto-stream</span>
          </span>
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
                className="p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors animate-fade-in"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-slate-400 text-[11px] tabular-nums">
                    {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : 'Just now'}
                  </span>
                  <span className="font-semibold text-slate-900 dark:text-white">
                    {ev.domain || 'Domain'}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900 text-[11px] font-medium font-mono">
                    {ev.signal || 'Signal'}
                  </span>
                </div>

                <div className="flex items-center space-x-3 text-xs">
                  <span className="inline-flex items-center px-2 py-0.5 rounded font-medium bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 text-[11px]">
                    🛡️ {ev.action || 'MASKED'}
                  </span>

                  {ev.risk_before !== undefined && ev.risk_after !== undefined && (
                    <span className="text-slate-500 tabular-nums">
                      {ev.risk_before} → <span className="font-semibold text-emerald-600 dark:text-emerald-400">{ev.risk_after}</span>
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

