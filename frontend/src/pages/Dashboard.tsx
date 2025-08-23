import React, { useState } from 'react';
import { LoginForm } from '@/components/auth/LoginForm';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { PlantsOverview, Device } from '@/components/plants/PlantsOverview';
import { DeviceDetail } from '@/components/devices/DeviceDetail';
import { toast } from 'sonner';
import { apiClient } from '@/services/api';

type ViewState = 'login' | 'register' | 'plants' | 'device';

interface User {
  id: string;
  name: string;
  email: string;
}

const Dashboard = () => {
  const [currentView, setCurrentView] = useState<ViewState>('login');
  const [isLogin, setIsLogin] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);

  const handleLogin = async (email: string, password: string) => {
    try {
      // HARDCODED DEMO CREDENTIALS - Remove in production
      if (email === 'demo@solar.com' && password === 'demo123') {
        console.log('Demo login successful');
        setUser({
          id: 'demo-user-1',
          name: 'Demo User',
          email: 'demo@solar.com'
        });
        setCurrentView('plants');
        toast.success('Welcome to the Solar PV Dashboard demo!');
        return;
      }

      // HARDCODED ADMIN CREDENTIALS - Remove in production
      if (email === 'admin@solar.com' && password === 'admin123') {
        console.log('Admin login successful');
        setUser({
          id: 'admin-user-1',
          name: 'Admin User',
          email: 'admin@solar.com'
        });
        setCurrentView('plants');
        toast.success('Welcome Admin! Full access granted.');
        return;
      }

      console.log('Login attempt:', email);
      const response = await apiClient.login({ email, password });
      
      setUser({
        id: response.user.id,
        name: response.user.name,
        email: response.user.email
      });
      setCurrentView('plants');
      toast.success(`Welcome back, ${response.user.name}!`);
    } catch (error) {
      console.error('Login failed:', error);
      toast.error('Login failed. Please try demo credentials: demo@solar.com / demo123 or admin@solar.com / admin123');
    }
  };

  const handleRegister = async (name: string, email: string, password: string) => {
    try {
      console.log('Register attempt:', name, email);
      const response = await apiClient.register({ name, email, password });
      
      setUser({
        id: response.user.id,
        name: response.user.name,
        email: response.user.email
      });
      setCurrentView('plants');
      toast.success(`Welcome, ${response.user.name}! Account created successfully.`);
    } catch (error) {
      console.error('Registration failed:', error);
      toast.error('Registration failed. Please try again.');
    }
  };

  const handleLogout = async () => {
    try {
      await apiClient.logout();
      setUser(null);
      setSelectedDevice(null);
      setCurrentView('login');
      setIsLogin(true);
      toast.info('Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      // Still log out locally even if API call fails
      setUser(null);
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
        onRegister={handleRegister} 
        onToggleAuth={toggleAuthMode}
      />
    );
  }

  if (currentView === 'plants' && user) {
    return (
      <PlantsOverview 
        user={user}
        onDeviceSelect={handleDeviceSelect}
        onLogout={handleLogout}
      />
    );
  }

  if (currentView === 'device' && selectedDevice) {
    return (
      <DeviceDetail 
        device={selectedDevice}
        onBack={handleBackToPlants}
      />
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
