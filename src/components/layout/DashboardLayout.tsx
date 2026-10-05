import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Menu, X, Shield, Radio } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { useDashboardStore } from '../../stores/dashboardStore';
import { useProtectionStore } from '../../stores/protectionStore';
import { dashboardWs, LiveDashboardEvent } from '../../services/websocket';
import { ThemeToggle } from '../common/ThemeToggle';

export const DashboardLayout: React.FC = () => {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [liveToast, setLiveToast] = useState<LiveDashboardEvent | null>(null);

  const { isAuthenticated, isInitialized } = useAuthStore();
  const { fetchAll, applyLiveEvent } = useDashboardStore();
  const { fetchSites, fetchSummary } = useProtectionStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (isInitialized && !isAuthenticated) {
      navigate('/login');
    }
  }, [isInitialized, isAuthenticated, navigate]);

  useEffect(() => {
    fetchAll();
    fetchSites();
    fetchSummary();

    dashboardWs.connect();

    const unsubscribeWs = dashboardWs.addEventListener((event) => {
      if (event.event !== 'CONNECTED' && event.event !== 'PONG') {
        applyLiveEvent(event);
        setLiveToast(event);
        if (event.event === 'SITE_PROTECTED' || event.event === 'SITE_UNPROTECTED' || event.event === 'SITE_STATUS_CHANGED') {
          fetchSites();
          fetchSummary();
        }
      }
    });

    return () => {
      unsubscribeWs();
    };
  }, []);

  useEffect(() => {
    if (liveToast) {
      const timer = setTimeout(() => setLiveToast(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [liveToast]);

  return (
    <div className="h-screen w-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex overflow-hidden font-sans transition-colors">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block shrink-0">
        <Sidebar />
      </div>

      {/* Mobile Drawer */}
      {mobileSidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            onClick={() => setMobileSidebarOpen(false)}
            className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs"
          />
          <div className="relative z-10 w-64 h-full">
            <Sidebar onCloseMobile={() => setMobileSidebarOpen(false)} />
          </div>
        </div>
      )}

      {/* Main Content Pane */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header Bar */}
        <header className="h-16 shrink-0 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 sm:px-8 flex items-center justify-between z-10 transition-colors">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
              aria-label="Open navigation menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-sm font-semibold text-slate-900 dark:text-white">Privacy Console</h1>
              <p className="text-xs text-slate-500 hidden sm:block">Real-time browser fingerprint virtualization</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>Protection Active</span>
            </span>

            <ThemeToggle />
          </div>
        </header>

        {/* Clean Live Event Toast Notification */}
        {liveToast && (
          <div className="fixed top-20 right-6 z-50 max-w-sm rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-3.5 shadow-lg text-xs space-y-1">
            <div className="flex items-center justify-between text-slate-900 dark:text-white font-medium">
              <div className="flex items-center space-x-1.5 text-blue-600 dark:text-blue-400 font-semibold">
                <Shield className="w-3.5 h-3.5" />
                <span>Probe Intercepted</span>
              </div>
              <button onClick={() => setLiveToast(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
            <p className="text-slate-600 dark:text-slate-300">
              <span className="font-semibold text-slate-900 dark:text-white">{liveToast.domain || 'Domain'}</span>: {liveToast.signal || 'Signal'} probe{' '}
              <span className="text-emerald-600 dark:text-emerald-400 font-medium">{liveToast.action || 'MASKED'}</span>
            </p>
            {liveToast.risk_before !== undefined && liveToast.risk_after !== undefined && (
              <p className="text-slate-500 text-[11px]">
                Risk reduction: <span className="line-through">{liveToast.risk_before}</span> → <span className="font-bold text-blue-600 dark:text-blue-400">{liveToast.risk_after}</span>
              </p>
            )}
          </div>
        )}

        {/* Page Content Viewport */}
        <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
