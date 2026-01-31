import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/page-header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { 
  DollarSign, 
  Truck, 
  Clock, 
  Award,
  Save,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

export default function CompanySettingsPage() {
  const [basePrice, setBasePrice] = useState(850);
  const [dynamicPricing, setDynamicPricing] = useState(true);
  const [highDemandMultiplier, setHighDemandMultiplier] = useState([1.15]);
  const [offPeakDiscount, setOffPeakDiscount] = useState([0.1]);
  const [maxDistance, setMaxDistance] = useState(25);
  const [fleetSize, setFleetSize] = useState(5);

  const handleSave = () => {
    toast.success('Configuración guardada');
  };

  return (
    <DashboardLayout role="company">
      <PageHeader 
        title="Configuración" 
        description="Gestiona tu perfil, precios y preferencias"
        actions={
          <Button onClick={handleSave} className="gap-2">
            <Save className="h-4 w-4" />
            Guardar Cambios
          </Button>
        }
      />

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Pricing Configuration */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-6">
            <DollarSign className="h-5 w-5 text-muted-foreground" />
            <h3 className="font-medium">Configuración de Precios</h3>
          </div>

          <div className="space-y-6">
            {/* Base Price */}
            <div className="space-y-2">
              <Label>Precio Base (por 10,000 litros)</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                <Input
                  type="number"
                  value={basePrice}
                  onChange={(e) => setBasePrice(Number(e.target.value))}
                  className="pl-8"
                />
              </div>
              <p className="text-xs text-muted-foreground">
                Este es el precio que los ciudadanos verán en condiciones normales
              </p>
            </div>

            {/* Dynamic Pricing Toggle */}
            <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg">
              <div>
                <div className="font-medium">Precios Dinámicos</div>
                <p className="text-sm text-muted-foreground">
                  Ajusta precios automáticamente según demanda
                </p>
              </div>
              <Switch 
                checked={dynamicPricing} 
                onCheckedChange={setDynamicPricing}
              />
            </div>

            {dynamicPricing && (
              <>
                {/* High Demand Multiplier */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label>Multiplicador Alta Demanda</Label>
                    <span className="text-sm font-medium">
                      +{((highDemandMultiplier[0] - 1) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <Slider
                    value={highDemandMultiplier}
                    onValueChange={setHighDemandMultiplier}
                    min={1}
                    max={1.5}
                    step={0.05}
                  />
                  <p className="text-xs text-muted-foreground">
                    Precio en alta demanda: ${(basePrice * highDemandMultiplier[0]).toFixed(0)}
                  </p>
                </div>

                {/* Off-Peak Discount */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label>Descuento Horas Valle</Label>
                    <span className="text-sm font-medium">
                      -{(offPeakDiscount[0] * 100).toFixed(0)}%
                    </span>
                  </div>
                  <Slider
                    value={offPeakDiscount}
                    onValueChange={setOffPeakDiscount}
                    min={0}
                    max={0.25}
                    step={0.05}
                  />
                  <p className="text-xs text-muted-foreground">
                    Precio en horas valle: ${(basePrice * (1 - offPeakDiscount[0])).toFixed(0)}
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Service Area */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-6">
            <Truck className="h-5 w-5 text-muted-foreground" />
            <h3 className="font-medium">Área de Servicio</h3>
          </div>

          <div className="space-y-6">
            {/* Max Distance */}
            <div className="space-y-2">
              <Label>Distancia Máxima de Entrega (km)</Label>
              <Input
                type="number"
                value={maxDistance}
                onChange={(e) => setMaxDistance(Number(e.target.value))}
              />
              <p className="text-xs text-muted-foreground">
                Solo recibirás pedidos dentro de este radio
              </p>
            </div>

            {/* Fleet Size */}
            <div className="space-y-2">
              <Label>Tamaño de Flota</Label>
              <Input
                type="number"
                value={fleetSize}
                onChange={(e) => setFleetSize(Number(e.target.value))}
              />
              <p className="text-xs text-muted-foreground">
                Número de unidades disponibles para entregas
              </p>
            </div>

            {/* Service Hours */}
            <div className="space-y-3">
              <Label>Horario de Servicio</Label>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-xs text-muted-foreground">Desde</Label>
                  <Input type="time" defaultValue="06:00" />
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">Hasta</Label>
                  <Input type="time" defaultValue="20:00" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Company Profile */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-6">
            <Award className="h-5 w-5 text-muted-foreground" />
            <h3 className="font-medium">Perfil de Empresa</h3>
          </div>

          <div className="space-y-6">
            <div className="space-y-2">
              <Label>Nombre de la Empresa</Label>
              <Input defaultValue="Pipas González" />
            </div>

            <div className="space-y-2">
              <Label>Teléfono de Contacto</Label>
              <Input defaultValue="+52 55 1234 5678" />
            </div>

            <div className="space-y-2">
              <Label>Certificaciones</Label>
              <div className="flex flex-wrap gap-2">
                {['SACMEX', 'ISO 9001'].map((cert) => (
                  <span 
                    key={cert}
                    className="px-3 py-1 bg-secondary text-sm rounded-full"
                  >
                    {cert}
                  </span>
                ))}
                <button className="px-3 py-1 border border-dashed border-border text-sm rounded-full text-muted-foreground hover:border-primary hover:text-primary transition-colors">
                  + Agregar
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-6">
            <AlertCircle className="h-5 w-5 text-muted-foreground" />
            <h3 className="font-medium">Notificaciones</h3>
          </div>

          <div className="space-y-4">
            {[
              { label: 'Nuevo pedido recibido', description: 'Alerta inmediata cuando llega un pedido', enabled: true },
              { label: 'Recordatorio de pedidos pendientes', description: 'Cada 15 minutos si hay pedidos sin aceptar', enabled: true },
              { label: 'Alertas de alta demanda', description: 'Cuando hay oportunidades en tu zona', enabled: true },
              { label: 'Resumen diario', description: 'Estadísticas del día anterior', enabled: false },
            ].map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg">
                <div>
                  <div className="font-medium text-sm">{item.label}</div>
                  <p className="text-xs text-muted-foreground">{item.description}</p>
                </div>
                <Switch defaultChecked={item.enabled} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
