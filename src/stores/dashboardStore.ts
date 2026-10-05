import { create } from 'zustand';
import {
  api,
  DashboardOverviewResponse,
  TimelinePoint,
  SignalStat,
  RiskDistribution,
  HealthResponse,
  getErrorMessage,
} from '../services/api';
import { LiveDashboardEvent } from '../services/websocket';

interface DashboardState {
  overview: DashboardOverviewResponse | null;
  timeline: TimelinePoint[];
  signals: SignalStat[];
  risk: RiskDistribution | null;
  health: HealthResponse | null;
  isLoading: boolean;
  isHealthLoading: boolean;
  error: string | null;

  fetchAll: () => Promise<void>;
  fetchOverview: () => Promise<void>;
  fetchTimeline: (hours?: number) => Promise<void>;
  fetchSignals: () => Promise<void>;
  fetchRisk: () => Promise<void>;
  fetchHealth: () => Promise<void>;
  applyLiveEvent: (event: LiveDashboardEvent) => void;
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  overview: null,
  timeline: [],
  signals: [],
  risk: null,
  health: null,
  isLoading: false,
  isHealthLoading: false,
  error: null,

  fetchHealth: async () => {
    set({ isHealthLoading: true });
    try {
      const health = await api.getHealth();
      set({ health, isHealthLoading: false });
    } catch (err) {
      set({
        health: { status: 'offline', database: 'disconnected', redis: 'disconnected', timestamp: new Date().toISOString() },
        isHealthLoading: false,
      });
    }
  },

  fetchOverview: async () => {
    try {
      const overview = await api.getDashboard();
      set({ overview, error: null });
    } catch (err) {
      set({ error: getErrorMessage(err) });
    }
  },

  fetchTimeline: async (hours = 24) => {
    try {
      const timeline = await api.getTimeline(hours);
      set({ timeline });
    } catch (err) {
      console.error('Failed to fetch timeline:', err);
    }
  },

  fetchSignals: async () => {
    try {
      const signals = await api.getSignals();
      set({ signals });
    } catch (err) {
      console.error('Failed to fetch signals:', err);
    }
  },

  fetchRisk: async () => {
    try {
      const risk = await api.getRisk();
      set({ risk });
    } catch (err) {
      console.error('Failed to fetch risk distribution:', err);
    }
  },

  fetchAll: async () => {
    set({ isLoading: true, error: null });
    try {
      const [overview, timeline, signals, risk] = await Promise.all([
        api.getDashboard().catch(() => null),
        api.getTimeline().catch(() => []),
        api.getSignals().catch(() => []),
        api.getRisk().catch(() => null),
      ]);
      set({ overview, timeline, signals, risk, isLoading: false });
      get().fetchHealth();
    } catch (err) {
      set({ error: getErrorMessage(err), isLoading: false });
    }
  },

  applyLiveEvent: (event: LiveDashboardEvent) => {
    const currentOverview = get().overview;
    if (currentOverview) {
      const updatedOverview: DashboardOverviewResponse = {
        ...currentOverview,
        fingerprint_probes: currentOverview.fingerprint_probes + 1,
        scans_today: currentOverview.scans_today + 1,
        signals_detected: currentOverview.signals_detected + 1,
        signals_masked: event.action === 'MASKED' ? currentOverview.signals_masked + 1 : currentOverview.signals_masked,
      };
      set({ overview: updatedOverview });
    }

    // Append to timeline
    if (event.timestamp) {
      set((state) => ({
        timeline: [
          ...state.timeline,
          {
            timestamp: event.timestamp || new Date().toISOString(),
            probes_count: 1,
            masked_count: event.action === 'MASKED' ? 1 : 0,
            avg_risk: event.risk_before || 50,
          },
        ],
      }));
    }
  },
}));
