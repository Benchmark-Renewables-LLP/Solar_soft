import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AreaChart, Area, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, Zap, DollarSign, Leaf, Sun, CloudRain, Wind, ArrowLeft, Download, Calendar, Target, Activity, TreePine, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

const Analytics = () => {
  const { isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  const navigate = useNavigate();
  const [timeRange, setTimeRange] = useState('30d');

  const handleBackToDashboard = () => {
    navigate('/');
  };

  // Carbon offset and environmental data
  const carbonData = {
    totalOffset: 2.4, // tons of CO2
    treesEquivalent: 31,
    carsOffRoad: 5.2, // days
    monthlyOffset: 0.2,
    yearlyProjection: 2.9
  };

  // Error history data
  const errorHistory = [
    { date: '2024-01-25', type: 'Communication Error', device: 'Inverter #3', severity: 'medium', resolved: true },
    { date: '2024-01-20', type: 'Voltage Fluctuation', device: 'Panel String A', severity: 'low', resolved: true },
    { date: '2024-01-15', type: 'Maintenance Required', device: 'Inverter #1', severity: 'high', resolved: false },
    { date: '2024-01-10', type: 'Temperature Alert', device: 'Panel String B', severity: 'medium', resolved: true },
    { date: '2024-01-05', type: 'Grid Disconnection', device: 'Main Switch', severity: 'high', resolved: true }
  ];

  // Mock data for different analytics
  const performanceData = [
    { date: '2024-01-01', generation: 45.2, efficiency: 89.5, revenue: 125.60 },
    { date: '2024-01-02', generation: 52.1, efficiency: 91.2, revenue: 144.85 },
    { date: '2024-01-03', generation: 48.7, efficiency: 88.9, revenue: 135.38 },
    { date: '2024-01-04', generation: 55.3, efficiency: 93.1, revenue: 153.73 },
    { date: '2024-01-05', generation: 41.8, efficiency: 87.2, revenue: 116.21 },
    { date: '2024-01-06', generation: 58.9, efficiency: 94.7, revenue: 163.75 },
    { date: '2024-01-07', generation: 47.3, efficiency: 89.8, revenue: 131.49 }
  ];

  const monthlyData = [
    { month: 'Jan', generation: 1250, target: 1200, revenue: 437.50 },
    { month: 'Feb', generation: 1380, target: 1300, revenue: 483.00 },
    { month: 'Mar', generation: 1520, target: 1450, revenue: 532.00 },
    { month: 'Apr', generation: 1680, target: 1600, revenue: 588.00 },
    { month: 'May', generation: 1750, target: 1700, revenue: 612.50 },
    { month: 'Jun', generation: 1820, target: 1750, revenue: 637.00 }
  ];

  const energyBreakdown = [
    { name: 'Solar Generation', value: 78.5, color: '#3B82F6' },
    { name: 'Grid Consumption', value: 21.5, color: '#EF4444' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button onClick={handleBackToDashboard} variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
                <p className="text-gray-600">Comprehensive performance insights and environmental impact</p>
              </div>
            </div>
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Export Report
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="environmental">Environmental</TabsTrigger>
            <TabsTrigger value="errors">Error History</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-5 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Generation</CardTitle>
                  <Zap className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">12,847 kWh</div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-green-600 flex items-center">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      +8.2% from last month
                    </span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Carbon Offset</CardTitle>
                  <TreePine className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{carbonData.totalOffset} tons</div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-green-600">≈ {carbonData.treesEquivalent} trees planted</span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">$4,296</div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-green-600 flex items-center">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      +12.5% from target
                    </span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Efficiency</CardTitle>
                  <Target className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">91.2%</div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-green-600 flex items-center">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      +2.1% improvement
                    </span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">System Health</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">98.5%</div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-green-600">All systems operational</span>
                  </p>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Monthly Performance */}
              <Card>
                <CardHeader>
                  <CardTitle>Monthly Performance</CardTitle>
                  <CardDescription>Generation vs targets over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={monthlyData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="generation" fill="#3B82F6" name="Generation (kWh)" />
                        <Bar dataKey="target" fill="#10B981" name="Target (kWh)" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Energy Mix */}
              <Card>
                <CardHeader>
                  <CardTitle>Energy Mix</CardTitle>
                  <CardDescription>Solar vs grid consumption</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={energyBreakdown}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          dataKey="value"
                          label={({ name, value }) => `${name}: ${value}%`}
                        >
                          {energyBreakdown.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="performance">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Performance Trends */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>Performance Trends</CardTitle>
                  <CardDescription>Energy generation and efficiency over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={performanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString()} />
                        <YAxis />
                        <Tooltip 
                          labelFormatter={(date) => new Date(date).toLocaleDateString()}
                          formatter={(value, name) => [
                            name === 'generation' ? `${value} kWh` : 
                            name === 'efficiency' ? `${value}%` : `$${value}`,
                            String(name).charAt(0).toUpperCase() + String(name).slice(1)
                          ]}
                        />
                        <Area type="monotone" dataKey="generation" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
                        <Area type="monotone" dataKey="efficiency" stroke="#10B981" fill="#10B981" fillOpacity={0.3} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="environmental">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Carbon Impact */}
              <Card>
                <CardHeader>
                  <CardTitle>Environmental Impact</CardTitle>
                  <CardDescription>Your contribution to sustainability</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Monthly CO₂ Saved</span>
                      <span className="font-medium">{carbonData.monthlyOffset} tons</span>
                    </div>
                    <Progress value={67} />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="text-center p-2 bg-green-50 rounded">
                      <TreePine className="h-6 w-6 mx-auto text-green-600 mb-1" />
                      <p className="font-medium">{carbonData.treesEquivalent}</p>
                      <p className="text-xs text-muted-foreground">Trees Equivalent</p>
                    </div>
                    <div className="text-center p-2 bg-blue-50 rounded">
                      <Leaf className="h-6 w-6 mx-auto text-blue-600 mb-1" />
                      <p className="font-medium">{carbonData.carsOffRoad}</p>
                      <p className="text-xs text-muted-foreground">Car Days Off Road</p>
                    </div>
                  </div>
                  
                  <div className="border-t pt-2">
                    <p className="text-sm text-muted-foreground">Yearly Projection</p>
                    <p className="text-lg font-bold text-green-600">{carbonData.yearlyProjection} tons CO₂</p>
                  </div>
                </CardContent>
              </Card>

              {/* Environmental Metrics */}
              <Card>
                <CardHeader>
                  <CardTitle>Sustainability Metrics</CardTitle>
                  <CardDescription>Environmental benefits breakdown</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Sun className="h-4 w-4 text-yellow-500" />
                        <span className="text-sm">Clean Energy Generated</span>
                      </div>
                      <span className="font-medium">12.8 MWh</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Wind className="h-4 w-4 text-blue-500" />
                        <span className="text-sm">Air Quality Improved</span>
                      </div>
                      <span className="font-medium">92%</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Leaf className="h-4 w-4 text-green-500" />
                        <span className="text-sm">Carbon Footprint Reduced</span>
                      </div>
                      <span className="font-medium">67%</span>
                    </div>
                  </div>
                  
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-green-800 mb-2">🌍 Global Impact</h4>
                    <p className="text-sm text-green-700">
                      Your solar system prevented <strong>2.4 tons</strong> of CO₂ from entering the atmosphere, 
                      equivalent to removing a car from the road for <strong>5.2 days</strong>.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="errors">
            <Card>
              <CardHeader>
                <CardTitle>System Error History</CardTitle>
                <CardDescription>Recent system alerts and maintenance events</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {errorHistory.map((error, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                      <div className="flex items-center space-x-3">
                        {error.resolved ? (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        ) : error.severity === 'high' ? (
                          <AlertTriangle className="h-5 w-5 text-red-600" />
                        ) : (
                          <Clock className="h-5 w-5 text-yellow-600" />
                        )}
                        <div>
                          <p className="font-medium">{error.type}</p>
                          <p className="text-sm text-muted-foreground">{error.device}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge 
                          variant={
                            error.severity === 'high' ? 'destructive' : 
                            error.severity === 'medium' ? 'default' : 
                            'secondary'
                          }
                        >
                          {error.severity}
                        </Badge>
                        <p className="text-sm text-muted-foreground mt-1">{error.date}</p>
                      </div>
                    </div>
                  ))}
                </div>
                
                {errorHistory.filter(e => !e.resolved).length > 0 && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <h4 className="font-semibold text-red-800 mb-2">⚠️ Action Required</h4>
                    <p className="text-sm text-red-700">
                      You have {errorHistory.filter(e => !e.resolved).length} unresolved issue(s) 
                      that require immediate attention.
                    </p>
                    <Button size="sm" className="mt-2" variant="destructive">
                      Schedule Maintenance
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Analytics;