import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Droplets, Plus, X, MapPin, AlertTriangle, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { PainPointMap } from '@/components/ui/pain-point-map';

interface PainPoint {
  id: string;
  lat: number;
  lng: number;
  type: 'no_water' | 'leak' | 'contamination' | 'low_pressure';
  description: string;
  createdAt: Date;
}

const painPointTypes = [
  { id: 'no_water', label: 'Sin agua', icon: '🚱', color: '#ef4444' },
  { id: 'leak', label: 'Fuga', icon: '💧', color: '#f97316' },
  { id: 'contamination', label: 'Agua contaminada', icon: '⚠️', color: '#eab308' },
  { id: 'low_pressure', label: 'Baja presión', icon: '📉', color: '#3b82f6' },
];

export default function Index() {
  const [painPoints, setPainPoints] = useState<PainPoint[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [formData, setFormData] = useState({
    type: 'no_water' as PainPoint['type'],
    description: '',
  });

  const [clickPosition, setClickPosition] = useState<{ x: number; y: number } | null>(null);
  const [mapRef, setMapRef] = useState<any>(null);

  const handleMapClick = (lat: number, lng: number, event?: { clientX: number; clientY: number }, map?: any) => {
    setSelectedLocation({ lat, lng });
    if (map) {
      setMapRef(map);
    }
    if (event) {
      const modalWidth = 340;
      const modalHeight = 380;
      const padding = 16;
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      let x = event.clientX + padding;
      let y = event.clientY - modalHeight / 2;

      // Check if modal fits on the right
      const fitsRight = x + modalWidth < viewportWidth - padding;
      // Check if modal fits on the left
      const fitsLeft = event.clientX - modalWidth - padding > padding;

      if (!fitsRight && fitsLeft) {
        // Put on left side
        x = event.clientX - modalWidth - padding;
      } else if (!fitsRight && !fitsLeft && map) {
        // No space on either side - pan the map to make room
        const offsetLng = 0.05; // Pan map to the right
        map.panTo([lat, lng - offsetLng], { animate: true });
        x = viewportWidth / 2 + padding;
        y = viewportHeight / 2 - modalHeight / 2;
      }

      // Vertical bounds
      if (y < padding + 80) y = padding + 80; // Account for header
      if (y + modalHeight > viewportHeight - padding - 50) {
        y = viewportHeight - modalHeight - padding - 50; // Account for stats bar
      }

      setClickPosition({ x, y });
    }
    setIsModalOpen(true);
  };

  // Get modal position style
  const getModalStyle = (): React.CSSProperties => {
    if (!clickPosition) {
      return {
        left: '50%',
        top: '50%',
        transform: 'translate(-50%, -50%)',
      };
    }

    return {
      left: clickPosition.x,
      top: clickPosition.y,
    };
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLocation) return;

    const newPoint: PainPoint = {
      id: Date.now().toString(),
      lat: selectedLocation.lat,
      lng: selectedLocation.lng,
      type: formData.type,
      description: formData.description,
      createdAt: new Date(),
    };

    setPainPoints([...painPoints, newPoint]);
    setIsModalOpen(false);
    setSelectedLocation(null);
    setFormData({ type: 'no_water', description: '' });
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedLocation(null);
    setFormData({ type: 'no_water', description: '' });
  };

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
              <span>{painPoints.length} reportes</span>
            </div>
          </div>
        </div>
      </header>

      {/* Instruction Banner */}
      <div className="bg-accent/10 border-b border-accent/20 py-2 px-4 text-center text-sm flex-shrink-0">
        <span className="text-accent font-medium">Haz clic en el mapa</span>
        <span className="text-muted-foreground"> para reportar un problema de agua en tu zona</span>
      </div>

      {/* Map Container - Full remaining height */}
      <div className="flex-1 relative">
        <div className="absolute inset-0">
          <PainPointMap
            painPoints={painPoints}
            onMapClick={handleMapClick}
            pendingLocation={selectedLocation}
          />
        </div>

        {/* Stats Bar - Floating at bottom */}
        <div className="absolute bottom-0 left-0 right-0 border-t border-border bg-card/95 backdrop-blur-sm py-2 px-4 z-[1000]">
          <div className="container mx-auto flex items-center justify-between text-sm">
            <div className="flex items-center gap-4">
              {painPointTypes.map((type) => {
                const count = painPoints.filter((p) => p.type === type.id).length;
                return (
                  <div key={type.id} className="flex items-center gap-1.5">
                    <span>{type.icon}</span>
                    <span className="text-muted-foreground hidden sm:inline">{type.label}:</span>
                    <span className="font-medium">{count}</span>
                  </div>
                );
              })}
            </div>
            <div className="flex items-center gap-1.5 text-muted-foreground text-xs">
              <Clock className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Última actualización:</span>
              <span>ahora</span>
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      <AnimatePresence>
        {isModalOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={closeModal}
              className="fixed inset-0 bg-black/50 z-[1002]"
            />

            {/* Modal Content */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              style={getModalStyle()}
              className="fixed w-[340px] bg-card border border-border rounded-xl shadow-2xl z-[1003] p-4"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Reportar Problema</h2>
                <button
                  onClick={closeModal}
                  className="p-1 hover:bg-secondary rounded-lg transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Location Preview */}
                <div className="flex items-center gap-2 p-2 bg-secondary/50 rounded-lg text-xs">
                  <MapPin className="h-3.5 w-3.5 text-accent" />
                  <span className="text-muted-foreground">Ubicación:</span>
                  <span className="font-mono">
                    {selectedLocation?.lat.toFixed(4)}, {selectedLocation?.lng.toFixed(4)}
                  </span>
                </div>

                {/* Problem Type */}
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Tipo de problema</label>
                  <div className="grid grid-cols-2 gap-1.5">
                    {painPointTypes.map((type) => (
                      <button
                        key={type.id}
                        type="button"
                        onClick={() => setFormData({ ...formData, type: type.id as PainPoint['type'] })}
                        className={`flex items-center gap-2 p-2.5 rounded-lg border transition-all text-left ${
                          formData.type === type.id
                            ? 'border-accent bg-accent/10 text-accent'
                            : 'border-border hover:border-accent/50'
                        }`}
                      >
                        <span>{type.icon}</span>
                        <span className="text-xs font-medium">{type.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Description */}
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

                {/* Submit */}
                <Button type="submit" className="w-full gap-2 mt-2">
                  <Plus className="h-4 w-4" />
                  Agregar Reporte
                </Button>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
