import { useEffect, useState } from 'react';
import { Reading, Alert } from '../api/types';

interface LiveMessage {
  reading: Reading;
  alert: Alert | null;
  mlScored: boolean;
}

export function useLiveStream(stationId?: string) {
  const [latestMessage, setLatestMessage] = useState<LiveMessage | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:3000/ws/stream';
    const wsUrl = stationId
      ? `${WS_BASE}?stationId=${stationId}`
      : WS_BASE;

    let ws: WebSocket | null = null;
    let reconnectTimeout: any = null;

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
            const data = JSON.parse(event.data);
            setLatestMessage(data);
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

  return { latestMessage, isConnected };
}
