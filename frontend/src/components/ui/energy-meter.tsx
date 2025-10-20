
import React from 'react';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Zap, TrendingUp, Battery } from 'lucide-react';

/**
 * Props for the EnergyMeter component
 */
interface EnergyMeterProps {
  /** Current energy generation in kilowatts (kW) */
  currentGeneration: number;
  /** Maximum system capacity in kilowatts (kW) */
  totalCapacity: number;
  /** System efficiency as a percentage (0-100) */
  efficiency: number;
  /** Additional CSS classes for styling customization */
  className?: string;
}

/**
 * EnergyMeter Component
 * 
 * A comprehensive energy generation meter that displays current generation,
 * system capacity, and efficiency in both circular and linear progress formats.
 * Features include:
 * - Animated circular progress indicator
 * - Real-time generation metrics
 * - System capacity information
 * - Efficiency indicator with color coding
 * - Glass morphism design aesthetic
 * 
 * @component
 * @example
 * ```tsx
 * <EnergyMeter 
 *   currentGeneration={15.2}
 *   totalCapacity={20.0}
 *   efficiency={92.5}
 *   className="mb-4"
 * />
 * ```
 */
export const EnergyMeter: React.FC<EnergyMeterProps> = ({
  currentGeneration,
  totalCapacity,
  efficiency,
  className = ''
}) => {
  // Calculate the percentage of capacity being used (0-100)
  const percentage = (currentGeneration / totalCapacity) * 100;
  // Ensure percentage doesn't exceed 100% for display purposes
  const formattedPercentage = Math.min(percentage, 100);

  return (
    <Card className={`glass-card ${className}`}>
      {/* Card header with title and icon */}
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-lg">
          {/* Icon container with gradient background */}
          <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500/20 to-cyan-500/20">
            <Zap className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          Energy Generation Meter
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Circular Progress Visualization */}
        <div className="relative flex items-center justify-center">
          <div className="relative w-32 h-32">
            {/* SVG-based circular progress indicator */}
            <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
              {/* Background circle (inactive state) */}
              <circle
                cx="50"
                cy="50"
                r="40"
                stroke="currentColor"
                strokeWidth="8"
                fill="transparent"
                className="text-muted/30"
              />
              {/* Progress circle (active state with gradient) */}
              <circle
                cx="50"
                cy="50"
                r="40"
                stroke="url(#gradient)"
                strokeWidth="8"
                fill="transparent"
                strokeDasharray={`${2.51 * formattedPercentage} 251.2`}
                strokeLinecap="round"
                className="transition-all duration-500 ease-out"
              />
              {/* Gradient definition for progress circle */}
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#06b6d4" />
                </linearGradient>
              </defs>
            </svg>
            
            {/* Center content showing percentage and label */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div className="text-2xl font-bold text-foreground">
                {formattedPercentage.toFixed(1)}%
              </div>
              <div className="text-xs text-muted-foreground">
                Capacity
              </div>
            </div>
          </div>
        </div>

        {/* Generation Statistics Grid */}
        <div className="grid grid-cols-2 gap-4">
          {/* Current generation display */}
          <div className="glass-surface p-3 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium">Current</span>
            </div>
            <div className="text-xl font-bold text-foreground">
              {currentGeneration.toFixed(1)} kW
            </div>
          </div>
          
          {/* System capacity display */}
          <div className="glass-surface p-3 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Battery className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium">Capacity</span>
            </div>
            <div className="text-xl font-bold text-foreground">
              {totalCapacity.toFixed(1)} kW
            </div>
          </div>
        </div>

        {/* Linear Progress Bar Section */}
        <div className="space-y-2">
          {/* Progress bar label and values */}
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Generation Progress</span>
            <span className="font-medium">{currentGeneration.toFixed(1)} / {totalCapacity.toFixed(1)} kW</span>
          </div>
          {/* Linear progress indicator */}
          <Progress 
            value={formattedPercentage} 
            className="h-3 glass-surface"
          />
        </div>

        {/* System Efficiency Indicator */}
        <div className="glass-surface p-3 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">System Efficiency</span>
            <div className="flex items-center gap-2">
              {/* Efficiency status dot with color coding */}
              <div className={`w-2 h-2 rounded-full ${
                efficiency > 90 ? 'bg-green-500' :
                efficiency > 75 ? 'bg-yellow-500' :
                'bg-red-500'
              }`} />
              {/* Efficiency percentage display */}
              <span className="font-bold text-lg">{efficiency.toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
