import { useEffect, useRef, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents, Circle, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.markercluster';
import { cn } from '@/lib/utils';
import { Droplet, CircleOff, AlertTriangle, TrendingDown, HelpCircle } from 'lucide-react';

// Ensure markercluster is available on L
declare global {
  interface Window {
    L: typeof L;
  }
}
if (typeof window !== 'undefined') {
  window.L = L;
}

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

interface Hotspot {
  id: number;
  cluster_label: number;
  lat: number;
  lon: number;
  risk_index: number;
  location_name: string;
  sampled_reports: number;
  estimated_total_reports: number;
}

// SVG icons for Leaflet markers (since Leaflet needs HTML strings)
const svgIcons = {
  sin_agua: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/></svg>`,
  fuga: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/></svg>`,
  agua_contaminada: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>`,
  baja_presion: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>`,
  otro: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>`,
};

// Lucide icon components for React rendering
const iconComponents = {
  sin_agua: CircleOff,
  fuga: Droplet,
  agua_contaminada: AlertTriangle,
  baja_presion: TrendingDown,
  otro: HelpCircle,
};

const painPointConfig: Record<string, { color: string; label: string }> = {
  sin_agua: { color: '#ef4444', label: 'Sin agua' },
  fuga: { color: '#f97316', label: 'Fuga' },
  agua_contaminada: { color: '#eab308', label: 'Agua contaminada' },
  baja_presion: { color: '#3b82f6', label: 'Baja presion' },
  otro: { color: '#6b7280', label: 'Otro' },
};

interface PainPointMapProps {
  painPoints: PainPoint[];
  hotspots?: Hotspot[];
  onMapClick: (lat: number, lng: number, event?: { clientX: number; clientY: number }, map?: L.Map) => void;
  onPointClick?: (point: PainPoint, event?: { clientX: number; clientY: number }) => void;
  pendingLocation?: { lat: number; lng: number } | null;
  className?: string;
}

function getRiskColor(riskIndex: number): string {
  const normalized = Math.max(0, Math.min(1, (riskIndex - 2) / 2));
  if (normalized < 0.33) return '#fbbf24';
  if (normalized < 0.66) return '#f97316';
  return '#dc2626';
}

function getCircleRadius(estimatedReports: number): number {
  const base = 300;
  const scale = Math.log10(Math.max(10, estimatedReports)) * 200;
  return Math.min(base + scale, 2000);
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

// Create individual marker icon with SVG
function createMarkerIcon(tipo: string) {
  const config = painPointConfig[tipo] || painPointConfig.otro;
  const svg = svgIcons[tipo as keyof typeof svgIcons] || svgIcons.otro;
  const size = 28;

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
        display: flex;
        align-items: center;
        justify-content: center;
      ">${svg}</div>
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
  hotspots = [],
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

        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {hotspots.map((hotspot) => (
          <Circle
            key={hotspot.id}
            center={[hotspot.lat, hotspot.lon]}
            radius={getCircleRadius(hotspot.estimated_total_reports)}
            pathOptions={{
              color: getRiskColor(hotspot.risk_index),
              fillColor: getRiskColor(hotspot.risk_index),
              fillOpacity: 0.25,
              weight: 2,
            }}
          >
            <Tooltip>
              <div className="text-sm">
                <div className="font-semibold">{hotspot.location_name}</div>
                <div>Indice de riesgo: {hotspot.risk_index.toFixed(2)}</div>
                <div>Reportes estimados: {hotspot.estimated_total_reports.toLocaleString()}</div>
              </div>
            </Tooltip>
          </Circle>
        ))}

        <ClusterLayer painPoints={painPoints} onPointClick={onPointClick} />

        {pendingLocation && (
          <Marker position={[pendingLocation.lat, pendingLocation.lng]} icon={pendingIcon}>
            <Popup>
              <div className="text-sm font-medium">Nueva ubicacion seleccionada</div>
            </Popup>
          </Marker>
        )}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-14 left-4 bg-card/95 border border-border rounded-lg p-3 text-xs z-[1100]">
        <div className="font-medium mb-2">Tipos de Problema</div>
        <div className="space-y-1.5">
          {Object.entries(painPointConfig).filter(([key]) => key !== 'otro').map(([key, config]) => {
            const IconComponent = iconComponents[key as keyof typeof iconComponents];
            return (
              <div key={key} className="flex items-center gap-2">
                <div
                  className="w-5 h-5 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: config.color }}
                >
                  <IconComponent className="w-3 h-3 text-white" />
                </div>
                <span>{config.label}</span>
              </div>
            );
          })}
        </div>
        {hotspots.length > 0 && (
          <>
            <div className="border-t border-border my-2" />
            <div className="font-medium mb-2">Zonas de Riesgo</div>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-full border-2" style={{ borderColor: '#fbbf24', backgroundColor: 'rgba(251, 191, 36, 0.25)' }} />
                <span>Bajo</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-full border-2" style={{ borderColor: '#f97316', backgroundColor: 'rgba(249, 115, 22, 0.25)' }} />
                <span>Medio</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-full border-2" style={{ borderColor: '#dc2626', backgroundColor: 'rgba(220, 38, 38, 0.25)' }} />
                <span>Alto</span>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Crosshair hint */}
      <div className="absolute top-4 right-4 bg-card/95 border border-border rounded-lg px-3 py-2 text-xs z-[1100] flex items-center gap-2">
        <div className="w-4 h-4 border-2 border-accent rounded-full flex items-center justify-center">
          <div className="w-1 h-1 bg-accent rounded-full" />
        </div>
        <span>Clic para reportar</span>
      </div>
    </div>
  );
}
