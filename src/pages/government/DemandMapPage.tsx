import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/page-header';
import { DemandMap } from '@/components/ui/demand-map';
import { mockDemandPoints, mockIncidents } from '@/data/mockData';
import { cn } from '@/lib/utils';

export default function DemandMapPage() {
  return (
    <DashboardLayout role="government">
      <PageHeader
        title="Mapa de Demanda"
        description="Visualización en tiempo real de solicitudes de agua"
      />

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Map */}
        <div className="lg:col-span-2">
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <DemandMap
              demandPoints={mockDemandPoints}
              incidents={mockIncidents}
              showIncidents={true}
              height="500px"
            />
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
