import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Droplets, Plus, X, MapPin, AlertTriangle, Clock, ExternalLink, Droplet, CircleOff, TrendingDown, LucideIcon, Moon, Sun, Flame, Activity } from 'lucide-react';
import { useTheme } from '@/components/theme-provider';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { PainPointMap } from '@/components/ui/pain-point-map';

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

interface Stats {
  total: number;
  con_ubicacion: number;
  por_tipo: Record<string, number>;
  por_alcaldia: Record<string, number>;
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

const API_URL = `http://${window.location.hostname}:8001/api`;

const painPointTypes: { id: string; label: string; Icon: LucideIcon; color: string }[] = [
  { id: 'sin_agua', label: 'Sin agua', Icon: CircleOff, color: '#ef4444' },
  { id: 'fuga', label: 'Fuga', Icon: Droplet, color: '#f97316' },
  { id: 'agua_contaminada', label: 'Agua contaminada', Icon: AlertTriangle, color: '#eab308' },
  { id: 'baja_presion', label: 'Baja presion', Icon: TrendingDown, color: '#3b82f6' },
];

export default function Index() {
  const { theme, setTheme } = useTheme();
  const [painPoints, setPainPoints] = useState<PainPoint[]>([]);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<PainPoint | null>(null);
  const [clickPosition, setClickPosition] = useState<{ x: number; y: number } | null>(null);
  const [formData, setFormData] = useState({
    type: 'sin_agua',
    description: '',
  });

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  // Fetch data from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [mapRes, statsRes, hotspotsRes] = await Promise.all([
          fetch(`${API_URL}/quejas/mapa?limit=1500`),
          fetch(`${API_URL}/quejas/estadisticas`),
          fetch(`${API_URL}/hotspots`)
        ]);

        if (mapRes.ok) {
          const mapData = await mapRes.json();
          setPainPoints(mapData.puntos);
        }

        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }

        if (hotspotsRes.ok) {
          const hotspotsData = await hotspotsRes.json();
          setHotspots(hotspotsData.hotspots);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleMapClick = (lat: number, lng: number, event?: { clientX: number; clientY: number }) => {
    setSelectedLocation({ lat, lng });
    setSelectedPoint(null);
    if (event) {
      const modalWidth = 340;
      const modalHeight = 380;
      const padding = 16;
      const viewportWidth = window.innerWidth;

      let x = event.clientX + padding;
      let y = event.clientY - modalHeight / 2;

      if (x + modalWidth > viewportWidth - padding) {
        x = event.clientX - modalWidth - padding;
      }
      if (x < padding) x = padding;
      if (y < padding + 80) y = padding + 80;
      if (y + modalHeight > window.innerHeight - padding - 50) {
        y = window.innerHeight - modalHeight - padding - 50;
      }

      setClickPosition({ x, y });
    }
    setIsModalOpen(true);
  };

  const handlePointClick = (point: PainPoint, event?: { clientX: number; clientY: number }) => {
    setSelectedPoint(point);
    setSelectedLocation(null);
    if (event) {
      const modalWidth = 340;
      const padding = 16;
      const viewportWidth = window.innerWidth;

      let x = event.clientX + padding;
      let y = event.clientY - 150;

      if (x + modalWidth > viewportWidth - padding) {
        x = event.clientX - modalWidth - padding;
      }
      if (x < padding) x = padding;
      if (y < padding + 80) y = padding + 80;

      setClickPosition({ x, y });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLocation) return;

    try {
      const response = await fetch(`${API_URL}/quejas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: selectedLocation.lat,
          lng: selectedLocation.lng,
          tipo: formData.type,
          texto: formData.description || 'Reporte de usuario',
          username: 'usuario_anonimo',
        }),
      });

      if (response.ok) {
        const newPoint = await response.json();
        setPainPoints([{ ...newPoint, isUserAdded: true }, ...painPoints]);
      } else {
        // Fallback to local-only if API fails
        const localPoint: PainPoint = {
          id: Date.now(),
          lat: selectedLocation.lat,
          lng: selectedLocation.lng,
          tipo: formData.type,
          texto: formData.description || 'Reporte de usuario',
          username: 'usuario_anonimo',
          alcaldia: null,
          created_at: new Date().toISOString(),
          isUserAdded: true,
        };
        setPainPoints([localPoint, ...painPoints]);
      }
    } catch (error) {
      console.error('Error submitting report:', error);
      // Fallback to local-only
      const localPoint: PainPoint = {
        id: Date.now(),
        lat: selectedLocation.lat,
        lng: selectedLocation.lng,
        tipo: formData.type,
        texto: formData.description || 'Reporte de usuario',
        username: 'usuario_anonimo',
        alcaldia: null,
        created_at: new Date().toISOString(),
        isUserAdded: true,
      };
      setPainPoints([localPoint, ...painPoints]);
    }

    closeModal();
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedLocation(null);
    setSelectedPoint(null);
    setFormData({ type: 'sin_agua', description: '' });
  };

  const getModalStyle = (): React.CSSProperties => {
    if (!clickPosition) {
      return { left: '50%', top: '50%', transform: 'translate(-50%, -50%)' };
    }
    return { left: clickPosition.x, top: clickPosition.y };
  };

  const typeConfig = painPointTypes.find(t => t.id === selectedPoint?.tipo) || painPointTypes[0];

  return (
    <div className="h-screen bg-background flex flex-col overflow-hidden">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur-sm z-[1001] flex-shrink-0">
        <div className="container mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Droplets className="h-6 w-6 text-accent" />
            <span className="font-semibold text-lg">AquaHub</span>
          </div>
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <MapPin className="h-4 w-4" />
              <span>CDMX</span>
            </div>
            <div className="h-4 w-px bg-border" />
            <div className="flex items-center gap-1.5">
              <AlertTriangle className="h-4 w-4 text-warning" />
              <span>{stats?.con_ubicacion || painPoints.length} reportes</span>
            </div>
            <div className="h-4 w-px bg-border" />
            <button
              onClick={toggleTheme}
              className="p-1.5 rounded-lg hover:bg-secondary transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Instruction Banner */}
      <div className="bg-accent/10 border-b border-accent/20 py-2 px-4 text-center text-sm flex-shrink-0">
        <span className="text-accent font-medium">Haz clic en el mapa</span>
        <span className="text-muted-foreground"> para reportar un problema de agua en tu zona</span>
      </div>

      {/* Main Content with Ad Bars */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Ad Bar */}
        <div className="hidden lg:flex w-[160px] flex-col bg-card/50 border-r border-border p-3 gap-3">
          <div className="flex-1 bg-secondary/30 rounded-lg flex items-center justify-center border border-dashed border-border">
            <span className="text-xs text-muted-foreground writing-vertical">Espacio Publicitario</span>
          </div>
          <div className="h-[250px] bg-secondary/30 rounded-lg flex items-center justify-center border border-dashed border-border">
            <span className="text-xs text-muted-foreground text-center px-2">Ad 160x250</span>
          </div>
        </div>

        {/* Map Container */}
        <div className="flex-1 relative">
          <div className="absolute inset-0">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-muted-foreground">Cargando datos...</div>
              </div>
            ) : (
              <PainPointMap
                painPoints={painPoints}
                hotspots={hotspots}
                onMapClick={handleMapClick}
                onPointClick={handlePointClick}
                pendingLocation={selectedLocation}
              />
            )}
          </div>

          {/* Recent Submissions Panel */}
          <div className="absolute top-4 left-4 w-[280px] bg-card/95 border border-border rounded-lg shadow-lg z-[1000] hidden md:block">
            <div className="flex items-center gap-2 p-3 border-b border-border">
              <Activity className="h-4 w-4 text-accent" />
              <h3 className="font-semibold text-sm">Reportes Recientes</h3>
            </div>
            <div className="max-h-[200px] overflow-y-auto">
              {painPoints.slice(0, 5).map((point) => {
                const config = painPointTypes.find(t => t.id === point.tipo) || painPointTypes[0];
                return (
                  <div key={point.id} className="p-2 border-b border-border/50 last:border-0 hover:bg-secondary/30 cursor-pointer" onClick={() => handlePointClick(point)}>
                    <div className="flex items-start gap-2">
                      <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: config.color }}>
                        <config.Icon className="w-3 h-3 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs truncate">{point.texto.slice(0, 60)}...</p>
                        <div className="flex items-center gap-2 text-[10px] text-muted-foreground mt-1">
                          <span>@{point.username}</span>
                          {point.alcaldia && <span>• {point.alcaldia}</span>}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Highest Density Zones Panel */}
          <div className="absolute top-4 right-4 w-[240px] bg-card/95 border border-border rounded-lg shadow-lg z-[1000] hidden md:block">
            <div className="flex items-center gap-2 p-3 border-b border-border">
              <Flame className="h-4 w-4 text-orange-500" />
              <h3 className="font-semibold text-sm">Zonas Criticas</h3>
            </div>
            <div className="p-2 space-y-2">
              {hotspots
                .sort((a, b) => b.risk_index - a.risk_index)
                .slice(0, 5)
                .map((hotspot, index) => (
                  <div key={hotspot.id} className="flex items-center gap-2 p-2 rounded-lg bg-secondary/30">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                      index === 0 ? 'bg-red-500' : index === 1 ? 'bg-orange-500' : 'bg-yellow-500'
                    }`}>
                      {index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium truncate">{hotspot.location_name}</p>
                      <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                        <span>Riesgo: {hotspot.risk_index.toFixed(1)}</span>
                        <span>• {hotspot.estimated_total_reports.toLocaleString()} reportes</span>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Stats Bar */}
          <div className="absolute bottom-0 left-0 right-0 border-t border-border bg-card/95 backdrop-blur-sm py-2 px-4 z-[1000]">
            <div className="container mx-auto flex items-center justify-between text-sm">
              <div className="flex items-center gap-4">
                {painPointTypes.map((type) => {
                  const count = stats?.por_tipo[type.id] || painPoints.filter((p) => p.tipo === type.id).length;
                  return (
                    <div key={type.id} className="flex items-center gap-1.5">
                      <div className="w-5 h-5 rounded-full flex items-center justify-center" style={{ backgroundColor: type.color }}>
                        <type.Icon className="w-3 h-3 text-white" />
                      </div>
                      <span className="text-muted-foreground hidden sm:inline">{type.label}:</span>
                      <span className="font-medium">{count}</span>
                    </div>
                  );
                })}
              </div>
              <div className="flex items-center gap-1.5 text-muted-foreground text-xs">
                <Clock className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Total:</span>
                <span>{stats?.total || painPoints.length} quejas</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Ad Bar */}
        <div className="hidden lg:flex w-[160px] flex-col bg-card/50 border-l border-border p-3 gap-3">
          <div className="h-[250px] bg-secondary/30 rounded-lg flex items-center justify-center border border-dashed border-border">
            <span className="text-xs text-muted-foreground text-center px-2">Ad 160x250</span>
          </div>
          <div className="flex-1 bg-secondary/30 rounded-lg flex items-center justify-center border border-dashed border-border">
            <span className="text-xs text-muted-foreground writing-vertical">Espacio Publicitario</span>
          </div>
        </div>
      </div>

      {/* Modal */}
      <AnimatePresence>
        {isModalOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={closeModal}
              className="fixed inset-0 bg-black/50 z-[1002]"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              style={getModalStyle()}
              className="fixed w-[340px] bg-card border border-border rounded-xl shadow-2xl z-[1003] p-4"
            >
              {/* View existing complaint */}
              {selectedPoint && (
                <>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: typeConfig.color }}>
                        <typeConfig.Icon className="w-4 h-4 text-white" />
                      </div>
                      <h2 className="font-semibold">{typeConfig.label}</h2>
                    </div>
                    <button onClick={closeModal} className="p-1 hover:bg-secondary rounded-lg">
                      <X className="h-5 w-5" />
                    </button>
                  </div>

                  <div className="space-y-3">
                    <p className="text-sm">{selectedPoint.texto}</p>

                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>@{selectedPoint.username}</span>
                      {selectedPoint.alcaldia && (
                        <>
                          <span>•</span>
                          <span>{selectedPoint.alcaldia}</span>
                        </>
                      )}
                    </div>

                    <div className="text-xs text-muted-foreground">
                      {new Date(selectedPoint.created_at).toLocaleDateString('es-MX', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>

                    {!selectedPoint.isUserAdded && (
                      <a
                        href={`https://twitter.com/${selectedPoint.username}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-xs text-accent hover:underline"
                      >
                        <ExternalLink className="h-3 w-3" />
                        Ver en Twitter
                      </a>
                    )}
                  </div>
                </>
              )}

              {/* Add new complaint */}
              {selectedLocation && !selectedPoint && (
                <>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold">Reportar Problema</h2>
                    <button onClick={closeModal} className="p-1 hover:bg-secondary rounded-lg">
                      <X className="h-5 w-5" />
                    </button>
                  </div>

                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="flex items-center gap-2 p-2 bg-secondary/50 rounded-lg text-xs">
                      <MapPin className="h-3.5 w-3.5 text-accent" />
                      <span className="text-muted-foreground">Ubicación:</span>
                      <span className="font-mono">
                        {selectedLocation.lat.toFixed(4)}, {selectedLocation.lng.toFixed(4)}
                      </span>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-sm font-medium">Tipo de problema</label>
                      <div className="grid grid-cols-2 gap-1.5">
                        {painPointTypes.map((type) => (
                          <button
                            key={type.id}
                            type="button"
                            onClick={() => setFormData({ ...formData, type: type.id })}
                            className={`flex items-center gap-2 p-2.5 rounded-lg border transition-all text-left ${
                              formData.type === type.id
                                ? 'border-accent bg-accent/10 text-accent'
                                : 'border-border hover:border-accent/50'
                            }`}
                          >
                            <div className="w-6 h-6 rounded-full flex items-center justify-center" style={{ backgroundColor: type.color }}>
                              <type.Icon className="w-3.5 h-3.5 text-white" />
                            </div>
                            <span className="text-xs font-medium">{type.label}</span>
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-sm font-medium">Descripción (opcional)</label>
                      <Textarea
                        placeholder="Describe el problema..."
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        rows={2}
                        className="resize-none text-sm"
                      />
                    </div>

                    <Button type="submit" className="w-full gap-2 mt-2">
                      <Plus className="h-4 w-4" />
                      Agregar Reporte
                    </Button>
                  </form>
                </>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
