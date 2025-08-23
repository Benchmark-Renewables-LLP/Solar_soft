import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Zap, TrendingUp, Activity, AlertTriangle, CheckCircle, Clock, Thermometer, Wind, Droplets } from 'lucide-react';

interface LiveData {
  totalGeneration: number;
  currentPower: number;
  efficiency: number;
  temperature: number;
  windSpeed: number;
  humidity: number;
  lastUpdate: Date;
}

interface ErrorLog {
  id: string;
  timestamp: Date;
  type: 'warning' | 'error' | 'info';
  device: string;
  message: string;
  resolved: boolean;
}

export const LiveDataPanel: React.FC = () => {
  const [liveData, setLiveData] = useState<LiveData>({
    totalGeneration: 2847.5,
    currentPower: 485.2,
    efficiency: 92.8,
    temperature: 24.5,
    windSpeed: 3.2,
    humidity: 68,
    lastUpdate: new Date()
  });

  const [errorHistory, setErrorHistory] = useState<ErrorLog[]>([
    {
      id: '1',
      timestamp: new Date(Date.now() - 5 * 60 * 1000),
      type: 'warning',
      device: 'Inverter A1',
      message: 'Temperature approaching upper limit',
      resolved: false
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 15 * 60 * 1000),
      type: 'error',
      device: 'Panel Array B1',
      message: 'Voltage fluctuation detected',
      resolved: true
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 30 * 60 * 1000),
      type: 'info',
      device: 'Smart Meter C1',
      message: 'Daily generation target achieved',
      resolved: true
    },
    {
      id: '4',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      type: 'warning',
      device: 'Inverter A2',
      message: 'Efficiency below optimal range',
      resolved: true
    }
  ]);

  // Update live data every second for demo
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveData(prev => ({
        totalGeneration: prev.totalGeneration + Math.random() * 0.05 + 0.01,
        currentPower: 400 + Math.random() * 200,
        efficiency: 88 + Math.random() * 8,
        temperature: 20 + Math.random() * 15,
        windSpeed: Math.random() * 8,
        humidity: 50 + Math.random() * 30,
        lastUpdate: new Date()
      }));
    }, 1000); // Update every second

    // Also add random error logs more frequently
    const errorInterval = setInterval(() => {
      if (Math.random() > 0.9) { // 10% chance every 3 seconds
        const newError: ErrorLog = {
          id: Date.now().toString(),
          timestamp: new Date(),
          type: Math.random() > 0.5 ? 'warning' : 'info',
          device: ['Inverter A1', 'Panel Array B1', 'Smart Meter C1', 'Inverter A2'][Math.floor(Math.random() * 4)],
          message: [
            'Performance optimization completed',
            'Routine maintenance check initiated',
            'Power generation peak detected',
            'Environmental conditions optimal',
            'Grid connection stable',
            'Temperature within normal range'
          ][Math.floor(Math.random() * 6)],
          resolved: Math.random() > 0.3
        };
        
        setErrorHistory(prev => [newError, ...prev.slice(0, 9)]);
      }
    }, 3000); // Check every 3 seconds

    return () => {
      clearInterval(interval);
      clearInterval(errorInterval);
    };
  }, []);

  const getErrorIcon = (type: string) => {
    switch (type) {
      case 'error': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default: return <CheckCircle className="w-4 h-4 text-blue-500" />;
    }
  };

  const getErrorBadgeVariant = (type: string) => {
    switch (type) {
      case 'error': return 'destructive';
      case 'warning': return 'secondary';
      default: return 'default';
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      {/* Live Data Monitoring */}
      <Card className="border-2 border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-green-700">
            <Activity className="w-5 h-5 animate-pulse" />
            Live System Monitoring
            <Badge variant="default" className="bg-green-500 text-white">
              LIVE
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-600">Total Generation</span>
                <Zap className="w-4 h-4 text-yellow-500" />
              </div>
              <div className="text-2xl font-bold text-green-600">
                {liveData.totalGeneration.toFixed(1)} kWh
              </div>
              <div className="text-xs text-slate-500">
                +{(Math.random() * 2 + 0.5).toFixed(1)} kWh/hr
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-600">Current Power</span>
                <TrendingUp className="w-4 h-4 text-blue-500" />
              </div>
              <div className="text-2xl font-bold text-blue-600">
                {liveData.currentPower.toFixed(1)} kW
              </div>
              <Progress value={liveData.currentPower / 6} className="h-2" />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 pt-2 border-t">
            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <Thermometer className="w-4 h-4 text-red-500" />
              </div>
              <div className="text-lg font-semibold">{liveData.temperature.toFixed(1)}°C</div>
              <div className="text-xs text-slate-500">Temperature</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <Wind className="w-4 h-4 text-cyan-500" />
              </div>
              <div className="text-lg font-semibold">{liveData.windSpeed.toFixed(1)} m/s</div>
              <div className="text-xs text-slate-500">Wind Speed</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <Droplets className="w-4 h-4 text-blue-500" />
              </div>
              <div className="text-lg font-semibold">{liveData.humidity.toFixed(0)}%</div>
              <div className="text-xs text-slate-500">Humidity</div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              Last update: {liveData.lastUpdate.toLocaleTimeString()}
            </span>
            <span className="flex items-center gap-1">
              Efficiency: {liveData.efficiency.toFixed(1)}%
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Error History */}
      <Card className="border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-red-50">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-orange-700">
            <AlertTriangle className="w-5 h-5" />
            System Activity Log
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {errorHistory.map((error) => (
              <div
                key={error.id}
                className="flex items-start gap-3 p-3 rounded-lg bg-white border border-slate-200 hover:shadow-sm transition-shadow"
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getErrorIcon(error.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-900 truncate">
                        {error.device}
                      </p>
                      <p className="text-xs text-slate-600 mt-1">
                        {error.message}
                      </p>
                    </div>
                    <Badge variant={getErrorBadgeVariant(error.type)} className="ml-2">
                      {error.type}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-slate-500">
                      {error.timestamp.toLocaleTimeString()}
                    </span>
                    {error.resolved && (
                      <Badge variant="outline" className="text-green-600 border-green-200">
                        Resolved
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
