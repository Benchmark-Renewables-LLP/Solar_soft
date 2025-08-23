import React, { useState, useEffect } from 'react';
import { ShieldCheck, ArrowLeft, RotateCcw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';

interface OTPVerificationProps {
  onVerify: (otp: string) => Promise<void>;
  onBack: () => void;
  email: string;
  onResend: () => Promise<void>;
}

export const OTPVerification: React.FC<OTPVerificationProps> = ({ 
  onVerify, 
  onBack, 
  email, 
  onResend 
}) => {
  const [otp, setOtp] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [countdown, setCountdown] = useState(60);
  const [canResend, setCanResend] = useState(false);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setCanResend(true);
    }
  }, [countdown]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (otp.length !== 6) {
      setError('Please enter a valid 6-digit OTP');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await onVerify(otp);
      toast.success("🎉 Account Verified!", {
        description: "Your account has been successfully verified and created!"
      });
    } catch (error) {
      const errorMessages = [
        "🔒 OTP mismatch! The stars aren't aligned yet.",
        "⚡ Verification failed! Double-check those magical digits.",
        "🌟 Invalid code! Try again with the power of precision.",
        "🔑 Wrong key! The solar vault remains locked."
      ];
      const randomError = errorMessages[Math.floor(Math.random() * errorMessages.length)];
      setError(randomError);
      toast.error("Verification Failed", {
        description: "Invalid OTP. Please check your email and try again."
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setIsLoading(true);
    try {
      await onResend();
      setCountdown(60);
      setCanResend(false);
      toast.success("OTP Resent", {
        description: "A new verification code has been sent to your email."
      });
    } catch (error) {
      toast.error("Failed to resend OTP", {
        description: "Please try again in a moment."
      });
    } finally {
      setIsLoading(false);
    }
  };

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
      <Card className="w-full max-w-md bg-white/10 backdrop-blur-xl border-white/20 shadow-2xl shadow-black/20">
        <CardHeader className="text-center">
          <div className="p-3 rounded-xl w-fit mx-auto mb-4 bg-gradient-to-r from-green-500 to-emerald-500">
            <ShieldCheck className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold text-white">
            Verify Your Account
          </CardTitle>
          <p className="text-white/80">
            We've sent a 6-digit code to <span className="font-medium">{email}</span>
          </p>
        </CardHeader>
        
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-6 bg-red-500/10 border-red-500/20 text-white">
              <AlertDescription className="font-medium text-white">
                {error}
              </AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="flex flex-col items-center space-y-4">
              <InputOTP
                maxLength={6}
                value={otp}
                onChange={(value) => setOtp(value)}
                disabled={isLoading}
              >
                <InputOTPGroup>
                  <InputOTPSlot index={0} className="bg-white/10 border-white/20 text-white text-lg font-bold" />
                  <InputOTPSlot index={1} className="bg-white/10 border-white/20 text-white text-lg font-bold" />
                  <InputOTPSlot index={2} className="bg-white/10 border-white/20 text-white text-lg font-bold" />
                  <InputOTPSlot index={3} className="bg-white/10 border-white/20 text-white text-lg font-bold" />
                  <InputOTPSlot index={4} className="bg-white/10 border-white/20 text-white text-lg font-bold" />
                  <InputOTPSlot index={5} className="bg-white/10 border-white/20 text-white text-lg font-bold" />
                </InputOTPGroup>
              </InputOTP>
              
              <p className="text-white/60 text-sm text-center">
                Enter the 6-digit verification code
              </p>
            </div>

            <div className="flex flex-col space-y-3">
              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white"
                disabled={isLoading || otp.length !== 6}
              >
                {isLoading ? 'Verifying...' : 'Verify Account'}
              </Button>

              <div className="flex items-center justify-between">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={onBack}
                  disabled={isLoading}
                  className="flex items-center space-x-2 text-white/80 hover:text-white hover:bg-white/10"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Back</span>
                </Button>

                <Button
                  type="button"
                  variant="ghost"
                  onClick={handleResend}
                  disabled={isLoading || !canResend}
                  className="flex items-center space-x-2 text-white/80 hover:text-white hover:bg-white/10"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>
                    {canResend ? 'Resend OTP' : `Resend in ${countdown}s`}
                  </span>
                </Button>
              </div>
            </div>
          </form>

          <div className="mt-6 text-center">
            <p className="text-white/60 text-sm">
              Didn't receive the code? Check your spam folder or try resending.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};