import React from 'react';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Zap, TrendingUp, Battery } from 'lucide-react';

interface EnergyMeterProps {
  currentGeneration: number;
  totalCapacity: number;
  efficiency: number;
  className?: string;
}

export const EnergyMeter: React.FC<EnergyMeterProps> = ({
  currentGeneration,
  totalCapacity,
  efficiency,
  className = ''
}) => {
  const percentage = (currentGeneration / totalCapacity) * 100;
  const formattedPercentage = Math.min(percentage, 100);

  return (
    <Card className={`glass-card ${className}`}>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-lg">
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
            {/* Background Circle */}
            <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="40"
                stroke="currentColor"
                strokeWidth="8"
                fill="transparent"
                className="text-muted/30"
              />
              {/* Progress Circle */}
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
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#06b6d4" />
                </linearGradient>
              </defs>
            </svg>
            {/* Center Content */}
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

        {/* Generation Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="glass-surface p-3 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium">Current</span>
            </div>
            <div className="text-xl font-bold text-foreground">
              {currentGeneration.toFixed(1)} kW
            </div>
          </div>
          
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

        {/* Linear Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Generation Progress</span>
            <span className="font-medium">{currentGeneration.toFixed(1)} / {totalCapacity.toFixed(1)} kW</span>
          </div>
          <Progress 
            value={formattedPercentage} 
            className="h-3 glass-surface"
          />
        </div>

        {/* Efficiency Indicator */}
        <div className="glass-surface p-3 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">System Efficiency</span>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                efficiency > 90 ? 'bg-green-500' :
                efficiency > 75 ? 'bg-yellow-500' :
                'bg-red-500'
              }`} />
              <span className="font-bold text-lg">{efficiency.toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};