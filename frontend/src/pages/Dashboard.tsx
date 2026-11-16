import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchStations, fetchAlerts, fetchStationReadings, injectSimulatedAnomaly } from '../api/client';
import { useLiveStream } from '../hooks/useLiveStream';
import { StationMap } from '../components/StationMap';
import { TimeSeriesChart } from '../components/TimeSeriesChart';
import { AlertFeed } from '../components/AlertFeed';

export const Dashboard: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedStationId, setSelectedStationId] = useState<string>('AWS001');
  const [injecting, setInjecting] = useState(false);

  // Queries
  const { data: stations = [] } = useQuery({ queryKey: ['stations'], queryFn: fetchStations });
  const { data: alerts = [] } = useQuery({ queryKey: ['alerts'], queryFn: () => fetchAlerts() });
  const { data: readings = [] } = useQuery({
    queryKey: ['readings', selectedStationId],
    queryFn: () => fetchStationReadings(selectedStationId),
    refetchInterval: 5000,
  });

  // WebSocket live updates
  const { latestMessage, isConnected } = useLiveStream(selectedStationId);

  // React to incoming live WebSocket events
  React.useEffect(() => {
    if (latestMessage) {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['readings', selectedStationId] });
      queryClient.invalidateQueries({ queryKey: ['stations'] });
    }
  }, [latestMessage, queryClient, selectedStationId]);

  const handleInject = async (type: string) => {
    setInjecting(true);
    try {
      await injectSimulatedAnomaly({
        stationId: selectedStationId,
        temperatureC: type === 'spike' ? 55.4 : 26.0,
        pressureHpa: type === 'dropout' ? 0.0 : 1011.0,
        humidityPct: 20.0,
        anomalyType: type,
      });
      // Refresh
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['alerts'] });
        queryClient.invalidateQueries({ queryKey: ['readings', selectedStationId] });
      }, 800);
    } catch (e) {
      console.error(e);
    } finally {
      setInjecting(false);
    }
  };

  const activeStation = stations.find((s) => s.stationId === selectedStationId) || stations[0];

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px', fontFamily: 'sans-serif' }}>
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ margin: 0, color: '#38bdf8', fontSize: '26px' }}>SkyGuard AI</h1>
          <p style={{ margin: '4px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
            SIH26073 Intelligent Anomaly Detection & Self-Healing for Automatic Weather Stations
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span
            style={{
              padding: '6px 12px',
              borderRadius: '9999px',
              background: isConnected ? '#064e3b' : '#7f1d1d',
              color: isConnected ? '#6ee7b7' : '#fca5a5',
              fontSize: '13px',
              fontWeight: 'bold',
            }}
          >
            ● {isConnected ? 'WebSocket Stream Connected' : 'Stream Disconnected'}
          </span>
          <button
            disabled={injecting}
            onClick={() => handleInject('spike')}
            style={{
              background: '#e11d48',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              cursor: injecting ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
            }}
          >
            {injecting ? 'Injecting...' : '⚡ Demo Inject Spike (55°C)'}
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '7fr 5fr', gap: '24px' }}>
        {/* Left Column: Map & Time Series */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ background: '#1e293b', padding: '16px', borderRadius: '8px', border: '1px solid #334155' }}>
            <h3 style={{ margin: '0 0 12px 0', color: '#38bdf8', fontSize: '16px' }}>
              Automatic Weather Station Geospatial Network
            </h3>
            <StationMap
              stations={stations}
              selectedStationId={selectedStationId}
              onSelectStation={(id) => setSelectedStationId(id)}
            />
          </div>

          <TimeSeriesChart
            readings={readings}
            stationName={activeStation ? `${activeStation.name} (${activeStation.stationId})` : selectedStationId}
          />
        </div>

        {/* Right Column: Alert Feed & Explainability */}
        <div>
          <AlertFeed alerts={alerts} />
        </div>
      </div>
    </div>
  );
};
