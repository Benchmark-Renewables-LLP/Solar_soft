
import React, { useState, useEffect } from 'react';
import { ArrowLeft, Download, Zap, Activity, TrendingUp, Gauge, CheckCircle, AlertTriangle, Shield, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Device } from '@/components/plants/PlantsOverview';
import { TimeRangeSelector } from './TimeRangeSelector';
import { DynamicChart } from './DynamicChart';
import { PanelVoltageChart } from './charts/PanelVoltageChart';
import { InputCurrentChart } from './charts/InputCurrentChart';
import { OutputCurrentChart } from './charts/OutputCurrentChart';
import { PowerGenerationChart } from './charts/PowerGenerationChart';

interface DeviceDetailProps {
  device: Device;
  onBack: () => void;
}

export type TimeRange = '1h' | '24h' | '7d' | '30d';

export const DeviceDetail: React.FC<DeviceDetailProps> = ({ device, onBack }) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState<TimeRange>('24h');
  const [activeTab, setActiveTab] = useState('control');
  const [realTimeData, setRealTimeData] = useState({
    voltage: 245.2,
    current: 18.5,
    power: 4537.2,
    temperature: 32.1,
    efficiency: 94.2,
    totalEnergy: 1247.8,
    todayYield: 197.4,
    monthlyYield: 5.8,
    totalYield: 156.7,
    stringDispersion: 2.3,
    fullLoadHours: 2.47,
    igbtTemp: 65.2,
    igbtMaxTemp: 85.0
  });

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      setRealTimeData(prev => ({
        voltage: prev.voltage + (Math.random() - 0.5) * 2,
        current: prev.current + (Math.random() - 0.5) * 1,
        power: prev.power + (Math.random() - 0.5) * 100,
        temperature: prev.temperature + (Math.random() - 0.5) * 0.5,
        efficiency: Math.max(85, Math.min(98, prev.efficiency + (Math.random() - 0.5) * 1)),
        totalEnergy: prev.totalEnergy + Math.random() * 0.1,
        todayYield: prev.todayYield + Math.random() * 0.5,
        monthlyYield: prev.monthlyYield + Math.random() * 0.01,
        totalYield: prev.totalYield + Math.random() * 0.01,
        stringDispersion: Math.max(0, Math.min(5, prev.stringDispersion + (Math.random() - 0.5) * 0.2)),
        fullLoadHours: prev.fullLoadHours + Math.random() * 0.01,
        igbtTemp: Math.max(40, Math.min(80, prev.igbtTemp + (Math.random() - 0.5) * 2)),
        igbtMaxTemp: prev.igbtMaxTemp
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleExportData = () => {
    console.log('Exporting data for device:', device.id, 'Time range:', selectedTimeRange);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-500';
      case 'offline': return 'text-red-500';
      case 'warning': return 'text-orange-500';
      case 'fault': return 'text-red-600';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'offline': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-orange-500" />;
      case 'fault': return <AlertTriangle className="w-5 h-5 text-red-600" />;
      default: return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  // Mock DC data for PV units
  const dcData = [
    { unit: 'PV1', voltage: 642.3, current: 8.5, power: 5459 },
    { unit: 'PV2', voltage: 638.7, current: 8.2, power: 5237 },
    { unit: 'PV3', voltage: 645.1, current: 8.7, power: 5612 },
    { unit: 'PV4', voltage: 640.9, current: 8.4, power: 5384 },
    { unit: 'PV5', voltage: 643.2, current: 8.6, power: 5531 },
    { unit: 'PV6', voltage: 639.5, current: 8.3, power: 5308 },
    { unit: 'PV7', voltage: 641.8, current: 8.5, power: 5455 }
  ];

  // Mock AC data for phases
  const acData = [
    { phase: 'L1', voltage: 239.4, current: 75.2, frequency: 50.02 },
    { phase: 'L2', voltage: 240.1, current: 74.8, frequency: 50.01 },
    { phase: 'L3', voltage: 238.9, current: 75.5, frequency: 50.03 }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button onClick={onBack} variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Plants
              </Button>
            </div>
            <Button onClick={handleExportData} variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Export Data
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Dashboard Title Section */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-3 rounded-xl">
              <Activity className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                Inverter Plant ID: {device.id}
              </h1>
              <div className="flex items-center space-x-2">
                {getStatusIcon(device.status)}
                <span className={`text-sm font-medium capitalize ${getStatusColor(device.status)}`}>
                  {device.status}
                </span>
              </div>
            </div>
          </div>
          <p className="text-slate-600 mb-4">
            Data Reporting Time: {new Date().toLocaleString()} UTC+05:30
          </p>
          
          {/* Navigation Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="control">Inverter Control</TabsTrigger>
              <TabsTrigger value="more">More</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* Basic Info Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              <div>
                <span className="font-bold text-slate-700">Name:</span>
                <p className="text-slate-600">{device.name}</p>
              </div>
              <div>
                <span className="font-bold text-slate-700">Serial Number:</span>
                <p className="text-slate-600">INV-{device.id.slice(-6).toUpperCase()}</p>
              </div>
              <div>
                <span className="font-bold text-slate-700">Model:</span>
                <p className="text-slate-600">SUN-60K-SG</p>
              </div>
              <div>
                <span className="font-bold text-slate-700">Plant:</span>
                <p className="text-slate-600">Solar Farm Alpha</p>
              </div>
              <div>
                <span className="font-bold text-slate-700">Machine Type:</span>
                <p className="text-slate-600 capitalize">{device.type}</p>
              </div>
              <div>
                <span className="font-bold text-slate-700">Warranty Status:</span>
                <p className="text-green-600 flex items-center">
                  <Shield className="w-4 h-4 mr-1" />
                  In Warranty (expires 2027-12-31)
                </p>
              </div>
              <div>
                <span className="font-bold text-slate-700">Version:</span>
                <p className="text-slate-600">v2.3.4</p>
              </div>
              <div>
                <span className="font-bold text-slate-700">AFCI:</span>
                <p className="text-slate-600">Enabled</p>
              </div>
              <div>
                <span className="font-bold text-slate-700">Datalogger:</span>
                <p className="text-slate-600">Connected</p>
              </div>
              <div>
                <span className="font-bold text-slate-700">Status:</span>
                <p className={`flex items-center ${getStatusColor(device.status)}`}>
                  {getStatusIcon(device.status)}
                  <span className="ml-1 capitalize">{device.status}</span>
                </p>
              </div>
              <div>
                <span className="font-bold text-slate-700">Rated Power:</span>
                <p className="text-slate-600">60 kW</p>
              </div>
              <div>
                <span className="font-bold text-slate-700">National Standard:</span>
                <p className="text-slate-600">IEC 62109</p>
              </div>
              <div>
                <span className="font-bold text-slate-700">Commissioning Date:</span>
                <p className="text-slate-600 flex items-center">
                  <Calendar className="w-4 h-4 mr-1" />
                  2023-03-15
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Real-time Info Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Real-time Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
              <Card className="bg-gradient-to-r from-blue-500 to-cyan-500 border-0 text-white">
                <CardContent className="p-4">
                  <div className="text-center">
                    <p className="text-sm opacity-90">Current Power</p>
                    <p className="text-xl font-bold">{(realTimeData.power / 1000).toFixed(1)} kW</p>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-r from-green-500 to-emerald-500 border-0 text-white">
                <CardContent className="p-4">
                  <div className="text-center">
                    <p className="text-sm opacity-90">Today Yield</p>
                    <p className="text-xl font-bold">{realTimeData.todayYield.toFixed(1)} kWh</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-r from-purple-500 to-pink-500 border-0 text-white">
                <CardContent className="p-4">
                  <div className="text-center">
                    <p className="text-sm opacity-90">Monthly Yield</p>
                    <p className="text-xl font-bold">{realTimeData.monthlyYield.toFixed(1)} MWh</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-r from-orange-500 to-red-500 border-0 text-white">
                <CardContent className="p-4">
                  <div className="text-center">
                    <p className="text-sm opacity-90">Total Yield</p>
                    <p className="text-xl font-bold">{realTimeData.totalYield.toFixed(1)} MWh</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-r from-teal-500 to-blue-500 border-0 text-white">
                <CardContent className="p-4">
                  <div className="text-center">
                    <p className="text-sm opacity-90">String Dispersion</p>
                    <p className="text-xl font-bold">{realTimeData.stringDispersion.toFixed(1)}%</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-r from-indigo-500 to-purple-500 border-0 text-white">
                <CardContent className="p-4">
                  <div className="text-center">
                    <p className="text-sm opacity-90">Full Load Hours</p>
                    <p className="text-xl font-bold">{realTimeData.fullLoadHours.toFixed(2)} h</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-r from-yellow-500 to-orange-500 border-0 text-white">
                <CardContent className="p-4">
                  <div className="text-center">
                    <p className="text-sm opacity-90">IGBT Temperature</p>
                    <p className="text-xl font-bold">{realTimeData.igbtTemp.toFixed(1)}°C</p>
                    <p className="text-xs opacity-75">(up to {realTimeData.igbtMaxTemp}°C)</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-r from-green-600 to-teal-600 border-0 text-white">
                <CardContent className="p-4">
                  <div className="text-center">
                    <p className="text-sm opacity-90">Alarm Status</p>
                    <p className="text-lg font-bold">No Alarms</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </CardContent>
        </Card>
           <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">Inverter Chart SN: INV-{device.id.slice(-6).toUpperCase()}</h2>
            <TimeRangeSelector
              selectedRange={selectedTimeRange}
              onRangeChange={setSelectedTimeRange}
            />
          </div>
          
          <DynamicChart timeRange={selectedTimeRange} deviceId={device.id} />
        </div>

        {/* DC Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="w-5 h-5" />
              <span>DC Data</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {dcData.map((pv) => (
                <Card key={pv.unit} className="border-2 border-blue-200">
                  <CardContent className="p-4">
                    <h3 className="font-bold text-lg text-center mb-3 text-blue-600">{pv.unit}</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="font-medium">Voltage:</span>
                        <span>{pv.voltage.toFixed(1)} V</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Current:</span>
                        <span>{pv.current.toFixed(1)} A</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Power:</span>
                        <span>{pv.power.toFixed(0)} W</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* AC Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span>AC Data</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {acData.map((phase) => (
                <Card key={phase.phase} className="border-2 border-green-200">
                  <CardContent className="p-4">
                    <h3 className="font-bold text-lg text-center mb-3 text-green-600">{phase.phase}</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="font-medium">Voltage:</span>
                        <span>{phase.voltage.toFixed(1)} V</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Current:</span>
                        <span>{phase.current.toFixed(1)} A</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Frequency:</span>
                        <span>{phase.frequency.toFixed(2)} Hz</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Chart Section */}
     

        {/* Additional Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PowerGenerationChart timeRange={selectedTimeRange} />
  
        </div>
      </div>
    </div>
  );
};
