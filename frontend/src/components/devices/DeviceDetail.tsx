import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, AlertTriangle, Wifi, WifiOff, Activity, Thermometer, Zap, Gauge, Calendar, Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { DynamicChart } from './DynamicChart';
import { TimeRangeSelector } from './TimeRangeSelector';
import { EnergyMeter } from '@/components/ui/energy-meter';

export type TimeRange = '1h' | '24h' | '7d' | '30d';

interface DeviceDetailProps {
  device: Device;
  onBack: () => void;
}

interface Device {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'offline' | 'warning';
  location: string;
  lastMaintenance: string;
  capacity?: number;
}

interface LiveData {
  voltage: number;
  current: number;
  power: number;
  temperature: number;
  efficiency: number;
  dailyYield: number;
  totalYield: number;
  igbtTemp: number;
  lastUpdate: Date;
}

interface DCData {
  id: string;
  voltage: number;
  current: number;
  power: number;
  efficiency: number;
}

interface ACData {
  id: string;
  voltage: number;
  current: number;
  power: number;
  frequency: number;
  powerFactor: number;
}

interface ErrorLog {
  id: string;
  timestamp: Date;
  type: 'warning' | 'error' | 'info';
  message: string;
  resolved: boolean;
}

interface WeatherData {
  temperature: number;
  humidity: number;
  windSpeed: number;
  solarIrradiance: number;
}

export const DeviceDetail: React.FC<DeviceDetailProps> = ({ device, onBack }) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState<TimeRange>('24h');
  
  const [liveData, setLiveData] = useState<LiveData>({
    voltage: 225.3,
    current: 14.2,
    power: 3.2,
    temperature: 35.1,
    efficiency: 95.5,
    dailyYield: 12.3,
    totalYield: 4567.8,
    igbtTemp: 52.1,
    lastUpdate: new Date()
  });

  const [dcData, setDcData] = useState<DCData[]>([
    { id: 'dc1', voltage: 220.1, current: 14.5, power: 3.19, efficiency: 95.2 },
    { id: 'dc2', voltage: 221.5, current: 14.7, power: 3.25, efficiency: 96.1 },
    { id: 'dc3', voltage: 219.8, current: 14.3, power: 3.14, efficiency: 94.8 },
    { id: 'dc4', voltage: 222.1, current: 14.9, power: 3.31, efficiency: 97.0 },
    { id: 'dc5', voltage: 218.9, current: 14.1, power: 3.09, efficiency: 94.2 }
  ]);

  const [acData, setAcData] = useState<ACData[]>([
    { id: 'ac1', voltage: 230.2, current: 12.1, power: 2.78, frequency: 50.1, powerFactor: 0.98 },
    { id: 'ac2', voltage: 231.5, current: 12.3, power: 2.85, frequency: 50.0, powerFactor: 0.99 },
    { id: 'ac3', voltage: 229.9, current: 11.9, power: 2.73, frequency: 50.2, powerFactor: 0.97 },
    { id: 'ac4', voltage: 232.1, current: 12.5, power: 2.90, frequency: 49.9, powerFactor: 0.96 },
    { id: 'ac5', voltage: 230.8, current: 12.0, power: 2.77, frequency: 50.1, powerFactor: 0.98 }
  ]);

  const [errorHistory, setErrorHistory] = useState<ErrorLog[]>([
    {
      id: '1',
      timestamp: new Date(Date.now() - 5 * 60 * 1000),
      type: 'warning',
      message: 'High temperature alert',
      resolved: false
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 15 * 60 * 1000),
      type: 'error',
      message: 'Voltage fluctuation detected',
      resolved: true
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 30 * 60 * 1000),
      type: 'info',
      message: 'System check passed',
      resolved: true
    }
  ]);

  const [weatherData, setWeatherData] = useState<WeatherData>({
    temperature: 28.5,
    humidity: 65,
    windSpeed: 3.2,
    solarIrradiance: 850
  });

  const [communicationStatus, setCommunicationStatus] = useState({
    lastContact: new Date(),
    signalStrength: 85,
    dataPacketsLost: 2
  });

  // Update live data every second for demo
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveData(prev => ({
        voltage: 220 + Math.random() * 20 - 10,
        current: 15 + Math.random() * 10 - 5,
        power: Math.max(0, prev.power + (Math.random() - 0.5) * 50),
        temperature: 25 + Math.random() * 15 - 5,
        efficiency: 85 + Math.random() * 10,
        dailyYield: prev.dailyYield + Math.random() * 0.1,
        totalYield: prev.totalYield + Math.random() * 0.01,
        igbtTemp: 45 + Math.random() * 20 - 10,
        lastUpdate: new Date()
      }));

      // Update DC data
      setDcData(prev => prev.map(item => ({
        ...item,
        voltage: parseFloat((220 + Math.random() * 40 - 20).toFixed(1)),
        current: parseFloat((15 + Math.random() * 10 - 5).toFixed(2)),
        power: parseFloat(((220 + Math.random() * 40 - 20) * (15 + Math.random() * 10 - 5) / 1000).toFixed(2)),
        efficiency: parseFloat((90 + Math.random() * 10).toFixed(1))
      })));

      // Update AC data
      setAcData(prev => prev.map(item => ({
        ...item,
        voltage: parseFloat((230 + Math.random() * 20 - 10).toFixed(1)),
        current: parseFloat((12 + Math.random() * 8 - 4).toFixed(2)),
        power: parseFloat(((230 + Math.random() * 20 - 10) * (12 + Math.random() * 8 - 4) / 1000).toFixed(2)),
        frequency: parseFloat((50 + Math.random() * 0.4 - 0.2).toFixed(2)),
        powerFactor: parseFloat((0.95 + Math.random() * 0.1 - 0.05).toFixed(3))
      })));

      // Update weather data
      setWeatherData(prev => ({
        temperature: 25 + Math.random() * 10,
        humidity: 50 + Math.random() * 30,
        windSpeed: Math.random() * 8,
        solarIrradiance: 700 + Math.random() * 300
      }));

      // Update communication status
      setCommunicationStatus(prev => ({
        lastContact: new Date(),
        signalStrength: 75 + Math.random() * 25,
        dataPacketsLost: Math.floor(Math.random() * 10)
      }));

      // Occasionally add new error logs
      if (Math.random() > 0.98) { // 2% chance each second
        const errorTypes: ('error' | 'warning' | 'info')[] = ['error', 'warning', 'info'];
        const randomType = errorTypes[Math.floor(Math.random() * errorTypes.length)];
        
        const newError: ErrorLog = {
          id: Date.now().toString(),
          timestamp: new Date(),
          type: randomType,
          message: [
            'Temperature spike detected',
            'Voltage fluctuation observed',
            'Performance optimization completed',
            'Grid synchronization successful',
            'Power factor correction applied',
            'Routine system check passed'
          ][Math.floor(Math.random() * 6)],
          resolved: Math.random() > 0.3
        };
        
        setErrorHistory(prev => [newError, ...prev.slice(0, 9)]);
      }
    }, 1000); // Update every second

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen gradient-mesh py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <Button onClick={onBack} variant="ghost" className="mb-4">
            <ArrowLeft className="mr-2 w-4 h-4" />
            Back to Plants
          </Button>
          
          {/* Enhanced Device Header */}
          <div className="glass-intense rounded-lg p-6 mb-6">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-3xl font-bold text-foreground mb-2">{device.name}</h1>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Zap className="w-4 h-4" />
                    {device.type}
                  </span>
                  <span className="flex items-center gap-1">
                    📍 {device.location}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    Last Maintenance: {device.lastMaintenance}
                  </span>
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-2 mb-2">
                  {device.status === 'online' && <Badge className="bg-green-500 text-white">● Online</Badge>}
                  {device.status === 'offline' && <Badge variant="destructive">● Offline</Badge>}
                  {device.status === 'warning' && <Badge variant="secondary">⚠ Warning</Badge>}
                  {communicationStatus.signalStrength > 50 ? 
                    <Wifi className="w-4 h-4 text-green-500" /> : 
                    <WifiOff className="w-4 h-4 text-red-500" />
                  }
                </div>
                <div className="text-xs text-muted-foreground">
                  Signal: {communicationStatus.signalStrength}%
                </div>
              </div>
            </div>
          </div>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="charts">Charts</TabsTrigger>
            <TabsTrigger value="diagnostics">Diagnostics</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Energy Meter - First Priority */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              <div className="lg:col-span-1">
                <EnergyMeter 
                  currentGeneration={liveData.power}
                  totalCapacity={device.capacity || 5.0}
                  efficiency={liveData.efficiency}
                />
              </div>
              
              {/* Compact Real-time Metrics */}
              <div className="lg:col-span-2 grid grid-cols-2 gap-4">
                <Card className="glass-card">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Temperature</p>
                        <p className="text-2xl font-bold">{liveData.temperature.toFixed(1)}°C</p>
                      </div>
                      <Thermometer className="w-8 h-8 text-orange-500 animate-pulse" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="glass-card">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Daily Yield</p>
                        <p className="text-2xl font-bold">{liveData.dailyYield.toFixed(1)} kWh</p>
                      </div>
                      <Zap className="w-8 h-8 text-purple-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="glass-card">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Voltage</p>
                        <p className="text-2xl font-bold">{liveData.voltage.toFixed(1)} V</p>
                      </div>
                      <Activity className="w-8 h-8 text-blue-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="glass-card">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Current</p>
                        <p className="text-2xl font-bold">{liveData.current.toFixed(1)} A</p>
                      </div>
                      <Gauge className="w-8 h-8 text-green-500" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Live Data Card */}
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-green-500 animate-pulse" />
                    Live Data
                    <Badge variant="outline" className="bg-green-50 text-green-700">LIVE</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Voltage</p>
                      <p className="text-xl font-bold">{liveData.voltage.toFixed(1)} V</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Current</p>
                      <p className="text-xl font-bold">{liveData.current.toFixed(1)} A</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">IGBT Temp</p>
                      <p className="text-xl font-bold">{liveData.igbtTemp.toFixed(1)}°C</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Yield</p>
                      <p className="text-xl font-bold">{liveData.totalYield.toFixed(1)} kWh</p>
                    </div>
                  </div>
                  <div className="pt-3 border-t">
                     <div className="flex items-center justify-between text-xs text-muted-foreground">
                       <span className="flex items-center gap-1">
                         <Clock className="w-3 h-3" />
                         Last Update: {liveData.lastUpdate.toLocaleTimeString()}
                       </span>
                     </div>
                  </div>
                </CardContent>
              </Card>

              {/* Weather & Environment */}
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle>Environmental Conditions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Temperature</p>
                      <p className="text-xl font-bold">{weatherData.temperature.toFixed(1)}°C</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Humidity</p>
                      <p className="text-xl font-bold">{weatherData.humidity.toFixed(0)}%</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Wind Speed</p>
                      <p className="text-xl font-bold">{weatherData.windSpeed.toFixed(1)} m/s</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Solar Irradiance</p>
                      <p className="text-xl font-bold">{weatherData.solarIrradiance.toFixed(0)} W/m²</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="performance" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* DC Data Table */}
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle>DC Input Data</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="max-h-64 overflow-y-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          <th className="px-3 py-2 text-left font-medium text-gray-500">ID</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-500">Voltage (V)</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-500">Current (A)</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-500">Power (kW)</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-500">Eff (%)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {dcData.map((item) => (
                          <tr key={item.id} className="hover:bg-gray-50">
                            <td className="px-3 py-2 font-medium">{item.id}</td>
                            <td className="px-3 py-2">{item.voltage}</td>
                            <td className="px-3 py-2">{item.current}</td>
                            <td className="px-3 py-2">{item.power}</td>
                            <td className="px-3 py-2">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                item.efficiency > 95 ? 'bg-green-100 text-green-800' :
                                item.efficiency > 90 ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {item.efficiency}%
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {/* AC Data Table */}
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle>AC Output Data</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="max-h-64 overflow-y-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          <th className="px-2 py-2 text-left font-medium text-gray-500">ID</th>
                          <th className="px-2 py-2 text-left font-medium text-gray-500">V (V)</th>
                          <th className="px-2 py-2 text-left font-medium text-gray-500">I (A)</th>
                          <th className="px-2 py-2 text-left font-medium text-gray-500">P (kW)</th>
                          <th className="px-2 py-2 text-left font-medium text-gray-500">Hz</th>
                          <th className="px-2 py-2 text-left font-medium text-gray-500">PF</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {acData.map((item) => (
                          <tr key={item.id} className="hover:bg-gray-50">
                            <td className="px-2 py-2 font-medium">{item.id}</td>
                            <td className="px-2 py-2">{item.voltage}</td>
                            <td className="px-2 py-2">{item.current}</td>
                            <td className="px-2 py-2">{item.power}</td>
                            <td className="px-2 py-2">{item.frequency}</td>
                            <td className="px-2 py-2">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                item.powerFactor > 0.97 ? 'bg-green-100 text-green-800' :
                                item.powerFactor > 0.95 ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {item.powerFactor}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Performance Summary */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Performance Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-2">System Efficiency</p>
                    <Progress value={liveData.efficiency} className="mb-2" />
                    <p className="text-sm text-gray-500">{liveData.efficiency.toFixed(1)}% of optimal</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-2">Power Output</p>
                    <Progress value={(liveData.power / 5) * 100} className="mb-2" />
                    <p className="text-sm text-gray-500">{liveData.power.toFixed(1)} kW / 5.0 kW rated</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-2">Daily Target</p>
                    <Progress value={(liveData.dailyYield / 30) * 100} className="mb-2" />
                    <p className="text-sm text-gray-500">{liveData.dailyYield.toFixed(1)} kWh / 30 kWh target</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="charts" className="space-y-6">
            <Card className="glass-card">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Device Analytics & Charts</CardTitle>
                  <TimeRangeSelector
                    selectedRange={selectedTimeRange}
                    onRangeChange={setSelectedTimeRange}
                  />
                </div>
              </CardHeader>
              <CardContent>
                <DynamicChart
                  timeRange={selectedTimeRange}
                  deviceId={device.id}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="diagnostics" className="space-y-6">
            {/* System Health */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>System Health Diagnostics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Activity className="w-6 h-6 text-white" />
                    </div>
                    <p className="font-medium text-green-800">System Status</p>
                    <p className="text-sm text-green-600">Operational</p>
                  </div>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Wifi className="w-6 h-6 text-white" />
                    </div>
                    <p className="font-medium text-blue-800">Communication</p>
                    <p className="text-sm text-blue-600">{communicationStatus.signalStrength}% Signal</p>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Thermometer className="w-6 h-6 text-white" />
                    </div>
                    <p className="font-medium text-orange-800">Temperature</p>
                    <p className="text-sm text-orange-600">Within Limits</p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Gauge className="w-6 h-6 text-white" />
                    </div>
                    <p className="font-medium text-purple-800">Performance</p>
                    <p className="text-sm text-purple-600">{liveData.efficiency.toFixed(0)}% Efficient</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Communication Status */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Communication Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Last Contact</span>
                    <span className="text-sm text-gray-600">{communicationStatus.lastContact.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Signal Strength</span>
                    <div className="flex items-center gap-2">
                      <Progress value={communicationStatus.signalStrength} className="w-20" />
                      <span className="text-sm text-gray-600">{communicationStatus.signalStrength}%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Data Packets Lost</span>
                    <span className="text-sm text-gray-600">{communicationStatus.dataPacketsLost}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            {/* Error History */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  System Activity Log
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {errorHistory.map((error) => (
                    <div key={error.id} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 border">
                      <div className="flex-shrink-0 mt-0.5">
                        {error.type === 'error' && <AlertTriangle className="w-4 h-4 text-red-500" />}
                        {error.type === 'warning' && <AlertTriangle className="w-4 h-4 text-yellow-500" />}
                        {error.type === 'info' && <Activity className="w-4 h-4 text-blue-500" />}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <p className="text-sm font-medium text-gray-900">{error.message}</p>
                          <Badge variant={error.type === 'error' ? 'destructive' : error.type === 'warning' ? 'secondary' : 'default'}>
                            {error.type}
                          </Badge>
                        </div>
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-gray-500">{error.timestamp.toLocaleString()}</span>
                          {error.resolved && (
                            <Badge variant="outline" className="text-green-600 border-green-200">Resolved</Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
