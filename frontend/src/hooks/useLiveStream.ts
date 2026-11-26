import { useEffect, useState } from 'react';
import { Reading, Alert } from '../api/types';

interface LiveMessage {
  reading: Reading;
  alert: Alert | null;
  mlScored: boolean;
}

/** Auto-detect ws:// vs wss:// based on page protocol if no env var is set. */
function getDefaultWsUrl(): string {
  if (typeof window !== 'undefined') {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//localhost:3000/ws/stream`;
  }
  return 'ws://localhost:3000/ws/stream';
}

export function useLiveStream(stationId?: string) {
  const [latestMessage, setLatestMessage] = useState<LiveMessage | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [mlOffline, setMlOffline] = useState(false);

  useEffect(() => {
    const WS_BASE = import.meta.env.VITE_WS_URL || getDefaultWsUrl();
    const wsUrl = stationId
      ? `${WS_BASE}?stationId=${stationId}`
      : WS_BASE;

    let ws: WebSocket | null = null;
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

    function connect() {
      try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => setIsConnected(true);
        ws.onclose = () => {
          setIsConnected(false);
          reconnectTimeout = setTimeout(connect, 3000);
        };
        ws.onerror = () => setIsConnected(false);

        ws.onmessage = (event) => {
          try {
            const data: LiveMessage = JSON.parse(event.data);
            setLatestMessage(data);
            // Track whether ML service is scoring readings
            setMlOffline(!data.mlScored);
          } catch (e) {
            console.error('Failed to parse WebSocket message:', e);
          }
        };
      } catch (err) {
        setIsConnected(false);
        reconnectTimeout = setTimeout(connect, 3000);
      }
    }

    connect();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [stationId]);

  return { latestMessage, isConnected, mlOffline };
}
