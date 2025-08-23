
export interface Device {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'offline' | 'warning';
  location: string;
  lastMaintenance: string;
  capacity?: number;
  efficiency?: number;
  manufacturer?: string;
  model?: string;
  serialNumber?: string;
  installDate?: string;
  // Additional properties for PlantsOverview compatibility
  plantId?: string;
  currentOutput?: number;
  lastUpdate?: Date;
}

export type TimeRange = '1h' | '24h' | '7d' | '30d';
