import { useEffect, useRef, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.markercluster';
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

interface PainPoint {
  id: number;
  lat: number;
  lng: number;
  tipo: string;
  texto: string;
  username: string;
  alcaldia: string | null;
  created_at: string;
  isUserAdded?: boolean;
}

const painPointConfig: Record<string, { color: string; icon: string; label: string }> = {
  sin_agua: { color: '#ef4444', icon: '🚱', label: 'Sin agua' },
  fuga: { color: '#f97316', icon: '💧', label: 'Fuga' },
  agua_contaminada: { color: '#eab308', icon: '⚠️', label: 'Agua contaminada' },
  baja_presion: { color: '#3b82f6', icon: '📉', label: 'Baja presión' },
  otro: { color: '#6b7280', icon: '❓', label: 'Otro' },
};

interface PainPointMapProps {
  painPoints: PainPoint[];
  onMapClick: (lat: number, lng: number, event?: { clientX: number; clientY: number }, map?: L.Map) => void;
  onPointClick?: (point: PainPoint, event?: { clientX: number; clientY: number }) => void;
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

// Custom cluster icon creator
function createClusterIcon(cluster: L.MarkerCluster) {
  const count = cluster.getChildCount();
  const markers = cluster.getAllChildMarkers();

  // Count by type
  const typeCounts: Record<string, number> = {};
  markers.forEach((marker: any) => {
    const tipo = marker.options.painPoint?.tipo || 'otro';
    typeCounts[tipo] = (typeCounts[tipo] || 0) + 1;
  });

  // Find dominant type
  const dominantType = Object.entries(typeCounts).reduce((a, b) =>
    a[1] > b[1] ? a : b
  )[0];

  const config = painPointConfig[dominantType] || painPointConfig.otro;

  // Size based on count
  let size = 40;
  let fontSize = 12;
  if (count >= 100) {
    size = 60;
    fontSize = 14;
  } else if (count >= 50) {
    size = 50;
    fontSize = 13;
  }

  return L.divIcon({
    html: `
      <div style="
        background: ${config.color};
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: ${fontSize}px;
        border: 3px solid white;
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
        opacity: 0.9;
      ">
        ${count}
      </div>
    `,
    className: 'custom-cluster-icon',
    iconSize: L.point(size, size),
    iconAnchor: L.point(size / 2, size / 2),
  });
}

// Create individual marker icon
function createMarkerIcon(tipo: string, isHighlighted = false) {
  const config = painPointConfig[tipo] || painPointConfig.otro;
  const size = isHighlighted ? 16 : 12;

  return L.divIcon({
    html: `
      <div style="
        background: ${config.color};
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        cursor: pointer;
      "></div>
    `,
    className: 'custom-marker-icon',
    iconSize: L.point(size, size),
    iconAnchor: L.point(size / 2, size / 2),
  });
}

// Cluster layer component
function ClusterLayer({
  painPoints,
  onPointClick
}: {
  painPoints: PainPoint[];
  onPointClick?: (point: PainPoint, event?: { clientX: number; clientY: number }) => void;
}) {
  const map = useMap();
  const clusterGroupRef = useRef<L.MarkerClusterGroup | null>(null);

  useEffect(() => {
    // Create cluster group
    const clusterGroup = L.markerClusterGroup({
      chunkedLoading: true,
      maxClusterRadius: 60,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      disableClusteringAtZoom: 16,
      iconCreateFunction: createClusterIcon,
      spiderLegPolylineOptions: {
        weight: 2,
        color: '#666',
        opacity: 0.5,
      },
    });

    // Add markers to cluster
    painPoints.forEach((point) => {
      const marker = L.marker([point.lat, point.lng], {
        icon: createMarkerIcon(point.tipo),
        painPoint: point,
      } as any);

      marker.on('click', (e: L.LeafletMouseEvent) => {
        e.originalEvent.stopPropagation();
        if (onPointClick) {
          onPointClick(point, {
            clientX: e.originalEvent.clientX,
            clientY: e.originalEvent.clientY,
          });
        }
      });

      clusterGroup.addLayer(marker);
    });

    map.addLayer(clusterGroup);
    clusterGroupRef.current = clusterGroup;

    return () => {
      map.removeLayer(clusterGroup);
    };
  }, [map, painPoints, onPointClick]);

  return null;
}

export function PainPointMap({
  painPoints,
  onMapClick,
  onPointClick,
  pendingLocation,
  className,
}: PainPointMapProps) {
  // Create custom icon for pending location
  const pendingIcon = useMemo(() => L.divIcon({
    html: '<div style="background: #1e96fc; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4); animation: pulse 1.5s infinite;"></div>',
    className: 'custom-pending-icon',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  }), []);

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
        .custom-cluster-icon {
          background: transparent !important;
        }
        .custom-marker-icon {
          background: transparent !important;
        }
        .marker-cluster {
          background: transparent !important;
        }
        .marker-cluster div {
          background: transparent !important;
        }
        .leaflet-marker-icon:hover {
          z-index: 1000 !important;
        }
      `}</style>

      <MapContainer
        center={CDMX_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        <MapClickHandler onMapClick={onMapClick} />

        {/* OpenStreetMap tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Clustered Pain Points */}
        <ClusterLayer painPoints={painPoints} onPointClick={onPointClick} />

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
          {Object.entries(painPointConfig).filter(([key]) => key !== 'otro').map(([key, config]) => (
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
