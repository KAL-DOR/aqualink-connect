import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/page-header';
import { StatCard } from '@/components/ui/stat-card';
import { StatusBadge } from '@/components/ui/status-badge';
import { Button } from '@/components/ui/button';
import { 
  Truck, 
  DollarSign, 
  Star, 
  TrendingUp,
  ArrowRight,
  Clock,
  MapPin
} from 'lucide-react';
import { mockCompanyStats, mockOrders } from '@/data/mockData';
import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

export default function CompanyDashboard() {
  const activeOrders = mockOrders.filter(o => 
    ['pending', 'accepted', 'in_transit'].includes(o.status)
  );

  return (
    <DashboardLayout role="company">
      <PageHeader 
        title="Dashboard de Empresa" 
        description="Pipas González - Gestión de pedidos y entregas"
      />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard 
          label="Pedidos Activos"
          value={mockCompanyStats.activeOrders}
          icon={<Truck className="h-5 w-5" />}
          variant="accent"
        />
        <StatCard 
          label="Entregas Esta Semana"
          value={mockCompanyStats.deliveriesThisWeek}
          icon={<TrendingUp className="h-5 w-5" />}
          trend={{ value: 18, positive: true }}
        />
        <StatCard 
          label="Ingresos del Mes"
          value={`$${(mockCompanyStats.revenue / 1000).toFixed(1)}k`}
          icon={<DollarSign className="h-5 w-5" />}
          variant="success"
          trend={{ value: 12, positive: true }}
        />
        <StatCard 
          label="Calificación"
          value={mockCompanyStats.averageRating}
          icon={<Star className="h-5 w-5" />}
        />
      </div>

      {/* Active Orders */}
      <div className="bg-card border border-border rounded-lg mb-6">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h3 className="font-medium">Pedidos Activos</h3>
          <Link to="/company/orders">
            <Button variant="ghost" size="sm" className="gap-1">
              Ver todos <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
        
        <div className="divide-y divide-border">
          {activeOrders.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              No hay pedidos activos en este momento
            </div>
          ) : (
            activeOrders.map((order) => (
              <div key={order.id} className="p-4 hover:bg-secondary/20 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{order.citizenName}</span>
                      <StatusBadge status={order.status} />
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5" />
                        {order.location.colonia}, {order.location.municipality}
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3.5 w-3.5" />
                        {formatDistanceToNow(order.createdAt, { addSuffix: true, locale: es })}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold">${order.totalPrice.toLocaleString()}</div>
                    <div className="text-sm text-muted-foreground">
                      {(order.quantity / 1000).toFixed(0)}k litros
                    </div>
                  </div>
                </div>
                
                {order.status === 'pending' && (
                  <div className="flex gap-2 mt-3">
                    <Button size="sm" className="flex-1">
                      Aceptar
                    </Button>
                    <Button size="sm" variant="outline">
                      Rechazar
                    </Button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Today's Performance */}
        <div className="bg-card border border-border rounded-lg p-5">
          <h3 className="font-medium mb-4">Rendimiento de Hoy</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Pedidos completados</span>
              <span className="font-semibold">8 de 12</span>
            </div>
            <div className="h-2 bg-secondary rounded-full overflow-hidden">
              <div className="h-full bg-success rounded-full" style={{ width: '66%' }} />
            </div>
            
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
              <div>
                <div className="text-2xl font-semibold">45 min</div>
                <div className="text-sm text-muted-foreground">Tiempo promedio de entrega</div>
              </div>
              <div>
                <div className="text-2xl font-semibold">78 km</div>
                <div className="text-sm text-muted-foreground">Distancia recorrida</div>
              </div>
            </div>
          </div>
        </div>

        {/* Demand Zones */}
        <div className="bg-card border border-border rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium">Zonas con Demanda Alta</h3>
            <Link to="/company/demand">
              <Button variant="ghost" size="sm" className="gap-1">
                Ver mapa <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          <div className="space-y-3">
            {[
              { zone: 'Iztapalapa Norte', requests: 23, distance: '12 km' },
              { zone: 'Santa Cruz Meyehualco', requests: 15, distance: '8 km' },
              { zone: 'Lomas de Zaragoza', requests: 12, distance: '15 km' },
              { zone: 'San Miguel', requests: 8, distance: '10 km' },
            ].map((item, idx) => (
              <div 
                key={idx} 
                className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg"
              >
                <div>
                  <div className="font-medium">{item.zone}</div>
                  <div className="text-sm text-muted-foreground">
                    {item.requests} solicitudes pendientes
                  </div>
                </div>
                <div className="text-right text-sm text-muted-foreground">
                  ~{item.distance}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-6 grid sm:grid-cols-2 gap-4">
        <Link to="/company/orders" className="block">
          <div className="p-4 bg-card border border-border rounded-lg hover:border-primary/50 transition-colors group">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-accent/10 text-accent">
                <Truck className="h-5 w-5" />
              </div>
              <div>
                <h4 className="font-medium group-hover:text-primary transition-colors">Gestionar Pedidos</h4>
                <p className="text-sm text-muted-foreground">Ver y administrar entregas</p>
              </div>
            </div>
          </div>
        </Link>
        <Link to="/company/settings" className="block">
          <div className="p-4 bg-card border border-border rounded-lg hover:border-primary/50 transition-colors group">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10 text-primary">
                <DollarSign className="h-5 w-5" />
              </div>
              <div>
                <h4 className="font-medium group-hover:text-primary transition-colors">Configurar Precios</h4>
                <p className="text-sm text-muted-foreground">Ajustar precios dinámicos</p>
              </div>
            </div>
          </div>
        </Link>
      </div>
    </DashboardLayout>
  );
}
