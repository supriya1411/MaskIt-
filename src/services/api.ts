import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

// ==========================================
// API BASE URL CONFIGURATION
// ==========================================
// In development, default to relative paths so requests flow through the Vite proxy.
// In production, set VITE_API_BASE_URL / VITE_WS_URL to the actual backend origin.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
export const WS_BASE_URL = import.meta.env.VITE_WS_URL ||
  `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/dashboard`;

// Health endpoint base (root of backend)
// When using relative API path, health is at the same origin
export const BACKEND_ROOT_URL = API_BASE_URL.startsWith('/')
  ? ''
  : API_BASE_URL.replace(/\/api\/v1\/?$/, '');

// ==========================================
// DATA MODELS & INTERFACES
// ==========================================

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
}

export interface SessionResponse {
  id: string;
  user_id: string;
  session_token: string;
  client_type: string;
  is_active: boolean;
  started_at: string;
  ended_at?: string | null;
  last_seen_at: string;
}

export interface ScreenSignal {
  width?: number;
  height?: number;
  color_depth?: number;
  pixel_ratio?: number;
}

export interface BrowserSignal {
  user_agent?: string;
  language?: string;
  languages?: string[];
  platform?: string;
  vendor?: string;
}

export interface TimezoneSignal {
  timezone?: string;
  offset?: number;
}

export interface HardwareSignal {
  cpu_cores?: number;
  device_memory?: number;
}

export interface WebGLSignal {
  vendor?: string;
  renderer?: string;
  version?: string;
}

export interface FingerprintAnalyzeRequest {
  domain?: string;
  screen?: ScreenSignal;
  browser?: BrowserSignal;
  timezone?: TimezoneSignal;
  hardware?: HardwareSignal;
  webgl?: WebGLSignal;
  canvas_hash?: string;
  media_device_count?: number;
  audio_hash?: string;
  font_count?: number;
}

export interface RiskFactor {
  signal: string;
  impact: number;
  reason: string;
}

export interface FingerprintAnalyzeResponse {
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  risk_factors: RiskFactor[];
  detected_signals: string[];
  recommendation: string;
  consistency_score: number;
  consistency_issues: string[];
}

export interface DashboardOverviewResponse {
  protected_sites: number;
  active_sites: number;
  scans_today: number;
  fingerprint_probes: number;
  signals_detected: number;
  signals_masked: number;
  high_risk_events: number;
  average_risk_before: number;
  average_risk_after: number;
  average_consistency: number;
  protection_rate: number;
}

export interface TimelinePoint {
  timestamp: string;
  probes_count: number;
  masked_count: number;
  avg_risk: number;
}

export interface SignalStat {
  signal: string;
  count: number;
  masked_count: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  impact_weight: number;
}

export interface RiskDistribution {
  low_count: number;
  medium_count: number;
  high_count: number;
  critical_count: number;
  average_score: number;
}

export interface ProtectedSite {
  id: string;
  domain: string;
  enabled: boolean;
  status: 'ACTIVE' | 'PAUSED';
  policy_id?: string | null;
  created_at: string;
  updated_at: string;
  last_activity_at?: string | null;
}

export interface ProtectionSummary {
  protected_sites: number;
  active_sites: number;
  protection_events: number;
  signals_protected: number;
  high_risk_probes: number;
  average_risk_before: number;
  average_risk_after: number;
  protection_rate: number;
}

export interface SiteAnalytics {
  site_id: string;
  domain: string;
  enabled: boolean;
  events: number;
  fingerprint_probes: number;
  canvas_events: number;
  webgl_events: number;
  navigator_events: number;
  screen_events: number;
  timezone_events: number;
  media_devices_events: number;
  audio_events: number;
  signals_masked: number;
  risk_before: number;
  risk_after: number;
  consistency_score: number;
  last_activity?: string | null;
}

export interface Policy {
  id: string;
  user_id?: string | null;
  name: string;
  enabled: boolean;
  masking_strength: 'LOW' | 'BALANCED' | 'AGGRESSIVE' | 'STEALTH';
  protected_signals: string[];
  strategy: 'STATIC' | 'DISTRIBUTION_SAMPLED' | 'AI_GENERATED';
  session_persistence: boolean;
  rules_json: {
    mask_canvas?: boolean;
    mask_webgl?: boolean;
    mask_navigator?: boolean;
    mask_screen?: boolean;
    mask_timezone?: boolean;
    mask_audio?: boolean;
    noise_level?: number;
    [key: string]: any;
  };
  created_at: string;
  updated_at: string;
}

export interface ExtensionConfigResponse {
  sync_interval: number;
  global_enabled: boolean;
  sites: Array<{
    domain: string;
    enabled: boolean;
    policy: Record<string, any>;
  }>;
}

export interface HealthResponse {
  status: string;
  database: string;
  redis: string;
  timestamp: string;
}

export interface AuditLogItem {
  id: string;
  user_id?: string | null;
  action: string;
  resource_type: string;
  resource_id?: string | null;
  details?: Record<string, any> | null;
  ip_address?: string | null;
  timestamp: string;
}

export interface TelemetryEventResponse {
  id: string;
  domain: string;
  event_type: string;
  signal_type?: string | null;
  action?: string | null;
  risk_score: number;
  risk_before?: number | null;
  risk_after?: number | null;
  consistency_score: number;
  source: string;
  timestamp: string;
}

// ==========================================
// AXIOS CLIENT INSTANCE
// ==========================================

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor: Inject Bearer token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('maskit_auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Friendly error message handling
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const err = error as AxiosError<{ detail?: string | Array<{ msg: string }> }>;
    if (err.response?.data?.detail) {
      if (typeof err.response.data.detail === 'string') {
        return err.response.data.detail;
      }
      if (Array.isArray(err.response.data.detail)) {
        return err.response.data.detail.map(d => d.msg).join(', ');
      }
    }
    if (err.response?.status === 401) {
      return 'Session expired or authentication failed. Please log in.';
    }
    if (err.response?.status === 403) {
      return 'Access forbidden for this operation.';
    }
    if (err.response?.status === 404) {
      return 'The requested resource was not found.';
    }
    if (err.response?.status === 429) {
      return 'Too many requests. Please wait a moment before trying again.';
    }
    if (err.response?.status === 500) {
      return 'Backend service encountered an error. Please verify backend logs.';
    }
    if (err.code === 'ERR_NETWORK') {
      return 'Cannot reach the MaskIt backend. Ensure the server is running on ' + API_BASE_URL;
    }
  }
  return error instanceof Error ? error.message : 'An unexpected error occurred.';
}

// ==========================================
// TYPED API FUNCTIONS
// ==========================================

export const api = {
  // --- Auth ---
  register: async (email: string, password: string): Promise<User> => {
    const { data } = await apiClient.post<User>('/auth/register', { email, password });
    return data;
  },

  login: async (email: string, password: string): Promise<TokenResponse> => {
    const { data } = await apiClient.post<TokenResponse>('/auth/login', { email, password });
    return data;
  },

  getMe: async (): Promise<User> => {
    const { data } = await apiClient.get<User>('/auth/me');
    return data;
  },

  // --- Session ---
  startSession: async (clientType: string = 'DASHBOARD'): Promise<SessionResponse> => {
    const { data } = await apiClient.post<SessionResponse>('/session/start', {
      client_type: clientType,
      user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : 'MaskIt Frontend',
    });
    return data;
  },

  endSession: async (sessionToken: string): Promise<SessionResponse> => {
    const { data } = await apiClient.post<SessionResponse>('/session/end', { session_token: sessionToken });
    return data;
  },

  // --- Fingerprint Analysis ---
  analyzeFingerprint: async (payload: FingerprintAnalyzeRequest): Promise<FingerprintAnalyzeResponse> => {
    const { data } = await apiClient.post<FingerprintAnalyzeResponse>('/fingerprint/analyze', payload);
    return data;
  },

  // --- Dashboard & Analytics ---
  getDashboard: async (): Promise<DashboardOverviewResponse> => {
    const { data } = await apiClient.get<DashboardOverviewResponse>('/dashboard/overview');
    return data;
  },

  getTimeline: async (hours: number = 24): Promise<TimelinePoint[]> => {
    const { data } = await apiClient.get<TimelinePoint[]>('/dashboard/timeline', { params: { hours } });
    return data;
  },

  getSignals: async (): Promise<SignalStat[]> => {
    const { data } = await apiClient.get<SignalStat[]>('/dashboard/signals');
    return data;
  },

  getRisk: async (): Promise<RiskDistribution> => {
    const { data } = await apiClient.get<RiskDistribution>('/dashboard/risk');
    return data;
  },

  // --- Protect My Data ---
  getProtectedSites: async (): Promise<ProtectedSite[]> => {
    const { data } = await apiClient.get<ProtectedSite[]>('/protection/sites');
    return data;
  },

  protectSite: async (domain: string, policyId?: string): Promise<ProtectedSite> => {
    const { data } = await apiClient.post<ProtectedSite>('/protection/sites', {
      domain,
      policy_id: policyId || null,
    });
    return data;
  },

  updateProtectedSite: async (siteId: string, payload: { enabled?: boolean; policy_id?: string }): Promise<ProtectedSite> => {
    const { data } = await apiClient.put<ProtectedSite>(`/protection/sites/${siteId}`, payload);
    return data;
  },

  deleteProtectedSite: async (siteId: string): Promise<void> => {
    await apiClient.delete(`/protection/sites/${siteId}`);
  },

  getProtectionSummary: async (): Promise<ProtectionSummary> => {
    const { data } = await apiClient.get<ProtectionSummary>('/protection/summary');
    return data;
  },

  getSiteAnalytics: async (siteId: string): Promise<SiteAnalytics> => {
    const { data } = await apiClient.get<SiteAnalytics>(`/protection/sites/${siteId}/analytics`);
    return data;
  },

  // --- Policies ---
  getPolicies: async (): Promise<Policy[]> => {
    const { data } = await apiClient.get<Policy[]>('/policies');
    return data;
  },

  createPolicy: async (payload: Partial<Policy>): Promise<Policy> => {
    const { data } = await apiClient.post<Policy>('/policies', payload);
    return data;
  },

  updatePolicy: async (policyId: string, payload: Partial<Policy>): Promise<Policy> => {
    const { data } = await apiClient.put<Policy>(`/policies/${policyId}`, payload);
    return data;
  },

  // --- Extension ---
  getExtensionConfig: async (): Promise<ExtensionConfigResponse> => {
    const { data } = await apiClient.get<ExtensionConfigResponse>('/extension/config');
    return data;
  },

  // --- Health ---
  getHealth: async (): Promise<HealthResponse> => {
    const healthUrl = `${BACKEND_ROOT_URL}/health`;
    const { data } = await axios.get<HealthResponse>(healthUrl, { timeout: 4000 });
    return data;
  },

  // --- Audit & Events ---
  getAuditLogs: async (limit: number = 50): Promise<AuditLogItem[]> => {
    const { data } = await apiClient.get<AuditLogItem[]>('/audit', { params: { limit } });
    return data;
  },

  getEvents: async (limit: number = 50): Promise<TelemetryEventResponse[]> => {
    const { data } = await apiClient.get<TelemetryEventResponse[]>('/events', { params: { limit } });
    return data;
  },
};
