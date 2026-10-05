import { create } from 'zustand';
import {
  api,
  ProtectedSite,
  ProtectionSummary,
  SiteAnalytics,
  getErrorMessage,
} from '../services/api';

interface ProtectionState {
  sites: ProtectedSite[];
  summary: ProtectionSummary | null;
  activeSiteAnalytics: SiteAnalytics | null;
  isLoading: boolean;
  isActionLoading: boolean;
  error: string | null;
  successMessage: string | null;

  fetchSites: () => Promise<void>;
  fetchSummary: () => Promise<void>;
  protectSite: (domain: string, policyId?: string) => Promise<boolean>;
  updateSite: (siteId: string, enabled: boolean, policyId?: string) => Promise<boolean>;
  deleteSite: (siteId: string) => Promise<boolean>;
  fetchSiteAnalytics: (siteId: string) => Promise<void>;
  clearFeedback: () => void;
}

export const useProtectionStore = create<ProtectionState>((set, get) => ({
  sites: [],
  summary: null,
  activeSiteAnalytics: null,
  isLoading: false,
  isActionLoading: false,
  error: null,
  successMessage: null,

  fetchSites: async () => {
    set({ isLoading: true, error: null });
    try {
      const sites = await api.getProtectedSites();
      set({ sites, isLoading: false });
    } catch (err) {
      set({ error: getErrorMessage(err), isLoading: false });
    }
  },

  fetchSummary: async () => {
    try {
      const summary = await api.getProtectionSummary();
      set({ summary });
    } catch (err) {
      console.error('Failed to fetch protection summary:', err);
    }
  },

  protectSite: async (domain: string, policyId?: string) => {
    set({ isActionLoading: true, error: null, successMessage: null });
    try {
      const site = await api.protectSite(domain, policyId);
      set({
        successMessage: `✓ ${site.domain} is now protected by MaskIt.`,
        isActionLoading: false,
      });
      // Refresh sites list and summary from backend
      await Promise.all([get().fetchSites(), get().fetchSummary()]);
      return true;
    } catch (err) {
      set({ error: getErrorMessage(err), isActionLoading: false });
      return false;
    }
  },

  updateSite: async (siteId: string, enabled: boolean, policyId?: string) => {
    set({ isActionLoading: true, error: null });
    try {
      const updated = await api.updateProtectedSite(siteId, { enabled, policy_id: policyId });
      set((state) => ({
        sites: state.sites.map((s) => (s.id === siteId ? updated : s)),
        isActionLoading: false,
        successMessage: `Shield status for ${updated.domain} updated to ${updated.status}.`,
      }));
      get().fetchSummary();
      return true;
    } catch (err) {
      set({ error: getErrorMessage(err), isActionLoading: false });
      return false;
    }
  },

  deleteSite: async (siteId: string) => {
    set({ isActionLoading: true, error: null });
    try {
      await api.deleteProtectedSite(siteId);
      set((state) => ({
        sites: state.sites.filter((s) => s.id !== siteId),
        isActionLoading: false,
        successMessage: 'Domain protection rule removed.',
      }));
      get().fetchSummary();
      return true;
    } catch (err) {
      set({ error: getErrorMessage(err), isActionLoading: false });
      return false;
    }
  },

  fetchSiteAnalytics: async (siteId: string) => {
    set({ isLoading: true, error: null });
    try {
      const analytics = await api.getSiteAnalytics(siteId);
      set({ activeSiteAnalytics: analytics, isLoading: false });
    } catch (err) {
      set({ error: getErrorMessage(err), isLoading: false });
    }
  },

  clearFeedback: () => set({ error: null, successMessage: null }),
}));
