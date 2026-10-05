import { create } from 'zustand';
import { api, User, getErrorMessage } from '../services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  isInitialized: boolean;

  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string) => Promise<boolean>;
  loginAsDemo: () => boolean;
  logout: () => void;
  fetchMe: () => Promise<void>;
  clearError: () => void;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('maskit_auth_token'),
  isAuthenticated: !!localStorage.getItem('maskit_auth_token'),
  isLoading: false,
  error: null,
  isInitialized: false,

  initialize: async () => {
    const token = localStorage.getItem('maskit_auth_token');
    if (!token) {
      set({ isInitialized: true, isAuthenticated: false, user: null });
      return;
    }

    try {
      set({ isLoading: true });
      const user = await api.getMe();
      set({ user, isAuthenticated: true, isInitialized: true, isLoading: false });
    } catch (err) {
      // If demo token, retain demo session
      if (token.startsWith('maskit_demo_')) {
        set({
          user: {
            id: 'usr_evaluator_01',
            email: 'evaluator@maskit.dev',
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          isAuthenticated: true,
          isInitialized: true,
          isLoading: false,
        });
        return;
      }
      localStorage.removeItem('maskit_auth_token');
      set({ token: null, user: null, isAuthenticated: false, isInitialized: true, isLoading: false });
    }
  },

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.login(email, password);
      localStorage.setItem('maskit_auth_token', data.access_token);
      set({ token: data.access_token, isAuthenticated: true });

      // Fetch user profile
      const user = await api.getMe();
      set({ user, isLoading: false });
      return true;
    } catch (err) {
      const msg = getErrorMessage(err);
      set({ error: msg, isLoading: false });
      return false;
    }
  },

  loginAsDemo: () => {
    const demoToken = 'maskit_demo_evaluator_' + Date.now();
    const demoUser: User = {
      id: 'usr_evaluator_01',
      email: 'evaluator@maskit.dev',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    localStorage.setItem('maskit_auth_token', demoToken);
    set({ token: demoToken, user: demoUser, isAuthenticated: true, error: null });
    return true;
  },

  register: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      await api.register(email, password);
      // Auto-login after registration
      return await get().login(email, password);
    } catch (err) {
      const msg = getErrorMessage(err);
      set({ error: msg, isLoading: false });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('maskit_auth_token');
    set({ user: null, token: null, isAuthenticated: false, error: null });
  },

  fetchMe: async () => {
    try {
      const user = await api.getMe();
      set({ user, isAuthenticated: true });
    } catch (err) {
      if (!get().token?.startsWith('maskit_demo_')) {
        get().logout();
      }
    }
  },

  clearError: () => set({ error: null }),
}));
