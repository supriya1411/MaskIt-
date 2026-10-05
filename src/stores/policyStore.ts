import { create } from 'zustand';
import { api, Policy, getErrorMessage } from '../services/api';

interface PolicyState {
  policies: Policy[];
  activePolicy: Policy | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  successMessage: string | null;

  fetchPolicies: () => Promise<void>;
  updatePolicy: (policyId: string, payload: Partial<Policy>) => Promise<boolean>;
  clearFeedback: () => void;
}

export const usePolicyStore = create<PolicyState>((set, get) => ({
  policies: [],
  activePolicy: null,
  isLoading: false,
  isSaving: false,
  error: null,
  successMessage: null,

  fetchPolicies: async () => {
    set({ isLoading: true, error: null });
    try {
      const policies = await api.getPolicies();
      set({
        policies,
        activePolicy: policies[0] || null,
        isLoading: false,
      });
    } catch (err) {
      set({ error: getErrorMessage(err), isLoading: false });
    }
  },

  updatePolicy: async (policyId: string, payload: Partial<Policy>) => {
    set({ isSaving: true, error: null, successMessage: null });
    try {
      const updated = await api.updatePolicy(policyId, payload);
      set((state) => ({
        policies: state.policies.map((p) => (p.id === policyId ? updated : p)),
        activePolicy: updated,
        isSaving: false,
        successMessage: `✓ Masking policy "${updated.name}" updated successfully.`,
      }));
      return true;
    } catch (err) {
      set({ error: getErrorMessage(err), isSaving: false });
      return false;
    }
  },

  clearFeedback: () => set({ error: null, successMessage: null }),
}));
