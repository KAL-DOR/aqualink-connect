// Core data types for AquaHub platform

export interface Location {
  lat: number;
  lng: number;
  address?: string;
  colonia?: string;
  municipality?: string;
}

export interface PipaProvider {
  id: string;
  name: string;
  rating: number;
  pricePerLiter: number; // MXN per 10,000L
  estimatedArrival: number; // minutes
  location: Location;
  fleetSize: number;
  available: boolean;
  certifications: string[];
  phone: string;
}

export interface WaterOrder {
  id: string;
  providerId: string;
  providerName: string;
  citizenName: string;
  citizenPhone: string;
  location: Location;
  quantity: number; // liters
  totalPrice: number;
  subsidyApplied: number;
  status: 'pending' | 'accepted' | 'in_transit' | 'delivered' | 'cancelled';
  createdAt: Date;
  estimatedDelivery?: Date;
  deliveredAt?: Date;
}

export interface IncidentReport {
  id: string;
  type: 'leak' | 'no_water' | 'contamination' | 'infrastructure' | 'other';
  location: Location;
  description: string;
  affectedHouseholds: number;
  duration: '1_day' | '1_3_days' | '3_plus_days';
  status: 'pending' | 'acknowledged' | 'in_progress' | 'resolved';
  reporterPhone: string;
  createdAt: Date;
  updatedAt: Date;
  photoUrl?: string;
}

export interface DemandPoint {
  id: string;
  location: Location;
  intensity: 'low' | 'medium' | 'high' | 'critical';
  requestCount: number;
  timestamp: Date;
}

export interface BroadcastAlert {
  id: string;
  title: string;
  message: string;
  targetZones: string[];
  sentAt: Date;
  recipientCount: number;
  type: 'shortage' | 'conservation' | 'program' | 'emergency';
}

export interface SubsidyProgram {
  id: string;
  name: string;
  budget: number;
  spent: number;
  beneficiaries: number;
  discountPercentage: number;
  eligibilityCriteria: string;
  active: boolean;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'bot';
  content: string;
  timestamp: Date;
  options?: ChatOption[];
}

export interface ChatOption {
  id: string;
  label: string;
  value: string;
}

export interface CompanyStats {
  totalOrders: number;
  activeOrders: number;
  revenue: number;
  averageRating: number;
  deliveriesThisWeek: number;
}

export interface GovernmentStats {
  activeIncidents: number;
  totalRequests: number;
  subsidiesDistributed: number;
  waterSaved: number; // liters
  responseTime: number; // average hours
}

export type UserRole = 'government' | 'company' | 'citizen';
