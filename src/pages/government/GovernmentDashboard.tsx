import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/page-header';
import { StatCard } from '@/components/ui/stat-card';
import { StatusBadge } from '@/components/ui/status-badge';
import { Button } from '@/components/ui/button';
import { 
  AlertTriangle, 
  Droplets, 
  DollarSign, 
  Clock, 
  TrendingUp,
  ArrowRight
} from 'lucide-react';
import { mockGovernmentStats, mockIncidents, droughtData } from '@/data/mockData';
import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

const incidentTypeLabels: Record<string, string> = {
  leak: 'Fuga',
  no_water: 'Sin Agua',
  contamination: 'Contaminación',
  infrastructure: 'Infraestructura',
  other: 'Otro',
};

export default function GovernmentDashboard() {
  const recentIncidents = mockIncidents.slice(0, 4);

  return (
    <DashboardLayout role="government">
      <PageHeader 
        title="Dashboard de Gobierno" 
        description="Monitoreo de servicios de agua y gestión de incidentes"
      />

      {/* Drought Alert Banner */}
      <div className="mb-6 p-4 rounded-lg border border-warning/30 bg-warning/5 flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-warning shrink-0 mt-0.5" />
        <div>
          <h4 className="font-medium text-foreground">Alerta de Sequía: Nivel Severo</h4>
          <p className="text-sm text-muted-foreground mt-1">
            Índice SPI: {droughtData.spiIndex} | Nivel de presas: {droughtData.reservoirLevel}%
          </p>
          <p className="text-sm text-muted-foreground">
            {droughtData.forecast}
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard 
          label="Incidentes Activos"
          value={mockGovernmentStats.activeIncidents}
          icon={<AlertTriangle className="h-5 w-5" />}
          variant="warning"
          trend={{ value: 8, positive: false }}
        />
        <StatCard 
          label="Solicitudes Hoy"
          value={mockGovernmentStats.totalRequests}
          icon={<Droplets className="h-5 w-5" />}
          variant="accent"
          trend={{ value: 12, positive: true }}
        />
        <StatCard 
          label="Subsidios Distribuidos"
          value={`$${(mockGovernmentStats.subsidiesDistributed / 1000).toFixed(0)}k`}
          icon={<DollarSign className="h-5 w-5" />}
          variant="success"
        />
        <StatCard 
          label="Tiempo de Respuesta"
          value={`${mockGovernmentStats.responseTime}h`}
          icon={<Clock className="h-5 w-5" />}
          trend={{ value: 15, positive: true }}
        />
      </div>

      {/* Two Column Layout */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent Incidents */}
        <div className="bg-card border border-border rounded-lg">
          <div className="p-4 border-b border-border flex items-center justify-between">
            <h3 className="font-medium">Incidentes Recientes</h3>
            <Link to="/government/incidents">
              <Button variant="ghost" size="sm" className="gap-1">
                Ver todos <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          <div className="divide-y divide-border">
            {recentIncidents.map((incident) => (
              <div key={incident.id} className="p-4 hover:bg-secondary/30 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-muted-foreground">
                        #{incident.id}
                      </span>
                      <StatusBadge status={incident.status} />
                    </div>
                    <p className="font-medium truncate">
                      {incidentTypeLabels[incident.type]} - {incident.location.colonia}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-1">
                      {incident.description}
                    </p>
                  </div>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {formatDistanceToNow(incident.createdAt, { addSuffix: true, locale: es })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Demand Overview */}
        <div className="bg-card border border-border rounded-lg">
          <div className="p-4 border-b border-border flex items-center justify-between">
            <h3 className="font-medium">Demanda por Zona</h3>
            <Link to="/government/demand">
              <Button variant="ghost" size="sm" className="gap-1">
                Ver mapa <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          <div className="p-4 space-y-4">
            <DemandBar zone="Iztapalapa" requests={247} percentage={85} intensity="critical" />
            <DemandBar zone="Gustavo A. Madero" requests={189} percentage={65} intensity="high" />
            <DemandBar zone="Tláhuac" requests={134} percentage={46} intensity="medium" />
            <DemandBar zone="Coyoacán" requests={98} percentage={34} intensity="medium" />
            <DemandBar zone="Tlalpan" requests={67} percentage={23} intensity="low" />
            <DemandBar zone="Xochimilco" requests={45} percentage={15} intensity="low" />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-6 grid sm:grid-cols-3 gap-4">
        <Link to="/government/alerts" className="block">
          <div className="p-4 bg-card border border-border rounded-lg hover:border-primary/50 transition-colors group">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10 text-primary">
                <TrendingUp className="h-5 w-5" />
              </div>
              <div>
                <h4 className="font-medium group-hover:text-primary transition-colors">Enviar Alerta</h4>
                <p className="text-sm text-muted-foreground">Comunicar a ciudadanos</p>
              </div>
            </div>
          </div>
        </Link>
        <Link to="/government/incidents" className="block">
          <div className="p-4 bg-card border border-border rounded-lg hover:border-primary/50 transition-colors group">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-warning/10 text-warning">
                <AlertTriangle className="h-5 w-5" />
              </div>
              <div>
                <h4 className="font-medium group-hover:text-primary transition-colors">Ver Incidentes</h4>
                <p className="text-sm text-muted-foreground">12 pendientes de revisión</p>
              </div>
            </div>
          </div>
        </Link>
        <Link to="/government/demand" className="block">
          <div className="p-4 bg-card border border-border rounded-lg hover:border-primary/50 transition-colors group">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-accent/10 text-accent">
                <Droplets className="h-5 w-5" />
              </div>
              <div>
                <h4 className="font-medium group-hover:text-primary transition-colors">Mapa de Demanda</h4>
                <p className="text-sm text-muted-foreground">Visualizar en tiempo real</p>
              </div>
            </div>
          </div>
        </Link>
      </div>
    </DashboardLayout>
  );
}

interface DemandBarProps {
  zone: string;
  requests: number;
  percentage: number;
  intensity: 'low' | 'medium' | 'high' | 'critical';
}

function DemandBar({ zone, requests, percentage, intensity }: DemandBarProps) {
  const intensityColors = {
    low: 'bg-success',
    medium: 'bg-warning',
    high: 'bg-orange-500',
    critical: 'bg-destructive',
  };

  return (
    <div>
      <div className="flex items-center justify-between text-sm mb-1.5">
        <span className="font-medium">{zone}</span>
        <span className="text-muted-foreground">{requests} solicitudes</span>
      </div>
      <div className="h-2 bg-secondary rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full transition-all ${intensityColors[intensity]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
