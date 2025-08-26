import React, { useState } from "react";
import { User, Eye, EyeOff } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { GoogleSignInButton } from "./GoogleSignInButton";
import { toast } from "sonner";

interface LoginFormProps {
  onLogin: (
    username: string,
    password: string,
    userType: "customer" | "installer"
  ) => void;
  onToggleAuth: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onLogin,
  onToggleAuth,
}) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [userType, setUserType] = useState<"customer" | "installer">(
    "customer"
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      await onLogin(username, password.trim(), userType);
      setUsername("");
      setPassword("");
    } catch (error) {
      const errorMessages =
        userType === "installer"
          ? [
              "🔧 Access denied! Your installer credentials seem to be taking a coffee break.",
              "⚡ Oops! Even the best installers sometimes mix up their wires... er, passwords!",
              "🏗️ Construction site closed! Double-check your installer credentials.",
            ]
          : [
              "☀️ Cloud cover detected! Your login credentials are hiding behind some clouds.",
              "🌅 The sun hasn't risen on your account yet - check those login details!",
              "⚡ Energy levels low! Your username or password needs a solar boost.",
            ];
      const randomError =
        errorMessages[Math.floor(Math.random() * errorMessages.length)];
      setError(randomError);
      toast.error("Login Failed", { description: randomError });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    console.log("Google Sign-In clicked - requires implementation");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50 flex items-center justify-center p-6">
      <Card className="w-full max-w-md shadow-2xl rounded-2xl">
        {/* Header */}
        <CardHeader className="text-center space-y-3">
          <div
            className={`p-4 rounded-2xl w-fit mx-auto shadow-lg ${
              userType === "installer"
                ? "bg-gradient-to-r from-orange-500 to-red-500"
                : "bg-gradient-to-r from-blue-500 to-cyan-500"
            }`}
          >
            <User className="w-7 h-7 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold text-slate-800">
            Sign In to Your Account
          </CardTitle>
          <p className="text-slate-600 text-sm">
            Welcome back! Let’s get you powered up ⚡
          </p>
        </CardHeader>

        <CardContent className="px-6 py-4">
          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
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

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
                  disabled={isLoading}
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="user-type"
                checked={userType === "installer"}
                onCheckedChange={() =>
                  setUserType(userType === "customer" ? "installer" : "customer")
                }
                disabled={isLoading}
              />
              <Label htmlFor="user-type" className="text-sm text-slate-700">
                Sign in as Installer
              </Label>
            </div>

            <Button
              type="submit"
              className={`w-full h-11 text-white font-semibold rounded-xl shadow-md transition-all ${
                userType === "installer"
                  ? "bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
                  : "bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600"
              }`}
              disabled={isLoading}
            >
              {isLoading
                ? "Signing In..."
                : `Sign In as ${
                    userType === "installer" ? "Installer" : "Customer"
                  }`}
            </Button>
          </form>

          {/* Divider */}
          <div className="mt-6">
            <div className="relative flex items-center">
              <span className="w-full border-t" />
              <span className="absolute left-1/2 -translate-x-1/2 bg-white px-2 text-xs text-slate-500 uppercase">
                Or continue with
              </span>
            </div>
            <GoogleSignInButton
              onClick={handleGoogleSignIn}
              className="mt-4 w-full"
            />
          </div>

          {/* Toggle Auth */}
          <div className="mt-6 text-center">
            <button
              onClick={onToggleAuth}
              className={`text-sm font-medium hover:underline transition-colors ${
                userType === "installer" ? "text-orange-600" : "text-blue-600"
              }`}
            >
              Don’t have an account? Sign up
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
