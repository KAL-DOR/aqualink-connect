import { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Marker, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { DemandPoint, IncidentReport } from '@/types';
import { cn } from '@/lib/utils';

// Fix for default marker icons in Leaflet with bundlers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Mexico City center coordinates
const CDMX_CENTER: [number, number] = [19.4326, -99.1332];
const DEFAULT_ZOOM = 11;

// Intensity colors matching our design system
const intensityColors = {
  low: '#22c55e',      // success green
  medium: '#eab308',   // warning yellow
  high: '#f97316',     // orange
  critical: '#ef4444', // destructive red
};

const intensityLabels = {
  low: 'Baja',
  medium: 'Media',
  high: 'Alta',
  critical: 'Crítica',
};

interface DemandMapProps {
  demandPoints: DemandPoint[];
  incidents?: IncidentReport[];
  showIncidents?: boolean;
  showUserLocation?: boolean;
  userLocation?: [number, number];
  className?: string;
  height?: string;
}

// Component to handle map view updates
function MapController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();

  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);

  return null;
}

export function DemandMap({
  demandPoints,
  incidents = [],
  showIncidents = false,
  showUserLocation = false,
  userLocation = CDMX_CENTER,
  className,
  height = '100%',
}: DemandMapProps) {
  // Create custom icon for incidents
  const incidentIcon = L.divIcon({
    html: '<div style="background: #1f271b; color: white; width: 24px; height: 24px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">⚠️</div>',
    className: 'custom-incident-icon',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });

  // Create custom icon for user location
  const userIcon = L.divIcon({
    html: '<div style="background: #23022e; width: 16px; height: 16px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.4);"></div>',
    className: 'custom-user-icon',
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });

  return (
    <div className={cn("relative rounded-lg overflow-hidden", className)} style={{ height }}>
      <MapContainer
        center={CDMX_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        <MapController center={CDMX_CENTER} zoom={DEFAULT_ZOOM} />

        {/* OpenStreetMap tiles with Spanish labels */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Demand Points */}
        {demandPoints.map((point) => (
          <CircleMarker
            key={point.id}
            center={[Number(point.location.lat), Number(point.location.lng)]}
            radius={Math.max(12, point.requestCount / 5)}
            pathOptions={{
              color: intensityColors[point.intensity],
              fillColor: intensityColors[point.intensity],
              fillOpacity: 0.7,
              weight: 2,
            }}
          >
            <Popup>
              <div className="text-sm">
                <div className="font-semibold">{point.location.colonia}</div>
                <div className="text-muted-foreground">{point.location.municipality}</div>
                <div className="mt-2 space-y-1">
                  <div><strong>{point.requestCount}</strong> solicitudes</div>
                  <div>Demanda: <span style={{ color: intensityColors[point.intensity] }}>{intensityLabels[point.intensity]}</span></div>
                  <div>~{(point.requestCount * 10).toLocaleString()} litros estimados</div>
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {/* Incident Markers */}
        {showIncidents && incidents.map((incident) => (
          <Marker
            key={incident.id}
            position={[Number(incident.location.lat), Number(incident.location.lng)]}
            icon={incidentIcon}
          >
            <Popup>
              <div className="text-sm">
                <div className="font-semibold">Incidente #{incident.id}</div>
                <div className="text-muted-foreground">{incident.location.colonia}</div>
                <div className="mt-2 space-y-1">
                  <div>Tipo: {incident.type}</div>
                  <div>Estado: {incident.status}</div>
                  <div>Afectados: ~{incident.affectedHouseholds} viviendas</div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* User Location Marker */}
        {showUserLocation && (
          <Marker position={userLocation} icon={userIcon}>
            <Popup>
              <div className="text-sm font-medium">Tu ubicación</div>
            </Popup>
          </Marker>
        )}
      </MapContainer>

      {/* Legend Overlay */}
      <div className="absolute bottom-4 left-4 bg-card/95 border border-border rounded-lg p-3 text-xs z-[1000]">
        <div className="font-medium mb-2">Nivel de Demanda</div>
        <div className="space-y-1.5">
          {(['critical', 'high', 'medium', 'low'] as const).map((level) => (
            <div key={level} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: intensityColors[level] }}
              />
              <span>{intensityLabels[level]}</span>
            </div>
          ))}
          {showIncidents && (
            <div className="flex items-center gap-2 pt-1 border-t border-border mt-2">
              <div className="w-3 h-3 bg-foreground rounded flex items-center justify-center text-[8px]">⚠</div>
              <span>Incidente</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
