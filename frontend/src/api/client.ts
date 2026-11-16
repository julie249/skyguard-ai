import { Station, Alert, Reading } from './types';

const API_BASE = 'http://localhost:3000';

export async function fetchStations(): Promise<Station[]> {
  const res = await fetch(`${API_BASE}/stations`);
  if (!res.ok) throw new Error('Failed to fetch stations');
  return res.json();
}

export async function fetchAlerts(stationId?: string): Promise<Alert[]> {
  const url = stationId ? `${API_BASE}/alerts?stationId=${stationId}` : `${API_BASE}/alerts`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch alerts');
  return res.json();
}

export async function fetchStationReadings(stationId: string): Promise<Reading[]> {
  const res = await fetch(`${API_BASE}/stations/${stationId}/readings?limit=40`);
  if (!res.ok) throw new Error('Failed to fetch readings');
  return res.json();
}

export async function injectSimulatedAnomaly(payload: {
  stationId: string;
  temperatureC?: number;
  pressureHpa?: number;
  humidityPct?: number;
  anomalyType?: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/simulate/inject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to inject anomaly');
  return res.json();
}
