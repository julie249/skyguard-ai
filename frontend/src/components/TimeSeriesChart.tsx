import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Reading } from '../api/types';

interface TimeSeriesChartProps {
  readings: Reading[];
  stationName: string;
}

export const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({ readings, stationName }) => {
  const chartData = readings.map((r) => ({
    time: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    temperature: r.temperatureC,
    pressure: r.pressureHpa,
    humidity: r.humidityPct,
  }));

  return (
    <div style={{ background: '#1e293b', padding: '16px', borderRadius: '8px', border: '1px solid #334155' }}>
      <h3 style={{ margin: '0 0 12px 0', color: '#38bdf8', fontSize: '16px' }}>
        Live Sensor Telemetry: {stationName}
      </h3>
      <div style={{ height: '300px', width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" stroke="#94a3b8" />
            <YAxis yAxisId="left" stroke="#f87171" label={{ value: '°C / %', angle: -90, position: 'insideLeft', fill: '#f87171' }} />
            <YAxis yAxisId="right" orientation="right" domain={[960, 1040]} stroke="#38bdf8" label={{ value: 'hPa', angle: 90, position: 'insideRight', fill: '#38bdf8' }} />
            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="temperature" name="Temp (°C)" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} />
            <Line yAxisId="left" type="monotone" dataKey="humidity" name="Humidity (%)" stroke="#3b82f6" strokeWidth={2} />
            <Line yAxisId="right" type="monotone" dataKey="pressure" name="Pressure (hPa)" stroke="#06b6d4" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
