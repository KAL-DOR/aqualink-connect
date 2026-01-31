import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/page-header';
import { mockDemandPoints } from '@/data/mockData';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Navigation } from 'lucide-react';

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

export default function CompanyDemandPage() {
  return (
    <DashboardLayout role="company">
      <PageHeader 
        title="Mapa de Demanda" 
        description="Visualiza dónde hay mayor demanda de agua"
      />

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Map */}
        <div className="lg:col-span-2">
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <div className="aspect-[16/10] bg-secondary/30 relative">
              {/* Simulated Map */}
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
                </svg>

                {/* Demand Points */}
                {mockDemandPoints.map((point, idx) => {
                  const x = 15 + (idx * 14) % 70;
                  const y = 10 + (idx * 20) % 75;
                  
                  return (
                    <div
                      key={point.id}
                      className="absolute group cursor-pointer"
                      style={{ left: `${x}%`, top: `${y}%` }}
                    >
                      <div className={cn(
                        "w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium text-white shadow-lg transition-transform hover:scale-110",
                        intensityColors[point.intensity]
                      )}>
                        {point.requestCount}
                      </div>
                      
                      {point.intensity === 'critical' && (
                        <div className={cn(
                          "absolute inset-0 rounded-full animate-ping",
                          intensityColors[point.intensity],
                          "opacity-30"
                        )} />
                      )}

                      {/* Tooltip */}
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                        <div className="bg-foreground text-background text-xs rounded-lg px-3 py-2 whitespace-nowrap shadow-lg">
                          <div className="font-medium">{point.requestCount} solicitudes</div>
                          <div className="text-muted-foreground/80">
                            Demanda {intensityLabels[point.intensity]}
                          </div>
                          <div className="mt-1 pt-1 border-t border-muted-foreground/20">
                            ~{(point.requestCount * 10000 / 1000).toFixed(0)}k litros estimados
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}

                {/* Your location marker */}
                <div className="absolute" style={{ left: '50%', top: '45%' }}>
                  <div className="relative">
                    <div className="w-4 h-4 bg-primary rounded-full border-2 border-primary-foreground shadow-lg" />
                    <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] font-medium bg-primary text-primary-foreground px-2 py-0.5 rounded whitespace-nowrap">
                      Tu ubicación
                    </div>
                  </div>
                </div>
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
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Opportunities */}
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-medium mb-4">Oportunidades Cercanas</h3>
            <div className="space-y-3">
              {[
                { zone: 'Iztapalapa Norte', requests: 45, distance: '8 km', revenue: '$38,250' },
                { zone: 'San Miguel', requests: 23, distance: '5 km', revenue: '$19,550' },
                { zone: 'Santa Cruz', requests: 18, distance: '12 km', revenue: '$15,300' },
              ].map((item, idx) => (
                <div 
                  key={idx}
                  className="p-3 bg-secondary/30 rounded-lg"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="font-medium">{item.zone}</div>
                      <div className="text-sm text-muted-foreground">
                        {item.requests} solicitudes · ~{item.distance}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-success">{item.revenue}</div>
                      <div className="text-xs text-muted-foreground">potencial</div>
                    </div>
                  </div>
                  <Button size="sm" variant="outline" className="w-full gap-1 mt-2">
                    <Navigation className="h-3.5 w-3.5" />
                    Navegar
                  </Button>
                </div>
              ))}
            </div>
          </div>

          {/* Pricing Recommendation */}
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-medium mb-4">Sugerencia de Precios</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Basado en la demanda actual, considera ajustar tus precios:
            </p>
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span>Precio base actual</span>
                <span className="font-medium">$850/10kL</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span>Precio sugerido (alta demanda)</span>
                <span className="font-medium text-warning">$935/10kL</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span>Aumento sugerido</span>
                <span className="font-medium text-success">+10%</span>
              </div>
            </div>
            <Button className="w-full mt-4" variant="outline">
              Aplicar Sugerencia
            </Button>
          </div>

          {/* Stats */}
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-medium mb-4">Resumen del Mercado</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Demanda total</span>
                <span className="font-medium">{mockDemandPoints.reduce((a, b) => a + b.requestCount, 0)} solicitudes</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Pipas activas</span>
                <span className="font-medium">18 operando</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Tiempo espera promedio</span>
                <span className="font-medium">52 min</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Tu posición en zona</span>
                <span className="font-medium">#2 en calificación</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
