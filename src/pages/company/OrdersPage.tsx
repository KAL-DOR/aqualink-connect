import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/page-header';
import { StatusBadge } from '@/components/ui/status-badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Search, 
  Filter,
  MapPin,
  Phone,
  Clock,
  Truck,
  Check,
  X
} from 'lucide-react';
import { mockOrders } from '@/data/mockData';
import { WaterOrder } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

export default function OrdersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [orders, setOrders] = useState(mockOrders);

  const filteredOrders = orders.filter(order => {
    const matchesSearch = 
      order.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.citizenName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.location.colonia?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || order.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const handleAccept = (orderId: string) => {
    setOrders(prev => prev.map(o => 
      o.id === orderId 
        ? { ...o, status: 'accepted' as const, estimatedDelivery: new Date(Date.now() + 1000 * 60 * 45) }
        : o
    ));
    toast.success('Pedido aceptado');
  };

  const handleReject = (orderId: string) => {
    setOrders(prev => prev.map(o => 
      o.id === orderId ? { ...o, status: 'cancelled' as const } : o
    ));
    toast.info('Pedido rechazado');
  };

  const handleStartDelivery = (orderId: string) => {
    setOrders(prev => prev.map(o => 
      o.id === orderId ? { ...o, status: 'in_transit' as const } : o
    ));
    toast.success('Entrega iniciada');
  };

  const handleComplete = (orderId: string) => {
    setOrders(prev => prev.map(o => 
      o.id === orderId ? { ...o, status: 'delivered' as const, deliveredAt: new Date() } : o
    ));
    toast.success('Entrega completada');
  };

  return (
    <DashboardLayout role="company">
      <PageHeader 
        title="Gestión de Pedidos" 
        description="Administra y da seguimiento a las entregas"
      />

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por ID, cliente o ubicación..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue placeholder="Estado" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos los estados</SelectItem>
            <SelectItem value="pending">Pendiente</SelectItem>
            <SelectItem value="accepted">Aceptado</SelectItem>
            <SelectItem value="in_transit">En Camino</SelectItem>
            <SelectItem value="delivered">Entregado</SelectItem>
            <SelectItem value="cancelled">Cancelado</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div className="bg-card border border-border rounded-lg p-3">
          <div className="text-2xl font-semibold text-warning">
            {orders.filter(o => o.status === 'pending').length}
          </div>
          <div className="text-sm text-muted-foreground">Pendientes</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-3">
          <div className="text-2xl font-semibold text-water">
            {orders.filter(o => o.status === 'accepted').length}
          </div>
          <div className="text-sm text-muted-foreground">Aceptados</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-3">
          <div className="text-2xl font-semibold text-accent">
            {orders.filter(o => o.status === 'in_transit').length}
          </div>
          <div className="text-sm text-muted-foreground">En Camino</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-3">
          <div className="text-2xl font-semibold text-success">
            {orders.filter(o => o.status === 'delivered').length}
          </div>
          <div className="text-sm text-muted-foreground">Entregados</div>
        </div>
      </div>

      {/* Orders List */}
      <div className="space-y-4">
        {filteredOrders.map((order) => (
          <OrderCard 
            key={order.id} 
            order={order}
            onAccept={() => handleAccept(order.id)}
            onReject={() => handleReject(order.id)}
            onStartDelivery={() => handleStartDelivery(order.id)}
            onComplete={() => handleComplete(order.id)}
          />
        ))}
        
        {filteredOrders.length === 0 && (
          <div className="bg-card border border-border rounded-lg p-8 text-center text-muted-foreground">
            No se encontraron pedidos
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

interface OrderCardProps {
  order: WaterOrder;
  onAccept: () => void;
  onReject: () => void;
  onStartDelivery: () => void;
  onComplete: () => void;
}

function OrderCard({ order, onAccept, onReject, onStartDelivery, onComplete }: OrderCardProps) {
  const isPending = order.status === 'pending';
  const isAccepted = order.status === 'accepted';
  const isInTransit = order.status === 'in_transit';

  return (
    <div className={cn(
      "bg-card border rounded-lg p-4 transition-all",
      isPending ? "border-warning/50 shadow-sm" : "border-border"
    )}>
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        {/* Order Info */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-medium text-muted-foreground">#{order.id}</span>
            <StatusBadge status={order.status} />
            {order.subsidyApplied > 0 && (
              <span className="text-xs px-2 py-0.5 bg-success/10 text-success rounded-full">
                Subsidio aplicado
              </span>
            )}
          </div>
          
          <h4 className="font-medium text-lg mb-2">{order.citizenName}</h4>
          
          <div className="grid sm:grid-cols-2 gap-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <MapPin className="h-4 w-4" />
              <span>{order.location.address}, {order.location.colonia}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Phone className="h-4 w-4" />
              <span>{order.citizenPhone}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Clock className="h-4 w-4" />
              <span>{formatDistanceToNow(order.createdAt, { addSuffix: true, locale: es })}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Truck className="h-4 w-4" />
              <span>{(order.quantity / 1000).toFixed(0)},000 litros</span>
            </div>
          </div>
        </div>

        {/* Price and Actions */}
        <div className="sm:text-right">
          <div className="text-2xl font-semibold mb-1">
            ${order.totalPrice.toLocaleString()}
          </div>
          {order.subsidyApplied > 0 && (
            <div className="text-sm text-success mb-3">
              -${order.subsidyApplied} subsidio
            </div>
          )}
          
          <div className="flex gap-2 sm:justify-end">
            {isPending && (
              <>
                <Button size="sm" onClick={onAccept} className="gap-1">
                  <Check className="h-4 w-4" />
                  Aceptar
                </Button>
                <Button size="sm" variant="outline" onClick={onReject} className="gap-1">
                  <X className="h-4 w-4" />
                  Rechazar
                </Button>
              </>
            )}
            {isAccepted && (
              <Button size="sm" onClick={onStartDelivery} className="gap-1">
                <Truck className="h-4 w-4" />
                Iniciar Entrega
              </Button>
            )}
            {isInTransit && (
              <Button size="sm" onClick={onComplete} className="gap-1">
                <Check className="h-4 w-4" />
                Completar
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
