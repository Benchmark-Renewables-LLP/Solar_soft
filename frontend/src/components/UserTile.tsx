
import React from 'react';
import { User, Zap, AlertTriangle, Info, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Alert {
  id: string;
  type: 'critical' | 'warning' | 'info';
  message: string;
  timestamp: Date;
}

export interface UserData {
  id: string;
  name: string;
  location: string;
  currentGeneration: number;
  totalGeneration: number;
  efficiency: number;
  status: 'online' | 'offline' | 'maintenance';
  alerts: Alert[];
}

interface UserTileProps {
  user: UserData;
  onClick: (userId: string) => void;
  showAlert?: Alert;
}

const UserTile: React.FC<UserTileProps> = ({ user, onClick, showAlert }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-500';
      case 'offline': return 'text-red-500';
      case 'maintenance': return 'text-yellow-500';
      default: return 'text-gray-500';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'critical': return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'info': return <Info className="w-4 h-4 text-blue-500" />;
      default: return null;
    }
  };

  const hasActiveAlerts = user.alerts.length > 0;

  return (
    <div className="relative">
      <div
        onClick={() => onClick(user.id)}
        className={cn(
          "bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900",
          "border border-slate-200 dark:border-slate-700 rounded-xl p-4 cursor-pointer",
          "transition-all duration-300 hover:shadow-lg hover:scale-105",
          "hover:border-blue-300 dark:hover:border-blue-600",
          hasActiveAlerts && "ring-2 ring-yellow-400 ring-opacity-50"
        )}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-2 rounded-lg">
              <User className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-slate-800 dark:text-slate-200">{user.name}</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400">{user.location}</p>
            </div>
          </div>
          <div className={cn("flex items-center space-x-1", getStatusColor(user.status))}>
            <div className="w-2 h-2 rounded-full bg-current animate-pulse" />
            <span className="text-xs font-medium capitalize">{user.status}</span>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-600 dark:text-slate-400">Current Gen.</span>
            <div className="flex items-center space-x-1">
              <Zap className="w-3 h-3 text-yellow-500" />
              <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                {user.currentGeneration.toFixed(1)} kW
              </span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-600 dark:text-slate-400">Total Gen.</span>
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              {user.totalGeneration.toFixed(1)} MWh
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-600 dark:text-slate-400">Efficiency</span>
            <span className="text-sm font-semibold text-green-600 dark:text-green-400">
              {user.efficiency}%
            </span>
          </div>
        </div>

        {hasActiveAlerts && (
          <div className="mt-3 flex items-center space-x-1">
            {getAlertIcon(user.alerts[0].type)}
            <span className="text-xs text-slate-600 dark:text-slate-400">
              {user.alerts.length} alert{user.alerts.length !== 1 ? 's' : ''}
            </span>
          </div>
        )}
      </div>

      {/* Alert Overlay */}
      {showAlert && (
        <div className="absolute inset-0 bg-black bg-opacity-50 rounded-xl flex items-center justify-center z-10 animate-fade-in">
          <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-xl max-w-xs mx-4">
            <div className="flex items-center space-x-2 mb-2">
              {getAlertIcon(showAlert.type)}
              <span className="font-semibold text-sm capitalize">{showAlert.type} Alert</span>
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">{showAlert.message}</p>
            <p className="text-xs text-slate-500 dark:text-slate-500">
              {showAlert.timestamp.toLocaleTimeString()}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserTile;
