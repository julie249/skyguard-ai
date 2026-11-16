import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Station } from '../api/types';

// Fix Leaflet marker icon asset paths
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface StationMapProps {
  stations: Station[];
  selectedStationId?: string;
  onSelectStation: (stationId: string) => void;
}

export const StationMap: React.FC<StationMapProps> = ({
  stations,
  selectedStationId: _selectedStationId,
  onSelectStation,
}) => {
  const centerLat = stations.length > 0 ? stations[0].lat : 28.6139;
  const centerLon = stations.length > 0 ? stations[0].lon : 77.209;

  return (
    <div style={{ height: '380px', width: '100%', borderRadius: '8px', overflow: 'hidden' }}>
      <MapContainer
        center={[centerLat, centerLon]}
        zoom={10}
        scrollWheelZoom={false}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {stations.map((st) => (
          <Marker
            key={st.stationId}
            position={[st.lat, st.lon]}
            eventHandlers={{
              click: () => onSelectStation(st.stationId),
            }}
          >
            <Popup>
              <div style={{ color: '#0f172a' }}>
                <h4 style={{ margin: '0 0 4px 0' }}>{st.name} ({st.stationId})</h4>
                <p style={{ margin: 0, fontSize: '12px' }}>
                  Region: {st.region} <br />
                  Elevation: {st.elevation}m <br />
                  Status: <strong>{st.healthStatus.toUpperCase()}</strong>
                </p>
                <button
                  onClick={() => onSelectStation(st.stationId)}
                  style={{
                    marginTop: '8px',
                    padding: '4px 8px',
                    background: '#0284c7',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  View Telemetry
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};
