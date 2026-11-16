import React, { useState } from 'react';
import { Alert } from '../api/types';
import { ExplainabilityPanel } from './ExplainabilityPanel';

interface AlertFeedProps {
  alerts: Alert[];
}

export const AlertFeed: React.FC<AlertFeedProps> = ({ alerts }) => {
  const [expandedAlertId, setExpandedAlertId] = useState<string | null>(
    alerts.length > 0 ? alerts[0].alertId : null
  );

  return (
    <div style={{ background: '#1e293b', padding: '16px', borderRadius: '8px', border: '1px solid #334155' }}>
      <h3 style={{ margin: '0 0 12px 0', color: '#f87171', fontSize: '16px' }}>
        Live Meteorological Alert Feed ({alerts.length})
      </h3>

      {alerts.length === 0 ? (
        <div style={{ color: '#94a3b8', padding: '24px', textAlign: 'center' }}>
          No open alerts detected. AWS network operational.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '520px', overflowY: 'auto' }}>
          {alerts.map((alert) => {
            const isExpanded = expandedAlertId === alert.alertId;
            return (
              <div
                key={alert.alertId}
                style={{
                  background: '#0f172a',
                  border: isExpanded ? '1px solid #f43f5e' : '1px solid #334155',
                  borderRadius: '6px',
                  padding: '12px',
                }}
              >
                <div
                  onClick={() => setExpandedAlertId(isExpanded ? null : alert.alertId)}
                  style={{ display: 'flex', justifyContent: 'space-between', cursor: 'pointer' }}
                >
                  <div>
                    <span style={{ fontWeight: 'bold', color: '#f8fafc' }}>{alert.stationId}</span>
                    <span style={{ marginLeft: '8px', color: '#94a3b8', fontSize: '12px' }}>
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div>
                    <span
                      style={{
                        background: alert.rootCause === 'genuine_extreme' ? '#7c2d12' : '#881337',
                        color: alert.rootCause === 'genuine_extreme' ? '#fdba74' : '#fda4af',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: 'bold',
                      }}
                    >
                      {alert.rootCause.toUpperCase()}
                    </span>
                  </div>
                </div>

                {isExpanded && <ExplainabilityPanel alert={alert} />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
