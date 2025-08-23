import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from '@/contexts/AuthContext';
import { 
  ArrowLeft,
  User, 
  Settings, 
  Bell, 
  Shield,
  Mail,
  Phone,
  MapPin,
  Edit3,
  Save,
  Camera,
  Key,
  Smartphone,
  Globe,
  Database,
  Download
} from "lucide-react";
import { toast } from "sonner";

const SettingsPage = () => {
  const { user, isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  
  // Set default profile based on user type
  const getDefaultProfile = () => {
    if (user?.username === 'admin') {
      return {
        fullName: "Priyanshu Uchat",
        email: "priyanshu.uchat@gmail.com",
        phone: "+91 98765 43210",
        address: "Mumbai, Maharashtra, India",
        company: "One Stop Energy Solutions Private Limited",
        role: "System Administrator",
        timezone: "UTC+05:30",
        language: "English",
        bio: "Solar energy enthusiast with 10+ years experience in renewable energy systems and sustainable solutions."
      };
    } else {
      return {
        fullName: user?.fullname || "Demo User",
        email: user?.email || "demo@example.com",
        phone: "+91 87654 32109",
        address: "Delhi, India",
        company: "Solar Solutions Inc.",
        role: "User",
        timezone: "UTC+05:30",
        language: "English",
        bio: "Solar energy enthusiast exploring renewable energy systems."
      };
    }
  };

  const [userProfile, setUserProfile] = useState(getDefaultProfile());

  const [systemSettings, setSystemSettings] = useState({
    autoBackup: true,
    emailNotifications: true,
    smsAlerts: false,
    darkMode: false,
    dataRetention: "1year",
    updateFrequency: "realtime",
    maintenanceMode: false,
    apiAccess: true
  });

  const [securitySettings, setSecuritySettings] = useState({
    twoFactorAuth: true,
    loginAlerts: true,
    sessionTimeout: "30min",
    passwordExpiry: "90days",
    allowedIPs: "",
    downloadReports: true
  });

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const handleSaveProfile = () => {
    setIsEditing(false);
    toast.success("Profile updated successfully!", {
      description: "Your changes have been saved to the system."
    });
  };

  const handleSystemSettingChange = (key: string, value: any) => {
    setSystemSettings(prev => ({
      ...prev,
      [key]: value
    }));
    toast.success("System setting updated!");
  };

  const handleSecuritySettingChange = (key: string, value: any) => {
    setSecuritySettings(prev => ({
      ...prev,
      [key]: value
    }));
    toast.success("Security setting updated!");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-emerald-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button onClick={handleBackToDashboard} variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                  System Configuration
                </h1>
                <p className="text-slate-600 mt-2">
                  Manage your profile, system settings, and security preferences
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="profile">User Profile</TabsTrigger>
            <TabsTrigger value="system">System Settings</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="data">Data Management</TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center space-x-2">
                    <User className="w-5 h-5" />
                    <span>Personal Information</span>
                  </CardTitle>
                  <Button 
                    onClick={isEditing ? handleSaveProfile : () => setIsEditing(true)}
                    variant={isEditing ? "default" : "outline"}
                  >
                    {isEditing ? (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        Save Changes
                      </>
                    ) : (
                      <>
                        <Edit3 className="w-4 h-4 mr-2" />
                        Edit Profile
                      </>
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Profile Picture Section */}
                <div className="flex items-center space-x-6">
                  <div className="relative">
                    <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                      {user?.username === 'admin' ? 'PU' : 'DU'}
                    </div>
                    {isEditing && (
                      <button className="absolute bottom-0 right-0 bg-white border border-slate-300 rounded-full p-2 hover:bg-slate-50">
                        <Camera className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-slate-700">{userProfile.fullName}</h3>
                    <p className="text-slate-500">{userProfile.role}</p>
                    <p className="text-sm text-slate-400">{userProfile.company}</p>
                  </div>
                </div>

                {/* Profile Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      value={userProfile.fullName}
                      onChange={(e) => setUserProfile(prev => ({ ...prev, fullName: e.target.value }))}
                      disabled={!isEditing}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={userProfile.email}
                      onChange={(e) => setUserProfile(prev => ({ ...prev, email: e.target.value }))}
                      disabled={!isEditing}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      value={userProfile.phone}
                      onChange={(e) => setUserProfile(prev => ({ ...prev, phone: e.target.value }))}
                      disabled={!isEditing}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="company">Company</Label>
                    <Input
                      id="company"
                      value={userProfile.company}
                      onChange={(e) => setUserProfile(prev => ({ ...prev, company: e.target.value }))}
                      disabled={!isEditing}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="timezone">Timezone</Label>
                    <Select 
                      value={userProfile.timezone} 
                      onValueChange={(value) => setUserProfile(prev => ({ ...prev, timezone: value }))}
                      disabled={!isEditing}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="UTC+05:30">India Standard Time (UTC+5:30)</SelectItem>
                        <SelectItem value="UTC-08:00">Pacific Time (UTC-8)</SelectItem>
                        <SelectItem value="UTC-05:00">Eastern Time (UTC-5)</SelectItem>
                        <SelectItem value="UTC+00:00">GMT (UTC+0)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="language">Language</Label>
                    <Select 
                      value={userProfile.language} 
                      onValueChange={(value) => setUserProfile(prev => ({ ...prev, language: value }))}
                      disabled={!isEditing}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="English">English</SelectItem>
                        <SelectItem value="Hindi">Hindi</SelectItem>
                        <SelectItem value="Spanish">Spanish</SelectItem>
                        <SelectItem value="French">French</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Input
                    id="address"
                    value={userProfile.address}
                    onChange={(e) => setUserProfile(prev => ({ ...prev, address: e.target.value }))}
                    disabled={!isEditing}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bio">Bio</Label>
                  <Textarea
                    id="bio"
                    value={userProfile.bio}
                    onChange={(e) => setUserProfile(prev => ({ ...prev, bio: e.target.value }))}
                    disabled={!isEditing}
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Settings className="w-5 h-5" />
                    <span>System Preferences</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Auto Backup</Label>
                      <p className="text-sm text-slate-500">Automatically backup system data daily</p>
                    </div>
                    <Switch
                      checked={systemSettings.autoBackup}
                      onCheckedChange={(value) => handleSystemSettingChange('autoBackup', value)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Email Notifications</Label>
                      <p className="text-sm text-slate-500">Receive system alerts via email</p>
                    </div>
                    <Switch
                      checked={systemSettings.emailNotifications}
                      onCheckedChange={(value) => handleSystemSettingChange('emailNotifications', value)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>SMS Alerts</Label>
                      <p className="text-sm text-slate-500">Critical alerts via SMS</p>
                    </div>
                    <Switch
                      checked={systemSettings.smsAlerts}
                      onCheckedChange={(value) => handleSystemSettingChange('smsAlerts', value)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Dark Mode</Label>
                      <p className="text-sm text-slate-500">Switch to dark theme</p>
                    </div>
                    <Switch
                      checked={systemSettings.darkMode}
                      onCheckedChange={(value) => handleSystemSettingChange('darkMode', value)}
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Database className="w-5 h-5" />
                    <span>Data Configuration</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label>Data Retention Period</Label>
                    <Select 
                      value={systemSettings.dataRetention} 
                      onValueChange={(value) => handleSystemSettingChange('dataRetention', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="6months">6 Months</SelectItem>
                        <SelectItem value="1year">1 Year</SelectItem>
                        <SelectItem value="2years">2 Years</SelectItem>
                        <SelectItem value="5years">5 Years</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Update Frequency</Label>
                    <Select 
                      value={systemSettings.updateFrequency} 
                      onValueChange={(value) => handleSystemSettingChange('updateFrequency', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="realtime">Real-time</SelectItem>
                        <SelectItem value="5min">Every 5 minutes</SelectItem>
                        <SelectItem value="15min">Every 15 minutes</SelectItem>
                        <SelectItem value="1hour">Hourly</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>API Access</Label>
                      <p className="text-sm text-slate-500">Allow third-party API integration</p>
                    </div>
                    <Switch
                      checked={systemSettings.apiAccess}
                      onCheckedChange={(value) => handleSystemSettingChange('apiAccess', value)}
                    />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="security" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Shield className="w-5 h-5" />
                    <span>Security Settings</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Two-Factor Authentication</Label>
                      <p className="text-sm text-slate-500">Extra security for your account</p>
                    </div>
                    <Switch
                      checked={securitySettings.twoFactorAuth}
                      onCheckedChange={(value) => handleSecuritySettingChange('twoFactorAuth', value)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Login Alerts</Label>
                      <p className="text-sm text-slate-500">Notify on new device logins</p>
                    </div>
                    <Switch
                      checked={securitySettings.loginAlerts}
                      onCheckedChange={(value) => handleSecuritySettingChange('loginAlerts', value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Session Timeout</Label>
                    <Select 
                      value={securitySettings.sessionTimeout} 
                      onValueChange={(value) => handleSecuritySettingChange('sessionTimeout', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="15min">15 minutes</SelectItem>
                        <SelectItem value="30min">30 minutes</SelectItem>
                        <SelectItem value="1hour">1 hour</SelectItem>
                        <SelectItem value="4hours">4 hours</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Password Expiry</Label>
                    <Select 
                      value={securitySettings.passwordExpiry} 
                      onValueChange={(value) => handleSecuritySettingChange('passwordExpiry', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="30days">30 days</SelectItem>
                        <SelectItem value="90days">90 days</SelectItem>
                        <SelectItem value="180days">180 days</SelectItem>
                        <SelectItem value="never">Never expires</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Key className="w-5 h-5" />
                    <span>Access Control</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label>Allowed IP Addresses</Label>
                    <Textarea
                      placeholder="Enter IP addresses (one per line)&#10;192.168.1.100&#10;10.0.0.50"
                      value={securitySettings.allowedIPs}
                      onChange={(e) => setSecuritySettings(prev => ({ ...prev, allowedIPs: e.target.value }))}
                      rows={4}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Download Reports</Label>
                      <p className="text-sm text-slate-500">Allow downloading system reports</p>
                    </div>
                    <Switch
                      checked={securitySettings.downloadReports}
                      onCheckedChange={(value) => handleSecuritySettingChange('downloadReports', value)}
                    />
                  </div>

                  <div className="pt-4 border-t border-slate-200">
                    <Button variant="outline" className="w-full">
                      <Key className="w-4 h-4 mr-2" />
                      Change Password
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="data" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Database className="w-5 h-5" />
                  <span>Data Management</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h3 className="font-semibold text-blue-800 mb-2">Database Status</h3>
                    <p className="text-2xl font-bold text-blue-600">127.3 GB</p>
                    <p className="text-sm text-blue-600">Total storage used</p>
                  </div>
                  
                  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <h3 className="font-semibold text-green-800 mb-2">Backup Status</h3>
                    <p className="text-lg font-bold text-green-600">Up to date</p>
                    <p className="text-sm text-green-600">Last backup: 2 hours ago</p>
                  </div>
                  
                  <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <h3 className="font-semibold text-purple-800 mb-2">Data Points</h3>
                    <p className="text-2xl font-bold text-purple-600">2.4M</p>
                    <p className="text-sm text-purple-600">Total records</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <div>
                      <h4 className="font-medium">Export All Data</h4>
                      <p className="text-sm text-slate-500">Download complete system data as CSV/JSON</p>
                    </div>
                    <Button variant="outline">
                      <Download className="w-4 h-4 mr-2" />
                      Export
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <div>
                      <h4 className="font-medium">Create Backup</h4>
                      <p className="text-sm text-slate-500">Manual backup of current system state</p>
                    </div>
                    <Button variant="outline">
                      <Database className="w-4 h-4 mr-2" />
                      Backup Now
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-200">
                    <div>
                      <h4 className="font-medium text-red-800">Purge Old Data</h4>
                      <p className="text-sm text-red-600">Remove data older than retention period</p>
                    </div>
                    <Button variant="destructive">
                      <Database className="w-4 h-4 mr-2" />
                      Purge Data
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default SettingsPage;
