import React, { useState, useEffect } from 'react';
import { UserPlus, ChevronRight, ChevronLeft, User, Zap, MapPin, AlertTriangle, Settings, Eye, EyeOff } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import { OTPVerification } from './OTPVerification';

interface EnhancedMultiStepRegistrationProps {
  onRegister: (userData: any) => Promise<void>;
  onToggleAuth: () => void;
}

interface FormData {
  username: string;
  fullname: string;
  password: string;
  confirmPassword: string;
  isInstaller: boolean;
  panelBrand: string;
  panelCapacity: string;
  panelType: string;
  inverterBrand: string;
  inverterCapacity: string;
  email: string;
  whatsappNumber: string;
  address: string;
}

export const EnhancedMultiStepRegistration: React.FC<EnhancedMultiStepRegistrationProps> = ({ onRegister, onToggleAuth }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [showOTP, setShowOTP] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    username: '',
    fullname: '',
    password: '',
    confirmPassword: '',
    isInstaller: false,
    panelBrand: '',
    panelCapacity: '',
    panelType: '',
    inverterBrand: '',
    inverterCapacity: '',
    email: '',
    whatsappNumber: '',
    address: '',
  });

  const totalSteps = 3;
  const progress = (currentStep / totalSteps) * 100;

  const handleInputChange = (field: keyof FormData, value: string | boolean) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const validateStep = () => {
    switch (currentStep) {
      case 1:
        if (!formData.fullname || !formData.username || !formData.password || !formData.confirmPassword) {
          setError('Please fill in all required fields');
          return false;
        }
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          return false;
        }
        if (formData.password.length < 6) {
          setError('Password must be at least 6 characters');
          return false;
        }
        break;
      case 2:
        if (formData.isInstaller && (!formData.panelBrand || !formData.panelCapacity || !formData.panelType || !formData.inverterBrand || !formData.inverterCapacity)) {
          setError('Please fill in all installer fields');
          return false;
        }
        break;
      case 3:
        if (!formData.email || !formData.whatsappNumber) {
          setError('Please fill in email and WhatsApp number');
          return false;
        }
        if (formData.isInstaller && !formData.address) {
          setError('Address is required for installers');
          return false;
        }
        break;
    }
    setError(null);
    return true;
  };

  const handleNext = () => {
    if (validateStep()) {
      if (currentStep < totalSteps) {
        setCurrentStep(currentStep + 1);
      }
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateStep()) return;
    
    // Show OTP verification instead of directly registering
    setShowOTP(true);
  };

  const handleOTPVerify = async (otp: string) => {
    setIsLoading(true);
    try {
      // Simulate OTP verification
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const userData = {
        username: formData.username,
        fullname: formData.fullname,
        password: formData.password,
        confirmPassword: formData.confirmPassword,
        isInstaller: formData.isInstaller,
        email: formData.email,
        whatsappNumber: formData.whatsappNumber,
        address: formData.address,
        panelBrand: formData.isInstaller ? formData.panelBrand : undefined,
        panelCapacity: formData.isInstaller ? formData.panelCapacity : undefined,
        panelType: formData.isInstaller ? formData.panelType : undefined,
        inverterBrand: formData.isInstaller ? formData.inverterBrand : undefined,
        inverterCapacity: formData.isInstaller ? formData.inverterCapacity : undefined,
      };
      
      await onRegister(userData);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOTPResend = async () => {
    // Simulate resending OTP
    await new Promise(resolve => setTimeout(resolve, 500));
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
              <Label htmlFor="fullname" className="text-white/90">Full Name</Label>
              <Input
                id="fullname"
                type="text"
                placeholder="Enter your full name"
                value={formData.fullname}
                onChange={(e) => handleInputChange('fullname', e.target.value)}
                required
                disabled={isLoading}
                className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="username" className="text-white/90">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                required
                disabled={isLoading}
                className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-white/90">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Create a password"
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  required
                  disabled={isLoading}
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/60 hover:text-white"
                  disabled={isLoading}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-white/90">Confirm Password</Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                  required
                  disabled={isLoading}
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/60 hover:text-white"
                  disabled={isLoading}
                >
                  {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            {!formData.isInstaller && (
              <div className="p-3 bg-white/10 border border-white/20 rounded-lg mb-4">
                <p className="text-sm text-white/80">
                  ℹ️ Customer Mode: Solar system information is optional. You can skip these fields if you don't have the details yet.
                </p>
              </div>
            )}

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white/90">
                Panel Information {!formData.isInstaller && <span className="text-sm font-normal text-white/60">(Optional)</span>}
              </h3>

              <div className="space-y-2">
                <Label htmlFor="panelBrand" className="text-white/90">Panel Brand</Label>
                <Select
                  value={formData.panelBrand}
                  onValueChange={(value) => handleInputChange('panelBrand', value)}
                  disabled={isLoading}
                >
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
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
                <Label htmlFor="panelCapacity" className="text-white/90">Panel Capacity (kW)</Label>
                <Input
                  id="panelCapacity"
                  type="number"
                  step="0.1"
                  placeholder="e.g., 5.0"
                  value={formData.panelCapacity}
                  onChange={(e) => handleInputChange('panelCapacity', e.target.value)}
                  required={formData.isInstaller}
                  disabled={isLoading}
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="panelType" className="text-white/90">Panel Type</Label>
                <Select
                  value={formData.panelType}
                  onValueChange={(value) => handleInputChange('panelType', value)}
                  disabled={isLoading}
                >
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
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

            <div className="space-y-4 border-t border-white/20 pt-4">
              <h3 className="text-lg font-semibold text-white/90">
                Inverter Information {!formData.isInstaller && <span className="text-sm font-normal text-white/60">(Optional)</span>}
              </h3>

              <div className="space-y-2">
                <Label htmlFor="inverterBrand" className="text-white/90">Inverter Brand</Label>
                <Select
                  value={formData.inverterBrand}
                  onValueChange={(value) => handleInputChange('inverterBrand', value)}
                  disabled={isLoading}
                >
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
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
                <Label htmlFor="inverterCapacity" className="text-white/90">Inverter Capacity (kW)</Label>
                <Input
                  id="inverterCapacity"
                  type="number"
                  step="0.1"
                  placeholder="e.g., 4.0"
                  value={formData.inverterCapacity}
                  onChange={(e) => handleInputChange('inverterCapacity', e.target.value)}
                  required={formData.isInstaller}
                  disabled={isLoading}
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40"
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            {!formData.isInstaller && (
              <div className="p-3 bg-white/10 border border-white/20 rounded-lg mb-4">
                <p className="text-sm text-white/80">
                  ℹ️ Customer Mode: Installation address is optional.
                </p>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email" className="text-white/90">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                required
                disabled={isLoading}
                className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="whatsappNumber" className="text-white/90">WhatsApp Number</Label>
              <Input
                id="whatsappNumber"
                type="tel"
                placeholder="Enter your WhatsApp number (e.g., +1234567890)"
                value={formData.whatsappNumber}
                onChange={(e) => handleInputChange('whatsappNumber', e.target.value)}
                required
                disabled={isLoading}
                className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="address" className="text-white/90">
                Installation Address {!formData.isInstaller && <span className="text-sm font-normal text-white/60">(Optional)</span>}
              </Label>
              <Input
                id="address"
                type="text"
                placeholder="Enter your installation address"
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                required={formData.isInstaller}
                disabled={isLoading}
                className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40"
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (showOTP) {
    return (
      <OTPVerification
        onVerify={handleOTPVerify}
        onBack={() => setShowOTP(false)}
        email={formData.email}
        onResend={handleOTPResend}
      />
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center p-4">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-green-600 via-emerald-600 to-teal-600">
        <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-transparent animate-pulse"></div>
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute top-3/4 right-1/4 w-80 h-80 bg-teal-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute bottom-1/4 left-1/2 w-72 h-72 bg-green-500/20 rounded-full blur-3xl animate-pulse delay-500"></div>
        </div>
      </div>
      
      {/* Glassmorphism Card */}
      <Card className="w-full max-w-lg bg-white/10 backdrop-blur-xl border-white/20 shadow-2xl shadow-black/20">
        <CardHeader className="text-center relative">
          <div className="absolute top-4 right-4">
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm rounded-lg p-2 border border-white/20">
              <Settings className="w-4 h-4 text-white/80" />
              <span className={`text-xs font-medium ${!formData.isInstaller ? 'text-white' : 'text-white/60'}`}>
                Customer
              </span>
              <Switch
                checked={formData.isInstaller}
                onCheckedChange={(value) => handleInputChange('isInstaller', value)}
                disabled={isLoading}
                className="data-[state=checked]:bg-green-500"
              />
              <span className={`text-xs font-medium ${formData.isInstaller ? 'text-white' : 'text-white/60'}`}>
                Installer
              </span>
            </div>
          </div>

          <div className="p-3 rounded-xl w-fit mx-auto mb-4 bg-gradient-to-r from-green-500 to-emerald-500">
            <UserPlus className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold text-white">
            Create Your Solar Account
          </CardTitle>
          <p className="text-white/80">
            Step {currentStep} of {totalSteps}: {getStepTitle(currentStep)}
          </p>
          <p className="text-sm text-white/60">
            {formData.isInstaller ? '🔧 Installer Mode' : '👤 Customer Mode'}
          </p>
        </CardHeader>

        <CardContent>
          <div className="mb-6">
            <Progress value={progress} className="w-full h-2 mb-2" />
            <div className="flex justify-between text-sm text-white/60">
              <span className={currentStep >= 1 ? 'text-white font-medium' : ''}>Account</span>
              <span className={currentStep >= 2 ? 'text-white font-medium' : ''}>Solar System</span>
              <span className={currentStep >= 3 ? 'text-white font-medium' : ''}>Contact</span>
            </div>
          </div>

          <div className="flex items-center justify-center mb-6">
            <div className="flex items-center space-x-2 p-3 bg-white/10 rounded-lg border border-white/20">
              <div className="text-white">{getStepIcon(currentStep)}</div>
              <span className="text-white font-medium">{getStepTitle(currentStep)}</span>
            </div>
          </div>

          {error && (
            <Alert variant="destructive" className="mb-6 animate-fade-in bg-red-500/10 border-red-500/20">
              <AlertTriangle className="h-4 w-4 text-white" />
              <AlertDescription className="font-medium text-white">{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-6">{renderStepContent()}</div>

            <div className="flex justify-between">
              <Button
                type="button"
                variant="outline"
                onClick={handlePrevious}
                disabled={currentStep === 1 || isLoading}
                className="flex items-center space-x-2 bg-white/10 border-white/20 text-white hover:bg-white/20"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Previous</span>
              </Button>

              {currentStep < totalSteps ? (
                <Button
                  type="button"
                  onClick={handleNext}
                  disabled={isLoading}
                  className="flex items-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white"
                >
                  <span>Next</span>
                  <ChevronRight className="w-4 h-4" />
                </Button>
              ) : (
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white"
                >
                  {isLoading ? 'Creating Account...' : 'Create Account'}
                </Button>
              )}
            </div>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={onToggleAuth}
              className="text-sm text-white/80 hover:text-white hover:underline"
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