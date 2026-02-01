import { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
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
const DEFAULT_ZOOM = 12;

interface PainPoint {
  id: string;
  lat: number;
  lng: number;
  type: 'no_water' | 'leak' | 'contamination' | 'low_pressure';
  description: string;
  createdAt: Date;
}

const painPointConfig = {
  no_water: { color: '#ef4444', icon: '🚱', label: 'Sin agua' },
  leak: { color: '#f97316', icon: '💧', label: 'Fuga' },
  contamination: { color: '#eab308', icon: '⚠️', label: 'Agua contaminada' },
  low_pressure: { color: '#3b82f6', icon: '📉', label: 'Baja presión' },
};

interface PainPointMapProps {
  painPoints: PainPoint[];
  onMapClick: (lat: number, lng: number, event?: { clientX: number; clientY: number }, map?: L.Map) => void;
  pendingLocation?: { lat: number; lng: number } | null;
  className?: string;
}

// Component to handle map clicks
function MapClickHandler({ onMapClick }: { onMapClick: (lat: number, lng: number, event?: { clientX: number; clientY: number }, map?: L.Map) => void }) {
  const map = useMap();
  useMapEvents({
    click: (e) => {
      onMapClick(e.latlng.lat, e.latlng.lng, {
        clientX: e.originalEvent.clientX,
        clientY: e.originalEvent.clientY,
      }, map);
    },
  });
  return null;
}

// Component to handle map view updates
function MapController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();

  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);

  return null;
}

export function PainPointMap({
  painPoints,
  onMapClick,
  pendingLocation,
  className,
}: PainPointMapProps) {
  // Create custom icon for pending location
  const pendingIcon = L.divIcon({
    html: '<div style="background: #1e96fc; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4); animation: pulse 1.5s infinite;"></div>',
    className: 'custom-pending-icon',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });

  return (
    <div className={cn("absolute inset-0", className)}>
      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.2); opacity: 0.8; }
        }
        .leaflet-container {
          background: #e5e7eb;
          cursor: crosshair !important;
        }
      `}</style>

      <MapContainer
        center={CDMX_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        <MapController center={CDMX_CENTER} zoom={DEFAULT_ZOOM} />
        <MapClickHandler onMapClick={onMapClick} />

        {/* OpenStreetMap tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Pain Points */}
        {painPoints.map((point) => {
          const config = painPointConfig[point.type];
          return (
            <CircleMarker
              key={point.id}
              center={[point.lat, point.lng]}
              radius={12}
              pathOptions={{
                color: config.color,
                fillColor: config.color,
                fillOpacity: 0.7,
                weight: 3,
              }}
            >
              <Popup>
                <div className="text-sm min-w-[150px]">
                  <div className="flex items-center gap-2 font-semibold mb-1">
                    <span>{config.icon}</span>
                    <span>{config.label}</span>
                  </div>
                  {point.description && (
                    <p className="text-muted-foreground mb-2">{point.description}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {point.createdAt.toLocaleString('es-MX', {
                      day: 'numeric',
                      month: 'short',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}

        {/* Pending Location Marker */}
        {pendingLocation && (
          <Marker position={[pendingLocation.lat, pendingLocation.lng]} icon={pendingIcon}>
            <Popup>
              <div className="text-sm font-medium">Nueva ubicación seleccionada</div>
            </Popup>
          </Marker>
        )}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-card/95 border border-border rounded-lg p-3 text-xs z-[1000]">
        <div className="font-medium mb-2">Tipos de Problema</div>
        <div className="space-y-1.5">
          {Object.entries(painPointConfig).map(([key, config]) => (
            <div key={key} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: config.color }}
              />
              <span>{config.icon}</span>
              <span>{config.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Crosshair hint */}
      <div className="absolute top-4 right-4 bg-card/95 border border-border rounded-lg px-3 py-2 text-xs z-[1000] flex items-center gap-2">
        <div className="w-4 h-4 border-2 border-accent rounded-full flex items-center justify-center">
          <div className="w-1 h-1 bg-accent rounded-full" />
        </div>
        <span>Clic para reportar</span>
      </div>
    </div>
  );
}
