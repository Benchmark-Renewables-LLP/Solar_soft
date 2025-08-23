import axios from 'axios';

const API_BASE_URL = import.meta.env.MODE === 'development' ? 'http://localhost:5000/api' : 'http://localhost:5000/api';

interface TimeSeriesData {
    timestamp: string;
    value: number;
}

interface User {
    id: string;
    username: string;
    fullname: string;
    email?: string;
}

interface AuthResponse {
    token: string;
    user: User;
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
                console.log('API Response:', response.data);
                return response.data;
            },
            (error) => {
                console.error('API Error:', error.message, error.response?.data || error);
                return Promise.reject(error);
            }
        );
    }

    async register(userData: { username: string; fullname: string; password: string; confirmPassword: string; isInstaller: boolean }): Promise<AuthResponse> {
        console.log('Register payload:', userData);
        try {
            const response = await this.api.post('/auth/register', userData);
            // Return mock data for now since backend is not connected
            return {
                token: 'mock-jwt-token',
                user: {
                    id: 'user-' + Date.now(),
                    username: userData.username,
                    fullname: userData.fullname,
                    email: userData.username === 'admin' ? 'priyanshu.uchat@gmail.com' : undefined
                }
            };
        } catch (error: any) {
            console.error('Registration failed:', error.message, error.response?.data || error);
            throw error;
        }
    }

    async login(credentials: { username: string; password: string; isInstaller: boolean }): Promise<AuthResponse> {
        console.log('Login payload:', credentials);
        try {
            const response = await this.api.post('/auth/login', credentials);
            // Return mock data for now since backend is not connected
            return {
                token: 'mock-jwt-token',
                user: {
                    id: 'user-' + Date.now(),
                    username: credentials.username,
                    fullname: credentials.username === 'admin' ? 'Priyanshu Uchat' : 
                             credentials.username === 'demo' ? 'Demo User' : 'User',
                    email: credentials.username === 'admin' ? 'priyanshu.uchat@gmail.com' : undefined
                }
            };
        } catch (error: any) {
            console.error('Login failed:', error.message, error.response?.data || error);
            throw error;
        }
    }

    async logout(): Promise<void> {
        try {
            await this.api.post('/auth/logout');
        } catch (error: any) {
            console.error('Logout failed:', error.message, error.response?.data || error);
            throw error;
        }
    }

    async getPlants(userType = 'demo') {
        try {
            const response = await this.api.get('/plants');
            return response.data;
        } catch (error: any) {
            console.error('Error fetching plants:', error.message, error.response?.data || error);
            console.log('User type for plants:', userType);
            
            // Return different plants based on user type with Indian locations
            if (userType === 'demo') {
                // Demo user sees only one plant
                return [
                    {
                        id: 'plant-1',
                        name: 'Rajasthan Solar Park',
                        location: 'Jodhpur, Rajasthan',
                        totalCapacity: 100,
                        currentGeneration: 85.2,
                        efficiency: 85,
                        deviceCount: 2,
                        status: 'online',
                        lastUpdate: new Date()
                    }
                ];
            } else {
                // Admin sees all plants with Indian locations
                return [
                    {
                        id: 'plant-1',
                        name: 'Gujarat Solar Farm',
                        location: 'Gandhinagar, Gujarat',
                        totalCapacity: 500,
                        currentGeneration: 425.8,
                        efficiency: 85,
                        deviceCount: 12,
                        status: 'online',
                        lastUpdate: new Date()
                    },
                    {
                        id: 'plant-2',
                        name: 'Thar Desert Power Station',
                        location: 'Jaisalmer, Rajasthan',
                        totalCapacity: 750,
                        currentGeneration: 680.2,
                        efficiency: 91,
                        deviceCount: 18,
                        status: 'online',
                        lastUpdate: new Date()
                    },
                    {
                        id: 'plant-3',
                        name: 'Karnataka Solar Valley',
                        location: 'Tumkur, Karnataka',
                        totalCapacity: 300,
                        currentGeneration: 0,
                        efficiency: 0,
                        deviceCount: 8,
                        status: 'maintenance',
                        lastUpdate: new Date()
                    },
                    {
                        id: 'plant-4',
                        name: 'Tamil Nadu Green Energy',
                        location: 'Coimbatore, Tamil Nadu',
                        totalCapacity: 450,
                        currentGeneration: 378.5,
                        efficiency: 84,
                        deviceCount: 15,
                        status: 'online',
                        lastUpdate: new Date()
                    },
                    {
                        id: 'plant-5',
                        name: 'Maharashtra Solar Hub',
                        location: 'Pune, Maharashtra',
                        totalCapacity: 600,
                        currentGeneration: 520.3,
                        efficiency: 87,
                        deviceCount: 20,
                        status: 'online',
                        lastUpdate: new Date()
                    }
                ];
            }
        }
    }

    async getDevices(userType = 'demo') {
        try {
            const response = await this.api.get('/devices');
            return response.data;
        } catch (error: any) {
            console.error('Error fetching devices:', error.message, error.response?.data || error);
            console.log('User type for devices:', userType);
            
            // Return different devices based on user type
            if (userType === 'demo') {
                // Demo user sees only 2 devices
                return [
                    { 
                        id: 'dev-1', 
                        plantId: 'plant-1', 
                        name: 'Solar Inverter RJ-01', 
                        type: 'inverter', 
                        status: 'online', 
                        currentOutput: 45.2, 
                        efficiency: 89, 
                        capacity: 50.0,
                        location: 'Block A',
                        lastMaintenance: '2024-01-15',
                        lastUpdate: new Date() 
                    },
                    { 
                        id: 'dev-2', 
                        plantId: 'plant-1', 
                        name: 'Panel Array RJ-B1', 
                        type: 'panel', 
                        status: 'online', 
                        currentOutput: 40.0, 
                        efficiency: 92, 
                        capacity: 45.0,
                        location: 'Block B',
                        lastMaintenance: '2024-01-10',
                        lastUpdate: new Date() 
                    }
                ];
            } else {
                // Admin has access to all devices across multiple plants
                return [
                    { id: 'dev-1', plantId: 'plant-1', name: 'Inverter GJ-A1 (High Capacity)', type: 'inverter', status: 'online', currentOutput: 85.2, efficiency: 94, location: 'Block A', lastMaintenance: '2024-01-15', lastUpdate: new Date() },
                    { id: 'dev-2', plantId: 'plant-1', name: 'Panel Array GJ-B1 (Premium)', type: 'panel', status: 'online', currentOutput: 78.7, efficiency: 96, location: 'Block B', lastMaintenance: '2024-01-10', lastUpdate: new Date() },
                    { id: 'dev-3', plantId: 'plant-1', name: 'Smart Meter GJ-C1 (Advanced)', type: 'meter', status: 'online', currentOutput: 81.3, efficiency: 93, location: 'Block C', lastMaintenance: '2024-01-20', lastUpdate: new Date() },
                    { id: 'dev-4', plantId: 'plant-1', name: 'Inverter GJ-A2 (Enterprise)', type: 'inverter', status: 'online', currentOutput: 72.1, efficiency: 91, location: 'Block A', lastMaintenance: '2024-01-12', lastUpdate: new Date() },
                    { id: 'dev-5', plantId: 'plant-2', name: 'Inverter RJ-D1 (Industrial)', type: 'inverter', status: 'online', currentOutput: 92.8, efficiency: 97, location: 'Sector D', lastMaintenance: '2024-01-18', lastUpdate: new Date() },
                    { id: 'dev-6', plantId: 'plant-2', name: 'Panel Array RJ-E1 (Mega)', type: 'panel', status: 'online', currentOutput: 88.3, efficiency: 95, location: 'Sector E', lastMaintenance: '2024-01-14', lastUpdate: new Date() },
                    { id: 'dev-7', plantId: 'plant-2', name: 'Smart Meter RJ-F1 (Pro)', type: 'meter', status: 'online', currentOutput: 87.5, efficiency: 96, location: 'Sector F', lastMaintenance: '2024-01-16', lastUpdate: new Date() },
                    { id: 'dev-8', plantId: 'plant-3', name: 'Central Inverter KA-X1', type: 'inverter', status: 'maintenance', currentOutput: 0, efficiency: 0, location: 'Central Hub', lastMaintenance: '2024-01-25', lastUpdate: new Date() },
                    { id: 'dev-9', plantId: 'plant-4', name: 'Solar Tracker TN-Y1', type: 'tracker', status: 'online', currentOutput: 95.5, efficiency: 98, location: 'East Wing', lastMaintenance: '2024-01-08', lastUpdate: new Date() },
                    { id: 'dev-10', plantId: 'plant-4', name: 'Weather Station TN-Z1', type: 'sensor', status: 'online', currentOutput: 0, efficiency: 100, location: 'Weather Hub', lastMaintenance: '2024-01-22', lastUpdate: new Date() },
                    { id: 'dev-11', plantId: 'plant-5', name: 'Inverter MH-P1 (Ultra)', type: 'inverter', status: 'online', currentOutput: 98.2, efficiency: 95, location: 'Main Block', lastMaintenance: '2024-01-05', lastUpdate: new Date() },
                    { id: 'dev-12', plantId: 'plant-5', name: 'Panel Array MH-Q1 (Advanced)', type: 'panel', status: 'online', currentOutput: 89.7, efficiency: 93, location: 'South Wing', lastMaintenance: '2024-01-12', lastUpdate: new Date() }
                ];
            }
        }
    }

    async getMultipleTimeSeriesData(deviceId: string, metrics: string[], timeRange: string): Promise<TimeSeriesData[]> {
        try {
            const response = await this.api.get(`/devices/${deviceId}/timeseries`, {
                params: { metrics: metrics.join(','), timeRange }
            });
            return response.data;
        } catch (error: any) {
            console.error('Error fetching time series data:', error.message, error.response?.data || error);
            // Return mock data for now
            return [];
        }
    }
}

export const apiClient = new ApiClient();
