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
  Users,
  Clock,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { mockIncidents } from '@/data/mockData';
import { IncidentReport } from '@/types';
import { formatDistanceToNow, format } from 'date-fns';
import { es } from 'date-fns/locale';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

const incidentTypeLabels: Record<string, string> = {
  leak: 'Fuga de Agua',
  no_water: 'Sin Suministro',
  contamination: 'Agua Contaminada',
  infrastructure: 'Daño a Infraestructura',
  other: 'Otro',
};

const incidentTypeIcons: Record<string, string> = {
  leak: '💧',
  no_water: '🚱',
  contamination: '⚠️',
  infrastructure: '🔧',
  other: '📋',
};

const durationLabels: Record<string, string> = {
  '1_day': 'Menos de 1 día',
  '1_3_days': '1-3 días',
  '3_plus_days': 'Más de 3 días',
};

export default function IncidentsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [selectedIncident, setSelectedIncident] = useState<IncidentReport | null>(null);

  const filteredIncidents = mockIncidents.filter(incident => {
    const matchesSearch = 
      incident.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      incident.location.colonia?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      incident.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || incident.status === statusFilter;
    const matchesType = typeFilter === 'all' || incident.type === typeFilter;

    return matchesSearch && matchesStatus && matchesType;
  });

  return (
    <DashboardLayout role="government">
      <PageHeader 
        title="Incidentes Reportados" 
        description="Gestión y seguimiento de reportes ciudadanos"
      />

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por ID, colonia o descripción..."
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
            <SelectItem value="acknowledged">Recibido</SelectItem>
            <SelectItem value="in_progress">En Proceso</SelectItem>
            <SelectItem value="resolved">Resuelto</SelectItem>
          </SelectContent>
        </Select>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="Tipo" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos los tipos</SelectItem>
            <SelectItem value="leak">Fuga</SelectItem>
            <SelectItem value="no_water">Sin Agua</SelectItem>
            <SelectItem value="contamination">Contaminación</SelectItem>
            <SelectItem value="infrastructure">Infraestructura</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div className="bg-card border border-border rounded-lg p-3">
          <div className="text-2xl font-semibold">{mockIncidents.filter(i => i.status === 'pending').length}</div>
          <div className="text-sm text-muted-foreground">Pendientes</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-3">
          <div className="text-2xl font-semibold">{mockIncidents.filter(i => i.status === 'in_progress').length}</div>
          <div className="text-sm text-muted-foreground">En Proceso</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-3">
          <div className="text-2xl font-semibold">{mockIncidents.filter(i => i.type === 'no_water').length}</div>
          <div className="text-sm text-muted-foreground">Sin Agua</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-3">
          <div className="text-2xl font-semibold">{mockIncidents.reduce((acc, i) => acc + i.affectedHouseholds, 0)}</div>
          <div className="text-sm text-muted-foreground">Viviendas Afectadas</div>
        </div>
      </div>

      {/* Incidents List */}
      <div className="bg-card border border-border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead className="bg-secondary/30">
              <tr>
                <th>ID / Tipo</th>
                <th>Ubicación</th>
                <th>Afectados</th>
                <th>Duración</th>
                <th>Estado</th>
                <th>Reportado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filteredIncidents.map((incident) => (
                <tr 
                  key={incident.id} 
                  className="hover:bg-secondary/20 cursor-pointer transition-colors"
                  onClick={() => setSelectedIncident(incident)}
                >
                  <td>
                    <div className="flex items-center gap-2">
                      <span className="text-xl">{incidentTypeIcons[incident.type]}</span>
                      <div>
                        <div className="font-medium">#{incident.id}</div>
                        <div className="text-xs text-muted-foreground">
                          {incidentTypeLabels[incident.type]}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center gap-1.5">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <span>{incident.location.colonia}, {incident.location.municipality}</span>
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center gap-1.5">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span>{incident.affectedHouseholds} viviendas</span>
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center gap-1.5">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span>{durationLabels[incident.duration]}</span>
                    </div>
                  </td>
                  <td>
                    <StatusBadge status={incident.status} />
                  </td>
                  <td className="text-muted-foreground">
                    {formatDistanceToNow(incident.createdAt, { addSuffix: true, locale: es })}
                  </td>
                  <td>
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Incident Detail Modal */}
      <Dialog open={!!selectedIncident} onOpenChange={() => setSelectedIncident(null)}>
        <DialogContent className="max-w-lg">
          {selectedIncident && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <span className="text-2xl">{incidentTypeIcons[selectedIncident.type]}</span>
                  Reporte #{selectedIncident.id}
                </DialogTitle>
              </DialogHeader>

              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <StatusBadge status={selectedIncident.status} />
                  <span className="text-sm text-muted-foreground">
                    {incidentTypeLabels[selectedIncident.type]}
                  </span>
                </div>

                <div className="bg-secondary/30 rounded-lg p-4">
                  <p className="text-sm">{selectedIncident.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-muted-foreground mb-1">Ubicación</div>
                    <div className="font-medium flex items-start gap-1">
                      <MapPin className="h-4 w-4 mt-0.5" />
                      {selectedIncident.location.colonia}, {selectedIncident.location.municipality}
                    </div>
                  </div>
                  <div>
                    <div className="text-muted-foreground mb-1">Viviendas Afectadas</div>
                    <div className="font-medium">{selectedIncident.affectedHouseholds}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground mb-1">Duración</div>
                    <div className="font-medium">{durationLabels[selectedIncident.duration]}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground mb-1">Reportado</div>
                    <div className="font-medium">
                      {format(selectedIncident.createdAt, "d MMM yyyy, HH:mm", { locale: es })}
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 pt-4 border-t border-border">
                  <Button className="flex-1">
                    Actualizar Estado
                  </Button>
                  <Button variant="outline" className="gap-1">
                    <ExternalLink className="h-4 w-4" />
                    Ver en Mapa
                  </Button>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
