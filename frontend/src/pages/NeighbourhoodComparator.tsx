import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from '@/contexts/AuthContext';
import { 
  MapPin, 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  Sun, 
  Users, 
  Award,
  BarChart3,
  Calendar,
  Filter,
  ArrowLeft,
  Download
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from "recharts";

interface NeighbourData {
  id: string;
  name: string;
  distance: string;
  monthlyGeneration: number;
  yearlyGeneration: number;
  efficiency: number;
  systemSize: number;
  trend: 'up' | 'down' | 'stable';
  rank: number;
  location: string;
  installationYear: number;
}

// Function to generate neighbors based on distance filter
const generateNeighborsByDistance = (maxDistance: string): NeighbourData[] => {
  const maxDistanceKm = parseFloat(maxDistance.replace('km', ''));
  
  const allNeighbours: NeighbourData[] = [
    // Your System (always included)
    {
      id: "your-system",
      name: "Your System",
      distance: "0 km",
      monthlyGeneration: 720,
      yearlyGeneration: 8200,
      efficiency: 87,
      systemSize: 5.8,
      trend: 'stable',
      rank: 4,
      location: "Your Location",
      installationYear: 2020
    },
    // 0.5km radius
    {
      id: "1",
      name: "Solar Villa A",
      distance: "0.2 km",
      monthlyGeneration: 850,
      yearlyGeneration: 9500,
      efficiency: 92,
      systemSize: 6.5,
      trend: 'up',
      rank: 1,
      location: "Oak Street 15",
      installationYear: 2021
    },
    {
      id: "2",
      name: "Green House B",
      distance: "0.4 km",
      monthlyGeneration: 780,
      yearlyGeneration: 8900,
      efficiency: 89,
      systemSize: 6.2,
      trend: 'up',
      rank: 2,
      location: "Pine Avenue 32",
      installationYear: 2022
    },
    // 1km radius
    {
      id: "3",
      name: "Solar Home C",
      distance: "0.8 km",
      monthlyGeneration: 650,
      yearlyGeneration: 7400,
      efficiency: 84,
      systemSize: 5.2,
      trend: 'down',
      rank: 7,
      location: "Maple Drive 78",
      installationYear: 2019
    },
    {
      id: "4",
      name: "EcoFarm D",
      distance: "0.9 km",
      monthlyGeneration: 760,
      yearlyGeneration: 8600,
      efficiency: 88,
      systemSize: 6.0,
      trend: 'up',
      rank: 3,
      location: "Cedar Lane 45",
      installationYear: 2021
    },
    // 2km radius
    {
      id: "5",
      name: "Solar Estate E",
      distance: "1.5 km",
      monthlyGeneration: 920,
      yearlyGeneration: 10200,
      efficiency: 94,
      systemSize: 7.2,
      trend: 'up',
      rank: 1,
      location: "Birch Road 123",
      installationYear: 2023
    },
    {
      id: "6",
      name: "Green Complex F",
      distance: "1.8 km",
      monthlyGeneration: 680,
      yearlyGeneration: 7800,
      efficiency: 85,
      systemSize: 5.5,
      trend: 'stable',
      rank: 6,
      location: "Willow Street 67",
      installationYear: 2020
    },
    // 5km radius
    {
      id: "7",
      name: "Solar Park G",
      distance: "3.2 km",
      monthlyGeneration: 1050,
      yearlyGeneration: 11800,
      efficiency: 96,
      systemSize: 8.5,
      trend: 'up',
      rank: 1,
      location: "Industrial Zone A",
      installationYear: 2023
    },
    {
      id: "8",
      name: "EcoVillage H",
      distance: "4.1 km",
      monthlyGeneration: 820,
      yearlyGeneration: 9200,
      efficiency: 90,
      systemSize: 6.8,
      trend: 'up',
      rank: 2,
      location: "Residential Complex B",
      installationYear: 2022
    },
    {
      id: "9",
      name: "Solar Farm I",
      distance: "4.8 km",
      monthlyGeneration: 1200,
      yearlyGeneration: 13500,
      efficiency: 98,
      systemSize: 10.0,
      trend: 'up',
      rank: 1,
      location: "Agricultural District",
      installationYear: 2024
    }
  ];

  // Filter by distance and sort by rank
  return allNeighbours
    .filter(neighbor => {
      const distance = parseFloat(neighbor.distance.replace(' km', ''));
      return distance <= maxDistanceKm;
    })
    .sort((a, b) => a.rank - b.rank);
};

const monthlyData = [
  { month: 'Jan', yourSystem: 620, average: 680, top: 750 },
  { month: 'Feb', yourSystem: 700, average: 720, top: 820 },
  { month: 'Mar', yourSystem: 780, average: 810, top: 890 },
  { month: 'Apr', yourSystem: 820, average: 850, top: 920 },
  { month: 'May', yourSystem: 850, average: 880, top: 950 },
  { month: 'Jun', yourSystem: 720, average: 760, top: 850 },
  { month: 'Jul', yourSystem: 680, average: 720, top: 800 },
  { month: 'Aug', yourSystem: 740, average: 780, top: 860 },
  { month: 'Sep', yourSystem: 790, average: 820, top: 900 },
  { month: 'Oct', yourSystem: 810, average: 840, top: 920 },
  { month: 'Nov', yourSystem: 750, average: 780, top: 850 },
  { month: 'Dec', yourSystem: 680, average: 710, top: 780 }
];

const efficiencyData = [
  { name: '85%+', value: 35, color: '#10B981' },
  { name: '75-85%', value: 45, color: '#F59E0B' },
  { name: '<75%', value: 20, color: '#EF4444' }
];

const NeighbourhoodComparator = () => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [selectedRange, setSelectedRange] = useState("1km");
  const [selectedMetric, setSelectedMetric] = useState("generation");
  const [sortBy, setSortBy] = useState("rank");

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const mockNeighbours = generateNeighborsByDistance(selectedRange);
  const yourSystem = mockNeighbours.find(n => n.name === "Your System");
  const otherSystems = mockNeighbours.filter(n => n.name !== "Your System");

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down': return <TrendingDown className="w-4 h-4 text-red-500" />;
      default: return <BarChart3 className="w-4 h-4 text-blue-500" />;
    }
  };

  const handleDownloadReport = () => {
    const reportData = {
      generatedDate: new Date().toISOString().split('T')[0],
      reportPeriod: selectedRange,
      yourSystem,
      neighbours: otherSystems,
      summary: {
        totalNeighbours: otherSystems.length,
        yourRank: yourSystem?.rank || 0,
        averageEfficiency: (otherSystems.reduce((sum, n) => sum + n.efficiency, 0) / otherSystems.length).toFixed(1),
        topPerformer: otherSystems.find(n => n.rank === 1)
      }
    };

    const reportContent = `
NEIGHBOURHOOD SOLAR COMPARISON REPORT
====================================

Report Details:
- Generated Date: ${reportData.generatedDate}
- Analysis Radius: ${reportData.reportPeriod}
- Total Neighbours Analyzed: ${reportData.summary.totalNeighbours}

Your System Performance:
- Name: ${yourSystem?.name}
- Monthly Generation: ${yourSystem?.monthlyGeneration} kWh
- Yearly Generation: ${yourSystem?.yearlyGeneration} kWh
- Efficiency: ${yourSystem?.efficiency}%
- System Size: ${yourSystem?.systemSize} kW
- Neighbourhood Rank: #${yourSystem?.rank}
- Installation Year: ${yourSystem?.installationYear}

Neighbourhood Overview:
- Average Efficiency: ${reportData.summary.averageEfficiency}%
- Top Performer: ${reportData.summary.topPerformer?.name} (${reportData.summary.topPerformer?.efficiency}%)

Detailed Neighbour Comparison:
${otherSystems.map(n => `
${n.name} (${n.distance}):
  - Monthly Generation: ${n.monthlyGeneration} kWh
  - Efficiency: ${n.efficiency}%
  - System Size: ${n.systemSize} kW
  - Rank: #${n.rank}
  - Trend: ${n.trend}
  - Location: ${n.location}
`).join('')}

Performance Insights:
- Systems performing better than yours: ${otherSystems.filter(n => n.efficiency > (yourSystem?.efficiency || 0)).length}
- Average system size in area: ${(otherSystems.reduce((sum, n) => sum + n.systemSize, 0) / otherSystems.length).toFixed(1)} kW
- Newest installation: ${Math.max(...otherSystems.map(n => n.installationYear))}
- Oldest installation: ${Math.min(...otherSystems.map(n => n.installationYear))}

Recommendations:
${yourSystem && yourSystem.rank > 3 ? `
- Consider panel cleaning and maintenance
- Check for shading issues
- Review inverter performance
- Contact top performers for optimization tips
` : `
- Excellent performance! You're in the top tier
- Share your optimization strategies with neighbours
- Continue current maintenance practices
`}

Generated by Solar PV Neighbourhood Comparator
Report ID: NCR-${Date.now()}
    `;

    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Neighbourhood_Solar_Report_${selectedRange}_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };
  const getRankBadge = (rank: number) => {
    if (rank <= 3) return <Badge className="bg-gradient-to-r from-yellow-400 to-orange-400 text-white">Top #{rank}</Badge>;
    if (rank <= 5) return <Badge variant="secondary">#{rank}</Badge>;
    return <Badge variant="outline">#{rank}</Badge>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-700">
      {/* Header */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm border-b border-slate-200 dark:border-slate-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button onClick={handleBackToDashboard} variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                  Neighbourhood Solar Comparator
                </h1>
                <p className="text-slate-600 dark:text-slate-400 mt-2">
                  Compare your solar performance with nearby installations
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button onClick={handleDownloadReport} variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Download Report
              </Button>
              <Button onClick={handleLogout} variant="outline">
                Logout
              </Button>
              <Select value={selectedRange} onValueChange={setSelectedRange}>
                <SelectTrigger className="w-40">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0.5km">Within 0.5km ({generateNeighborsByDistance('0.5km').length - 1} homes)</SelectItem>
                  <SelectItem value="1km">Within 1km ({generateNeighborsByDistance('1km').length - 1} homes)</SelectItem>
                  <SelectItem value="2km">Within 2km ({generateNeighborsByDistance('2km').length - 1} homes)</SelectItem>
                  <SelectItem value="5km">Within 5km ({generateNeighborsByDistance('5km').length - 1} homes)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Your System Overview */}
        <Card className="mb-8 bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Award className="w-6 h-6 text-blue-600" />
              <span>Your System Performance</span>
              {yourSystem && getRankBadge(yourSystem.rank)}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {yourSystem && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{yourSystem.monthlyGeneration} kWh</div>
                  <div className="text-sm text-slate-600">This Month</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{yourSystem.efficiency}%</div>
                  <div className="text-sm text-slate-600">Efficiency</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">#{yourSystem.rank}</div>
                  <div className="text-sm text-slate-600">Neighbourhood Rank</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{yourSystem.systemSize} kW</div>
                  <div className="text-sm text-slate-600">System Size</div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Tabs defaultValue="comparison" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="comparison">Performance Comparison</TabsTrigger>
            <TabsTrigger value="trends">Monthly Trends</TabsTrigger>
            <TabsTrigger value="insights">Insights & Tips</TabsTrigger>
          </TabsList>

          <TabsContent value="comparison" className="space-y-6">
            {/* Neighbour Comparison Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {otherSystems.map((neighbour) => (
                <Card key={neighbour.id} className="relative hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-lg">{neighbour.name}</CardTitle>
                        <div className="flex items-center space-x-2 text-sm text-slate-600 mt-1">
                          <MapPin className="w-4 h-4" />
                          <span>{neighbour.distance}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getTrendIcon(neighbour.trend)}
                        {getRankBadge(neighbour.rank)}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-lg font-semibold text-blue-600">
                          {neighbour.monthlyGeneration} kWh
                        </div>
                        <div className="text-xs text-slate-600">Monthly Generation</div>
                      </div>
                      <div>
                        <div className="text-lg font-semibold text-green-600">
                          {neighbour.efficiency}%
                        </div>
                        <div className="text-xs text-slate-600">Efficiency</div>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>System Size</span>
                        <span className="font-medium">{neighbour.systemSize} kW</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Installation Year</span>
                        <span className="font-medium">{neighbour.installationYear}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Location</span>
                        <span className="font-medium text-slate-600">{neighbour.location}</span>
                      </div>
                    </div>

                    <div className="pt-2">
                      <div className="flex justify-between text-sm mb-2">
                        <span>Performance vs Yours</span>
                        <span className={`font-medium ${neighbour.efficiency > (yourSystem?.efficiency || 0) ? 'text-green-600' : 'text-red-600'}`}>
                          {neighbour.efficiency > (yourSystem?.efficiency || 0) ? '+' : ''}
                          {neighbour.efficiency - (yourSystem?.efficiency || 0)}%
                        </span>
                      </div>
                      <Progress 
                        value={Math.min(100, (neighbour.efficiency / 100) * 100)} 
                        className="h-2"
                      />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="trends" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Monthly Performance Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Monthly Performance Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={monthlyData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="yourSystem" stroke="#3B82F6" strokeWidth={3} name="Your System" />
                        <Line type="monotone" dataKey="average" stroke="#10B981" strokeWidth={2} name="Neighbourhood Avg" />
                        <Line type="monotone" dataKey="top" stroke="#F59E0B" strokeWidth={2} name="Top Performer" strokeDasharray="5 5" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Efficiency Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Neighbourhood Efficiency Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={efficiencyData}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          label={({ name, value }) => `${name}: ${value}%`}
                        >
                          {efficiencyData.map((entry, index) => (
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

          <TabsContent value="insights" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Performance Insights */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                    <span>Performance Insights</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <h4 className="font-semibold text-green-800 mb-2">✅ Strong Points</h4>
                    <ul className="text-sm text-green-700 space-y-1">
                      <li>• Consistent monthly performance</li>
                      <li>• Above-average efficiency in summer months</li>
                      <li>• Good system reliability</li>
                    </ul>
                  </div>
                  
                  <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                    <h4 className="font-semibold text-orange-800 mb-2">🔧 Improvement Opportunities</h4>
                    <ul className="text-sm text-orange-700 space-y-1">
                      <li>• Consider panel cleaning to boost efficiency</li>
                      <li>• Monitor for shading issues during winter</li>
                      <li>• Regular inverter maintenance</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>

              {/* Optimization Tips */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Sun className="w-5 h-5 text-yellow-600" />
                    <span>Optimization Tips</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <h5 className="font-medium text-blue-800">Panel Maintenance</h5>
                      <p className="text-sm text-blue-700 mt-1">
                        Regular cleaning can improve efficiency by 3-5%. Top performers clean panels monthly.
                      </p>
                    </div>
                    
                    <div className="p-3 bg-purple-50 rounded-lg">
                      <h5 className="font-medium text-purple-800">System Monitoring</h5>
                      <p className="text-sm text-purple-700 mt-1">
                        Enable real-time monitoring to quickly identify and resolve performance issues.
                      </p>
                    </div>
                    
                    <div className="p-3 bg-teal-50 rounded-lg">
                      <h5 className="font-medium text-teal-800">Seasonal Adjustments</h5>
                      <p className="text-sm text-teal-700 mt-1">
                        Adjust panel angles seasonally for 10-15% performance improvement.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default NeighbourhoodComparator;