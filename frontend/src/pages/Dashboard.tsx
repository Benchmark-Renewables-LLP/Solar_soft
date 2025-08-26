import React, { useState } from 'react';
import { LoginForm } from '@/components/auth/LoginForm';
import { MultiStepRegistration } from '@/components/auth/MultiStepRegistration';
import { OTPVerification } from '@/components/auth/OTPVerification';
import { PlantsOverview } from '@/components/plants/PlantsOverview';
import { DeviceDetail } from '@/components/devices/DeviceDetail';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import UserGuide from '@/components/onboarding/UserGuide';
import { toast } from 'sonner';
import { apiClient } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { Device } from '@/types/device';

type ViewState = 'login' | 'register' | 'verify-otp' | 'plants' | 'device';

const Dashboard = () => {
    const { user, isAuthenticated, login, logout, isLoading } = useAuth();
    const [currentView, setCurrentView] = useState<ViewState>('login');
    const [isLogin, setIsLogin] = useState(true);
    const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
    const [showUserGuide, setShowUserGuide] = useState(false);
    const [registrationEmail, setRegistrationEmail] = useState<string | null>(null);

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
        } catch (error: any) {
            console.error('Login failed:', error);
            let errorMessage = 'Login failed. Please try again.';
            if (error.response?.status === 401) {
                errorMessage = '⚡ Incorrect username/email or password. Check your solar credentials!';
            } else if (error.response?.status === 403) {
                errorMessage = '🔐 Account not verified. Check your email for the OTP!';
            } else if (error.response?.status === 422) {
                errorMessage = '🔋 Invalid input. Ensure username and password meet requirements!';
            } else if (error.response?.status === 500) {
                errorMessage = '🛠️ Solar server is down! Our team is working to restore power.';
            }
            toast.error('Login Failed', { description: errorMessage });
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
            setRegistrationEmail(userData.email);
            setCurrentView('verify-otp');
            toast.success('Registration successful! Check your email for the OTP.');
        } catch (error: any) {
            console.error('Registration failed:', error);
            let errorMessage = 'Registration failed. Please try again.';
            if (error.response?.status === 400) {
                errorMessage = '🔌 Username or email already exists. Try a different one!';
            } else if (error.response?.status === 422) {
                errorMessage = '🔋 Invalid input. Check your details and try again!';
            } else if (error.response?.status === 500) {
                errorMessage = '🛠️ Solar server is down! Our team is working to restore power.';
            }
            toast.error('Registration Failed', { description: errorMessage });
            throw error;
        }
    };

    const handleVerifyOTP = async (otp: string) => {
        if (!registrationEmail) {
            throw new Error('No email provided for OTP verification');
        }
        try {
            const response = await apiClient.verifyOTP({ email: registrationEmail, otp });
            login(response.user, response.token);
            setCurrentView('plants');
            toast.success(`Welcome to the Solar Family, ${response.user.name}! Account verified.`);
        } catch (error: any) {
            console.error('OTP verification failed:', error);
            let errorMessage = 'OTP verification failed. Please try again.';
            if (error.response?.status === 400) {
                errorMessage = '🔐 Invalid or expired OTP. Check the code or resend!';
            } else if (error.response?.status === 500) {
                errorMessage = '🛠️ Solar server is down! Our team is working to restore power.';
            }
            toast.error('OTP Verification Failed', { description: errorMessage });
            throw error;
        }
    };

    const handleResendOTP = async () => {
        if (!registrationEmail) {
            throw new Error('No email provided for OTP resend');
        }
        try {
            const response = await apiClient.register({
                username: "temp",
                name: "temp",
                email: registrationEmail,
                password: "temp",
                userType: "customer",
                whatsappNumber: "temp",
            });
            toast.success('OTP resent! Check your email.');
        } catch (error: any) {
            console.error('Resend OTP failed:', error);
            toast.error('Failed to resend OTP', { description: 'Please try again in a moment.' });
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

    if (currentView === 'verify-otp' && registrationEmail) {
        return (
            <OTPVerification 
                onVerify={handleVerifyOTP}
                onBack={() => setCurrentView('register')}
                email={registrationEmail}
                onResend={handleResendOTP}
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