import React, { useState } from 'react';
import { LoginForm } from '@/components/auth/LoginForm';
import { MultiStepRegistration } from '@/components/auth/MultiStepRegistration';
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

    React.useEffect(() => {
        if (isAuthenticated && user) {
            setCurrentView('plants');
            const hasSeenGuide = localStorage.getItem('hasSeenGuide');
            if (!hasSeenGuide) {
                setShowUserGuide(true);
                localStorage.setItem('hasSeenGuide', 'true');
            }
        } else if (!isLoading) {
            setCurrentView('login');
        }
    }, [isAuthenticated, user, isLoading]);

    const handleLogin = async (username: string, password: string, userType: 'customer' | 'installer') => {
        try {
            console.log('Login attempt with API:', username, userType);
            const response = await apiClient.login({ username: username.trim(), password: password.trim(), userType });
            login(response.user, response.token);
            setCurrentView('plants');
            toast.success(`Welcome back, ${response.user.name}!`);
        } catch (error) {
            console.error('Login failed:', error);
            toast.error('Login failed. Please check your credentials.');
            throw error;
        }
    };

    const handleRegister = async (userData: {
        username: string;
        fullname: string;
        password: string;
        confirmPassword: string;
        email: string;
        whatsappNumber: string;
        address?: string;
        panelBrand?: string;
        panelCapacity?: string;
        panelType?: string;
        inverterBrand?: string;
        inverterCapacity?: string;
        isInstaller: boolean;
    }) => {
        try {
            console.log('Register attempt:', userData.fullname, userData.username);
            const response = await apiClient.register({
                username: userData.username.trim(),
                name: userData.fullname.trim(),
                email: userData.email.trim(),
                password: userData.password.trim(),
                userType: userData.isInstaller ? 'installer' : 'customer',
                whatsappNumber: userData.whatsappNumber.trim(),
                address: userData.address?.trim(),
                panelBrand: userData.panelBrand?.trim(),
                panelCapacity: userData.panelCapacity ? parseFloat(userData.panelCapacity) : undefined,
                panelType: userData.panelType?.trim(),
                inverterBrand: userData.inverterBrand?.trim(),
                inverterCapacity: userData.inverterCapacity ? parseFloat(userData.inverterCapacity) : undefined,
            });
            login(response.user, response.token);
            setCurrentView('plants');
            toast.success(`Welcome to the Solar Family, ${response.user.name}! Account created successfully.`);
        } catch (error: any) {
            console.error('Registration failed:', error);
            toast.error('Registration failed. ' + (error.response?.data?.detail || 'Please try again.'));
            throw error;
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
            logout();
            setSelectedDevice(null);
            setCurrentView('login');
            setIsLogin(true);
            toast.info('Logged out successfully');
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
            <MultiStepRegistration 
                onRegister={handleRegister}
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

    return (
        <LoginForm 
            onLogin={handleLogin} 
            onToggleAuth={toggleAuthMode}
        />
    );
};

export default Dashboard;