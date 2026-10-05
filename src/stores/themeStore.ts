import { create } from 'zustand';

export type ThemeMode = 'light' | 'dark';

interface ThemeState {
  theme: ThemeMode;
  toggleTheme: () => void;
  setTheme: (theme: ThemeMode) => void;
  initTheme: () => void;
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: 'light',

  initTheme: () => {
    const savedTheme = localStorage.getItem('maskit_theme') as ThemeMode | null;
    const theme = savedTheme || 'light';
    set({ theme });

    if (typeof document !== 'undefined') {
      const root = document.documentElement;
      root.classList.remove('dark', 'light');
      root.classList.add(theme);
    }
  },

  setTheme: (newTheme) => {
    localStorage.setItem('maskit_theme', newTheme);
    set({ theme: newTheme });
    if (typeof document !== 'undefined') {
      const root = document.documentElement;
      root.classList.remove('dark', 'light');
      root.classList.add(newTheme);
    }
  },

  toggleTheme: () => {
    const next = get().theme === 'light' ? 'dark' : 'light';
    get().setTheme(next);
  },
}));
