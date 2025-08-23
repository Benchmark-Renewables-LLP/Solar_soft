
import React from 'react';
import { MultiStepRegistration } from './MultiStepRegistration';
import { apiClient } from '../../services/api';
import { toast } from 'sonner';

interface RegisterFormProps {
    onToggleAuth: () => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onToggleAuth }) => {
    const handleRegister = async (userData: { username: string; fullname: string; password: string; confirmPassword: string; isInstaller: boolean }) => {
        try {
            console.log('Register payload:', userData);
            const response = await apiClient.register(userData);
            toast.success(`Welcome, ${response.user.fullname}! Account created successfully.`);
        } catch (error) {
            console.error('Registration error:', error);
            toast.error('Registration failed. Please try again.');
            throw error;
        }
    };

    return (
        <MultiStepRegistration
            onRegister={handleRegister}
            onToggleAuth={onToggleAuth}
        />
    );
};
