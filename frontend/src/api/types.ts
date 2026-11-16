export interface Station {
  stationId: string;
  name: string;
  lat: number;
  lon: number;
  elevation: number;
  region: string;
  healthStatus: 'healthy' | 'warning' | 'critical';
}

export interface Reading {
  id: string;
  stationId: string;
  timestamp: string;
  temperatureC: number;
  pressureHpa: number;
  humidityPct: number;
}

export interface Alert {
  alertId: string;
  stationId: string;
  timestamp: string;
  detectedAt: string;
  confidence: number;
  rootCause: 'sensor_fault' | 'comms_error' | 'genuine_extreme' | 'unknown';
  triggeringFeatures: string[];
  explanation: {
    feature_contributions: Record<string, number>;
    summary: string;
  };
  spatialSupport?: {
    agreement_score: number;
    agreeing_neighbors_count: number;
    total_neighbors_evaluated: number;
    is_corroborated: boolean;
    suggested_correction?: number | null;
    summary?: string;
  } | null;
  suggestedCorrection?: number | null;
  status: 'open' | 'acknowledged' | 'resolved';
}
