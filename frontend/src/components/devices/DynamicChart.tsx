import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import {
  Activity,
  Zap,
  TrendingUp,
  Calendar,
  Download,
  Plus,
  RotateCcw,
  ChevronDown,
  AlertTriangle,
  CheckCircle,
  Clock,
} from "lucide-react";
import { TimeRange } from "./DeviceDetail";
import { TimeRangeSelector } from "./TimeRangeSelector";
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
  {
    id: "dc_voltage",
    name: "DC Voltage",
    icon: Zap,
    color: "#3B82F6",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv1",
    name: "DC Voltage PV1",
    icon: Zap,
    color: "#10B981",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv2",
    name: "DC Voltage PV2",
    icon: Zap,
    color: "#F59E0B",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv3",
    name: "DC Voltage PV3",
    icon: Zap,
    color: "#EF4444",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv4",
    name: "DC Voltage PV4",
    icon: Zap,
    color: "#8B5CF6",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv5",
    name: "DC Voltage PV5",
    icon: Zap,
    color: "#EC4899",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv6",
    name: "DC Voltage PV6",
    icon: Zap,
    color: "#06B6D4",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv7",
    name: "DC Voltage PV7",
    icon: Zap,
    color: "#84CC16",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv8",
    name: "DC Voltage PV8",
    icon: Zap,
    color: "#F97316",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv9",
    name: "DC Voltage PV9",
    icon: Zap,
    color: "#6366F1",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv10",
    name: "DC Voltage PV10",
    icon: Zap,
    color: "#14B8A6",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv11",
    name: "DC Voltage PV11",
    icon: Zap,
    color: "#F43F5E",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_pv12",
    name: "DC Voltage PV12",
    icon: Zap,
    color: "#A855F7",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_mppt1",
    name: "DC Voltage MPPT1",
    icon: Zap,
    color: "#059669",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_mppt2",
    name: "DC Voltage MPPT2",
    icon: Zap,
    color: "#DC2626",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_mppt3",
    name: "DC Voltage MPPT3",
    icon: Zap,
    color: "#7C3AED",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_mppt4",
    name: "DC Voltage MPPT4",
    icon: Zap,
    color: "#DB2777",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_mppt5",
    name: "DC Voltage MPPT5",
    icon: Zap,
    color: "#0891B2",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_voltage_mppt6",
    name: "DC Voltage MPPT6",
    icon: Zap,
    color: "#65A30D",
    unit: "V",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_current",
    name: "DC Current",
    icon: Zap,
    color: "#F59E0B",
    unit: "A",
    type: "line",
    category: "dc",
  },
  {
    id: "dc_power",
    name: "DC Power",
    icon: Zap,
    color: "#EF4444",
    unit: "kW",
    type: "line",
    category: "dc",
  },

  // AC Parameters
  {
    id: "ac_voltage_l1",
    name: "AC Voltage L1",
    icon: Activity,
    color: "#EF4444",
    unit: "V",
    type: "line",
    category: "ac",
  },
  {
    id: "ac_voltage_l2",
    name: "AC Voltage L2",
    icon: Activity,
    color: "#8B5CF6",
    unit: "V",
    type: "line",
    category: "ac",
  },
  {
    id: "ac_voltage_l3",
    name: "AC Voltage L3",
    icon: Activity,
    color: "#EC4899",
    unit: "V",
    type: "line",
    category: "ac",
  },
  {
    id: "ac_current_l1",
    name: "AC Current L1",
    icon: Activity,
    color: "#10B981",
    unit: "A",
    type: "line",
    category: "ac",
  },
  {
    id: "ac_current_l2",
    name: "AC Current L2",
    icon: Activity,
    color: "#F59E0B",
    unit: "A",
    type: "line",
    category: "ac",
  },
  {
    id: "ac_current_l3",
    name: "AC Current L3",
    icon: Activity,
    color: "#06B6D4",
    unit: "A",
    type: "line",
    category: "ac",
  },
  {
    id: "ac_output_frequency",
    name: "AC Output Frequency",
    icon: Activity,
    color: "#84CC16",
    unit: "Hz",
    type: "line",
    category: "ac",
  },

  // Output Parameters
  {
    id: "total_power",
    name: "Total Power",
    icon: TrendingUp,
    color: "#F59E0B",
    unit: "kW",
    type: "line",
    category: "output",
  },
  {
    id: "reactive_power",
    name: "Reactive Power",
    icon: TrendingUp,
    color: "#8B5CF6",
    unit: "kVAR",
    type: "line",
    category: "output",
  },
  {
    id: "today_yield",
    name: "Today Yield",
    icon: TrendingUp,
    color: "#10B981",
    unit: "kWh",
    type: "line",
    category: "output",
  },
  {
    id: "total_yield",
    name: "Total Yield",
    icon: TrendingUp,
    color: "#06B6D4",
    unit: "MWh",
    type: "line",
    category: "output",
  },
  {
    id: "igbt_temperature",
    name: "IGBT Inner Temperature",
    icon: TrendingUp,
    color: "#EF4444",
    unit: "°C",
    type: "line",
    category: "output",
  },
  {
    id: "string_dispersion",
    name: "String Dispersion Rate",
    icon: TrendingUp,
    color: "#EC4899",
    unit: "%",
    type: "line",
    category: "output",
  },
  {
    id: "insulation_resistance",
    name: "Insulation Resistance Real-time Value",
    icon: TrendingUp,
    color: "#06B6D4",
    unit: "kΩ",
    type: "line",
    category: "output",
  },
];

// Generate sample data based on the parameter type
const generateSampleData = (parameterId: string, timeRange: TimeRange) => {
  const dataPoints =
    timeRange === "1h"
      ? 60
      : timeRange === "24h"
      ? 24
      : timeRange === "7d"
      ? 7
      : 30;
  const data = [];

  for (let i = 0; i < dataPoints; i++) {
    const time =
      timeRange === "1h"
        ? `${String(Math.floor(i)).padStart(2, "0")}:${String(i % 60).padStart(
            2,
            "0"
          )}`
        : timeRange === "24h"
        ? `${String(i).padStart(2, "0")}:00`
        : timeRange === "7d"
        ? `Day ${i + 1}`
        : `Week ${i + 1}`;

    let value = 0;

    // Generate realistic data patterns
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

// Mock DC data for PV units - more comprehensive
const dcData = [
  { parameter: "PV1 Voltage", value: "642.3 V", status: "Normal" },
  { parameter: "PV1 Current", value: "8.5 A", status: "Normal" },
  { parameter: "PV1 Power", value: "5.46 kW", status: "Normal" },
  { parameter: "PV2 Voltage", value: "638.7 V", status: "Normal" },
  { parameter: "PV2 Current", value: "8.2 A", status: "Normal" },
  { parameter: "PV2 Power", value: "5.24 kW", status: "Normal" },
  { parameter: "PV3 Voltage", value: "645.1 V", status: "Normal" },
  { parameter: "PV3 Current", value: "8.7 A", status: "Normal" },
  { parameter: "PV3 Power", value: "5.61 kW", status: "Normal" },
  { parameter: "PV4 Voltage", value: "640.9 V", status: "Normal" },
  { parameter: "PV4 Current", value: "8.4 A", status: "Normal" },
  { parameter: "PV4 Power", value: "5.38 kW", status: "Normal" },
  { parameter: "MPPT1 Voltage", value: "645.1 V", status: "Normal" },
  { parameter: "MPPT1 Current", value: "17.2 A", status: "Normal" },
  { parameter: "MPPT2 Voltage", value: "641.8 V", status: "Normal" },
  { parameter: "MPPT2 Current", value: "16.8 A", status: "Normal" },
  { parameter: "Total DC Power", value: "34.2 kW", status: "Normal" },
];

const acData = [
  { parameter: "AC Voltage L1", value: "239.4 V", status: "Normal" },
  { parameter: "AC Current L1", value: "75.2 A", status: "Normal" },
  { parameter: "AC Power L1", value: "18.0 kW", status: "Normal" },
  { parameter: "AC Voltage L2", value: "240.1 V", status: "Normal" },
  { parameter: "AC Current L2", value: "74.8 A", status: "Normal" },
  { parameter: "AC Power L2", value: "17.9 kW", status: "Normal" },
  { parameter: "AC Voltage L3", value: "238.9 V", status: "Normal" },
  { parameter: "AC Current L3", value: "75.5 A", status: "Normal" },
  { parameter: "AC Power L3", value: "18.0 kW", status: "Normal" },
  { parameter: "AC Frequency", value: "50.02 Hz", status: "Normal" },
  { parameter: "Total AC Power", value: "53.9 kW", status: "Normal" },
  { parameter: "Power Factor", value: "0.98", status: "Normal" },
  { parameter: "Efficiency", value: "94.2%", status: "Normal" },
];

// Mock alarm history data
const alarmHistory = [
  {
    id: 1,
    time: "2025-06-21 14:30:15",
    type: "Warning",
    message: "IGBT Temperature High",
    status: "Resolved",
    duration: "5 min",
  },
  {
    id: 2,
    time: "2025-06-21 12:15:42",
    type: "Info",
    message: "Grid Frequency Variation",
    status: "Resolved",
    duration: "2 min",
  },
  {
    id: 3,
    time: "2025-06-21 09:45:23",
    type: "Warning",
    message: "String Dispersion Rate High",
    status: "Resolved",
    duration: "8 min",
  },
  {
    id: 4,
    time: "2025-06-20 16:22:11",
    type: "Error",
    message: "DC Isolation Fault",
    status: "Resolved",
    duration: "15 min",
  },
  {
    id: 5,
    time: "2025-06-20 11:08:35",
    type: "Info",
    message: "System Maintenance Mode",
    status: "Resolved",
    duration: "30 min",
  },
];

export const DynamicChart: React.FC<DynamicChartProps> = ({
  timeRange,
  deviceId,
}) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState<TimeRange>("24h");

  const [selectedParameters, setSelectedParameters] = useState<string[]>([
    "total_power",
    "insulation_resistance",
  ]);
  const [viewMode, setViewMode] = useState<
    "recommended" | "dc" | "ac" | "output"
  >("recommended");
  const [chartData, setChartData] = useState<any[]>([]);
  const [expandedCategory, setExpandedCategory] =
    useState<string>("DC Voltage");

  useEffect(() => {
    const newData = generateSampleData(
      selectedParameters[0] || "total_power",
      timeRange
    );
    setChartData(newData);
  }, [selectedParameters, timeRange]);

  const handleParameterToggle = (parameterId: string) => {
    setSelectedParameters((prev) => {
      if (prev.includes(parameterId)) {
        return prev.filter((id) => id !== parameterId);
      } else {
        return [...prev, parameterId].slice(0, 2);
      }
    });
  };

  const getParametersByCategory = (category: string) => {
    switch (category) {
      case "dc":
        return chartParameters.filter((p) => p.category === "dc");
      case "ac":
        return chartParameters.filter((p) => p.category === "ac");
      case "output":
        return chartParameters.filter((p) => p.category === "output");
      default:
        return chartParameters.filter((p) => p.category === "output");
    }
  };

  const getAlarmIcon = (type: string) => {
    switch (type) {
      case "Error":
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case "Warning":
        return <AlertTriangle className="w-4 h-4 text-orange-500" />;
      case "Info":
        return <CheckCircle className="w-4 h-4 text-blue-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    return status === "Normal" ? "text-green-600" : "text-red-600";
  };

  return (
    <div className="space-y-6">
      {/* DC/AC Data Tables */}

      {/* Dynamic Chart Section */}
      <div className="grid grid-cols-4 gap-6">
        {/* Left Sidebar - Parameter Selection */}
        <div className="col-span-1">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium">
                  Select Parameters(2)
                </CardTitle>
                <div className="flex items-center space-x-1">
                  <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                    <Plus className="w-3 h-3" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                    <RotateCcw className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              {/* Analysis Type Tabs */}
              <Tabs
                value={viewMode}
                onValueChange={(value: any) => setViewMode(value)}
                className="mb-4"
              >
                <div className="space-y-2">
                  <h4 className="text-xs font-medium text-slate-600 mb-2">
                    Recommended Analysis
                  </h4>
                  <div className="grid grid-cols-3 gap-1">
                    <Button
                      variant={viewMode === "dc" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setViewMode("dc")}
                      className="text-xs h-7"
                    >
                      DC Analysis
                    </Button>
                    <Button
                      variant={viewMode === "ac" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setViewMode("ac")}
                      className="text-xs h-7"
                    >
                      AC Analysis
                    </Button>
                    <Button
                      variant={viewMode === "output" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setViewMode("output")}
                      className="text-xs h-7"
                    >
                      Output Analysis
                    </Button>
                  </div>
                </div>
              </Tabs>

              {/* Inverter Dropdown */}
              <div className="mb-4">
                <Button
                  variant="outline"
                  className="w-full justify-between text-xs h-8"
                >
                  Inverter(2)
                  <ChevronDown className="w-3 h-3" />
                </Button>
              </div>

              {/* Parameter Categories */}
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {/* DC Voltage Category */}
                <div>
                  <Button
                    variant="ghost"
                    onClick={() =>
                      setExpandedCategory(
                        expandedCategory === "DC Voltage" ? "" : "DC Voltage"
                      )
                    }
                    className="w-full justify-between text-xs h-7 px-2"
                  >
                    <div className="flex items-center space-x-2">
                      <ChevronDown
                        className={`w-3 h-3 transition-transform ${
                          expandedCategory === "DC Voltage" ? "rotate-180" : ""
                        }`}
                      />
                      <span>DC Voltage</span>
                    </div>
                  </Button>
                  {expandedCategory === "DC Voltage" && (
                    <div className="ml-4 space-y-1 mt-1">
                      {chartParameters
                        .filter((p) => p.category === "dc")
                        .map((param) => (
                          <div
                            key={param.id}
                            className="flex items-center space-x-2"
                          >
                            <input
                              type="checkbox"
                              id={param.id}
                              checked={selectedParameters.includes(param.id)}
                              onChange={() => handleParameterToggle(param.id)}
                              className="rounded border-gray-300 h-3 w-3"
                            />
                            <label
                              htmlFor={param.id}
                              className="text-xs cursor-pointer"
                            >
                              {param.name}
                            </label>
                          </div>
                        ))}
                    </div>
                  )}
                </div>

                {/* AC Category */}
                <div>
                  <Button
                    variant="ghost"
                    onClick={() =>
                      setExpandedCategory(
                        expandedCategory === "AC Parameters"
                          ? ""
                          : "AC Parameters"
                      )
                    }
                    className="w-full justify-between text-xs h-7 px-2"
                  >
                    <div className="flex items-center space-x-2">
                      <ChevronDown
                        className={`w-3 h-3 transition-transform ${
                          expandedCategory === "AC Parameters"
                            ? "rotate-180"
                            : ""
                        }`}
                      />
                      <span>AC Parameters</span>
                    </div>
                  </Button>
                  {expandedCategory === "AC Parameters" && (
                    <div className="ml-4 space-y-1 mt-1">
                      {chartParameters
                        .filter((p) => p.category === "ac")
                        .map((param) => (
                          <div
                            key={param.id}
                            className="flex items-center space-x-2"
                          >
                            <input
                              type="checkbox"
                              id={param.id}
                              checked={selectedParameters.includes(param.id)}
                              onChange={() => handleParameterToggle(param.id)}
                              className="rounded border-gray-300 h-3 w-3"
                            />
                            <label
                              htmlFor={param.id}
                              className="text-xs cursor-pointer"
                            >
                              {param.name}
                            </label>
                          </div>
                        ))}
                    </div>
                  )}
                </div>

                {/* Output Category */}
                <div>
                  <Button
                    variant="ghost"
                    onClick={() =>
                      setExpandedCategory(
                        expandedCategory === "Output Parameters"
                          ? ""
                          : "Output Parameters"
                      )
                    }
                    className="w-full justify-between text-xs h-7 px-2"
                  >
                    <div className="flex items-center space-x-2">
                      <ChevronDown
                        className={`w-3 h-3 transition-transform ${
                          expandedCategory === "Output Parameters"
                            ? "rotate-180"
                            : ""
                        }`}
                      />
                      <span>Output Parameters</span>
                    </div>
                  </Button>
                  {expandedCategory === "Output Parameters" && (
                    <div className="ml-4 space-y-1 mt-1">
                      {chartParameters
                        .filter((p) => p.category === "output")
                        .map((param) => (
                          <div
                            key={param.id}
                            className="flex items-center space-x-2"
                          >
                            <input
                              type="checkbox"
                              id={param.id}
                              checked={selectedParameters.includes(param.id)}
                              onChange={() => handleParameterToggle(param.id)}
                              className="rounded border-gray-300 h-3 w-3"
                            />
                            <label
                              htmlFor={param.id}
                              className="text-xs cursor-pointer"
                            >
                              {param.name}
                            </label>
                          </div>
                        ))}
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Side - Chart */}
        <div className="col-span-3">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <h3 className="text-lg font-semibold">
                    Inverter Chart SN: {deviceId.slice(-6).toUpperCase()}
                  </h3>
                  <span className="text-sm text-slate-500">21/06/2025</span>
                </div>
                <div className="flex items-center space-x-2"></div>
              </div>

              <div className="flex items-center space-x-8 text-sm text-slate-600 mt-2">
                <span>Daily Yield : 246.5kWh</span>
                <span>Daily Earning : 2.712kINR</span>
                <span>Today Full Load Hours : 3.08h</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis
                      dataKey="time"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 12, fill: "#666" }}
                    />
                    <YAxis
                      yAxisId="left"
                      orientation="left"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 12, fill: "#666" }}
                      label={{
                        value: "kW",
                        angle: -90,
                        position: "insideLeft",
                      }}
                    />
                    <YAxis
                      yAxisId="right"
                      orientation="right"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 12, fill: "#666" }}
                      label={{
                        value: "kΩ",
                        angle: 90,
                        position: "insideRight",
                      }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "white",
                        border: "1px solid #e2e8f0",
                        borderRadius: "6px",
                        fontSize: "12px",
                      }}
                    />

                    {selectedParameters.includes("total_power") && (
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="value"
                        stroke="#F59E0B"
                        strokeWidth={2}
                        dot={false}
                        name="Total Power"
                      />
                    )}

                    {selectedParameters.includes("insulation_resistance") && (
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="value"
                        stroke="#06B6D4"
                        strokeWidth={2}
                        dot={false}
                        strokeDasharray="5 5"
                        name="Insulation Resistance Real-time Value"
                      />
                    )}
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="flex items-center justify-center space-x-6 mt-4 text-sm">
                {selectedParameters.includes("total_power") && (
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-0.5 bg-orange-500"></div>
                    <span>Total Power</span>
                  </div>
                )}
                {selectedParameters.includes("insulation_resistance") && (
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-0.5 bg-cyan-500 border-dashed border-t-2"></div>
                    <span>Insulation Resistance Real-time Value</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* DC Data Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="w-5 h-5 text-blue-600" />
              <span>DC Parameters (PV Strings & MPPT)</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Parameter</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {dcData.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">
                      {item.parameter}
                    </TableCell>
                    <TableCell>{item.value}</TableCell>
                    <TableCell className={getStatusColor(item.status)}>
                      {item.status}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* AC Data Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-green-600" />
              <span>AC Parameters (3-Phase Output)</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Parameter</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {acData.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">
                      {item.parameter}
                    </TableCell>
                    <TableCell>{item.value}</TableCell>
                    <TableCell className={getStatusColor(item.status)}>
                      {item.status}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      {/* Alarm History Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            <span>Alarm History</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Message</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Duration</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {alarmHistory.map((alarm) => (
                <TableRow key={alarm.id}>
                  <TableCell className="font-mono text-sm">
                    {alarm.time}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      {getAlarmIcon(alarm.type)}
                      <span>{alarm.type}</span>
                    </div>
                  </TableCell>
                  <TableCell>{alarm.message}</TableCell>
                  <TableCell>
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        alarm.status === "Resolved"
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {alarm.status}
                    </span>
                  </TableCell>
                  <TableCell>{alarm.duration}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};
