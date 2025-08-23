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
          <p className="text-slate-600">
            Your comprehensive solar power monitoring and management system. This dashboard helps you track, analyze, and optimize your solar installations.
          </p>
          <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-4 rounded-lg border border-blue-200">
            <h4 className="font-semibold text-blue-800 mb-2">What you can do:</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Monitor real-time power generation</li>
              <li>• Track device performance and efficiency</li>
              <li>• Receive alerts for maintenance needs</li>
              <li>• Analyze historical data trends</li>
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
          <p className="text-slate-600">
            View all your solar installations at a glance. Each plant card shows key metrics and current status.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <Card className="bg-green-50 border-green-200">
              <CardContent className="p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">Plant Status</span>
                  <Badge variant="outline" className="text-green-600 border-green-300">Online</Badge>
                </div>
                <div className="text-xs text-slate-600">
                  <div>Capacity: 500 kW</div>
                  <div>Current: 425.8 kW</div>
                  <div>Efficiency: 85%</div>
                </div>
              </CardContent>
            </Card>
            <div className="text-sm text-slate-600">
              <p className="font-medium mb-2">Key Metrics:</p>
              <ul className="space-y-1">
                <li>• Total Capacity</li>
                <li>• Current Generation</li>
                <li>• Efficiency Rating</li>
                <li>• Device Count</li>
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
          <p className="text-slate-600">
            Monitor individual devices like inverters, panels, and meters. Click "View Details" to see comprehensive analytics.
          </p>
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h4 className="font-semibold text-blue-800 mb-2">Device Types:</h4>
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div className="text-center">
                <div className="bg-white p-2 rounded border">
                  <div className="font-medium">Inverter</div>
                  <div className="text-xs text-slate-600">Power conversion</div>
                </div>
              </div>
              <div className="text-center">
                <div className="bg-white p-2 rounded border">
                  <div className="font-medium">Panel</div>
                  <div className="text-xs text-slate-600">Solar collection</div>
                </div>
              </div>
              <div className="text-center">
                <div className="bg-white p-2 rounded border">
                  <div className="font-medium">Meter</div>
                  <div className="text-xs text-slate-600">Energy measurement</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "Status Indicators",
      icon: <Settings className="w-8 h-8 text-purple-500" />,
      content: (
        <div className="space-y-4">
          <p className="text-slate-600">
            Understand device and plant status indicators to quickly identify issues and opportunities.
          </p>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm"><strong>Online:</strong> Device is operating normally</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
              <span className="text-sm"><strong>Warning:</strong> Performance issues detected</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-sm"><strong>Offline/Fault:</strong> Device needs attention</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="text-sm"><strong>Maintenance:</strong> Scheduled maintenance mode</span>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "Data Analytics",
      icon: <BarChart3 className="w-8 h-8 text-cyan-500" />,
      content: (
        <div className="space-y-4">
          <p className="text-slate-600">
            Access detailed charts and historical data by clicking on any device. Analyze trends and optimize performance.
          </p>
          <div className="bg-gradient-to-r from-cyan-50 to-blue-50 p-4 rounded-lg border border-cyan-200">
            <h4 className="font-semibold text-cyan-800 mb-2">Available Charts:</h4>
            <div className="grid grid-cols-2 gap-2 text-sm text-cyan-700">
              <div>• Power Generation</div>
              <div>• Panel Voltages</div>
              <div>• Input Currents</div>
              <div>• Output Currents</div>
            </div>
          </div>
          <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
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
        <div className="space-y-4">
          <p className="text-slate-600">
            You're all set! Here are your next steps to make the most of your Solar PV Dashboard.
          </p>
          <div className="space-y-3">
            <Card className="bg-emerald-50 border-emerald-200">
              <CardContent className="p-4">
                <h4 className="font-semibold text-emerald-800 mb-2">Quick Actions:</h4>
                <ul className="text-sm text-emerald-700 space-y-2">
                  <li>1. Browse your demo plants and devices</li>
                  <li>2. Click "View Details" on any device</li>
                  <li>3. Explore different time ranges in charts</li>
                  <li>4. Check device status indicators</li>
                </ul>
              </CardContent>
            </Card>
            <div className="text-center pt-4">
              <Button onClick={onClose} className="bg-gradient-to-r from-emerald-500 to-green-500">
                Start Exploring
              </Button>
            </div>
          </div>
        </div>
      )
    }
  ];

  const nextStep = () => {
    if (currentStep < guideSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  if (!isOpen) return null;

  const currentGuideStep = guideSteps[currentStep];

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {currentGuideStep.icon}
              <CardTitle className="text-xl">{currentGuideStep.title}</CardTitle>
            </div>
            <Button
              onClick={onClose}
              variant="ghost"
              size="sm"
              className="text-white hover:bg-white/20"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm opacity-90">
              Step {currentStep + 1} of {guideSteps.length}
            </span>
            <div className="flex space-x-1">
              {guideSteps.map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full ${
                    index === currentStep ? 'bg-white' : 'bg-white/40'
                  }`}
                />
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6 min-h-[300px]">
          {currentGuideStep.content}
        </CardContent>
        <div className="px-6 pb-6">
          <div className="flex justify-between">
            <Button
              onClick={prevStep}
              disabled={currentStep === 0}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Previous</span>
            </Button>
            {currentStep < guideSteps.length - 1 ? (
              <Button
                onClick={nextStep}
                className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-cyan-500"
              >
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </Button>
            ) : (
              <Button
                onClick={onClose}
                className="bg-gradient-to-r from-emerald-500 to-green-500"
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