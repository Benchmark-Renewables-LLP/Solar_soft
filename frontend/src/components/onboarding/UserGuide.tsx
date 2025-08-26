import React, { useState } from 'react';
import { X, ChevronLeft, ChevronRight, Play, Eye, BarChart3, Settings, Users, Zap } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface UserGuideProps {
  onClose: () => void;
  isOpen: boolean;
}

const UserGuide: React.FC<UserGuideProps> = ({ onClose, isOpen }) => {
  const [currentStep, setCurrentStep] = useState(0);

  const guideSteps = [
    {
      title: "Welcome to Solar PV Dashboard",
      icon: <Zap className="w-8 h-8 text-yellow-500" />,
      content: (
        <div className="space-y-4">
          <p className="text-slate-700 leading-relaxed">
            Your comprehensive solar power monitoring and management system. This dashboard helps you track, analyze, and optimize your solar installations.
          </p>
          <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-5 rounded-xl border border-blue-200 shadow-sm">
            <h4 className="font-semibold text-blue-800 mb-2">What you can do:</h4>
            <ul className="text-sm text-blue-700 space-y-1 list-disc pl-5">
              <li>Monitor real-time power generation</li>
              <li>Track device performance and efficiency</li>
              <li>Receive alerts for maintenance needs</li>
              <li>Analyze historical data trends</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      title: "Plants Overview",
      icon: <Users className="w-8 h-8 text-green-500" />,
      content: (
        <div className="space-y-4">
          <p className="text-slate-700 leading-relaxed">
            View all your solar installations at a glance. Each plant card shows key metrics and current status.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <Card className="bg-green-50 border-green-200 hover:shadow-md transition rounded-xl">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">Plant Status</span>
                  <Badge variant="outline" className="text-green-600 border-green-300">Online</Badge>
                </div>
                <div className="text-xs text-slate-600 space-y-1">
                  <div>Capacity: 500 kW</div>
                  <div>Current: 425.8 kW</div>
                  <div>Efficiency: 85%</div>
                </div>
              </CardContent>
            </Card>
            <div className="text-sm text-slate-600">
              <p className="font-medium mb-2">Key Metrics:</p>
              <ul className="space-y-1 list-disc pl-5">
                <li>Total Capacity</li>
                <li>Current Generation</li>
                <li>Efficiency Rating</li>
                <li>Device Count</li>
              </ul>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "Device Monitoring",
      icon: <Eye className="w-8 h-8 text-blue-500" />,
      content: (
        <div className="space-y-4">
          <p className="text-slate-700 leading-relaxed">
            Monitor individual devices like inverters, panels, and meters. Click <strong>“View Details”</strong> to see comprehensive analytics.
          </p>
          <div className="bg-blue-50 p-5 rounded-xl border border-blue-200 shadow-sm">
            <h4 className="font-semibold text-blue-800 mb-3">Device Types:</h4>
            <div className="grid grid-cols-3 gap-3 text-sm">
              {[
                { title: "Inverter", desc: "Power conversion" },
                { title: "Panel", desc: "Solar collection" },
                { title: "Meter", desc: "Energy measurement" }
              ].map((d, i) => (
                <div key={i} className="bg-white p-3 rounded-lg border hover:shadow-sm transition text-center">
                  <div className="font-medium">{d.title}</div>
                  <div className="text-xs text-slate-600">{d.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )
    },
    {
      title: "Status Indicators",
      icon: <Settings className="w-8 h-8 text-purple-500" />,
      content: (
        <div className="space-y-5">
          <p className="text-slate-700 leading-relaxed">
            Understand device and plant status indicators to quickly identify issues and opportunities.
          </p>
          <div className="space-y-3">
            {[{ color: "green", label: "Online", desc: "Device is operating normally" },
              { color: "orange", label: "Warning", desc: "Performance issues detected" },
              { color: "red", label: "Offline/Fault", desc: "Device needs attention" },
              { color: "yellow", label: "Maintenance", desc: "Scheduled maintenance mode" }].map((s, i) => (
              <div key={i} className="flex items-center space-x-3">
                <div className={`w-3 h-3 bg-${s.color}-500 rounded-full ${s.color === 'green' ? 'animate-pulse' : ''}`}></div>
                <span className="text-sm"><strong>{s.label}:</strong> {s.desc}</span>
              </div>
            ))}
          </div>
        </div>
      )
    },
    {
      title: "Data Analytics",
      icon: <BarChart3 className="w-8 h-8 text-cyan-500" />,
      content: (
        <div className="space-y-5">
          <p className="text-slate-700 leading-relaxed">
            Access detailed charts and historical data by clicking on any device. Analyze trends and optimize performance.
          </p>
          <div className="bg-gradient-to-r from-cyan-50 to-blue-50 p-5 rounded-xl border border-cyan-200 shadow-sm">
            <h4 className="font-semibold text-cyan-800 mb-2">Available Charts:</h4>
            <div className="grid grid-cols-2 gap-2 text-sm text-cyan-700">
              <div>• Power Generation</div>
              <div>• Panel Voltages</div>
              <div>• Input Currents</div>
              <div>• Output Currents</div>
            </div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <p className="text-sm text-yellow-800">
              <strong>Tip:</strong> Use time range selectors to view data from 1 hour to 1 year for comprehensive analysis.
            </p>
          </div>
        </div>
      )
    },
    {
      title: "Get Started",
      icon: <Play className="w-8 h-8 text-emerald-500" />,
      content: (
        <div className="space-y-5">
          <p className="text-slate-700 leading-relaxed">
            You're all set! Here are your next steps to make the most of your Solar PV Dashboard.
          </p>
          <Card className="bg-emerald-50 border-emerald-200 shadow-sm">
            <CardContent className="p-5">
              <h4 className="font-semibold text-emerald-800 mb-3">Quick Actions:</h4>
              <ul className="text-sm text-emerald-700 space-y-2 list-decimal pl-5">
                <li>Browse your demo plants and devices</li>
                <li>Click "View Details" on any device</li>
                <li>Explore different time ranges in charts</li>
                <li>Check device status indicators</li>
              </ul>
            </CardContent>
          </Card>
          <div className="text-center pt-4">
            <Button onClick={onClose} className="bg-gradient-to-r from-emerald-500 to-green-500 px-6 py-2 text-white font-medium rounded-xl shadow hover:shadow-md transition">
              Start Exploring
            </Button>
          </div>
        </div>
      )
    }
  ];

  const nextStep = () => setCurrentStep((s) => Math.min(s + 1, guideSteps.length - 1));
  const prevStep = () => setCurrentStep((s) => Math.max(s - 1, 0));

  if (!isOpen) return null;

  const currentGuideStep = guideSteps[currentStep];

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-hidden rounded-2xl shadow-xl animate-fadeIn">
        <CardHeader className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {currentGuideStep.icon}
              <CardTitle className="text-xl font-semibold">{currentGuideStep.title}</CardTitle>
            </div>
            <Button
              onClick={onClose}
              variant="ghost"
              size="sm"
              className="text-white hover:bg-white/20 rounded-full"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex items-center justify-between mt-2">
            <span className="text-sm opacity-90">
              Step {currentStep + 1} of {guideSteps.length}
            </span>
            <div className="flex space-x-2">
              {guideSteps.map((_, index) => (
                <div
                  key={index}
                  className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${
                    index === currentStep ? 'bg-white scale-110' : 'bg-white/40'
                  }`}
                />
              ))}
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-6 min-h-[320px] overflow-y-auto">
          {currentGuideStep.content}
        </CardContent>

        <div className="px-6 pb-6">
          <div className="flex justify-between">
            <Button
              onClick={prevStep}
              disabled={currentStep === 0}
              variant="outline"
              className="flex items-center space-x-2 rounded-xl disabled:opacity-50"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Previous</span>
            </Button>
            {currentStep < guideSteps.length - 1 ? (
              <Button
                onClick={nextStep}
                className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-6 py-2 rounded-xl shadow hover:shadow-md transition"
              >
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </Button>
            ) : (
              <Button
                onClick={onClose}
                className="bg-gradient-to-r from-emerald-500 to-green-500 text-white px-6 py-2 rounded-xl shadow hover:shadow-md transition"
              >
                Get Started
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default UserGuide;
