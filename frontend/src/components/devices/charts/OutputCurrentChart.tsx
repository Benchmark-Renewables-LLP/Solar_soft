
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import { TimeRange } from '../DeviceDetail';

interface OutputCurrentChartProps {
  timeRange: TimeRange;
}

export const OutputCurrentChart: React.FC<OutputCurrentChartProps> = ({ timeRange }) => {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const generateData = () => {
      const now = new Date();
      let points = 24;
      let interval = 60;

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
        const baseCurrent = 20;
        
        mockData.push({
          time: timeRange === '1h' ? time.toLocaleTimeString() : 
                timeRange === '24h' ? time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) :
                time.toLocaleDateString(),
          timestamp: time.getTime(),
          Output1: baseCurrent + Math.sin(i * 0.1) * 4 + Math.random() * 2.5,
          Output2: baseCurrent + Math.sin(i * 0.12) * 3 + Math.random() * 2,
          Output3: baseCurrent + Math.sin(i * 0.08) * 4.5 + Math.random() * 3
        });
      }
      
      setData(mockData);
    };

    generateData();
  }, [timeRange]);

  const chartConfig = {
    Output1: { label: "Output 1", color: "#8b5cf6" },
    Output2: { label: "Output 2", color: "#ec4899" },
    Output3: { label: "Output 3", color: "#06b6d4" }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <span>Output Currents</span>
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
                domain={['dataMin - 1', 'dataMax + 1']}
                label={{ value: 'Current (A)', angle: -90, position: 'insideLeft' }}
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
