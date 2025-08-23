
import React from 'react';
import { ArrowLeft, Zap, TrendingUp, Battery, Thermometer, Gauge, Clock } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { UserData } from './UserTile';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface UserDashboardProps {
  user: UserData;
  onBack: () => void;
}

// Sample data for charts
const powerPlantData = [
  { month: 'Jan', generation: 45.2 },
  { month: 'Feb', generation: 52.1 },
  { month: 'Mar', generation: 61.3 },
  { month: 'Apr', generation: 68.7 },
  { month: 'May', generation: 75.4 },
  { month: 'Jun', generation: 82.1 },
  { month: 'Jul', generation: 89.6 },
  { month: 'Aug', generation: 87.3 },
  { month: 'Sep', generation: 78.9 },
  { month: 'Oct', generation: 66.2 },
  { month: 'Nov', generation: 55.8 },
  { month: 'Dec', generation: 48.4 },
];

const pvArrayData = [
  { time: '00:00', PV1: 0, PV2: 0, PV3: 0, PV4: 0, PV5: 0, PV6: 0, PV7: 0, PV8: 0, PV9: 0, PV10: 0 },
  { time: '06:00', PV1: 2.1, PV2: 1.9, PV3: 2.3, PV4: 2.0, PV5: 2.2, PV6: 1.8, PV7: 2.4, PV8: 2.1, PV9: 1.9, PV10: 2.0 },
  { time: '09:00', PV1: 5.2, PV2: 4.8, PV3: 5.6, PV4: 5.1, PV5: 5.3, PV6: 4.7, PV7: 5.8, PV8: 5.2, PV9: 4.9, PV10: 5.0 },
  { time: '12:00', PV1: 8.1, PV2: 7.9, PV3: 8.4, PV4: 8.0, PV5: 8.2, PV6: 7.8, PV7: 8.6, PV8: 8.1, PV9: 7.9, PV10: 8.0 },
  { time: '15:00', PV1: 6.8, PV2: 6.5, PV3: 7.1, PV4: 6.7, PV5: 6.9, PV6: 6.4, PV7: 7.3, PV8: 6.8, PV9: 6.6, PV10: 6.7 },
  { time: '18:00', PV1: 3.2, PV2: 3.0, PV3: 3.4, PV4: 3.1, PV5: 3.3, PV6: 2.9, PV7: 3.5, PV8: 3.2, PV9: 3.0, PV10: 3.1 },
  { time: '21:00', PV1: 0, PV2: 0, PV3: 0, PV4: 0, PV5: 0, PV6: 0, PV7: 0, PV8: 0, PV9: 0, PV10: 0 },
];

const UserDashboard: React.FC<UserDashboardProps> = ({ user, onBack }) => {
  const metrics = [
    { 
      label: 'Current Generation', 
      value: `${user.currentGeneration.toFixed(1)} kW`, 
      icon: Zap, 
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/20'
    },
    { 
      label: 'Peak Generation', 
      value: '8.4 kW', 
      icon: TrendingUp, 
      color: 'text-green-500',
      bgColor: 'bg-green-50 dark:bg-green-900/20'
    },
    { 
      label: 'Battery Level', 
      value: '87%', 
      icon: Battery, 
      color: 'text-blue-500',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20'
    },
    { 
      label: 'Temperature', 
      value: '42°C', 
      icon: Thermometer, 
      color: 'text-red-500',
      bgColor: 'bg-red-50 dark:bg-red-900/20'
    },
    { 
      label: 'System Load', 
      value: '6.2 kW', 
      icon: Gauge, 
      color: 'text-purple-500',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20'
    },
    { 
      label: 'Uptime', 
      value: '99.8%', 
      icon: Clock, 
      color: 'text-cyan-500',
      bgColor: 'bg-cyan-50 dark:bg-cyan-900/20'
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <Button onClick={onBack} variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-slate-800 dark:text-slate-200">{user.name}</h1>
              <p className="text-slate-600 dark:text-slate-400">{user.location}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">{user.efficiency}%</p>
            <p className="text-sm text-slate-600 dark:text-slate-400">Efficiency</p>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
          {metrics.map((metric, index) => (
            <Card key={index} className={`${metric.bgColor} border-0 shadow-sm hover:shadow-md transition-shadow`}>
              <CardContent className="p-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg bg-white dark:bg-slate-800 ${metric.color}`}>
                    <metric.icon className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-sm text-slate-600 dark:text-slate-400">{metric.label}</p>
                    <p className="text-lg font-semibold text-slate-800 dark:text-slate-200">{metric.value}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Power Plant Generation Bar Chart */}
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <div className="p-2 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <span>Monthly Power Generation</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={powerPlantData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="generation" fill="url(#barGradient)" radius={[4, 4, 0, 0]} />
                  <defs>
                    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.8}/>
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* PV Arrays Line Chart */}
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <span>PV Array Performance</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={pvArrayData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="PV1" stroke="#EF4444" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="PV2" stroke="#F97316" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="PV3" stroke="#EAB308" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="PV4" stroke="#22C55E" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="PV5" stroke="#06B6D4" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="PV6" stroke="#3B82F6" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="PV7" stroke="#8B5CF6" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="PV8" stroke="#EC4899" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="PV9" stroke="#6B7280" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="PV10" stroke="#374151" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Historic Voltage Section */}
        <Card className="mt-6 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                <Gauge className="w-5 h-5 text-white" />
              </div>
              <span>Historic Voltage Generation</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={pvArrayData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="PV1" 
                  stroke="url(#voltageGradient)" 
                  strokeWidth={3} 
                  dot={{ fill: '#8B5CF6', strokeWidth: 2 }}
                />
                <defs>
                  <linearGradient id="voltageGradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#EC4899" stopOpacity={0.8}/>
                  </linearGradient>
                </defs>
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default UserDashboard;
