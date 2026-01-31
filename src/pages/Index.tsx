import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Droplets, Building2, Truck, MessageCircle, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function Index() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Droplets className="h-7 w-7 text-water" />
            <span className="font-semibold text-lg">AquaHub</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link to="/citizen" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Ciudadanos
            </Link>
            <Link to="/government" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Gobierno
            </Link>
            <Link to="/company" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Empresas
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="py-20 lg:py-32">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-water/10 text-water rounded-full text-sm mb-6">
              <Droplets className="h-4 w-4" />
              Plataforma Unificada de Servicios de Agua
            </div>
            <h1 className="text-4xl lg:text-6xl font-semibold tracking-tight mb-6 max-w-3xl mx-auto">
              Conectando agua con quienes la necesitan
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
              AquaHub conecta gobiernos, ciudadanos y distribuidores de agua para crear una respuesta coordinada a la escasez hídrica en México.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link to="/citizen">
                <Button size="lg" className="gap-2">
                  <MessageCircle className="h-5 w-5" />
                  Probar WhatsApp Bot
                </Button>
              </Link>
              <Link to="/government">
                <Button size="lg" variant="outline" className="gap-2">
                  Ver Dashboard
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Portals */}
      <section className="py-16 bg-secondary/30">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl font-semibold text-center mb-12">Tres Portales, Una Plataforma</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <PortalCard
              icon={<Building2 className="h-8 w-8" />}
              title="Gobierno"
              description="Monitorea incidentes, gestiona subsidios y envía alertas a la población."
              href="/government"
              color="primary"
            />
            <PortalCard
              icon={<MessageCircle className="h-8 w-8" />}
              title="Ciudadanos"
              description="Pide agua, reporta problemas y recibe alertas via WhatsApp."
              href="/citizen"
              color="water"
            />
            <PortalCard
              icon={<Truck className="h-8 w-8" />}
              title="Empresas"
              description="Visualiza demanda, gestiona pedidos y optimiza rutas."
              href="/company"
              color="accent"
            />
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-semibold text-water">1,247</div>
              <div className="text-muted-foreground">Solicitudes Hoy</div>
            </div>
            <div>
              <div className="text-4xl font-semibold text-success">23</div>
              <div className="text-muted-foreground">Pipas Activas</div>
            </div>
            <div>
              <div className="text-4xl font-semibold text-warning">12</div>
              <div className="text-muted-foreground">Incidentes Pendientes</div>
            </div>
            <div>
              <div className="text-4xl font-semibold text-accent">$342k</div>
              <div className="text-muted-foreground">Subsidios Distribuidos</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>AquaHub — Hackathon RtSH Mexico City 2026</p>
        </div>
      </footer>
    </div>
  );
}

interface PortalCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  href: string;
  color: 'primary' | 'water' | 'accent';
}

function PortalCard({ icon, title, description, href, color }: PortalCardProps) {
  const colorClasses = {
    primary: 'group-hover:bg-primary group-hover:text-primary-foreground',
    water: 'group-hover:bg-water group-hover:text-water-foreground',
    accent: 'group-hover:bg-accent group-hover:text-accent-foreground',
  };

  return (
    <Link to={href} className="group">
      <div className="bg-card border border-border rounded-lg p-6 h-full transition-all hover:shadow-lg hover:border-primary/30">
        <div className={`w-14 h-14 rounded-lg bg-secondary flex items-center justify-center mb-4 transition-colors ${colorClasses[color]}`}>
          {icon}
        </div>
        <h3 className="text-lg font-medium mb-2">{title}</h3>
        <p className="text-muted-foreground text-sm">{description}</p>
        <div className="mt-4 flex items-center gap-1 text-sm font-medium text-primary opacity-0 group-hover:opacity-100 transition-opacity">
          Acceder <ArrowRight className="h-4 w-4" />
        </div>
      </div>
    </Link>
  );
}
