import React from 'react';

interface SensorHealthCardProps {
  stationId: string;
  uptimePct: number;
  lastSeen: string;
  anomalies24h: number;
  driftForecastScore: number; // 0.0 - 1.0 (degradation probability)
}

export const SensorHealthCard: React.FC<SensorHealthCardProps> = ({
  stationId,
  uptimePct,
  lastSeen,
  anomalies24h,
  driftForecastScore,
}) => {
  const isHealthy = driftForecastScore < 0.4 && anomalies24h < 3;
  const isWarning = driftForecastScore >= 0.4 && driftForecastScore < 0.7;

  return (
    <div
      style={{
        background: '#1e293b',
        border: '1px solid #334155',
        borderRadius: '8px',
        padding: '16px',
        marginTop: '16px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h4 style={{ margin: 0, color: '#38bdf8', fontSize: '15px' }}>
          Predictive Sensor Health: {stationId}
        </h4>
        <span
          style={{
            background: isHealthy ? '#064e3b' : isWarning ? '#78350f' : '#7f1d1d',
            color: isHealthy ? '#6ee7b7' : isWarning ? '#fde047' : '#fca5a5',
            padding: '2px 8px',
            borderRadius: '4px',
            fontSize: '11px',
            fontWeight: 'bold',
          }}
        >
          {isHealthy ? 'OPTIMAL' : isWarning ? 'DEGRADATION RISK' : 'CRITICAL'}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginTop: '12px' }}>
        <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px' }}>
          <div style={{ color: '#94a3b8', fontSize: '11px' }}>Network Uptime</div>
          <div style={{ color: '#f8fafc', fontSize: '16px', fontWeight: 'bold' }}>{uptimePct}%</div>
        </div>
        <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px' }}>
          <div style={{ color: '#94a3b8', fontSize: '11px' }}>24h Anomalies</div>
          <div style={{ color: anomalies24h > 0 ? '#f87171' : '#f8fafc', fontSize: '16px', fontWeight: 'bold' }}>
            {anomalies24h}
          </div>
        </div>
        <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px' }}>
          <div style={{ color: '#94a3b8', fontSize: '11px' }}>Degradation Risk</div>
          <div style={{ color: driftForecastScore > 0.5 ? '#fbbf24' : '#4ade80', fontSize: '16px', fontWeight: 'bold' }}>
            {(driftForecastScore * 100).toFixed(0)}%
          </div>
        </div>
        <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px' }}>
          <div style={{ color: '#94a3b8', fontSize: '11px' }}>Last Telemetry</div>
          <div style={{ color: '#f8fafc', fontSize: '12px', marginTop: '4px' }}>{lastSeen}</div>
        </div>
      </div>
    </div>
  );
};
