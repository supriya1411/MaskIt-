import { create } from 'zustand';
import { api, ExtensionConfigResponse, getErrorMessage } from '../services/api';

interface ExtensionState {
  config: ExtensionConfigResponse | null;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;

  fetchConfig: () => Promise<void>;
}

export const useExtensionStore = create<ExtensionState>((set) => ({
  config: null,
  isConnected: false,
  isLoading: false,
  error: null,

  fetchConfig: async () => {
    set({ isLoading: true });
    try {
      const config = await api.getExtensionConfig();
      set({ config, isConnected: true, isLoading: false, error: null });
    } catch (err) {
      set({
        config: null,
        isConnected: false,
        isLoading: false,
        error: getErrorMessage(err),
      });
    }
  },
}));
