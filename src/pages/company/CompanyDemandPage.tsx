import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/page-header';
import { DemandMap } from '@/components/ui/demand-map';
import { mockDemandPoints } from '@/data/mockData';
import { Button } from '@/components/ui/button';
import { Navigation } from 'lucide-react';

export default function CompanyDemandPage() {
  // Company location (example: near Iztapalapa)
  const companyLocation: [number, number] = [19.3800, -99.0900];

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
            <DemandMap
              demandPoints={mockDemandPoints}
              showUserLocation={true}
              userLocation={companyLocation}
              height="500px"
            />
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
