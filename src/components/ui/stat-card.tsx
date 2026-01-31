import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: {
    value: number;
    positive: boolean;
  };
  variant?: 'default' | 'accent' | 'warning' | 'success' | 'destructive';
  className?: string;
}

const variantStyles = {
  default: 'bg-card border-border',
  accent: 'bg-accent/10 border-accent/20',
  warning: 'bg-warning/10 border-warning/20',
  success: 'bg-success/10 border-success/20',
  destructive: 'bg-destructive/10 border-destructive/20',
};

const iconStyles = {
  default: 'text-muted-foreground',
  accent: 'text-accent',
  warning: 'text-warning',
  success: 'text-success',
  destructive: 'text-destructive',
};

export function StatCard({ label, value, icon, trend, variant = 'default', className }: StatCardProps) {
  return (
    <div className={cn(
      "rounded-lg border p-5 transition-all hover:shadow-sm",
      variantStyles[variant],
      className
    )}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground mb-1">{label}</p>
          <p className="text-3xl font-semibold tracking-tight">{value}</p>
          {trend && (
            <p className={cn(
              "text-sm mt-1",
              trend.positive ? "text-success" : "text-destructive"
            )}>
              {trend.positive ? '↑' : '↓'} {Math.abs(trend.value)}% vs. semana pasada
            </p>
          )}
        </div>
        {icon && (
          <div className={cn("p-2 rounded-lg bg-secondary/50", iconStyles[variant])}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
