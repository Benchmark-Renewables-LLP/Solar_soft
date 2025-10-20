
import React from 'react';
import { User, Zap, AlertTriangle, Info, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Alert object structure for user notifications
 */
export interface Alert {
  /** Unique identifier for the alert */
  id: string;
  /** Alert severity level determining display style and priority */
  type: 'critical' | 'warning' | 'info';
  /** Human-readable alert message */
  message: string;
  /** When the alert was created */
  timestamp: Date;
}

/**
 * User data structure containing solar energy system information
 */
export interface UserData {
  /** Unique user identifier */
  id: string;
  /** User's display name */
  name: string;
  /** Geographic location of the user's solar installation */
  location: string;
  /** Current power generation in kilowatts (kW) */
  currentGeneration: number;
  /** Total accumulated energy generation in megawatt-hours (MWh) */
  totalGeneration: number;
  /** System efficiency as a percentage (0-100) */
  efficiency: number;
  /** Current operational status of the solar system */
  status: 'online' | 'offline' | 'maintenance';
  /** Array of active alerts for this user */
  alerts: Alert[];
}

/**
 * Props for the UserTile component
 */
interface UserTileProps {
  /** User data to display in the tile */
  user: UserData;
  /** Click handler called when the tile is clicked, receives the user ID */
  onClick: (userId: string) => void;
  /** Optional alert to show as an overlay on this tile */
  showAlert?: Alert;
}

/**
 * UserTile Component
 * 
 * Displays a compact card showing individual user's solar energy system information.
 * Features include real-time generation data, system status, alert indicators,
 * and interactive capabilities for navigation to detailed views.
 * 
 * @component
 * @example
 * ```tsx
 * const userData = {
 *   id: 'user-1',
 *   name: 'John Smith',
 *   location: 'California, USA',
 *   currentGeneration: 15.2,
 *   totalGeneration: 125.8,
 *   efficiency: 94,
 *   status: 'online',
 *   alerts: []
 * }
 * 
 * <UserTile 
 *   user={userData}
 *   onClick={(userId) => navigate(`/users/${userId}`)}
 *   showAlert={currentAlert}
 * />
 * ```
 */
const UserTile: React.FC<UserTileProps> = ({ user, onClick, showAlert }) => {
  /**
   * Returns the appropriate CSS class for status indicator color
   * @param status - The current system status
   * @returns CSS class string for status color
   */
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-500';
      case 'offline': return 'text-red-500';
      case 'maintenance': return 'text-yellow-500';
      default: return 'text-gray-500';
    }
  };

  /**
   * Returns the appropriate icon component for the given alert type
   * @param type - The alert severity type
   * @returns React element representing the alert icon
   */
  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'critical': return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'info': return <Info className="w-4 h-4 text-blue-500" />;
      default: return null;
    }
  };

  // Check if this user has any active alerts
  const hasActiveAlerts = user.alerts.length > 0;

  return (
    <div className="relative">
      {/* Main tile container with interactive styling */}
      <div
        onClick={() => onClick(user.id)}
        className={cn(
          // Base styling with gradient background
          "bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900",
          // Border and layout
          "border border-slate-200 dark:border-slate-700 rounded-xl p-4 cursor-pointer",
          // Interactive animations and transitions
          "transition-all duration-300 hover:shadow-lg hover:scale-105",
          // Hover state border color
          "hover:border-blue-300 dark:hover:border-blue-600",
          // Alert indication ring
          hasActiveAlerts && "ring-2 ring-yellow-400 ring-opacity-50"
        )}
      >
        {/* Header section with user info and status */}
        <div className="flex items-center justify-between mb-3">
          {/* User identification section */}
          <div className="flex items-center space-x-2">
            {/* User avatar with gradient background */}
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-2 rounded-lg">
              <User className="w-4 h-4 text-white" />
            </div>
            {/* User name and location */}
            <div>
              <h3 className="font-semibold text-sm text-slate-800 dark:text-slate-200">{user.name}</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400">{user.location}</p>
            </div>
          </div>
          {/* Status indicator with animated dot */}
          <div className={cn("flex items-center space-x-1", getStatusColor(user.status))}>
            <div className="w-2 h-2 rounded-full bg-current animate-pulse" />
            <span className="text-xs font-medium capitalize">{user.status}</span>
          </div>
        </div>

        {/* Metrics section displaying energy generation data */}
        <div className="space-y-2">
          {/* Current generation with lightning icon */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-600 dark:text-slate-400">Current Gen.</span>
            <div className="flex items-center space-x-1">
              <Zap className="w-3 h-3 text-yellow-500" />
              <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                {user.currentGeneration.toFixed(1)} kW
              </span>
            </div>
          </div>
          
          {/* Total generation display */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-600 dark:text-slate-400">Total Gen.</span>
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              {user.totalGeneration.toFixed(1)} MWh
            </span>
          </div>
          
          {/* System efficiency display */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-600 dark:text-slate-400">Efficiency</span>
            <span className="text-sm font-semibold text-green-600 dark:text-green-400">
              {user.efficiency}%
            </span>
          </div>
        </div>

        {/* Alert count indicator (shown only when alerts exist) */}
        {hasActiveAlerts && (
          <div className="mt-3 flex items-center space-x-1">
            {getAlertIcon(user.alerts[0].type)}
            <span className="text-xs text-slate-600 dark:text-slate-400">
              {user.alerts.length} alert{user.alerts.length !== 1 ? 's' : ''}
            </span>
          </div>
        )}
      </div>

      {/* Alert overlay (displayed when showAlert prop is provided) */}
      {showAlert && (
        <div className="absolute inset-0 bg-black bg-opacity-50 rounded-xl flex items-center justify-center z-10 animate-fade-in">
          <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-xl max-w-xs mx-4">
            {/* Alert header with icon and type */}
            <div className="flex items-center space-x-2 mb-2">
              {getAlertIcon(showAlert.type)}
              <span className="font-semibold text-sm capitalize">{showAlert.type} Alert</span>
            </div>
            {/* Alert message */}
            <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">{showAlert.message}</p>
            {/* Alert timestamp */}
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
