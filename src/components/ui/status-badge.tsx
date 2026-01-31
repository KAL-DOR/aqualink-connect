import { cn } from '@/lib/utils';

type Status = 'pending' | 'acknowledged' | 'in_progress' | 'resolved' | 'accepted' | 'in_transit' | 'delivered' | 'cancelled';

interface StatusBadgeProps {
  status: Status;
  className?: string;
}

const statusConfig: Record<Status, { label: string; className: string }> = {
  pending: { 
    label: 'Pendiente', 
    className: 'bg-warning/10 text-warning border-warning/20' 
  },
  acknowledged: { 
    label: 'Recibido', 
    className: 'bg-water/10 text-water border-water/20' 
  },
  in_progress: { 
    label: 'En Proceso', 
    className: 'bg-accent/10 text-accent border-accent/20' 
  },
  resolved: { 
    label: 'Resuelto', 
    className: 'bg-success/10 text-success border-success/20' 
  },
  accepted: { 
    label: 'Aceptado', 
    className: 'bg-water/10 text-water border-water/20' 
  },
  in_transit: { 
    label: 'En Camino', 
    className: 'bg-accent/10 text-accent border-accent/20' 
  },
  delivered: { 
    label: 'Entregado', 
    className: 'bg-success/10 text-success border-success/20' 
  },
  cancelled: { 
    label: 'Cancelado', 
    className: 'bg-destructive/10 text-destructive border-destructive/20' 
  },
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status];
  
  return (
    <span className={cn(
      "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
      config.className,
      className
    )}>
      <span className={cn(
        "w-1.5 h-1.5 rounded-full mr-1.5",
        status === 'pending' && "bg-warning",
        status === 'acknowledged' && "bg-water",
        status === 'in_progress' && "bg-accent",
        status === 'resolved' && "bg-success",
        status === 'accepted' && "bg-water",
        status === 'in_transit' && "bg-accent",
        status === 'delivered' && "bg-success",
        status === 'cancelled' && "bg-destructive"
      )} />
      {config.label}
    </span>
  );
}
