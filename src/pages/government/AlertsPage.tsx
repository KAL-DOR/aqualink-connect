import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/page-header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Send, 
  Users, 
  Clock,
  CheckCircle2
} from 'lucide-react';
import { mockAlerts } from '@/data/mockData';
import { formatDistanceToNow, format } from 'date-fns';
import { es } from 'date-fns/locale';
import { toast } from 'sonner';

const zones = [
  'Iztapalapa',
  'Gustavo A. Madero',
  'Tláhuac',
  'Coyoacán',
  'Tlalpan',
  'Xochimilco',
  'Milpa Alta',
  'Cuauhtémoc',
];

const alertTypeLabels: Record<string, { label: string; emoji: string }> = {
  shortage: { label: 'Corte de Agua', emoji: '🚱' },
  conservation: { label: 'Conservación', emoji: '💧' },
  program: { label: 'Programa', emoji: '📢' },
  emergency: { label: 'Emergencia', emoji: '🚨' },
};

export default function AlertsPage() {
  const [alertType, setAlertType] = useState<string>('shortage');
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [selectedZones, setSelectedZones] = useState<string[]>([]);
  const [sending, setSending] = useState(false);

  const estimatedRecipients = selectedZones.length * 5000; // Mock calculation

  const handleZoneToggle = (zone: string) => {
    setSelectedZones(prev => 
      prev.includes(zone) 
        ? prev.filter(z => z !== zone)
        : [...prev, zone]
    );
  };

  const handleSelectAll = () => {
    if (selectedZones.length === zones.length) {
      setSelectedZones([]);
    } else {
      setSelectedZones([...zones]);
    }
  };

  const handleSend = async () => {
    if (!title || !message || selectedZones.length === 0) {
      toast.error('Por favor completa todos los campos');
      return;
    }

    setSending(true);
    // Simulate sending
    await new Promise(resolve => setTimeout(resolve, 1500));
    setSending(false);
    
    toast.success(`Alerta enviada a ${estimatedRecipients.toLocaleString()} ciudadanos`);
    setTitle('');
    setMessage('');
    setSelectedZones([]);
  };

  return (
    <DashboardLayout role="government">
      <PageHeader 
        title="Alertas y Comunicación" 
        description="Envía notificaciones a ciudadanos via WhatsApp"
      />

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Send Alert Form */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="font-medium mb-6">Nueva Alerta</h3>
          
          <div className="space-y-5">
            {/* Alert Type */}
            <div className="space-y-2">
              <Label>Tipo de Alerta</Label>
              <Select value={alertType} onValueChange={setAlertType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(alertTypeLabels).map(([key, { label, emoji }]) => (
                    <SelectItem key={key} value={key}>
                      <span className="flex items-center gap-2">
                        <span>{emoji}</span>
                        <span>{label}</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Title */}
            <div className="space-y-2">
              <Label>Título</Label>
              <Input 
                placeholder="Ej: Corte programado de agua"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            {/* Message */}
            <div className="space-y-2">
              <Label>Mensaje</Label>
              <Textarea 
                placeholder="Escribe el mensaje que recibirán los ciudadanos..."
                rows={4}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                {message.length}/500 caracteres
              </p>
            </div>

            {/* Target Zones */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Zonas Destino</Label>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={handleSelectAll}
                  className="text-xs"
                >
                  {selectedZones.length === zones.length ? 'Deseleccionar todo' : 'Seleccionar todo'}
                </Button>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {zones.map((zone) => (
                  <div 
                    key={zone}
                    className="flex items-center gap-2 p-2 rounded-lg border border-border hover:bg-secondary/30 cursor-pointer transition-colors"
                    onClick={() => handleZoneToggle(zone)}
                  >
                    <Checkbox 
                      checked={selectedZones.includes(zone)} 
                      onCheckedChange={() => handleZoneToggle(zone)}
                    />
                    <span className="text-sm">{zone}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recipients Estimate */}
            {selectedZones.length > 0 && (
              <div className="flex items-center gap-2 p-3 bg-secondary/30 rounded-lg">
                <Users className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">
                  Estimado: <span className="font-medium">{estimatedRecipients.toLocaleString()}</span> destinatarios
                </span>
              </div>
            )}

            {/* Send Button */}
            <Button 
              className="w-full gap-2" 
              onClick={handleSend}
              disabled={sending || !title || !message || selectedZones.length === 0}
            >
              {sending ? (
                <>
                  <span className="animate-spin">⏳</span>
                  Enviando...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  Enviar Alerta
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Alert History */}
        <div className="bg-card border border-border rounded-lg">
          <div className="p-4 border-b border-border">
            <h3 className="font-medium">Alertas Enviadas</h3>
          </div>
          <div className="divide-y divide-border">
            {mockAlerts.map((alert) => {
              const typeInfo = alertTypeLabels[alert.type];
              return (
                <div key={alert.id} className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">{typeInfo.emoji}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium truncate">{alert.title}</h4>
                        <CheckCircle2 className="h-4 w-4 text-success shrink-0" />
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                        {alert.message}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Users className="h-3 w-3" />
                          {alert.recipientCount.toLocaleString()} destinatarios
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatDistanceToNow(alert.sentAt, { addSuffix: true, locale: es })}
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {alert.targetZones.map((zone) => (
                          <span 
                            key={zone}
                            className="px-2 py-0.5 bg-secondary text-xs rounded"
                          >
                            {zone}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
