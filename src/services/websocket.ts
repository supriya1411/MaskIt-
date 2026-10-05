import { WS_BASE_URL } from './api';

export interface LiveDashboardEvent {
  event: string;
  domain?: string;
  signal?: string;
  action?: string;
  risk_before?: number;
  risk_after?: number;
  consistency?: number;
  timestamp?: string;
  [key: string]: any;
}

type EventListener = (event: LiveDashboardEvent) => void;
type StatusListener = (status: 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED') => void;

class DashboardWebSocketService {
  private ws: WebSocket | null = null;
  private listeners: Set<EventListener> = new Set();
  private statusListeners: Set<StatusListener> = new Set();
  private reconnectTimeout: any = null;
  private pingInterval: any = null;
  private shouldReconnect: boolean = true;
  private status: 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED' = 'DISCONNECTED';

  public connect() {
    this.shouldReconnect = true;
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.setStatus('CONNECTING');

    try {
      this.ws = new WebSocket(WS_BASE_URL);

      this.ws.onopen = () => {
        this.setStatus('CONNECTED');
        this.startPing();
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyListeners(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      this.ws.onerror = () => {
        // Will trigger onclose and attempt reconnect
      };

      this.ws.onclose = () => {
        this.setStatus('DISCONNECTED');
        this.stopPing();
        if (this.shouldReconnect) {
          this.scheduleReconnect();
        }
      };
    } catch (err) {
      this.setStatus('DISCONNECTED');
      if (this.shouldReconnect) {
        this.scheduleReconnect();
      }
    }
  }

  public disconnect() {
    this.shouldReconnect = false;
    this.stopPing();
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.setStatus('DISCONNECTED');
  }

  public addEventListener(listener: EventListener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  public addStatusListener(listener: StatusListener) {
    this.statusListeners.add(listener);
    listener(this.status);
    return () => this.statusListeners.delete(listener);
  }

  public getStatus() {
    return this.status;
  }

  private setStatus(newStatus: 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED') {
    this.status = newStatus;
    this.statusListeners.forEach((fn) => fn(newStatus));
  }

  private notifyListeners(data: LiveDashboardEvent) {
    this.listeners.forEach((fn) => fn(data));
  }

  private startPing() {
    this.stopPing();
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        try {
          this.ws.send(JSON.stringify({ action: 'PING' }));
        } catch (e) {}
      }
    }, 25000);
  }

  private stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
    this.reconnectTimeout = setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect();
      }
    }, 4000);
  }
}

export const dashboardWs = new DashboardWebSocketService();
