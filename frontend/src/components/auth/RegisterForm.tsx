
import React from 'react';
import { MultiStepRegistration } from './MultiStepRegistration';

interface RegisterFormProps {
  onRegister: (name: string, email: string, password: string) => void;
  onToggleAuth: () => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onRegister, onToggleAuth }) => {
  const handleRegister = (userData: any) => {
    // Transform the multi-step form data to match the expected format
    onRegister(userData.username, userData.email, userData.password);
  };

  return (
    <MultiStepRegistration
      onRegister={handleRegister}
      onToggleAuth={onToggleAuth}
    />
  );
};
