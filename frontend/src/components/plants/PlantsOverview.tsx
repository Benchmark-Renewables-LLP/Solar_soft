
import React, { useState, useEffect } from 'react';
import { Factory, MapPin, Zap, Users, Settings, Eye, HelpCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { usePlantsData } from '@/hooks/usePlantsData';
import UserGuide from '@/components/onboarding/UserGuide';
import { LiveDataPanel } from '@/components/dashboard/LiveDataPanel';
import { Device } from '@/types/device';

export interface Plant {
  id: string;
  name: string;
  location: string;
  totalCapacity: number;
  currentGeneration: number;
  efficiency: number;
  deviceCount: number;
  status: 'online' | 'offline' | 'maintenance';
  lastUpdate: Date;
}

interface PlantsOverviewProps {
  user: any;
  onDeviceSelect: (device: Device) => void;
  onLogout: () => void;
}

// Utility functions for status styling
const getStatusBg = (status: string) => {
  switch (status) {
    case 'online': return 'bg-green-50 border-green-200';
    case 'offline': return 'bg-red-50 border-red-200';
    case 'warning': return 'bg-orange-50 border-orange-200';
    case 'fault': return 'bg-red-100 border-red-300';
    case 'maintenance': return 'bg-yellow-50 border-yellow-200';
    default: return 'bg-gray-50 border-gray-200';
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'online': return 'text-green-500';
    case 'offline': return 'text-red-500';
    case 'warning': return 'text-orange-500';
    case 'fault': return 'text-red-600';
    case 'maintenance': return 'text-yellow-500';
    default: return 'text-gray-500';
  }
};

export const PlantsOverview: React.FC<PlantsOverviewProps> = ({ user, onDeviceSelect, onLogout }) => {
  // Updated user type detection - check for demo username or demo123
  const userType = (user?.username === 'admin') ? 'admin' : 'demo';
  const { plants, devices, isLoading, error } = usePlantsData(userType);
  const [showGuide, setShowGuide] = useState(false);

  // Show guide for demo user on first visit
  useEffect(() => {
    if (userType === 'demo') {
      const hasSeenGuide = localStorage.getItem('demo-guide-seen');
      if (!hasSeenGuide) {
        setShowGuide(true);
      }
    }
  }, [userType]);

  const handleCloseGuide = () => {
    setShowGuide(false);
    if (userType === 'demo') {
      localStorage.setItem('demo-guide-seen', 'true');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading plants and devices...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error loading data: {error.message}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-mesh">
      {/* Header */}
      <div className="glass-intense border-b sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-3 rounded-xl">
                <Factory className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                  Plants & Devices
                </h1>
                <p className="text-slate-600">Welcome back, {user.name || user.fullname || user.username}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                onClick={() => setShowGuide(true)}
                variant="outline"
                size="sm"
                className="flex items-center space-x-2"
              >
                <HelpCircle className="w-4 h-4" />
                <span>Guide</span>
              </Button>
              <Button onClick={onLogout} variant="outline">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Live Data Panel */}
        <LiveDataPanel />
        
        {/* Plants Overview */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-800 mb-6">
            Solar Plants Overview 
            {userType === 'demo' && <span className="text-sm text-slate-500 ml-2">(Demo View - Limited Data)</span>}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {plants.map((plant) => (
              <Card key={plant.id} className="glass-card hover:glass-intense transition-all duration-300">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-lg">{plant.name}</span>
                    <div className={`flex items-center space-x-1 ${getStatusColor(plant.status)}`}>
                      <div className="w-2 h-2 rounded-full bg-current animate-pulse" />
                      <span className="text-xs font-medium capitalize">{plant.status}</span>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center space-x-2 text-slate-600">
                    <MapPin className="w-4 h-4" />
                    <span className="text-sm">{plant.location}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-slate-600">Capacity:</span>
                      <p className="font-semibold">{plant.totalCapacity} kW</p>
                    </div>
                    <div>
                      <span className="text-slate-600">Current:</span>
                      <p className="font-semibold">{plant.currentGeneration} kW</p>
                    </div>
                    <div>
                      <span className="text-slate-600">Efficiency:</span>
                      <p className="font-semibold text-green-600">{plant.efficiency}%</p>
                    </div>
                    <div>
                      <span className="text-slate-600">Devices:</span>
                      <p className="font-semibold">{plant.deviceCount}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Devices List */}
        <div>
          <h2 className="text-2xl font-bold text-slate-800 mb-6">
            Devices
            {userType === 'demo' && <span className="text-sm text-slate-500 ml-2">(Showing {devices.length} devices)</span>}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {devices.map((device) => {
              const plant = plants.find(p => p.id === device.plantId);
              return (
                <Card key={device.id} className="glass-card hover:glass-intense transition-all duration-300 hover:scale-105 cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-slate-800">{device.name}</h3>
                      <div className={`flex items-center space-x-1 ${getStatusColor(device.status)}`}>
                        <div className="w-2 h-2 rounded-full bg-current animate-pulse" />
                        <span className="text-xs font-medium capitalize">{device.status}</span>
                      </div>
                    </div>
                    <p className="text-xs text-slate-600 mb-3">{plant?.name}</p>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-600">Type:</span>
                        <span className="font-medium capitalize">{device.type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Output:</span>
                        <span className="font-medium">{device.currentOutput} kW</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Efficiency:</span>
                        <span className="font-medium text-green-600">{device.efficiency}%</span>
                      </div>
                    </div>
                    <Button
                      onClick={() => onDeviceSelect(device)}
                      className="w-full mt-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white"
                      size="sm"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View Details
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </div>

      <UserGuide isOpen={showGuide} onClose={handleCloseGuide} />
    </div>
  );
};
