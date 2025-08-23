
import React, { useState } from 'react';
import { RegisterForm } from '../components/auth/RegisterForm';
import { LoginForm } from '../components/auth/LoginForm';
import { useNavigate } from 'react-router-dom';

const AuthView: React.FC = () => {
  const [isRegistering, setIsRegistering] = useState(false);
  const navigate = useNavigate();

  const handleRegisterSuccess = () => {
    alert('Registration successful! Redirecting to dashboard...');
    navigate('/dashboard');
  };

  const handleLoginSuccess = () => {
    alert('Login successful! Redirecting to dashboard...');
    navigate('/dashboard');
  };

  return (
    <div>
      {isRegistering ? (
        <RegisterForm onToggleAuth={() => setIsRegistering(false)} />
      ) : (
        <LoginForm onLogin={handleLoginSuccess} onToggleAuth={() => setIsRegistering(true)} />
      )}
    </div>
  );
};

export default AuthView;
