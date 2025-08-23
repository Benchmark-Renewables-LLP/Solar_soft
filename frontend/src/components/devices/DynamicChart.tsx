
import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  Activity,
  Zap,
  TrendingUp,
  Plus,
  RotateCcw,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { TimeRange } from "./DeviceDetail";

interface DynamicChartProps {
  timeRange: TimeRange;
  deviceId: string;
}

interface ChartParameter {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  unit: string;
  type: "line" | "bar";
  category: string;
}

const chartParameters: ChartParameter[] = [
  // DC Voltage Parameters
  { id: "dc_voltage", name: "DC Voltage", icon: Zap, color: "#3B82F6", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv1", name: "DC Voltage PV1", icon: Zap, color: "#10B981", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv2", name: "DC Voltage PV2", icon: Zap, color: "#F59E0B", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv3", name: "DC Voltage PV3", icon: Zap, color: "#EF4444", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv4", name: "DC Voltage PV4", icon: Zap, color: "#8B5CF6", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv5", name: "DC Voltage PV5", icon: Zap, color: "#EC4899", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv6", name: "DC Voltage PV6", icon: Zap, color: "#06B6D4", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv7", name: "DC Voltage PV7", icon: Zap, color: "#84CC16", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv8", name: "DC Voltage PV8", icon: Zap, color: "#F97316", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv9", name: "DC Voltage PV9", icon: Zap, color: "#6366F1", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv10", name: "DC Voltage PV10", icon: Zap, color: "#14B8A6", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv11", name: "DC Voltage PV11", icon: Zap, color: "#F43F5E", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_pv12", name: "DC Voltage PV12", icon: Zap, color: "#A855F7", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_mppt1", name: "DC Voltage MPPT1", icon: Zap, color: "#059669", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_mppt2", name: "DC Voltage MPPT2", icon: Zap, color: "#DC2626", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_mppt3", name: "DC Voltage MPPT3", icon: Zap, color: "#7C3AED", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_mppt4", name: "DC Voltage MPPT4", icon: Zap, color: "#DB2777", unit: "V", type: "line", category: "dc" },
  { id: "dc_voltage_mppt5", name: "DC Voltage MPPT5", icon: Zap, color: "#0891B2", unit: "V", type: "line", category: "dc" },

  // AC Parameters
  { id: "ac_voltage_l1", name: "AC Voltage L1", icon: Activity, color: "#EF4444", unit: "V", type: "line", category: "ac" },
  { id: "ac_voltage_l2", name: "AC Voltage L2", icon: Activity, color: "#8B5CF6", unit: "V", type: "line", category: "ac" },
  { id: "ac_voltage_l3", name: "AC Voltage L3", icon: Activity, color: "#EC4899", unit: "V", type: "line", category: "ac" },
  { id: "ac_current_l1", name: "AC Current L1", icon: Activity, color: "#10B981", unit: "A", type: "line", category: "ac" },
  { id: "ac_current_l2", name: "AC Current L2", icon: Activity, color: "#F59E0B", unit: "A", type: "line", category: "ac" },
  { id: "ac_current_l3", name: "AC Current L3", icon: Activity, color: "#06B6D4", unit: "A", type: "line", category: "ac" },

  // Output Parameters
  { id: "total_power", name: "Total Power", icon: TrendingUp, color: "#F59E0B", unit: "kW", type: "line", category: "output" },
  { id: "insulation_resistance", name: "Insulation Resistance Real-time Value", icon: TrendingUp, color: "#06B6D4", unit: "kΩ", type: "line", category: "output" },
  { id: "igbt_temperature", name: "IGBT Inner Temperature", icon: TrendingUp, color: "#EF4444", unit: "°C", type: "line", category: "output" },
];

// Generate sample data
const generateSampleData = (parameterId: string, timeRange: TimeRange) => {
  const dataPoints = timeRange === "1h" ? 60 : timeRange === "24h" ? 24 : timeRange === "7d" ? 7 : 30;
  const data = [];

  for (let i = 0; i < dataPoints; i++) {
    const time = timeRange === "1h" 
      ? `${String(Math.floor(i)).padStart(2, "0")}:${String(i % 60).padStart(2, "0")}`
      : timeRange === "24h" 
      ? `${String(i).padStart(2, "0")}:00`
      : timeRange === "7d" 
      ? `Day ${i + 1}`
      : `Week ${i + 1}`;

    let value = 0;

    if (parameterId === "total_power") {
      const hourFactor = timeRange === "24h" ? i / 24 : 0.5;
      const peakHour = 0.5;
      const powerCurve = Math.exp(-Math.pow((hourFactor - peakHour) * 4, 2));
      value = 75 * powerCurve + Math.random() * 5;
    } else if (parameterId === "insulation_resistance") {
      value = 1000 + Math.sin(i * 0.2) * 100 + Math.random() * 50;
    } else if (parameterId.includes("dc_voltage")) {
      value = 650 + Math.sin(i * 0.5) * 20 + Math.random() * 10;
    } else if (parameterId.includes("ac_voltage")) {
      value = 240 + Math.sin(i * 0.3) * 5 + Math.random() * 3;
    } else if (parameterId.includes("current")) {
      value = 25 + Math.sin(i * 0.4) * 5 + Math.random() * 2;
    } else if (parameterId === "igbt_temperature") {
      value = 65 + Math.sin(i * 0.1) * 10 + Math.random() * 3;
    } else {
      value = Math.random() * 100;
    }

    data.push({ time, value: Number(value.toFixed(2)) });
  }

  return data;
};

export const DynamicChart: React.FC<DynamicChartProps> = ({ timeRange, deviceId }) => {
  const [selectedParameters, setSelectedParameters] = useState<string[]>(["total_power", "insulation_resistance"]);
  const [activeTab, setActiveTab] = useState<string>("output");
  const [selectedInverter, setSelectedInverter] = useState<string>("inverter-1");
  const [isParametersPanelOpen, setIsParametersPanelOpen] = useState(true);
  const [isDcVoltageOpen, setIsDcVoltageOpen] = useState(true);

  // Mock daily data from your reference image
  const dailyStats = {
    dailyYield: "246.3kWh",
    dailyEarning: "2.712kINR", 
    todayFullLoadHours: "3.08h",
    date: "21/06/2025"
  };

  const handleParameterToggle = (parameterId: string) => {
    setSelectedParameters(prev => 
      prev.includes(parameterId) 
        ? prev.filter(id => id !== parameterId)
        : [...prev, parameterId]
    );
  };

  const handleSelectAll = (category: string) => {
    const categoryParams = chartParameters
      .filter(param => param.category === category)
      .map(param => param.id);
    setSelectedParameters(prev => [...new Set([...prev, ...categoryParams])]);
  };

  const handleDeselectAll = (category: string) => {
    const categoryParams = chartParameters
      .filter(param => param.category === category)
      .map(param => param.id);
    setSelectedParameters(prev => prev.filter(id => !categoryParams.includes(id)));
  };

  // Combine data for all selected parameters
  const chartData = React.useMemo(() => {
    if (selectedParameters.length === 0) return [];
    
    const firstParam = selectedParameters[0];
    const baseData = generateSampleData(firstParam, timeRange);
    
    return baseData.map((point, index) => {
      const dataPoint: any = { time: point.time };
      selectedParameters.forEach(paramId => {
        const param = chartParameters.find(p => p.id === paramId);
        if (param) {
          const paramData = generateSampleData(paramId, timeRange);
          dataPoint[paramId] = paramData[index]?.value || 0;
        }
      });
      return dataPoint;
    });
  }, [selectedParameters, timeRange]);

  const dcVoltageParams = chartParameters.filter(param => 
    param.category === "dc" && param.id.includes("voltage")
  );

  const getCurrentTabParams = () => {
    return chartParameters.filter(param => param.category === activeTab);
  };

  return (
    <div className="grid grid-cols-12 gap-6">
      {/* Left Sidebar - Parameter Selection - Made wider */}
      <div className="col-span-4">
        <Card className="h-fit bg-white/90 backdrop-blur-sm border border-slate-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center space-x-2">
                <Plus className="w-5 h-5" />
                <span>Select Parameters({selectedParameters.length})</span>
              </CardTitle>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setIsParametersPanelOpen(!isParametersPanelOpen)}
              >
                {isParametersPanelOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </Button>
            </div>
          </CardHeader>
          
          <Collapsible open={isParametersPanelOpen}>
            <CollapsibleContent>
              <CardContent className="space-y-4">
                {/* Recommended Analysis */}
                <div className="text-sm text-slate-600 mb-4">
                  Recommended Analysis
                </div>

                {/* Analysis Tabs */}
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className="grid w-full grid-cols-3 bg-slate-100">
                    <TabsTrigger value="dc" className="text-xs">DC Analysis</TabsTrigger>
                    <TabsTrigger value="ac" className="text-xs">AC Analysis</TabsTrigger>
                    <TabsTrigger 
                      value="output" 
                      className={`text-xs ${activeTab === "output" ? "bg-slate-800 text-white" : ""}`}
                    >
                      Output Analysis
                    </TabsTrigger>
                  </TabsList>
                </Tabs>

                {/* Inverter Selector */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">Inverter(2)</label>
                  <Select value={selectedInverter} onValueChange={setSelectedInverter}>
                    <SelectTrigger className="w-full bg-white border border-slate-300">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white border border-slate-300 shadow-lg z-50">
                      <SelectItem value="inverter-1">Inverter 1</SelectItem>
                      <SelectItem value="inverter-2">Inverter 2</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* DC Parameters Box */}
                {activeTab === "dc" && (
                  <div className="border border-slate-300 rounded-lg p-3 bg-white/50">
                    <div className="text-sm font-medium text-slate-700 mb-3">DC Parameters (PV Strings & MPPT)</div>
                    
                    {/* DC Voltage Section */}
                    <Collapsible open={isDcVoltageOpen} onOpenChange={setIsDcVoltageOpen}>
                      <CollapsibleTrigger className="flex items-center justify-between w-full text-sm font-medium py-2 hover:bg-slate-50 rounded px-2 mb-2">
                        <span>DC Voltage</span>
                        {isDcVoltageOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </CollapsibleTrigger>
                      <CollapsibleContent className="space-y-2 max-h-32 overflow-y-auto border border-slate-200 rounded bg-slate-50 p-2 mb-3">
                        {dcVoltageParams.slice(0, 5).map((param) => (
                          <div key={param.id} className="flex items-center space-x-2 py-1">
                            <Checkbox
                              id={param.id}
                              checked={selectedParameters.includes(param.id)}
                              onCheckedChange={() => handleParameterToggle(param.id)}
                              className="border-slate-400"
                            />
                            <label 
                              htmlFor={param.id} 
                              className="text-sm text-slate-700 cursor-pointer flex-1"
                            >
                              {param.name}
                            </label>
                          </div>
                        ))}
                        {dcVoltageParams.length > 5 && (
                          <div className="max-h-24 overflow-y-auto space-y-2 border-t border-slate-300 pt-2">
                            {dcVoltageParams.slice(5).map((param) => (
                              <div key={param.id} className="flex items-center space-x-2 py-1">
                                <Checkbox
                                  id={param.id}
                                  checked={selectedParameters.includes(param.id)}
                                  onCheckedChange={() => handleParameterToggle(param.id)}
                                  className="border-slate-400"
                                />
                                <label 
                                  htmlFor={param.id} 
                                  className="text-sm text-slate-700 cursor-pointer flex-1"
                                >
                                  {param.name}
                                </label>
                              </div>
                            ))}
                          </div>
                        )}
                      </CollapsibleContent>
                    </Collapsible>
                  </div>
                )}

                {/* AC Parameters Box */}
                {activeTab === "ac" && (
                  <div className="border border-slate-300 rounded-lg p-3 bg-white/50">
                    <div className="text-sm font-medium text-slate-700 mb-3">AC Parameters</div>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {getCurrentTabParams().slice(0, 5).map((param) => (
                        <div key={param.id} className="flex items-center space-x-2 py-1">
                          <Checkbox
                            id={param.id}
                            checked={selectedParameters.includes(param.id)}
                            onCheckedChange={() => handleParameterToggle(param.id)}
                            className="border-slate-400"
                          />
                          <label 
                            htmlFor={param.id} 
                            className="text-sm text-slate-700 cursor-pointer flex-1"
                          >
                            {param.name}
                          </label>
                        </div>
                      ))}
                      {getCurrentTabParams().length > 5 && (
                        <div className="max-h-20 overflow-y-auto space-y-2 border-t border-slate-300 pt-2">
                          {getCurrentTabParams().slice(5).map((param) => (
                            <div key={param.id} className="flex items-center space-x-2 py-1">
                              <Checkbox
                                id={param.id}
                                checked={selectedParameters.includes(param.id)}
                                onCheckedChange={() => handleParameterToggle(param.id)}
                                className="border-slate-400"
                              />
                              <label 
                                htmlFor={param.id} 
                                className="text-sm text-slate-700 cursor-pointer flex-1"
                              >
                                {param.name}
                              </label>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Output Parameters Box */}
                {activeTab === "output" && (
                  <div className="border border-slate-300 rounded-lg p-3 bg-white/50">
                    <div className="text-sm font-medium text-slate-700 mb-3">Output Parameters</div>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {getCurrentTabParams().slice(0, 5).map((param) => (
                        <div key={param.id} className="flex items-center space-x-2 py-1">
                          <Checkbox
                            id={param.id}
                            checked={selectedParameters.includes(param.id)}
                            onCheckedChange={() => handleParameterToggle(param.id)}
                            className="border-slate-400"
                          />
                          <label 
                            htmlFor={param.id} 
                            className="text-sm text-slate-700 cursor-pointer flex-1"
                          >
                            {param.name}
                          </label>
                        </div>
                      ))}
                      {getCurrentTabParams().length > 5 && (
                        <div className="max-h-20 overflow-y-auto space-y-2 border-t border-slate-300 pt-2">
                          {getCurrentTabParams().slice(5).map((param) => (
                            <div key={param.id} className="flex items-center space-x-2 py-1">
                              <Checkbox
                                id={param.id}
                                checked={selectedParameters.includes(param.id)}
                                onCheckedChange={() => handleParameterToggle(param.id)}
                                className="border-slate-400"
                              />
                              <label 
                                htmlFor={param.id} 
                                className="text-sm text-slate-700 cursor-pointer flex-1"
                              >
                                {param.name}
                              </label>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex space-x-2 pt-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleSelectAll(activeTab)}
                    className="flex-1"
                  >
                    Select All
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleDeselectAll(activeTab)}
                    className="flex-1"
                  >
                    Clear All
                  </Button>
                </div>
              </CardContent>
            </CollapsibleContent>
          </Collapsible>
        </Card>
      </div>

      {/* Right Chart Area - Made narrower to accommodate wider sidebar */}
      <div className="col-span-8">
        <Card className="bg-white/90 backdrop-blur-sm border border-slate-200">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl">Inverter Chart SN: DEV-2</CardTitle>
                <div className="text-sm text-slate-600 mt-2">
                  <span className="font-medium">{dailyStats.date}</span>
                </div>
                <div className="flex space-x-6 mt-2 text-sm">
                  <span>Daily Yield: <span className="font-semibold text-blue-600">{dailyStats.dailyYield}</span></span>
                  <span>Daily Earning: <span className="font-semibold text-green-600">{dailyStats.dailyEarning}</span></span>
                  <span>Today Full Load Hours: <span className="font-semibold text-purple-600">{dailyStats.todayFullLoadHours}</span></span>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {selectedParameters.length > 0 ? (
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis 
                      dataKey="time" 
                      stroke="#64748b"
                      fontSize={12}
                    />
                    <YAxis 
                      stroke="#64748b"
                      fontSize={12}
                    />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <Legend />
                    {selectedParameters.map((paramId) => {
                      const param = chartParameters.find(p => p.id === paramId);
                      if (!param) return null;
                      
                      return (
                        <Line
                          key={paramId}
                          type="monotone"
                          dataKey={paramId}
                          stroke={param.color}
                          strokeWidth={2}
                          dot={false}
                          name={`${param.name} (${param.unit})`}
                        />
                      );
                    })}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-96 flex items-center justify-center bg-slate-50 rounded-lg border-2 border-dashed border-slate-300">
                <div className="text-center">
                  <TrendingUp className="w-12 h-12 text-slate-400 mx-auto mb-3" />
                  <p className="text-slate-600">Select parameters to view chart</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
