import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api';

interface TimeSeriesData {
  timestamp: string;
  value: number;
}

interface User {
  id: string;
  name: string;
  email: string;
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

class ApiClient {
  private api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  constructor() {
    this.api.interceptors.response.use(
      (response) => {
        return response.data;
      },
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  async getTimeSeriesData(deviceId: string, metric: string, timeRange: string): Promise<TimeSeriesData[]> {
    try {
      const response = await this.api.get(`/devices/${deviceId}/timeseries?metric=${metric}&timeRange=${timeRange}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching ${metric} data for device ${deviceId}:`, error);
      throw error;
    }
  }

  async getMultipleTimeSeriesData(deviceId: string, metrics: string[], timeRange: string): Promise<{ [metric: string]: TimeSeriesData[] }> {
    try {
      const response = await this.api.get(`/devices/${deviceId}/timeseries/multiple`, {
        params: {
          metrics: metrics.join(','),
          timeRange: timeRange
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching multiple time series data for device ${deviceId}:`, error);
      throw error;
    }
  }

  async login(credentials: { email: string; password: string }): Promise<{ user: User; token: string }> {
    try {
      const response = await this.api.post('/auth/login', credentials);
      return response.data; // Fixed: explicitly access .data
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  async register(userData: { name: string; email: string; password: string }): Promise<{ user: User; token: string }> {
    try {
      const response = await this.api.post('/auth/register', userData);
      return response.data; // Fixed: explicitly access .data
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/auth/logout');
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  }

  async getPlants() {
    // HARDCODED SAMPLE DATA - Replace with real API call in production
    return [
      {
        id: 'plant-1',
        name: 'Solar Farm Alpha',
        location: 'California, USA',
        totalCapacity: 5000,
        currentGeneration: 3850,
        efficiency: 92,
        deviceCount: 24,
        status: 'online',
        lastUpdate: new Date()
      },
      {
        id: 'plant-2',
        name: 'Industrial Complex Beta',
        location: 'Arizona, USA',
        totalCapacity: 3200,
        currentGeneration: 2100,
        efficiency: 87,
        deviceCount: 18,
        status: 'online',
        lastUpdate: new Date()
      },
      {
        id: 'plant-3',
        name: 'Residential Grid Gamma',
        location: 'Nevada, USA',
        totalCapacity: 1500,
        currentGeneration: 0,
        efficiency: 0,
        deviceCount: 8,
        status: 'offline',
        lastUpdate: new Date()
      },
      {
        id: 'plant-4',
        name: 'Commercial Center Delta',
        location: 'Texas, USA',
        totalCapacity: 2800,
        currentGeneration: 1950,
        efficiency: 78,
        deviceCount: 15,
        status: 'maintenance',
        lastUpdate: new Date()
      }
    ];
  }

  async getDevices() {
    // HARDCODED SAMPLE DATA - Replace with real API call in production
    return [
      // Plant 1 devices
      {
        id: 'device-1',
        plantId: 'plant-1',
        name: 'Inverter A1',
        type: 'inverter',
        status: 'online',
        currentOutput: 245.5,
        efficiency: 94,
        lastUpdate: new Date()
      },
      {
        id: 'device-2',
        plantId: 'plant-1',
        name: 'Panel Array B1',
        type: 'panel',
        status: 'online',
        currentOutput: 185.2,
        efficiency: 91,
        lastUpdate: new Date()
      },
      {
        id: 'device-3',
        plantId: 'plant-1',
        name: 'Meter C1',
        type: 'meter',
        status: 'online',
        currentOutput: 0,
        efficiency: 100,
        lastUpdate: new Date()
      },
      // Plant 2 devices
      {
        id: 'device-4',
        plantId: 'plant-2',
        name: 'Inverter A2',
        type: 'inverter',
        status: 'online',
        currentOutput: 155.8,
        efficiency: 89,
        lastUpdate: new Date()
      },
      {
        id: 'device-5',
        plantId: 'plant-2',
        name: 'Panel Array B2',
        type: 'panel',
        status: 'warning',
        currentOutput: 120.3,
        efficiency: 82,
        lastUpdate: new Date()
      },
      {
        id: 'device-6',
        plantId: 'plant-2',
        name: 'Meter C2',
        type: 'meter',
        status: 'online',
        currentOutput: 0,
        efficiency: 100,
        lastUpdate: new Date()
      },
      // Plant 3 devices (offline)
      {
        id: 'device-7',
        plantId: 'plant-3',
        name: 'Inverter A3',
        type: 'inverter',
        status: 'offline',
        currentOutput: 0,
        efficiency: 0,
        lastUpdate: new Date()
      },
      {
        id: 'device-8',
        plantId: 'plant-3',
        name: 'Panel Array B3',
        type: 'panel',
        status: 'offline',
        currentOutput: 0,
        efficiency: 0,
        lastUpdate: new Date()
      },
      // Plant 4 devices (maintenance)
      {
        id: 'device-9',
        plantId: 'plant-4',
        name: 'Inverter A4',
        type: 'inverter',
        status: 'fault',
        currentOutput: 0,
        efficiency: 0,
        lastUpdate: new Date()
      },
      {
        id: 'device-10',
        plantId: 'plant-4',
        name: 'Panel Array B4',
        type: 'panel',
        status: 'maintenance',
        currentOutput: 95.2,
        efficiency: 65,
        lastUpdate: new Date()
      },
      // Additional devices for variety
      {
        id: 'device-11',
        plantId: 'plant-1',
        name: 'Inverter D1',
        type: 'inverter',
        status: 'online',
        currentOutput: 220.1,
        efficiency: 93,
        lastUpdate: new Date()
      },
      {
        id: 'device-12',
        plantId: 'plant-2',
        name: 'Panel Array E2',
        type: 'panel',
        status: 'online',
        currentOutput: 165.7,
        efficiency: 88,
        lastUpdate: new Date()
      }
    ];
  }
}

export const apiClient = new ApiClient();
