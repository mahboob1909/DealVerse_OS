"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { 
  Settings,
  User,
  Bell,
  Shield,
  Palette,
  Database,
  Key,
  Globe,
  Mail,
  Phone,
  Building,
  Save,
  Upload,
  Download,
  Trash2,
  Eye,
  EyeOff,
  AlertTriangle,
  CheckCircle
} from "lucide-react";
import { useState } from "react";

export default function SettingsPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    sms: false,
    deals: true,
    compliance: true,
    reports: false
  });

  const [profile, setProfile] = useState({
    firstName: "Sarah",
    lastName: "Chen",
    email: "sarah.chen@dealverse.com",
    phone: "+1 (555) 123-4567",
    title: "Senior Investment Banker",
    department: "M&A Division",
    location: "New York, NY"
  });

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-dealverse-navy to-dealverse-blue bg-clip-text text-transparent">
          Settings
        </h1>
        <p className="text-dealverse-medium-gray dark:text-dealverse-light-gray">
          Manage your account settings and preferences
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="billing">Billing</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold text-dealverse-navy">Profile Information</CardTitle>
                  <CardDescription className="text-dealverse-medium-gray">
                    Update your personal information and contact details
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label className="text-sm font-medium text-dealverse-navy">First Name</label>
                      <Input 
                        value={profile.firstName}
                        onChange={(e) => setProfile({...profile, firstName: e.target.value})}
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-dealverse-navy">Last Name</label>
                      <Input 
                        value={profile.lastName}
                        onChange={(e) => setProfile({...profile, lastName: e.target.value})}
                        className="mt-1"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-dealverse-navy">Email Address</label>
                    <Input 
                      type="email"
                      value={profile.email}
                      onChange={(e) => setProfile({...profile, email: e.target.value})}
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium text-dealverse-navy">Phone Number</label>
                    <Input 
                      value={profile.phone}
                      onChange={(e) => setProfile({...profile, phone: e.target.value})}
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium text-dealverse-navy">Job Title</label>
                    <Input 
                      value={profile.title}
                      onChange={(e) => setProfile({...profile, title: e.target.value})}
                      className="mt-1"
                    />
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label className="text-sm font-medium text-dealverse-navy">Department</label>
                      <Input 
                        value={profile.department}
                        onChange={(e) => setProfile({...profile, department: e.target.value})}
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-dealverse-navy">Location</label>
                      <Input 
                        value={profile.location}
                        onChange={(e) => setProfile({...profile, location: e.target.value})}
                        className="mt-1"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end space-x-2 pt-4">
                    <Button variant="outline">Cancel</Button>
                    <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90">
                      <Save className="h-4 w-4 mr-2" />
                      Save Changes
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div>
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-dealverse-navy">Profile Picture</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-center">
                    <Avatar className="h-24 w-24">
                      <AvatarImage src="/avatars/sarah-chen.png" alt="Profile" />
                      <AvatarFallback className="bg-gradient-to-br from-dealverse-blue to-dealverse-green text-white text-xl font-semibold">
                        SC
                      </AvatarFallback>
                    </Avatar>
                  </div>
                  <div className="space-y-2">
                    <Button variant="outline" className="w-full">
                      <Upload className="h-4 w-4 mr-2" />
                      Upload New Photo
                    </Button>
                    <Button variant="outline" className="w-full text-dealverse-coral">
                      <Trash2 className="h-4 w-4 mr-2" />
                      Remove Photo
                    </Button>
                  </div>
                  <p className="text-xs text-dealverse-medium-gray text-center">
                    JPG, PNG or GIF. Max size 2MB.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-dealverse-navy">Password & Authentication</CardTitle>
                <CardDescription className="text-dealverse-medium-gray">
                  Manage your password and two-factor authentication
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-dealverse-navy">Current Password</label>
                  <div className="relative mt-1">
                    <Input 
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter current password"
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute right-2 top-1/2 transform -translate-y-1/2"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-dealverse-navy">New Password</label>
                  <Input 
                    type="password"
                    placeholder="Enter new password"
                    className="mt-1"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium text-dealverse-navy">Confirm New Password</label>
                  <Input 
                    type="password"
                    placeholder="Confirm new password"
                    className="mt-1"
                  />
                </div>

                <div className="border-t pt-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-dealverse-navy">Two-Factor Authentication</h4>
                      <p className="text-sm text-dealverse-medium-gray">Add an extra layer of security</p>
                    </div>
                    <Switch />
                  </div>
                </div>

                <Button className="w-full bg-dealverse-blue hover:bg-dealverse-blue/90">
                  <Save className="h-4 w-4 mr-2" />
                  Update Password
                </Button>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-dealverse-navy">Security Status</CardTitle>
                <CardDescription className="text-dealverse-medium-gray">
                  Your account security overview
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-dealverse-green" />
                    <div>
                      <p className="font-medium text-dealverse-navy">Strong Password</p>
                      <p className="text-sm text-dealverse-medium-gray">Your password meets security requirements</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="h-5 w-5 text-dealverse-amber" />
                    <div>
                      <p className="font-medium text-dealverse-navy">Two-Factor Authentication</p>
                      <p className="text-sm text-dealverse-medium-gray">Enable 2FA for better security</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-dealverse-green" />
                    <div>
                      <p className="font-medium text-dealverse-navy">Email Verified</p>
                      <p className="text-sm text-dealverse-medium-gray">Your email address is verified</p>
                    </div>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <h5 className="font-medium text-dealverse-navy mb-2">Recent Activity</h5>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-dealverse-medium-gray">Last login:</span>
                      <span>Today, 9:30 AM</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-dealverse-medium-gray">Location:</span>
                      <span>New York, NY</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-dealverse-medium-gray">Device:</span>
                      <span>Chrome on Windows</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-dealverse-navy">Notification Preferences</CardTitle>
              <CardDescription className="text-dealverse-medium-gray">
                Choose how you want to be notified about important updates
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="font-medium text-dealverse-navy mb-4">Notification Channels</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Mail className="h-5 w-5 text-dealverse-blue" />
                      <div>
                        <p className="font-medium text-dealverse-navy">Email Notifications</p>
                        <p className="text-sm text-dealverse-medium-gray">Receive notifications via email</p>
                      </div>
                    </div>
                    <Switch 
                      checked={notifications.email}
                      onCheckedChange={(checked) => setNotifications({...notifications, email: checked})}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Bell className="h-5 w-5 text-dealverse-blue" />
                      <div>
                        <p className="font-medium text-dealverse-navy">Push Notifications</p>
                        <p className="text-sm text-dealverse-medium-gray">Receive browser push notifications</p>
                      </div>
                    </div>
                    <Switch 
                      checked={notifications.push}
                      onCheckedChange={(checked) => setNotifications({...notifications, push: checked})}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Phone className="h-5 w-5 text-dealverse-blue" />
                      <div>
                        <p className="font-medium text-dealverse-navy">SMS Notifications</p>
                        <p className="text-sm text-dealverse-medium-gray">Receive text message alerts</p>
                      </div>
                    </div>
                    <Switch 
                      checked={notifications.sms}
                      onCheckedChange={(checked) => setNotifications({...notifications, sms: checked})}
                    />
                  </div>
                </div>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium text-dealverse-navy mb-4">Notification Types</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-dealverse-navy">Deal Updates</p>
                      <p className="text-sm text-dealverse-medium-gray">Notifications about deal progress and changes</p>
                    </div>
                    <Switch 
                      checked={notifications.deals}
                      onCheckedChange={(checked) => setNotifications({...notifications, deals: checked})}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-dealverse-navy">Compliance Alerts</p>
                      <p className="text-sm text-dealverse-medium-gray">Important compliance and regulatory updates</p>
                    </div>
                    <Switch 
                      checked={notifications.compliance}
                      onCheckedChange={(checked) => setNotifications({...notifications, compliance: checked})}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-dealverse-navy">Weekly Reports</p>
                      <p className="text-sm text-dealverse-medium-gray">Weekly summary and performance reports</p>
                    </div>
                    <Switch 
                      checked={notifications.reports}
                      onCheckedChange={(checked) => setNotifications({...notifications, reports: checked})}
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90">
                  <Save className="h-4 w-4 mr-2" />
                  Save Preferences
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="preferences" className="space-y-6">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-dealverse-navy">Application Preferences</CardTitle>
              <CardDescription className="text-dealverse-medium-gray">
                Customize your DealVerse OS experience
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-dealverse-navy">Dark Mode</p>
                    <p className="text-sm text-dealverse-medium-gray">Switch to dark theme</p>
                  </div>
                  <Switch />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-dealverse-navy">Auto-save</p>
                    <p className="text-sm text-dealverse-medium-gray">Automatically save changes</p>
                  </div>
                  <Switch defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-dealverse-navy">Compact View</p>
                    <p className="text-sm text-dealverse-medium-gray">Show more information in less space</p>
                  </div>
                  <Switch />
                </div>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium text-dealverse-navy mb-4">Language & Region</h4>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="text-sm font-medium text-dealverse-navy">Language</label>
                    <select className="w-full mt-1 p-2 border border-gray-300 rounded-md">
                      <option>English (US)</option>
                      <option>English (UK)</option>
                      <option>Spanish</option>
                      <option>French</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-dealverse-navy">Timezone</label>
                    <select className="w-full mt-1 p-2 border border-gray-300 rounded-md">
                      <option>Eastern Time (ET)</option>
                      <option>Central Time (CT)</option>
                      <option>Mountain Time (MT)</option>
                      <option>Pacific Time (PT)</option>
                    </select>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integrations" className="space-y-6">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-dealverse-navy">Third-Party Integrations</CardTitle>
              <CardDescription className="text-dealverse-medium-gray">
                Connect DealVerse OS with your favorite tools
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-dealverse-light-gray rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-dealverse-blue/20 rounded-lg flex items-center justify-center">
                      <Mail className="h-5 w-5 text-dealverse-blue" />
                    </div>
                    <div>
                      <p className="font-medium text-dealverse-navy">Microsoft Outlook</p>
                      <p className="text-sm text-dealverse-medium-gray">Sync calendar and emails</p>
                    </div>
                  </div>
                  <Button variant="outline">Connect</Button>
                </div>

                <div className="flex items-center justify-between p-4 border border-dealverse-light-gray rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-dealverse-green/20 rounded-lg flex items-center justify-center">
                      <Database className="h-5 w-5 text-dealverse-green" />
                    </div>
                    <div>
                      <p className="font-medium text-dealverse-navy">Salesforce</p>
                      <p className="text-sm text-dealverse-medium-gray">Import client data and contacts</p>
                    </div>
                  </div>
                  <Badge className="bg-dealverse-green/10 text-dealverse-green">Connected</Badge>
                </div>

                <div className="flex items-center justify-between p-4 border border-dealverse-light-gray rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-dealverse-amber/20 rounded-lg flex items-center justify-center">
                      <Building className="h-5 w-5 text-dealverse-amber" />
                    </div>
                    <div>
                      <p className="font-medium text-dealverse-navy">Bloomberg Terminal</p>
                      <p className="text-sm text-dealverse-medium-gray">Real-time market data</p>
                    </div>
                  </div>
                  <Button variant="outline">Connect</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="billing" className="space-y-6">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-dealverse-navy">Billing & Subscription</CardTitle>
              <CardDescription className="text-dealverse-medium-gray">
                Manage your subscription and billing information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="p-4 bg-dealverse-blue/5 border border-dealverse-blue/20 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-dealverse-navy">Enterprise Plan</h4>
                    <p className="text-sm text-dealverse-medium-gray">Full access to all features</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-dealverse-navy">$299</p>
                    <p className="text-sm text-dealverse-medium-gray">per month</p>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-dealverse-navy mb-4">Payment Method</h4>
                <div className="p-4 border border-dealverse-light-gray rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-dealverse-blue/20 rounded flex items-center justify-center">
                        <span className="text-xs font-bold text-dealverse-blue">••••</span>
                      </div>
                      <div>
                        <p className="font-medium text-dealverse-navy">•••• •••• •••• 4242</p>
                        <p className="text-sm text-dealverse-medium-gray">Expires 12/25</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">Update</Button>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-dealverse-navy mb-4">Billing History</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 border border-dealverse-light-gray rounded-lg">
                    <div>
                      <p className="font-medium text-dealverse-navy">January 2024</p>
                      <p className="text-sm text-dealverse-medium-gray">Enterprise Plan</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-dealverse-navy">$299.00</p>
                      <Button variant="ghost" size="sm">
                        <Download className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
