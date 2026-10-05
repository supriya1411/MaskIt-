import React, { useEffect } from 'react';
import {
  Settings,
  Server,
  Database,
  Layers,
  RefreshCw,
  LogOut,
  User,
  Shield,
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { useDashboardStore } from '../stores/dashboardStore';
import { API_BASE_URL, WS_BASE_URL } from '../services/api';

export const SettingsPage: React.FC = () => {
  const { user, logout } = useAuthStore();
  const { health, isHealthLoading, fetchHealth } = useDashboardStore();

  useEffect(() => {
    fetchHealth();
  }, []);

  const isHealthy = health?.status === 'healthy';
  const isDbConnected = health?.database === 'connected';

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center space-x-2">
          <Settings className="w-5 h-5 text-blue-600" />
          <span>Settings & Diagnostics</span>
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Backend API endpoints, system connectivity, and account details
        </p>
      </div>

      {/* Backend Diagnostics */}
      <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Server className="w-4 h-4 text-blue-600" />
            <h3 className="font-semibold text-sm text-slate-900 dark:text-white">
              Service Diagnostics
            </h3>
          </div>
          <button
            onClick={() => fetchHealth()}
            disabled={isHealthLoading}
            className="text-xs text-blue-600 dark:text-blue-400 font-medium hover:underline flex items-center space-x-1"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isHealthLoading ? 'animate-spin' : ''}`} />
            <span>Check Status</span>
          </button>
        </div>

        <div className="space-y-3 text-xs">
          <div>
            <span className="text-slate-500 block mb-1">REST API Gateway:</span>
            <code className="px-2.5 py-1.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 font-mono text-slate-700 dark:text-slate-300 block">
              {API_BASE_URL}
            </code>
          </div>

          <div>
            <span className="text-slate-500 block mb-1">Live WebSocket Feed:</span>
            <code className="px-2.5 py-1.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 font-mono text-slate-700 dark:text-slate-300 block">
              {WS_BASE_URL}
            </code>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
            <div className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40">
              <span className="text-[11px] text-slate-400 block mb-0.5">API STATUS</span>
              <span className={`font-semibold ${isHealthy ? 'text-emerald-600' : 'text-rose-600'}`}>
                {isHealthy ? 'Operational' : 'Unavailable'}
              </span>
            </div>

            <div className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40">
              <span className="text-[11px] text-slate-400 block mb-0.5">POSTGRESQL</span>
              <span className={`font-semibold ${isDbConnected ? 'text-emerald-600' : 'text-rose-600'}`}>
                {isDbConnected ? 'Connected' : 'Unavailable'}
              </span>
            </div>

            <div className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40">
              <span className="text-[11px] text-slate-400 block mb-0.5">CACHE LAYER</span>
              <span className="font-semibold text-emerald-600">
                {health?.redis === 'connected' ? 'Connected' : 'Fallback (Memory)'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Account Info */}
      <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-100 dark:border-slate-800 pb-3">
          <User className="w-4 h-4 text-blue-600" />
          <h3 className="font-semibold text-sm text-slate-900 dark:text-white">
            Account & Session
          </h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-slate-500 block mb-0.5">Active Account:</span>
            <span className="font-semibold text-slate-900 dark:text-white">{user?.email || 'Authenticated User'}</span>
          </div>

          <div>
            <span className="text-slate-500 block mb-0.5">Protection Status:</span>
            <span className="font-semibold text-emerald-600">Active</span>
          </div>
        </div>

        <div className="pt-2">
          <button
            onClick={logout}
            className="px-4 py-2 border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 hover:bg-rose-100 text-rose-600 font-medium text-xs rounded-lg transition-colors flex items-center space-x-1.5"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign out of console</span>
          </button>
        </div>
      </div>
    </div>
  );
};
