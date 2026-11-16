import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Alert } from '../api/types';

interface ExplainabilityPanelProps {
  alert: Alert;
}

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({ alert }) => {
  const contributions = alert.explanation?.feature_contributions || {};
  const data = Object.entries(contributions).map(([feature, score]) => ({
    feature: feature.replace('_', ' ').toUpperCase(),
    score: Math.round(Number(score) * 100),
  }));

  const colors = ['#f43f5e', '#38bdf8', '#fbbf24', '#a855f7'];

  return (
    <div style={{ background: '#0f172a', padding: '16px', borderRadius: '6px', border: '1px solid #1e293b', marginTop: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h4 style={{ margin: 0, color: '#f43f5e', fontSize: '14px' }}>
          Root Cause: {alert.rootCause.replace('_', ' ').toUpperCase()} ({(alert.confidence * 100).toFixed(0)}% Confidence)
        </h4>
        {alert.suggestedCorrection && (
          <span style={{ background: '#065f46', color: '#6ee7b7', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>
            Self-Healing Est: {alert.suggestedCorrection.toFixed(1)}°C
          </span>
        )}
      </div>

      <p style={{ margin: '8px 0', fontSize: '13px', color: '#cbd5e1' }}>
        {alert.explanation?.summary}
      </p>

      {alert.spatialSupport && (
        <div style={{ background: '#1e293b', padding: '8px', borderRadius: '4px', fontSize: '12px', color: '#94a3b8', marginBottom: '10px' }}>
          <strong>Spatial Validation:</strong> {alert.spatialSupport.summary}
        </div>
      )}

      <div style={{ height: '140px', width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
            <XAxis type="number" domain={[0, 100]} unit="%" stroke="#64748b" />
            <YAxis type="category" dataKey="feature" stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569' }} />
            <Bar dataKey="score" radius={[0, 4, 4, 0]}>
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
