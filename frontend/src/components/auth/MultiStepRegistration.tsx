
import React, { useState, useEffect } from 'react';
import * as Yup from 'yup';
import { UserPlus, ChevronRight, ChevronLeft, User, Zap, MapPin, AlertTriangle, Settings, Eye, EyeOff, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';

interface MultiStepRegistrationProps {
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

const validationSchema = Yup.object().shape({
  username: Yup.string()
    .trim()
    .required('Username is required')
    .min(3, 'Username must be at least 3 characters'),
  fullname: Yup.string()
    .trim()
    .required('Full name is required'),
  password: Yup.string()
    .trim()
    .required('Password is required')
    .min(6, 'Password must be at least 6 characters'),
  confirmPassword: Yup.string()
    .trim()
    .required('Confirm password is required')
    .oneOf([Yup.ref('password')], 'Passwords must match'),
  email: Yup.string()
    .trim()
    .email('Invalid email format')
    .required('Email is required'),
  whatsappNumber: Yup.string()
    .trim()
    .matches(/^\+?[1-9]\d{9,14}$/, 'Invalid WhatsApp number (e.g., +1234567890)')
    .required('WhatsApp number is required'),
  address: Yup.string()
    .trim()
    .when('isInstaller', (isInstaller, schema) => {
      return isInstaller[0] ? schema.required('Address is required for installers') : schema;
    }),
  panelBrand: Yup.string()
    .when('isInstaller', (isInstaller, schema) => {
      return isInstaller[0] ? schema.required('Panel brand is required for installers') : schema;
    }),
  panelCapacity: Yup.string()
    .when('isInstaller', (isInstaller, schema) => {
      return isInstaller[0] ? schema.required('Panel capacity is required for installers').matches(/^\d*\.?\d+$/, 'Must be a valid number (e.g., 5.0)') : schema;
    }),
  panelType: Yup.string()
    .when('isInstaller', (isInstaller, schema) => {
      return isInstaller[0] ? schema.required('Panel type is required for installers') : schema;
    }),
  inverterBrand: Yup.string()
    .when('isInstaller', (isInstaller, schema) => {
      return isInstaller[0] ? schema.required('Inverter brand is required for installers') : schema;
    }),
  inverterCapacity: Yup.string()
    .when('isInstaller', (isInstaller, schema) => {
      return isInstaller[0] ? schema.required('Inverter capacity is required for installers').matches(/^\d*\.?\d+$/, 'Must be a valid number (e.g., 4.0)') : schema;
    }),
  isInstaller: Yup.boolean(),
});

export const MultiStepRegistration: React.FC<MultiStepRegistrationProps> = ({ onRegister, onToggleAuth }) => {
  const [currentStep, setCurrentStep] = useState(1);
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

  // Real-time validation for immediate feedback
  const handleInputChange = (field: keyof FormData, value: string | boolean) => {
    const trimmedValue = typeof value === 'string' ? value.trim() : value;
    setFormData((prev) => ({
      ...prev,
      [field]: trimmedValue,
    }));
    
    // Clear error when user starts typing
    if (error) {
      setError(null);
    }
  };

  const getFieldSpecificError = (field: string, value: any) => {
    const solarFieldErrors: Record<string, string[]> = {
      fullname: [
        "🌞 Solar panels need a real name to generate power! What's your actual name?",
        "⚡ Name's looking a bit dim - brighten it up with your full name!",
        "🔋 Battery not charged enough for that name! Give us the full voltage!",
        "☀️ Your name needs more solar energy - try adding your last name too!"
      ],
      username: [
        "🌩️ Username storm brewing! Pick a more electrifying handle!",
        "⚙️ That username's not conducting enough power - try something more energetic!",
        "🔌 Username short-circuit detected! Need at least 3 characters to power up!",
        "📡 Username signal too weak! Boost the strength with more characters!"
      ],
      password: [
        "🔐 Password security lower than solar output on a cloudy day! Needs 6+ characters!",
        "⚡ Your password has less energy than a dead battery! Charge it up!",
        "🌨️ Password frozen solid! Needs more heat - add some special characters!",
        "🔋 Password running on empty! Need at least 6 characters to power the system!"
      ],
      confirmPassword: [
        "🔄 Password inverter malfunction! Your passwords are generating different outputs!",
        "⚡ Circuit mismatch! Your passwords aren't conducting the same current!",
        "🔌 Wiring error detected! Make sure both password cables match!",
        "📡 Signal interference! Your password confirmation isn't syncing!"
      ],
      email: [
        "📧 Email satellite dish is broken! That doesn't look like a valid signal!",
        "🌐 Internet grid down! Check your email address format!",
        "📡 Email transmission failed! Add an @ symbol to boost the signal!",
        "💻 Email processor overheating! Cool it down with a proper email format!"
      ],
      whatsappNumber: [
        "📱 WhatsApp solar panel not aligned! Check your number format (+1234567890)!",
        "📞 Phone battery dead! That number doesn't have enough digits to call!",
        "🛰️ Communication satellite can't reach that number! Try the international format!",
        "📶 Signal strength too low! Add country code for better reception!"
      ],
      address: [
        "🏠 Solar GPS can't locate that address! Give us more detailed coordinates!",
        "🗺️ Map data corrupted! We need your full address to install panels!",
        "📍 Location beacon not found! Help us pinpoint your solar installation site!",
        "🛰️ Google Earth offline! Provide a complete address for satellite view!"
      ],
      panelBrand: [
        "☀️ Solar panel brand scanner malfunctioned! Pick a manufacturer!",
        "🔧 Panel selection bot confused! Choose your solar panel brand!",
        "⚡ Brand detector short-circuited! Select a panel manufacturer!",
        "🏭 Factory database connection lost! Pick a panel brand!"
      ],
      panelCapacity: [
        "⚡ Wattage meter broken! Enter your panel capacity in numbers!",
        "🔋 Power calculator offline! How many kW can your panels generate?",
        "📊 Capacity sensor malfunctioned! Input a valid number (e.g., 5.0)!",
        "⚙️ Performance analyzer crashed! Enter panel capacity as a number!"
      ],
      panelType: [
        "🔬 Panel analysis lab closed! Select your panel technology type!",
        "⚗️ Solar cell detector needs calibration! Choose your panel type!",
        "🧪 Technology scanner offline! Pick monocrystalline, polycrystalline, or thin-film!",
        "🔎 Panel microscope broken! Select the type of solar cells!"
      ],
      inverterBrand: [
        "🔄 Inverter brand database corrupted! Select your AC/DC converter manufacturer!",
        "⚡ Brand recognition software crashed! Pick your inverter maker!",
        "🔌 Inverter scanner offline! Choose who made your power converter!",
        "⚙️ Manufacturer lookup failed! Select your inverter brand!"
      ],
      inverterCapacity: [
        "🔋 Inverter capacity meter exploded! Enter the kW rating as a number!",
        "⚡ Power converter calculator fried! How many kW can it handle?",
        "📊 AC output analyzer down! Input inverter capacity (e.g., 4.0)!",
        "⚙️ Capacity measurement tool broken! Enter a valid number!"
      ]
    };

    if (!value || (typeof value === 'string' && value.trim() === '')) {
      const errors = solarFieldErrors[field] || ["Field is required"];
      return errors[Math.floor(Math.random() * errors.length)];
    }

    // Specific validation errors
    if (field === 'username' && value.length < 3) {
      return solarFieldErrors.username[2]; // Short circuit message
    }
    if (field === 'password' && value.length < 6) {
      return solarFieldErrors.password[3]; // Battery empty message
    }
    if (field === 'confirmPassword' && value !== formData.password) {
      return solarFieldErrors.confirmPassword[0]; // Inverter malfunction
    }
    if (field === 'email' && !value.includes('@')) {
      return solarFieldErrors.email[2]; // Add @ symbol
    }
    if (field === 'whatsappNumber' && !/^\+?[1-9]\d{9,14}$/.test(value)) {
      return solarFieldErrors.whatsappNumber[1]; // Not enough digits
    }
    if ((field === 'panelCapacity' || field === 'inverterCapacity') && !/^\d*\.?\d+$/.test(value)) {
      return solarFieldErrors[field][3]; // Enter as number
    }

    return null;
  };

  const validateCurrentStep = () => {
    const requiredFields: Record<number, string[]> = {
      1: ['fullname', 'username', 'password', 'confirmPassword'],
      2: formData.isInstaller 
        ? ['panelBrand', 'panelCapacity', 'panelType', 'inverterBrand', 'inverterCapacity']
        : [], // Optional for customers
      3: ['email', 'whatsappNumber', ...(formData.isInstaller ? ['address'] : [])]
    };

    const fieldsToValidate = requiredFields[currentStep] || [];
    
    for (const field of fieldsToValidate) {
      const value = formData[field as keyof FormData];
      const error = getFieldSpecificError(field, value);
      if (error) {
        setError(error);
        return false;
      }
    }
    
    setError(null);
    return true;
  };

  const handleNext = () => {
    if (validateCurrentStep()) {
      if (currentStep < totalSteps) {
        setCurrentStep(currentStep + 1);
        setError(null);
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
    if (!validateCurrentStep()) return;
    
    setIsLoading(true);
    setError(null);
    
    // Simulate registration process without backend
    try {
      // Mock successful registration
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
      
      toast.success("🎉 Welcome to the Solar Family!", {
        description: `Your ${formData.isInstaller ? 'installer' : 'customer'} account has been created successfully. Time to harness the sun!`,
      });
      
      // Reset form and navigate to success
      console.log('Registration completed successfully with data:', formData);
      
      // Call onRegister with mock successful response
      await onRegister({
        username: formData.username,
        fullname: formData.fullname,
        password: formData.password,
        confirmPassword: formData.confirmPassword,
        isInstaller: formData.isInstaller,
        email: formData.email,
        whatsappNumber: formData.whatsappNumber,
        address: formData.address
      });
      
    } catch (error: any) {
      const solarErrors = [
        "🌩️ Solar flare detected! Registration temporarily scattered across the photosphere. Try again!",
        "⚡ Circuit breaker tripped! Our registration inverter needs a quick reset. Give it another spark!",
        "🔋 Battery bank depleted! Registration couldn't store enough energy. Charging up for retry...",
        "☁️ Cloudy skies ahead! Registration got lost in the weather patterns. Clear skies coming soon!",
        "🛰️ Solar satellite offline! Your registration didn't reach our orbital station. Re-establishing connection...",
        "🌞 Solar eclipse in progress! Registration temporarily blocked. Wait for the sun to shine again!",
        "⚙️ MPPT controller malfunction! Registration couldn't find maximum power point. Recalibrating...",
        "🔌 Inverter hiccup! Your registration got stuck in DC mode. Converting to AC shortly...",
        "📡 Smart meter error! Registration readings came back as 'NaN'. Refreshing the grid connection...",
        "🏠 Net metering confusion! Registration tried to feed power back to the grid instead of our servers!"
      ];
      const randomError = solarErrors[Math.floor(Math.random() * solarErrors.length)];
      setError(randomError);
      toast.error("Registration Failed", {
        description: "Oops! Something went haywire in our solar system. Please try again!",
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
                disabled={isLoading}
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
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Create a password"
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  required
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2"
                  disabled={isLoading}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                  required
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2"
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
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg mb-4">
                <p className="text-sm text-blue-700">
                  ℹ️ Customer Mode: Solar system information is optional. You can skip these fields if you don't have the details yet.
                </p>
              </div>
            )}

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-700">
                Panel Information {!formData.isInstaller && <span className="text-sm font-normal text-slate-500">(Optional)</span>}
              </h3>

              <div className="space-y-2">
                <Label htmlFor="panelBrand">Panel Brand</Label>
                <Select
                  value={formData.panelBrand}
                  onValueChange={(value) => handleInputChange('panelBrand', value)}
                  disabled={isLoading}
                >
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
                  required={formData.isInstaller}
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="panelType">Panel Type</Label>
                <Select
                  value={formData.panelType}
                  onValueChange={(value) => handleInputChange('panelType', value)}
                  disabled={isLoading}
                >
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
              <h3 className="text-lg font-semibold text-slate-700">
                Inverter Information {!formData.isInstaller && <span className="text-sm font-normal text-slate-500">(Optional)</span>}
              </h3>

              <div className="space-y-2">
                <Label htmlFor="inverterBrand">Inverter Brand</Label>
                <Select
                  value={formData.inverterBrand}
                  onValueChange={(value) => handleInputChange('inverterBrand', value)}
                  disabled={isLoading}
                >
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
                  required={formData.isInstaller}
                  disabled={isLoading}
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            {!formData.isInstaller && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg mb-4">
                <p className="text-sm text-blue-700">
                  ℹ️ Customer Mode: Installation address is optional for customers.
                </p>
              </div>
            )}

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
                placeholder="Enter your WhatsApp number (e.g., +1234567890)"
                value={formData.whatsappNumber}
                onChange={(e) => handleInputChange('whatsappNumber', e.target.value)}
                required
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">
                Installation Address {!formData.isInstaller && <span className="text-sm font-normal text-slate-500">(Optional)</span>}
              </Label>
              <Input
                id="address"
                type="text"
                placeholder="Enter your installation address"
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                required={formData.isInstaller}
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-700 flex">
      {/* Left Side - Features Showcase */}
      <div className="hidden lg:flex lg:w-1/2 xl:w-2/5 bg-gradient-to-br from-blue-600 via-cyan-600 to-emerald-600 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative z-10 flex flex-col justify-center px-12 py-16 text-white">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-4">
              Join the Solar Revolution! ☀️
            </h1>
            <p className="text-xl text-blue-100 mb-8">
              Monitor, optimize, and maximize your solar energy with our advanced dashboard
            </p>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-start space-x-4 p-4 bg-white/10 rounded-lg backdrop-blur-sm border border-white/20">
              <div className="bg-yellow-400 p-2 rounded-lg">
                <Zap className="w-6 h-6 text-yellow-900" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Real-time Monitoring</h3>
                <p className="text-blue-100">Track your solar generation, efficiency, and savings in real-time with beautiful charts and analytics</p>
              </div>
            </div>

            <div className="flex items-start space-x-4 p-4 bg-white/10 rounded-lg backdrop-blur-sm border border-white/20">
              <div className="bg-green-400 p-2 rounded-lg">
                <MapPin className="w-6 h-6 text-green-900" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Neighbourhood Comparison</h3>
                <p className="text-blue-100">Compare your performance with neighbours and get insights to optimize your system</p>
              </div>
            </div>

            <div className="flex items-start space-x-4 p-4 bg-white/10 rounded-lg backdrop-blur-sm border border-white/20">
              <div className="bg-purple-400 p-2 rounded-lg">
                <Settings className="w-6 h-6 text-purple-900" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Smart Alerts & Maintenance</h3>
                <p className="text-blue-100">Get intelligent alerts for maintenance, weather impacts, and performance issues</p>
              </div>
            </div>

            <div className="flex items-start space-x-4 p-4 bg-white/10 rounded-lg backdrop-blur-sm border border-white/20">
              <div className="bg-orange-400 p-2 rounded-lg">
                <BarChart3 className="w-6 h-6 text-orange-900" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Advanced Analytics</h3>
                <p className="text-blue-100">Deep insights into your energy production, consumption patterns, and ROI calculations</p>
              </div>
            </div>
          </div>

          <div className="mt-8 p-4 bg-gradient-to-r from-green-400/20 to-emerald-400/20 rounded-lg border border-green-300/30">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm font-semibold">Join 10,000+ Happy Solar Users</span>
            </div>
            <p className="text-sm text-green-100">
              "This platform helped me increase my solar efficiency by 23% and saved me $2,400 last year!" - Sarah M.
            </p>
          </div>
        </div>
        
        {/* Animated Background Elements */}
        <div className="absolute top-10 right-10 w-20 h-20 bg-yellow-300/20 rounded-full animate-bounce"></div>
        <div className="absolute bottom-20 left-10 w-16 h-16 bg-green-300/20 rounded-full animate-pulse"></div>
        <div className="absolute top-1/2 right-1/4 w-12 h-12 bg-blue-300/20 rounded-full animate-ping"></div>
      </div>

      {/* Right Side - Registration Form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <Card className="bg-white/90 backdrop-blur-sm border border-slate-200 shadow-2xl">
            <CardHeader className="space-y-1 pb-6">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-3 rounded-xl">
                  <UserPlus className="w-8 h-8 text-white" />
                </div>
              </div>
              <CardTitle className="text-2xl font-bold text-center bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                Create Your Solar Account
              </CardTitle>
              <p className="text-center text-slate-600">
                Join thousands of solar enthusiasts
              </p>
              
              {/* Progress Bar */}
              <div className="mt-6">
                <div className="flex justify-between text-sm text-slate-600 mb-2">
                  <span>Step {currentStep} of {totalSteps}</span>
                  <span>{Math.round(progress)}% Complete</span>
                </div>
                <Progress value={progress} className="h-2" />
              </div>
              
              {/* Step Indicator */}
              <div className="flex justify-center space-x-8 mt-4">
                {[1, 2, 3].map((step) => (
                  <div 
                    key={step} 
                    className={`flex flex-col items-center space-y-2 ${
                      step <= currentStep ? 'text-blue-600' : 'text-slate-400'
                    }`}
                  >
                    <div className={`p-2 rounded-full border-2 ${
                      step <= currentStep 
                        ? 'border-blue-600 bg-blue-50' 
                        : 'border-slate-300 bg-slate-50'
                    }`}>
                      {getStepIcon(step)}
                    </div>
                    <span className="text-xs font-medium">{getStepTitle(step)}</span>
                  </div>
                ))}
              </div>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Account Type Toggle */}
                {currentStep === 1 && (
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border border-blue-200">
                    <div>
                      <Label htmlFor="installer-toggle" className="font-medium text-slate-700">
                        Are you an installer?
                      </Label>
                      <p className="text-sm text-slate-600">
                        {formData.isInstaller ? 'Professional installer account' : 'Customer/homeowner account'}
                      </p>
                    </div>
                    <Switch
                      id="installer-toggle"
                      checked={formData.isInstaller}
                      onCheckedChange={(checked) => handleInputChange('isInstaller', checked)}
                      disabled={isLoading}
                    />
                  </div>
                )}

                {/* Dynamic Step Content */}
                {renderStepContent()}

                {/* Fun Error Message */}
                {error && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-700 font-medium">
                      {error}
                    </AlertDescription>
                  </Alert>
                )}

                {/* Navigation Buttons */}
                <div className="flex justify-between space-x-4 pt-6">
                  {currentStep > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handlePrevious}
                      disabled={isLoading}
                      className="flex items-center space-x-2"
                    >
                      <ChevronLeft className="w-4 h-4" />
                      <span>Previous</span>
                    </Button>
                  )}
                  
                  <div className="flex-1"></div>
                  
                  {currentStep < totalSteps ? (
                    <Button
                      type="button"
                      onClick={handleNext}
                      disabled={isLoading}
                      className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
                    >
                      <span>Next</span>
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  ) : (
                    <Button
                      type="submit"
                      disabled={isLoading}
                      className="flex items-center space-x-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                    >
                      {isLoading ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Creating Account...</span>
                        </>
                      ) : (
                        <>
                          <UserPlus className="w-4 h-4" />
                          <span>Create Account</span>
                        </>
                      )}
                    </Button>
                  )}
                </div>

                {/* Login Link */}
                <div className="text-center pt-6 border-t border-slate-200">
                  <p className="text-slate-600">
                    Already have an account?{' '}
                    <button
                      type="button"
                      onClick={onToggleAuth}
                      className="text-blue-600 hover:text-blue-700 font-medium hover:underline"
                      disabled={isLoading}
                    >
                      Sign in here
                    </button>
                  </p>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
