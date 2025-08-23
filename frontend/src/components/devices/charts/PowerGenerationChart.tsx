
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import { TimeRange } from '../DeviceDetail';

interface PowerGenerationChartProps {
  timeRange: TimeRange;
}

export const PowerGenerationChart: React.FC<PowerGenerationChartProps> = ({ timeRange }) => {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const generateData = () => {
      const now = new Date();
      let points = 24;
      let interval = 60;

      switch (timeRange) {
        case '1h':
          points = 12;
          interval = 5;
          break;
        case '24h':
          points = 24;
          interval = 60;
          break;
        case '7d':
          points = 7;
          interval = 1440;
          break;
        case '30d':
          points = 30;
          interval = 1440;
          break;
      }

      const mockData = [];
      for (let i = points; i >= 0; i--) {
        const time = new Date(now.getTime() - i * interval * 60000);
        const basePower = 4500;
        
        mockData.push({
          time: timeRange === '1h' ? time.toLocaleTimeString() : 
                timeRange === '24h' ? time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) :
                time.toLocaleDateString(),
          timestamp: time.getTime(),
          generation: basePower + Math.sin(i * 0.2) * 1000 + Math.random() * 500,
          capacity: 5000
        });
      }
      
      setData(mockData);
    };

    generateData();
  }, [timeRange]);

  const chartConfig = {
    generation: { label: "Power Generation", color: "#10b981" },
    capacity: { label: "Total Capacity", color: "#e5e7eb" }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <span>Power Generation</span>
          <span className="text-sm text-slate-600">- {timeRange}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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
                label={{ value: 'Power (W)', angle: -90, position: 'insideLeft' }}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Legend />
              <Bar dataKey="capacity" fill="#e5e7eb" name="Total Capacity" />
              <Bar dataKey="generation" fill="#10b981" name="Power Generation" />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
