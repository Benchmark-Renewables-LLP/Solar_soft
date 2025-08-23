
import React, { useState, useEffect } from 'react';
import { Sun, Activity, Users, Zap } from 'lucide-react';
import UserTile, { UserData, Alert } from '@/components/UserTile';
import UserDashboard from '@/components/UserDashboard';
import AlertSystem from '@/components/AlertSystem';
import { Card, CardContent } from '@/components/ui/card';

const Index = () => {
  const [selectedUser, setSelectedUser] = useState<string | null>(null);
  const [users, setUsers] = useState<UserData[]>([]);
  const [alertOverlay, setAlertOverlay] = useState<{ userId: string; alert: Alert } | null>(null);

  // Generate sample user data
  useEffect(() => {
    const generateUsers = (): UserData[] => {
      const locations = [
        'Solar Farm A', 'Rooftop B-1', 'Industrial C', 'Residential D',
        'Commercial E', 'Farm F-2', 'School G', 'Hospital H',
        'Factory I-3', 'Office J', 'Mall K-1', 'Park L',
        'Station M', 'Center N-2', 'Plaza O', 'Tower P-4',
        'Complex Q', 'Building R-1', 'Unit S-3', 'Site T-2'
      ];

      const statuses: Array<'online' | 'offline' | 'maintenance'> = ['online', 'offline', 'maintenance'];
      
      return Array.from({ length: 20 }, (_, i) => {
        const alerts: Alert[] = [];
        
        // Randomly add alerts to some users
        if (Math.random() > 0.7) {
          const alertTypes: Array<'critical' | 'warning' | 'info'> = ['critical', 'warning', 'info'];
          const alertMessages = {
            critical: ['System overheating', 'Power failure'],
            warning: ['Low efficiency', 'High temperature'],
            info: ['Maintenance due', 'Update available']
          };
          
          const alertType = alertTypes[Math.floor(Math.random() * alertTypes.length)];
          alerts.push({
            id: `alert-${i}`,
            type: alertType,
            message: alertMessages[alertType][Math.floor(Math.random() * alertMessages[alertType].length)],
            timestamp: new Date()
          });
        }

        return {
          id: `user-${i + 1}`,
          name: `PV Unit ${String.fromCharCode(65 + i)}${i + 1}`,
          location: locations[i],
          currentGeneration: Math.random() * 10 + 1,
          totalGeneration: Math.random() * 1000 + 100,
          efficiency: Math.floor(Math.random() * 30 + 70),
          status: statuses[Math.floor(Math.random() * statuses.length)],
          alerts
        };
      });
    };

    setUsers(generateUsers());
  }, []);

  const handleUserClick = (userId: string) => {
    setSelectedUser(userId);
  };

  const handleBackToDashboard = () => {
    setSelectedUser(null);
  };

  const handleAlertShow = (userId: string, alert: Alert) => {
    setAlertOverlay({ userId, alert });
  };

  const handleAlertHide = () => {
    setAlertOverlay(null);
  };

  const selectedUserData = users.find(user => user.id === selectedUser);

  if (selectedUserData) {
    return <UserDashboard user={selectedUserData} onBack={handleBackToDashboard} />;
  }

  const totalGeneration = users.reduce((sum, user) => sum + user.currentGeneration, 0);
  const onlineUsers = users.filter(user => user.status === 'online').length;
  const totalAlerts = users.reduce((sum, user) => sum + user.alerts.length, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-700">
      <AlertSystem onAlertShow={handleAlertShow} onAlertHide={handleAlertHide} />
      
      {/* Header */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm border-b border-slate-200 dark:border-slate-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-3 rounded-xl">
                <Sun className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                  Solar PV Dashboard
                </h1>
                <p className="text-slate-600 dark:text-slate-400">Real-time monitoring and analytics</p>
              </div>
            </div>
            <div className="flex space-x-4">
              <Card className="bg-gradient-to-r from-green-500 to-emerald-500 border-0 text-white">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <Zap className="w-5 h-5" />
                    <div>
                      <p className="text-sm opacity-90">Total Generation</p>
                      <p className="text-xl font-bold">{totalGeneration.toFixed(1)} kW</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-r from-blue-500 to-cyan-500 border-0 text-white">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <Users className="w-5 h-5" />
                    <div>
                      <p className="text-sm opacity-90">Online Units</p>
                      <p className="text-xl font-bold">{onlineUsers}/20</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-r from-purple-500 to-pink-500 border-0 text-white">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <Activity className="w-5 h-5" />
                    <div>
                      <p className="text-sm opacity-90">Active Alerts</p>
                      <p className="text-xl font-bold">{totalAlerts}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Main Dashboard */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {users.map((user) => (
            <UserTile
              key={user.id}
              user={user}
              onClick={handleUserClick}
              showAlert={alertOverlay?.userId === user.id ? alertOverlay.alert : undefined}
            />
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm border-t border-slate-200 dark:border-slate-700 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <p className="text-slate-600 dark:text-slate-400">
              © 2024 Solar PV Management System. Real-time monitoring enabled.
            </p>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-slate-600 dark:text-slate-400">System Online</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
