import { ReactNode, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Droplets, 
  LayoutDashboard, 
  AlertTriangle, 
  Truck, 
  Send, 
  BarChart3, 
  Settings,
  MessageCircle,
  Menu,
  X,
  Building2,
  Users
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { UserRole } from '@/types';

interface NavItem {
  label: string;
  href: string;
  icon: ReactNode;
}

const governmentNav: NavItem[] = [
  { label: 'Dashboard', href: '/government', icon: <LayoutDashboard className="h-5 w-5" /> },
  { label: 'Incidentes', href: '/government/incidents', icon: <AlertTriangle className="h-5 w-5" /> },
  { label: 'Mapa de Demanda', href: '/government/demand', icon: <BarChart3 className="h-5 w-5" /> },
  { label: 'Alertas', href: '/government/alerts', icon: <Send className="h-5 w-5" /> },
];

const companyNav: NavItem[] = [
  { label: 'Dashboard', href: '/company', icon: <LayoutDashboard className="h-5 w-5" /> },
  { label: 'Pedidos', href: '/company/orders', icon: <Truck className="h-5 w-5" /> },
  { label: 'Mapa de Demanda', href: '/company/demand', icon: <BarChart3 className="h-5 w-5" /> },
  { label: 'Configuración', href: '/company/settings', icon: <Settings className="h-5 w-5" /> },
];

interface DashboardLayoutProps {
  children: ReactNode;
  role: UserRole;
}

export function DashboardLayout({ children, role }: DashboardLayoutProps) {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const navItems = role === 'government' ? governmentNav : companyNav;
  const roleLabel = role === 'government' ? 'Gobierno' : 'Empresa';
  const roleIcon = role === 'government' ? <Building2 className="h-5 w-5" /> : <Truck className="h-5 w-5" />;

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile header */}
      <header className="lg:hidden fixed top-0 left-0 right-0 z-50 h-16 border-b border-border bg-card flex items-center px-4">
        <button 
          onClick={() => setSidebarOpen(true)}
          className="p-2 hover:bg-secondary rounded-lg"
        >
          <Menu className="h-6 w-6" />
        </button>
        <div className="flex items-center gap-2 ml-4">
          <Droplets className="h-6 w-6 text-water" />
          <span className="font-semibold">AquaHub</span>
        </div>
      </header>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="lg:hidden fixed inset-0 z-50 bg-foreground/20"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={cn(
        "fixed top-0 left-0 z-50 h-full w-64 bg-sidebar text-sidebar-foreground flex flex-col transition-transform duration-300 lg:translate-x-0",
        sidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-sidebar-border">
          <Link to="/" className="flex items-center gap-2">
            <Droplets className="h-7 w-7 text-sidebar-primary" />
            <span className="font-semibold text-lg">AquaHub</span>
          </Link>
          <button 
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 hover:bg-sidebar-accent rounded-lg"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Role indicator */}
        <div className="px-4 py-3 border-b border-sidebar-border">
          <div className="flex items-center gap-2 text-sm text-sidebar-foreground/70">
            {roleIcon}
            <span>{roleLabel}</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.href}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive 
                    ? "bg-sidebar-primary text-sidebar-primary-foreground" 
                    : "text-sidebar-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                )}
              >
                {item.icon}
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Citizen Bot Link */}
        <div className="p-4 border-t border-sidebar-border">
          <Link
            to="/citizen"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium bg-sidebar-accent text-sidebar-accent-foreground hover:bg-sidebar-primary hover:text-sidebar-primary-foreground transition-colors"
          >
            <MessageCircle className="h-5 w-5" />
            WhatsApp Simulator
          </Link>
        </div>

        {/* Portal switcher */}
        <div className="p-4 border-t border-sidebar-border">
          <div className="text-xs uppercase tracking-wider text-sidebar-foreground/50 mb-2">
            Cambiar portal
          </div>
          <div className="space-y-1">
            <Link
              to="/government"
              className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors",
                role === 'government' 
                  ? "bg-sidebar-accent text-sidebar-accent-foreground" 
                  : "text-sidebar-foreground/60 hover:text-sidebar-foreground"
              )}
            >
              <Building2 className="h-4 w-4" />
              Gobierno
            </Link>
            <Link
              to="/company"
              className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors",
                role === 'company' 
                  ? "bg-sidebar-accent text-sidebar-accent-foreground" 
                  : "text-sidebar-foreground/60 hover:text-sidebar-foreground"
              )}
            >
              <Truck className="h-4 w-4" />
              Empresa
            </Link>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className={cn(
        "min-h-screen pt-16 lg:pt-0 lg:pl-64 transition-all"
      )}>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="p-4 lg:p-8"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
