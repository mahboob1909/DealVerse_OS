"use client";

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import {
  Mail,
  Smartphone,
  MessageSquare,
  Bell,
  Clock,
  Shield,
  Volume2,
  VolumeX,
  Settings,
  Save,
  RotateCcw
} from "lucide-react";
import { NotificationPreferences as PreferencesType } from "@/lib/types/notifications";

interface NotificationPreferencesProps {
  preferences: PreferencesType | null;
  onUpdatePreferences: (updates: Partial<PreferencesType>) => Promise<void>;
}

export function NotificationPreferences({
  preferences,
  onUpdatePreferences
}: NotificationPreferencesProps) {
  const [localPreferences, setLocalPreferences] = useState<Partial<PreferencesType>>(
    preferences || {}
  );
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const updateLocalPreference = (key: keyof PreferencesType, value: any) => {
    setLocalPreferences(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    if (!hasChanges) return;

    setIsSaving(true);
    try {
      await onUpdatePreferences(localPreferences);
      setHasChanges(false);
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    setLocalPreferences(preferences || {});
    setHasChanges(false);
  };

  if (!preferences) {
    return (
      <div className="p-4 text-center text-sm text-muted-foreground">
        Loading preferences...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Notification Preferences</h3>
          <p className="text-sm text-muted-foreground">
            Customize how and when you receive notifications
          </p>
        </div>
        
        {hasChanges && (
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-1" />
              Reset
            </Button>
            <Button size="sm" onClick={handleSave} disabled={isSaving}>
              <Save className="h-4 w-4 mr-1" />
              {isSaving ? 'Saving...' : 'Save'}
            </Button>
          </div>
        )}
      </div>

      {/* Delivery Channels */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Delivery Channels
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell className="h-4 w-4 text-blue-600" />
              <Label htmlFor="in-app">In-App Notifications</Label>
            </div>
            <Switch
              id="in-app"
              checked={localPreferences.in_app_enabled ?? true}
              onCheckedChange={(checked) => updateLocalPreference('in_app_enabled', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Mail className="h-4 w-4 text-green-600" />
              <Label htmlFor="email">Email Notifications</Label>
            </div>
            <Switch
              id="email"
              checked={localPreferences.email_enabled ?? true}
              onCheckedChange={(checked) => updateLocalPreference('email_enabled', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Smartphone className="h-4 w-4 text-purple-600" />
              <Label htmlFor="push">Push Notifications</Label>
            </div>
            <Switch
              id="push"
              checked={localPreferences.push_enabled ?? true}
              onCheckedChange={(checked) => updateLocalPreference('push_enabled', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-orange-600" />
              <Label htmlFor="sms">SMS Notifications</Label>
            </div>
            <Switch
              id="sms"
              checked={localPreferences.sms_enabled ?? false}
              onCheckedChange={(checked) => updateLocalPreference('sms_enabled', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Notification Categories */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Notification Categories</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="document">Document Notifications</Label>
            <Switch
              id="document"
              checked={localPreferences.document_notifications ?? true}
              onCheckedChange={(checked) => updateLocalPreference('document_notifications', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="collaboration">Collaboration Notifications</Label>
            <Switch
              id="collaboration"
              checked={localPreferences.collaboration_notifications ?? true}
              onCheckedChange={(checked) => updateLocalPreference('collaboration_notifications', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="system">System Notifications</Label>
            <Switch
              id="system"
              checked={localPreferences.system_notifications ?? true}
              onCheckedChange={(checked) => updateLocalPreference('system_notifications', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="security">Security Notifications</Label>
            <Switch
              id="security"
              checked={localPreferences.security_notifications ?? true}
              onCheckedChange={(checked) => updateLocalPreference('security_notifications', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="workflow">Workflow Notifications</Label>
            <Switch
              id="workflow"
              checked={localPreferences.workflow_notifications ?? true}
              onCheckedChange={(checked) => updateLocalPreference('workflow_notifications', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="ai-analysis">AI Analysis Notifications</Label>
            <Switch
              id="ai-analysis"
              checked={localPreferences.ai_analysis_notifications ?? true}
              onCheckedChange={(checked) => updateLocalPreference('ai_analysis_notifications', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Priority & Timing */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Priority & Timing
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="priority">Minimum Priority Level</Label>
            <Select
              value={localPreferences.minimum_priority || 'low'}
              onValueChange={(value) => updateLocalPreference('minimum_priority', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select minimum priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {localPreferences.quiet_hours_enabled ? (
                <VolumeX className="h-4 w-4 text-gray-600" />
              ) : (
                <Volume2 className="h-4 w-4 text-blue-600" />
              )}
              <Label htmlFor="quiet-hours">Enable Quiet Hours</Label>
            </div>
            <Switch
              id="quiet-hours"
              checked={localPreferences.quiet_hours_enabled ?? false}
              onCheckedChange={(checked) => updateLocalPreference('quiet_hours_enabled', checked)}
            />
          </div>

          {localPreferences.quiet_hours_enabled && (
            <div className="grid grid-cols-2 gap-4 pl-6">
              <div className="space-y-2">
                <Label htmlFor="quiet-start">Start Time</Label>
                <Input
                  id="quiet-start"
                  type="time"
                  value={localPreferences.quiet_hours_start || '22:00'}
                  onChange={(e) => updateLocalPreference('quiet_hours_start', e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="quiet-end">End Time</Label>
                <Input
                  id="quiet-end"
                  type="time"
                  value={localPreferences.quiet_hours_end || '08:00'}
                  onChange={(e) => updateLocalPreference('quiet_hours_end', e.target.value)}
                />
              </div>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="timezone">Timezone</Label>
            <Select
              value={localPreferences.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone}
              onValueChange={(value) => updateLocalPreference('timezone', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select timezone" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="America/New_York">Eastern Time</SelectItem>
                <SelectItem value="America/Chicago">Central Time</SelectItem>
                <SelectItem value="America/Denver">Mountain Time</SelectItem>
                <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                <SelectItem value="Europe/London">London</SelectItem>
                <SelectItem value="Europe/Paris">Paris</SelectItem>
                <SelectItem value="Asia/Tokyo">Tokyo</SelectItem>
                <SelectItem value="Asia/Shanghai">Shanghai</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Email Digest */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Mail className="h-4 w-4" />
            Email Digest
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="digest">Enable Email Digest</Label>
            <Switch
              id="digest"
              checked={localPreferences.digest_enabled ?? true}
              onCheckedChange={(checked) => updateLocalPreference('digest_enabled', checked)}
            />
          </div>

          {localPreferences.digest_enabled && (
            <>
              <div className="space-y-2">
                <Label htmlFor="digest-frequency">Frequency</Label>
                <Select
                  value={localPreferences.digest_frequency || 'daily'}
                  onValueChange={(value) => updateLocalPreference('digest_frequency', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select frequency" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="digest-time">Delivery Time</Label>
                <Input
                  id="digest-time"
                  type="time"
                  value={localPreferences.digest_time || '09:00'}
                  onChange={(e) => updateLocalPreference('digest_time', e.target.value)}
                />
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Advanced Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Advanced Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="group-similar">Group Similar Notifications</Label>
            <Switch
              id="group-similar"
              checked={localPreferences.group_similar_notifications ?? true}
              onCheckedChange={(checked) => updateLocalPreference('group_similar_notifications', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="auto-dismiss">Auto-dismiss Read Notifications</Label>
            <Switch
              id="auto-dismiss"
              checked={localPreferences.auto_dismiss_read ?? false}
              onCheckedChange={(checked) => updateLocalPreference('auto_dismiss_read', checked)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="max-notifications">Max Notifications Per Day</Label>
            <Input
              id="max-notifications"
              type="number"
              min="1"
              max="1000"
              value={localPreferences.max_notifications_per_day || ''}
              onChange={(e) => updateLocalPreference('max_notifications_per_day', parseInt(e.target.value) || undefined)}
              placeholder="No limit"
            />
          </div>
        </CardContent>
      </Card>

      {/* Save Button (Mobile) */}
      {hasChanges && (
        <div className="sticky bottom-0 bg-white border-t p-4 -mx-4">
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleReset} className="flex-1">
              Reset Changes
            </Button>
            <Button onClick={handleSave} disabled={isSaving} className="flex-1">
              {isSaving ? 'Saving...' : 'Save Preferences'}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
