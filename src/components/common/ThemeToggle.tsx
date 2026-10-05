import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useThemeStore } from '../../stores/themeStore';

export const ThemeToggle: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { theme, toggleTheme } = useThemeStore();
  const isDark = theme === 'dark';

  return (
    <button
      onClick={toggleTheme}
      type="button"
      aria-label={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
      title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
      className={`p-2 rounded-lg border transition-colors ${
        isDark
          ? 'bg-slate-800 border-slate-700 text-slate-300 hover:text-white hover:bg-slate-700'
          : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50'
      } ${className}`}
    >
      {isDark ? (
        <Sun className="w-4 h-4 text-amber-400" />
      ) : (
        <Moon className="w-4 h-4 text-slate-600" />
      )}
    </button>
  );
};
