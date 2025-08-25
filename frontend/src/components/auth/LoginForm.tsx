import React, { useState } from 'react';
import { User, Lock, Eye, EyeOff, Building, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { GoogleSignInButton } from './GoogleSignInButton';
import { toast } from 'sonner';

interface LoginFormProps {
    onLogin: (username: string, password: string, userType: 'customer' | 'installer') => void;
    onToggleAuth: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin, onToggleAuth }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [userType, setUserType] = useState<'customer' | 'installer'>('customer');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            await onLogin(username, password.trim(), userType); // Trim password
            setUsername('');
            setPassword('');
        } catch (error) {
            const errorMessages = userType === 'installer' 
                ? [
                    "🔧 Access denied! Your installer credentials seem to be taking a coffee break.",
                    "⚡ Oops! Even the best installers sometimes mix up their wires... er, passwords!",
                    "🏗️ Construction site closed! Double-check your installer credentials."
                ]
                : [
                    "☀️ Cloud cover detected! Your login credentials are hiding behind some clouds.",
                    "🌅 The sun hasn't risen on your account yet - check those login details!",
                    "⚡ Energy levels low! Your username or password needs a solar boost."
                ];
            const randomError = errorMessages[Math.floor(Math.random() * errorMessages.length)];
            setError(randomError);
            toast.error("Login Failed", { description: randomError });
        } finally {
            setIsLoading(false);
        }
    };

    const handleGoogleSignIn = async () => {
        console.log('Google Sign-In clicked - requires implementation');
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50 flex items-center justify-center p-4">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <div className={`p-3 rounded-xl w-fit mx-auto mb-4 ${userType === 'installer' ? 'bg-gradient-to-r from-orange-500 to-red-500' : 'bg-gradient-to-r from-blue-500 to-cyan-500'}`}>
                        <User className="w-6 h-6 text-white" />
                    </div>
                    <CardTitle className="text-2xl font-bold text-slate-800">
                        Sign In to Your Account
                    </CardTitle>
                    <p className="text-slate-600 mt-2">
                        Welcome back! Let's get you powered up.
                    </p>
                </CardHeader>

                <div className={`p-4 mx-6 rounded-lg border ${userType === 'installer' ? 'bg-orange-50 border-orange-200' : 'bg-blue-50 border-blue-200'}`}>
                    <h3 className={`font-semibold mb-2 ${userType === 'installer' ? 'text-orange-800' : 'text-blue-800'}`}>Demo Credentials</h3>
                    <div className={`text-sm space-y-1 ${userType === 'installer' ? 'text-orange-700' : 'text-blue-700'}`}>
                        <p><strong>Demo User:</strong> demo / demo123</p>
                        <p><strong>Admin User:</strong> admin / admin123</p>
                        <p className="text-xs mt-2 opacity-75">Try wrong credentials to see fun error messages! 🎉</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-2 px-6">
                    <div className="space-y-2 px-6">
                        <Label htmlFor="username">Username or Email</Label>
                        <Input
                            id="username"
                            type="text"
                            placeholder="Enter your username or email"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            disabled={isLoading}
                        />
                    </div>

                    <div className="space-y-4">
                        <Label htmlFor="password">Password</Label>
                        <div className="relative px-6">
                            <Input
                                id="password"
                                type={showPassword ? 'text' : 'password'}
                                placeholder="Enter your password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                disabled={isLoading}
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
                                disabled={isLoading}
                                tabIndex={-1}
                            >
                                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center space-x-2">
                        <Switch
                            id="user-type"
                            checked={userType === 'installer'}
                            onCheckedChange={() => setUserType(userType === 'customer' ? 'installer' : 'customer')}
                            disabled={isLoading}
                        />
                        <Label htmlFor="user-type">Sign in as Installer</Label>
                    </div>

                    <Button 
                        type="submit" 
                        className={`w-full ${userType === 'installer' ? 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600' : 'bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600'}`}
                        disabled={isLoading}
                    >
                        {isLoading ? 'Signing In...' : `Sign In as ${userType === 'installer' ? 'Installer' : 'Customer'}`}
                    </Button>
                </form>
                
                <div className="mt-4">
                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <span className="w-full border-t" />
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-white px-2 text-muted-foreground">Or continue with</span>
                        </div>
                    </div>
                    <GoogleSignInButton onClick={handleGoogleSignIn} className="mt-4" />
                </div>
                
                <div className="mt-4 text-center">
                    <button
                        onClick={onToggleAuth}
                        className={`text-sm hover:underline ${userType === 'installer' ? 'text-orange-600' : 'text-blue-600'}`}
                    >
                        Don't have an account? Sign up
                    </button>
                </div>
            </Card>
        </div>
    );
};