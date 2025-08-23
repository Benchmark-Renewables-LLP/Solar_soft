
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import { TimeRange } from '../DeviceDetail';

interface PanelVoltageChartProps {
  timeRange: TimeRange;
}

export const PanelVoltageChart: React.FC<PanelVoltageChartProps> = ({ timeRange }) => {
  const [data, setData] = useState<any[]>([]);

  // Generate mock data based on time range
  useEffect(() => {
    const generateData = () => {
      const now = new Date();
      let points = 24;
      let interval = 60; // minutes

      switch (timeRange) {
        case '1h':
          points = 60;
          interval = 1;
          break;
        case '24h':
          points = 24;
          interval = 60;
          break;
        case '7d':
          points = 168;
          interval = 60;
          break;
        case '30d':
          points = 720;
          interval = 60;
          break;
      }

      const mockData = [];
      for (let i = points; i >= 0; i--) {
        const time = new Date(now.getTime() - i * interval * 60000);
        const baseVoltage = 240;
        
        mockData.push({
          time: timeRange === '1h' ? time.toLocaleTimeString() : 
                timeRange === '24h' ? time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) :
                time.toLocaleDateString(),
          timestamp: time.getTime(),
          PV1: baseVoltage + Math.sin(i * 0.1) * 10 + Math.random() * 5,
          PV2: baseVoltage + Math.sin(i * 0.12) * 8 + Math.random() * 4,
          PV3: baseVoltage + Math.sin(i * 0.08) * 12 + Math.random() * 6,
          PV4: baseVoltage + Math.sin(i * 0.15) * 7 + Math.random() * 3,
          PV5: baseVoltage + Math.sin(i * 0.09) * 9 + Math.random() * 4,
          PV6: baseVoltage + Math.sin(i * 0.11) * 11 + Math.random() * 5,
          PV7: baseVoltage + Math.sin(i * 0.13) * 6 + Math.random() * 3,
          PV8: baseVoltage + Math.sin(i * 0.07) * 13 + Math.random() * 7,
          PV9: baseVoltage + Math.sin(i * 0.14) * 8 + Math.random() * 4,
          PV10: baseVoltage + Math.sin(i * 0.06) * 10 + Math.random() * 5
        });
      }
      
      setData(mockData);
    };

    generateData();
  }, [timeRange]);

  const chartConfig = {
    PV1: { label: "PV1", color: "#ef4444" },
    PV2: { label: "PV2", color: "#3b82f6" },
    PV3: { label: "PV3", color: "#10b981" },
    PV4: { label: "PV4", color: "#f59e0b" },
    PV5: { label: "PV5", color: "#8b5cf6" },
    PV6: { label: "PV6", color: "#ec4899" },
    PV7: { label: "PV7", color: "#06b6d4" },
    PV8: { label: "PV8", color: "#84cc16" },
    PV9: { label: "PV9", color: "#f97316" },
    PV10: { label: "PV10", color: "#6366f1" }
  };

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <span>Panel Voltages (PV1-PV10)</span>
          <span className="text-sm text-slate-600">- {timeRange}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="time" 
                stroke="#64748b"
                fontSize={12}
                interval="preserveStartEnd"
              />
              <YAxis 
                stroke="#64748b"
                fontSize={12}
                domain={['dataMin - 5', 'dataMax + 5']}
                label={{ value: 'Voltage (V)', angle: -90, position: 'insideLeft' }}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Legend />
              {Object.entries(chartConfig).map(([key, config]) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={config.color}
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
