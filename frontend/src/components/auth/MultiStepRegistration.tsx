import React, { useState } from 'react';
import { UserPlus, ChevronRight, ChevronLeft, User, Zap, MapPin, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';

interface MultiStepRegistrationProps {
  onRegister: (userData: any) => void;
  onToggleAuth: () => void;
}

interface FormData {
  // Account Information
  username: string;
  fullname: string;
  password: string;
  confirmPassword: string;
  
  // Solar System Information
  panelBrand: string;
  panelCapacity: string;
  panelType: string;
  inverterBrand: string;
  inverterCapacity: string;
  
  // Contact and Address Information
  email: string;
  whatsappNumber: string;
  address: string;
}

export const MultiStepRegistration: React.FC<MultiStepRegistrationProps> = ({ onRegister, onToggleAuth }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState<FormData>({
    fullname: '',
    username: '',
    password: '',
    confirmPassword: '',
    panelBrand: '',
    panelCapacity: '',
    panelType: '',
    inverterBrand: '',
    inverterCapacity: '',
    email: '',
    whatsappNumber: '',
    address: ''
  });

  const totalSteps = 3;
  const progress = (currentStep / totalSteps) * 100;

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const validateCurrentStep = () => {
    switch (currentStep) {
      case 1:
        if (!formData.username.trim()) {
          setError("🤖 Beep! Username required. Even robots need names!");
          return false;
        }
        if (!formData.password.trim()) {
          setError("🔒 Password missing! Your account needs a secret handshake.");
          return false;
        }
        if (formData.password.length < 6) {
          setError("🔐 Password too short! Make it at least 6 characters - your future self will thank you.");
          return false;
        }
        if (formData.password !== formData.confirmPassword) {
          setError("🔄 Password mismatch! They should be twins, not distant cousins.");
          return false;
        }
        break;
      case 2:
        if (!formData.panelBrand) {
          setError("☀️ Panel brand missing! Every solar hero needs their cape brand.");
          return false;
        }
        if (!formData.panelCapacity) {
          setError("⚡ Panel capacity required! How much solar power are we talking about?");
          return false;
        }
        if (!formData.inverterBrand) {
          setError("🔄 Inverter brand missing! The DC to AC translator needs a name tag.");
          return false;
        }
        break;
      case 3:
        if (!formData.email.trim()) {
          setError("📧 Email missing! How else will we send you sunny updates?");
          return false;
        }
        if (!formData.email.includes('@')) {
          setError("📮 Invalid email! The @ symbol is not optional - it's the star of the show.");
          return false;
        }
        if (!formData.address.trim()) {
          setError("🏠 Address required! Where should we map your solar journey?");
          return false;
        }
        break;
    }
    return true;
  };

  const handleNext = () => {
    if (validateCurrentStep() && currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
      setError('');
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateCurrentStep()) {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await onRegister(formData);
      toast.success("🎉 Welcome to the Solar Family!", {
        description: "Your account has been created successfully. Time to harness the sun!"
      });
    } catch (error) {
      const creativeErrors = [
        "🌩️ Houston, we have a problem! Registration hit a snag in the solar system.",
        "⚡ Circuit overload! Our servers are having a power surge. Please try again.",
        "🔋 Battery low! Registration failed to charge up. Give it another shot.",
        "☁️ Cloudy conditions ahead! Registration got stuck in the weather. Try again soon.",
        "🛰️ Satellite connection lost! Your registration didn't reach our solar station."
      ];

      const randomError = creativeErrors[Math.floor(Math.random() * creativeErrors.length)];
      setError(randomError);
      
      toast.error("Registration Failed", {
        description: "Something went wrong while creating your account. Please try again."
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getStepIcon = (step: number) => {
    switch (step) {
      case 1: return <User className="w-6 h-6" />;
      case 2: return <Zap className="w-6 h-6" />;
      case 3: return <MapPin className="w-6 h-6" />;
      default: return <User className="w-6 h-6" />;
    }
  };

  const getStepTitle = (step: number) => {
    switch (step) {
      case 1: return 'Account Information';
      case 2: return 'Solar System Information';
      case 3: return 'Contact & Address Information';
      default: return 'Account Information';
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="fullname">Full Name</Label>
              <Input
                id="fullname"
                type="text"
                placeholder="Enter your full name"
                value={formData.fullname}
                onChange={(e) => handleInputChange('fullname', e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Create a password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-700">Panel Information</h3>
              
              <div className="space-y-2">
                <Label htmlFor="panelBrand">Panel Brand</Label>
                <Select value={formData.panelBrand} onValueChange={(value) => handleInputChange('panelBrand', value)} disabled={isLoading}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select panel brand" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sunpower">SunPower</SelectItem>
                    <SelectItem value="lg">LG</SelectItem>
                    <SelectItem value="panasonic">Panasonic</SelectItem>
                    <SelectItem value="jinko">Jinko Solar</SelectItem>
                    <SelectItem value="trina">Trina Solar</SelectItem>
                    <SelectItem value="canadian">Canadian Solar</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="panelCapacity">Panel Capacity (kW)</Label>
                <Input
                  id="panelCapacity"
                  type="number"
                  step="0.1"
                  placeholder="e.g., 5.0"
                  value={formData.panelCapacity}
                  onChange={(e) => handleInputChange('panelCapacity', e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="panelType">Panel Type</Label>
                <Select value={formData.panelType} onValueChange={(value) => handleInputChange('panelType', value)} disabled={isLoading}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select panel type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="monocrystalline">Monocrystalline</SelectItem>
                    <SelectItem value="polycrystalline">Polycrystalline</SelectItem>
                    <SelectItem value="thin-film">Thin Film</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-4 border-t pt-4">
              <h3 className="text-lg font-semibold text-slate-700">Inverter Information</h3>
              
              <div className="space-y-2">
                <Label htmlFor="inverterBrand">Inverter Brand</Label>
                <Select value={formData.inverterBrand} onValueChange={(value) => handleInputChange('inverterBrand', value)} disabled={isLoading}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select inverter brand" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sma">SMA</SelectItem>
                    <SelectItem value="fronius">Fronius</SelectItem>
                    <SelectItem value="solaredge">SolarEdge</SelectItem>
                    <SelectItem value="huawei">Huawei</SelectItem>
                    <SelectItem value="growatt">Growatt</SelectItem>
                    <SelectItem value="solis">Solis</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="inverterCapacity">Inverter Capacity (kW)</Label>
                <Input
                  id="inverterCapacity"
                  type="number"
                  step="0.1"
                  placeholder="e.g., 4.0"
                  value={formData.inverterCapacity}
                  onChange={(e) => handleInputChange('inverterCapacity', e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="whatsappNumber">WhatsApp Number</Label>
              <Input
                id="whatsappNumber"
                type="tel"
                placeholder="Enter your WhatsApp number"
                value={formData.whatsappNumber}
                onChange={(e) => handleInputChange('whatsappNumber', e.target.value)}
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="address">Installation Address</Label>
              <Input
                id="address"
                type="text"
                placeholder="Enter your installation address"
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <div className="p-3 rounded-xl w-fit mx-auto mb-4 bg-gradient-to-r from-green-500 to-emerald-500">
            <UserPlus className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-600 to-emerald-600">
            Create Your Solar Account
          </CardTitle>
          <p className="text-slate-600">
            Step {currentStep} of {totalSteps}: {getStepTitle(currentStep)}
          </p>
        </CardHeader>
        
        <CardContent>
          {/* Progress Bar */}
          <div className="mb-6">
            <Progress value={progress} className="w-full h-2 mb-2" />
            <div className="flex justify-between text-sm text-slate-500">
              <span className={currentStep >= 1 ? 'text-green-600 font-medium' : ''}>Account</span>
              <span className={currentStep >= 2 ? 'text-green-600 font-medium' : ''}>Solar System</span>
              <span className={currentStep >= 3 ? 'text-green-600 font-medium' : ''}>Contact</span>
            </div>
          </div>

          {/* Step Indicator */}
          <div className="flex items-center justify-center mb-6">
            <div className="flex items-center space-x-2 p-3 bg-green-50 rounded-lg">
              <div className="text-green-600">
                {getStepIcon(currentStep)}
              </div>
              <span className="text-green-700 font-medium">
                {getStepTitle(currentStep)}
              </span>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive" className="mb-6 animate-fade-in">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="font-medium">
                {error}
              </AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            {/* Step Content */}
            <div className="mb-6">
              {renderStepContent()}
            </div>

            {/* Navigation Buttons */}
            <div className="flex justify-between">
              <Button
                type="button"
                variant="outline"
                onClick={handlePrevious}
                disabled={currentStep === 1 || isLoading}
                className="flex items-center space-x-2"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Previous</span>
              </Button>

              {currentStep < totalSteps ? (
                <Button
                  type="button"
                  onClick={handleNext}
                  disabled={isLoading}
                  className="flex items-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-500"
                >
                  <span>Next</span>
                  <ChevronRight className="w-4 h-4" />
                </Button>
              ) : (
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="bg-gradient-to-r from-green-500 to-emerald-500"
                >
                  {isLoading ? 'Creating Account...' : 'Create Account'}
                </Button>
              )}
            </div>
          </form>
          
          <div className="mt-6 text-center">
            <button
              onClick={onToggleAuth}
              className="text-sm text-green-600 hover:underline"
              disabled={isLoading}
            >
              Already have an account? Sign in
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
