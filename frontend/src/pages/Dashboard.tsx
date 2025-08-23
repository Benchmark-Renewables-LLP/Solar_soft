
import React, { useState } from 'react';
import { LoginForm } from '@/components/auth/LoginForm';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { PlantsOverview } from '@/components/plants/PlantsOverview';
import { DeviceDetail } from '@/components/devices/DeviceDetail';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import UserGuide from '@/components/onboarding/UserGuide';
import { toast } from 'sonner';
import { apiClient } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { Device } from '@/types/device';

type ViewState = 'login' | 'register' | 'plants' | 'device';

const Dashboard = () => {
  const { user, isAuthenticated, login, logout, isLoading } = useAuth();
  const [currentView, setCurrentView] = useState<ViewState>('login');
  const [isLogin, setIsLogin] = useState(true);
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
  const [showUserGuide, setShowUserGuide] = useState(false);

  // Auto-navigate to plants if user is authenticated
  React.useEffect(() => {
    if (isAuthenticated && user) {
      setCurrentView('plants');
      // Show user guide on first login
      const hasSeenGuide = localStorage.getItem('hasSeenGuide');
      if (!hasSeenGuide) {
        setShowUserGuide(true);
        localStorage.setItem('hasSeenGuide', 'true');
      }
    } else if (!isLoading) {
      setCurrentView('login');
    }
  }, [isAuthenticated, user, isLoading]);

  const handleLogin = async (username: string, password: string) => {
    try {
      // HARDCODED DEMO CREDENTIALS - Remove in production
      if (username === 'demo' && password === 'demo123') {
        console.log('Demo login successful');
        const demoUser = {
          id: 'demo-user-1',
          username: 'demo',
          fullname: 'Demo User'
        };
        login(demoUser, 'demo-token');
        setCurrentView('plants');
        toast.success('Welcome to the Solar PV Dashboard demo!');
        return;
      }

      // HARDCODED ADMIN CREDENTIALS - Remove in production
      if (username === 'admin' && password === 'admin123') {
        console.log('Admin login successful');
        const adminUser = {
          id: 'admin-user-1',
          username: 'admin',
          fullname: 'Admin User'
        };
        login(adminUser, 'admin-token');
        setCurrentView('plants');
        toast.success('Welcome Admin! Full access granted.');
        return;
      }

      console.log('Login attempt with API:', username);
      const response = await apiClient.login({ username, password, isInstaller: false });
      
      login(response.user, response.token);
      setCurrentView('plants');
      toast.success(`Welcome back, ${response.user.fullname}!`);
    } catch (error) {
      console.error('Login failed - throwing error for funky message:', error);
      // This error will be caught by LoginForm and show the funky message
      throw error;
    }
  };

  const handleRegister = async (userData: { username: string; fullname: string; password: string; confirmPassword: string; isInstaller: boolean }) => {
    try {
      console.log('Register attempt:', userData.fullname, userData.username);
      const response = await apiClient.register(userData);
      
      login(response.user, response.token);
      setCurrentView('plants');
      toast.success(`Welcome, ${response.user.fullname}! Account created successfully.`);
    } catch (error) {
      console.error('Registration failed:', error);
      toast.error('Registration failed. Please try again.');
    }
  };

  const handleLogout = async () => {
    try {
      await apiClient.logout();
      logout();
      setSelectedDevice(null);
      setCurrentView('login');
      setIsLogin(true);
      toast.info('Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      // Still log out locally even if API call fails
      logout();
      setSelectedDevice(null);
      setCurrentView('login');
      setIsLogin(true);
    }
  };

  const handleDeviceSelect = (device: Device) => {
    setSelectedDevice(device);
    setCurrentView('device');
  };

  const handleBackToPlants = () => {
    setSelectedDevice(null);
    setCurrentView('plants');
  };

  const toggleAuthMode = () => {
    setIsLogin(!isLogin);
    setCurrentView(isLogin ? 'register' : 'login');
  };

  const handleCloseUserGuide = () => {
    setShowUserGuide(false);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Render based on current view state
  if (currentView === 'login') {
    return (
      <LoginForm 
        onLogin={handleLogin} 
        onToggleAuth={toggleAuthMode}
      />
    );
  }

  if (currentView === 'register') {
    return (
      <RegisterForm 
        onToggleAuth={toggleAuthMode}
      />
    );
  }

  if (currentView === 'plants' && user) {
    return (
      <DashboardLayout onLogout={handleLogout}>
        <PlantsOverview 
          user={user}
          onDeviceSelect={handleDeviceSelect}
          onLogout={handleLogout}
        />
        <UserGuide 
          isOpen={showUserGuide} 
          onClose={handleCloseUserGuide} 
        />
      </DashboardLayout>
    );
  }

  if (currentView === 'device' && selectedDevice) {
    return (
      <DashboardLayout onLogout={handleLogout}>
        <DeviceDetail 
          device={selectedDevice}
          onBack={handleBackToPlants}
        />
        <UserGuide 
          isOpen={showUserGuide} 
          onClose={handleCloseUserGuide} 
        />
      </DashboardLayout>
    );
  }

  // Fallback to login if something goes wrong
  return (
    <LoginForm 
      onLogin={handleLogin} 
      onToggleAuth={toggleAuthMode}
    />
  );
};

export default Dashboard;
