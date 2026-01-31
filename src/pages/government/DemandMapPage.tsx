import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/page-header';
import { mockDemandPoints, mockIncidents } from '@/data/mockData';
import { cn } from '@/lib/utils';

const intensityColors = {
  low: 'bg-success',
  medium: 'bg-warning',
  high: 'bg-chart-5',
  critical: 'bg-destructive',
};

const intensityLabels = {
  low: 'Baja',
  medium: 'Media',
  high: 'Alta',
  critical: 'Crítica',
};

export default function DemandMapPage() {
  return (
    <DashboardLayout role="government">
      <PageHeader 
        title="Mapa de Demanda" 
        description="Visualización en tiempo real de solicitudes de agua"
      />

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Map Placeholder */}
        <div className="lg:col-span-2">
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <div className="aspect-[16/10] bg-secondary/30 relative">
              {/* Simulated Map View */}
              <div className="absolute inset-0 p-8">
                <svg viewBox="0 0 400 300" className="w-full h-full opacity-20">
                  <path 
                    d="M50,150 Q100,50 200,80 T350,150 T200,250 T50,150" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="1"
                  />
                  <path 
                    d="M80,100 L120,80 L180,120 L150,180 L80,160 Z" 
                    fill="currentColor" 
                    opacity="0.1"
                  />
                  <path 
                    d="M200,60 L280,90 L300,160 L250,200 L180,170 Z" 
                    fill="currentColor" 
                    opacity="0.15"
                  />
                  <path 
                    d="M100,180 L160,200 L150,260 L80,240 Z" 
                    fill="currentColor" 
                    opacity="0.1"
                  />
                </svg>

                {/* Demand Points */}
                {mockDemandPoints.map((point, idx) => {
                  // Map lat/lng to relative positions
                  const x = 20 + (idx * 12) % 60;
                  const y = 15 + (idx * 18) % 70;
                  
                  return (
                    <div
                      key={point.id}
                      className="absolute group"
                      style={{ left: `${x}%`, top: `${y}%` }}
                    >
                      <div className={cn(
                        "w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium text-white shadow-lg cursor-pointer transition-transform hover:scale-110",
                        intensityColors[point.intensity]
                      )}>
                        {point.requestCount}
                      </div>
                      
                      {/* Tooltip */}
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                        <div className="bg-foreground text-background text-xs rounded px-2 py-1 whitespace-nowrap">
                          {point.requestCount} solicitudes
                          <div className="text-muted-foreground/80">
                            Demanda {intensityLabels[point.intensity]}
                          </div>
                        </div>
                      </div>

                      {/* Pulse animation for critical */}
                      {point.intensity === 'critical' && (
                        <div className={cn(
                          "absolute inset-0 rounded-full animate-ping",
                          intensityColors[point.intensity],
                          "opacity-30"
                        )} />
                      )}
                    </div>
                  );
                })}

                {/* Incident markers */}
                {mockIncidents.slice(0, 3).map((incident, idx) => {
                  const x = 25 + (idx * 25);
                  const y = 40 + (idx * 15);
                  
                  return (
                    <div
                      key={incident.id}
                      className="absolute"
                      style={{ left: `${x}%`, top: `${y}%` }}
                    >
                      <div className="w-5 h-5 bg-foreground text-background rounded flex items-center justify-center text-xs">
                        ⚠️
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Map Controls */}
              <div className="absolute top-4 right-4 flex flex-col gap-2">
                <button className="w-8 h-8 bg-card border border-border rounded shadow-sm flex items-center justify-center hover:bg-secondary">
                  +
                </button>
                <button className="w-8 h-8 bg-card border border-border rounded shadow-sm flex items-center justify-center hover:bg-secondary">
                  −
                </button>
              </div>

              {/* Legend */}
              <div className="absolute bottom-4 left-4 bg-card/95 border border-border rounded-lg p-3 text-xs">
                <div className="font-medium mb-2">Nivel de Demanda</div>
                <div className="space-y-1.5">
                  {(['critical', 'high', 'medium', 'low'] as const).map((level) => (
                    <div key={level} className="flex items-center gap-2">
                      <div className={cn("w-3 h-3 rounded-full", intensityColors[level])} />
                      <span>{intensityLabels[level]}</span>
                    </div>
                  ))}
                  <div className="flex items-center gap-2 pt-1 border-t border-border mt-2">
                    <div className="w-3 h-3 bg-foreground rounded flex items-center justify-center text-[8px]">⚠</div>
                    <span>Incidente</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar Stats */}
        <div className="space-y-4">
          {/* Summary Card */}
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-medium mb-4">Resumen en Tiempo Real</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Total Solicitudes</span>
                <span className="font-semibold">{mockDemandPoints.reduce((a, b) => a + b.requestCount, 0)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Zonas Críticas</span>
                <span className="font-semibold text-destructive">
                  {mockDemandPoints.filter(p => p.intensity === 'critical').length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Pipas Activas</span>
                <span className="font-semibold">23</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Incidentes Abiertos</span>
                <span className="font-semibold">{mockIncidents.filter(i => i.status !== 'resolved').length}</span>
              </div>
            </div>
          </div>

          {/* Hotspots */}
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-medium mb-4">Zonas con Mayor Demanda</h3>
            <div className="space-y-3">
              {[
                { zone: 'Iztapalapa Norte', requests: 97, change: '+23%' },
                { zone: 'Tláhuac Centro', requests: 52, change: '+15%' },
                { zone: 'GAM Oriente', requests: 45, change: '+8%' },
                { zone: 'Coyoacán Sur', requests: 28, change: '-5%' },
              ].map((item, idx) => (
                <div key={idx} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded bg-secondary flex items-center justify-center text-xs font-medium">
                      {idx + 1}
                    </span>
                    <span>{item.zone}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{item.requests}</span>
                    <span className={cn(
                      "text-xs",
                      item.change.startsWith('+') ? "text-destructive" : "text-success"
                    )}>
                      {item.change}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Provider Activity */}
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-medium mb-4">Actividad de Pipas</h3>
            <div className="space-y-3">
              {[
                { name: 'Pipas González', deliveries: 8, status: 'active' },
                { name: 'AguaPura MX', deliveries: 6, status: 'active' },
                { name: 'HidroExpress', deliveries: 4, status: 'active' },
                { name: 'Agua del Valle', deliveries: 5, status: 'busy' },
              ].map((provider, idx) => (
                <div key={idx} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      "w-2 h-2 rounded-full",
                      provider.status === 'active' ? 'bg-success' : 'bg-warning'
                    )} />
                    <span>{provider.name}</span>
                  </div>
                  <span className="text-muted-foreground">{provider.deliveries} entregas hoy</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
