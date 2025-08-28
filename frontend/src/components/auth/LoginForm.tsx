import React, { useState } from "react";
import { User, Eye, EyeOff } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { GoogleSignInButton } from "./GoogleSignInButton";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import logo from "../../../assets/logo.png";// ✅ Only if you're using Next.js

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
    <motion.div
      className="min-h-screen relative flex flex-col p-6 
                 bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50 
                 dark:from-slate-900 dark:via-slate-950 dark:to-black
                 transition-colors duration-500"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* ✅ Company Logo + Name */}
      <div className="absolute top-6 left-6 flex items-center space-x-3">
        <img src={logo} 
          alt="Company Logo"
          width={40}
          height={40}
          className="rounded-md shadow-md"
        />
        <span className="text-[30px] font-bold text-slate-900 dark:text-white tracking-wide">
          SolarSync
        </span>
      </div>

      {/* Solar Animated Background */}
      <motion.div
        className="absolute w-[700px] h-[800px] rounded-full 
                   bg-gradient-to-br from-yellow-300 via-orange-400 to-red-500 
                   blur-3xl opacity-20 dark:opacity-30"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 60, ease: "linear" }}
      />
      <motion.div
        className="absolute w-[400px] h-[400px] rounded-full 
                   bg-gradient-to-br from-sky-300 via-cyan-400 to-emerald-500 
                   blur-3xl opacity-20 dark:opacity-30"
        animate={{ rotate: -360 }}
        transition={{ repeat: Infinity, duration: 90, ease: "linear" }}
      />

      {/* Card (centered form) */}
      <div className="flex flex-1 items-center justify-center">
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 120, damping: 15 }}
        >
          <Card className="w-full max-w-lg shadow-2xl rounded-3xl backdrop-blur-lg
                           bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-700">
            {/* Header */}
            <CardHeader className="text-center space-y-3 p-6">
              <motion.div
                whileHover={{ scale: 1.1, rotate: 3 }}
                whileTap={{ scale: 0.95 }}
                className={`p-5 rounded-2xl w-fit mx-auto shadow-xl 
                  ${
                    userType === "installer"
                      ? "bg-gradient-to-r from-orange-500 to-red-500"
                      : "bg-gradient-to-r from-blue-500 to-cyan-500"
                  }`}
              >
                <User className="w-8 h-6 text-white" />
              </motion.div>
              <CardTitle className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                Sign In to Your Account
              </CardTitle>
              <p className="text-slate-600 dark:text-slate-300 text-base leading-relaxed">
                Welcome back! Let’s get you powered up ⚡
              </p>
            </CardHeader>

            <CardContent className="px-8 py-4">
              {/* Error Animation */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    className="mb-4 text-red-500 dark:text-red-400 text-sm text-center font-medium"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                  >
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label
                    htmlFor="username"
                    className="text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300"
                  >
                    Username or Email
                  </Label>
                  <motion.div whileFocusWithin={{ scale: 1.02 }}>
                    <Input
                      id="username"
                      type="text"
                      placeholder="Enter your username or email"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                      disabled={isLoading}
                      className="text-sm rounded-lg font-medium text-slate-800 dark:text-slate-100 
                                 placeholder:text-slate-400 dark:placeholder:text-slate-500 "
                    />
                  </motion.div>
                </div>

                <div className="space-y-2">
                  <Label
                    htmlFor="password"
                    className="text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300"
                  >
                    Password
                  </Label>
                  <motion.div
                    className="relative"
                    whileFocusWithin={{ scale: 1.02 }}
                  >
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      disabled={isLoading}
                      className="text-sm font-medium text-slate-800 dark:text-slate-100 
                                 placeholder:text-slate-400 dark:placeholder:text-slate-500"
                    />
                    <motion.button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 
                                 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 
                                 transition-colors"
                      disabled={isLoading}
                      tabIndex={-1}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      {showPassword ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </motion.button>
                  </motion.div>
                </div>

                <motion.div
                  className="flex items-center space-x-2"
                  whileHover={{ scale: 1.02 }}
                >
                  <Switch
                    id="user-type"
                    checked={userType === "installer"}
                    onCheckedChange={() =>
                      setUserType(
                        userType === "customer" ? "installer" : "customer"
                      )
                    }
                    disabled={isLoading}
                  />
                  <Label
                    htmlFor="user-type"
                    className="text-sm text-slate-700 dark:text-slate-300"
                  >
                    Sign in as Installer
                  </Label>
                </motion.div>

                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    type="submit"
                    className={`w-full h-12 font-bold tracking-wide uppercase text-white rounded-xl shadow-lg transition-all
                      ${
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
                </motion.div>
              </form>

              {/* Divider */}
              <motion.div
                className="mt-8"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <div className="relative flex items-center">
                  <span className="w-full border-t dark:border-slate-700" />
                  <span className="absolute left-1/2 -translate-x-1/2 bg-white dark:bg-slate-900 
                                   px-2 text-xs text-slate-500 dark:text-slate-400 uppercase">
                    Or continue with
                  </span>
                </div>
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <GoogleSignInButton
                    onClick={handleGoogleSignIn}
                    className="mt-4 w-full"
                  />
                </motion.div>
              </motion.div>

              {/* Toggle Auth */}
              <motion.div
                className="mt-6 text-center"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <button
                  onClick={onToggleAuth}
                  className={`text-sm font-medium hover:underline underline-offset-4 transition-colors 
                    ${
                      userType === "installer"
                        ? "text-orange-600"
                        : "text-blue-600"
                    }
                    dark:text-emerald-400`}
                >
                  Don’t have an account? Sign up
                </button>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
};
