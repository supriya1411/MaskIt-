import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Fingerprint,
  ShieldCheck,
  Globe,
  Radio,
  Sliders,
  Settings,
  LogOut,
  Server,
  Database,
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { useDashboardStore } from '../../stores/dashboardStore';

interface SidebarProps {
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile }) => {
  const { user, logout } = useAuthStore();
  const { health } = useDashboardStore();
  const navigate = useNavigate();

  const navItems = [
    { label: 'Overview', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Browser Scanner', path: '/scan', icon: Fingerprint },
    { label: 'Protect Domains', path: '/protect', icon: ShieldCheck },
    { label: 'Protected Sites', path: '/sites', icon: Globe },
    { label: 'Live Activity', path: '/activity', icon: Radio },
    { label: 'Masking Policies', path: '/policies', icon: Sliders },
    { label: 'Settings', path: '/settings', icon: Settings },
  ];

  const isDbConnected = health?.database === 'connected';
  const isHealthy = health?.status === 'healthy';

  return (
    <aside className="w-64 h-full bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col justify-between transition-colors">
      <div className="flex flex-col flex-1 overflow-y-auto px-4 py-5 space-y-6">
        {/* Brand Header */}
        <div className="px-2 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <span className="font-bold text-base text-slate-900 dark:text-white block leading-none">
              MaskIt
            </span>
            <span className="text-xs text-slate-500 dark:text-slate-400">Security Console</span>
          </div>
        </div>

        {/* Nav Links */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onCloseMobile}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 font-semibold'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Clean System Status */}
        <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 text-xs space-y-2">
          <div className="flex items-center justify-between text-slate-500 font-medium">
            <span>System Status</span>
            <span className={`inline-flex items-center space-x-1 ${isHealthy ? 'text-emerald-600' : 'text-rose-600'}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${isHealthy ? 'bg-emerald-500' : 'bg-rose-500'}`} />
              <span>{isHealthy ? 'Operational' : 'Offline'}</span>
            </span>
          </div>

          <div className="space-y-1 text-slate-600 dark:text-slate-400">
            <div className="flex items-center justify-between">
              <span className="flex items-center space-x-1.5">
                <Server className="w-3 h-3 text-slate-400" />
                <span>API Gateway</span>
              </span>
              <span className="font-medium text-slate-700 dark:text-slate-300">
                {isHealthy ? 'Online' : 'Offline'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center space-x-1.5">
                <Database className="w-3 h-3 text-slate-400" />
                <span>PostgreSQL</span>
              </span>
              <span className="font-medium text-slate-700 dark:text-slate-300">
                {isDbConnected ? 'Connected' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* User Footer */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
        <div className="flex items-center justify-between">
          <div className="truncate">
            <span className="text-xs font-semibold text-slate-900 dark:text-white block truncate">
              {user?.email || 'User'}
            </span>
            <span className="text-[11px] text-slate-500 block">Protection Enabled</span>
          </div>

          <button
            onClick={() => {
              logout();
              navigate('/login');
            }}
            title="Sign out"
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
