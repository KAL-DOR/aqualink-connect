import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";

// Government Pages
import GovernmentDashboard from "./pages/government/GovernmentDashboard";
import IncidentsPage from "./pages/government/IncidentsPage";
import DemandMapPage from "./pages/government/DemandMapPage";
import AlertsPage from "./pages/government/AlertsPage";

// Company Pages
import CompanyDashboard from "./pages/company/CompanyDashboard";
import OrdersPage from "./pages/company/OrdersPage";
import CompanyDemandPage from "./pages/company/CompanyDemandPage";
import CompanySettingsPage from "./pages/company/CompanySettingsPage";

// Citizen Pages
import CitizenChat from "./pages/citizen/CitizenChat";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          
          {/* Government Routes */}
          <Route path="/government" element={<GovernmentDashboard />} />
          <Route path="/government/incidents" element={<IncidentsPage />} />
          <Route path="/government/demand" element={<DemandMapPage />} />
          <Route path="/government/alerts" element={<AlertsPage />} />
          
          {/* Company Routes */}
          <Route path="/company" element={<CompanyDashboard />} />
          <Route path="/company/orders" element={<OrdersPage />} />
          <Route path="/company/demand" element={<CompanyDemandPage />} />
          <Route path="/company/settings" element={<CompanySettingsPage />} />
          
          {/* Citizen Routes */}
          <Route path="/citizen" element={<CitizenChat />} />
          
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
