"use client";

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import {
  Bell,
  BellRing,
  Check,
  CheckCheck,
  X,
  Settings,
  Filter,
  Activity,
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
  Clock,
  Users,
  FileText,
  Shield,
  Workflow,
  Brain
} from "lucide-react";
import { useNotifications } from "@/hooks/use-notifications";
import { NotificationItem } from "./notification-item";
import { ActivityFeedItem } from "./activity-feed-item";
import { NotificationPreferences } from "./notification-preferences";
import { LiveNotification } from "@/lib/types/notifications";
import { formatDistanceToNow } from "date-fns";

interface NotificationCenterProps {
  userId: string;
  compact?: boolean;
  maxHeight?: string;
  showActivityFeed?: boolean;
  showPreferences?: boolean;
}

export function NotificationCenter({
  userId,
  compact = false,
  maxHeight = "600px",
  showActivityFeed = true,
  showPreferences = true
}: NotificationCenterProps) {
  const [activeTab, setActiveTab] = useState('notifications');
  const [showFilters, setShowFilters] = useState(false);

  const {
    notifications,
    unreadCount,
    totalCount,
    isLoading,
    error,
    activityFeed,
    markAsRead,
    markAllAsRead,
    dismissNotification,
    dismissAll,
    executeAction,
    filterByCategory,
    filterByPriority,
    clearFilters,
    preferences,
    updatePreferences,
    isConnected,
    connectionError
  } = useNotifications({ user_id: userId, max_notifications: 50 });

  const getCategoryIcon = (category: LiveNotification['category']) => {
    switch (category) {
      case 'document': return <FileText className="h-4 w-4" />;
      case 'collaboration': return <Users className="h-4 w-4" />;
      case 'system': return <Settings className="h-4 w-4" />;
      case 'security': return <Shield className="h-4 w-4" />;
      case 'workflow': return <Workflow className="h-4 w-4" />;
      case 'ai_analysis': return <Brain className="h-4 w-4" />;
      default: return <Bell className="h-4 w-4" />;
    }
  };

  const getPriorityColor = (priority: LiveNotification['priority']) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-blue-600 bg-blue-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getConnectionStatus = () => {
    if (connectionError) return { icon: <XCircle className="h-4 w-4" />, text: 'Connection Error', color: 'text-red-600' };
    if (!isConnected) return { icon: <AlertTriangle className="h-4 w-4" />, text: 'Disconnected', color: 'text-yellow-600' };
    return { icon: <CheckCircle className="h-4 w-4" />, text: 'Connected', color: 'text-green-600' };
  };

  const connectionStatus = getConnectionStatus();

  if (compact) {
    return (
      <Popover>
        <PopoverTrigger asChild>
          <Button variant="ghost" size="sm" className="relative">
            {unreadCount > 0 ? (
              <BellRing className="h-5 w-5" />
            ) : (
              <Bell className="h-5 w-5" />
            )}
            {unreadCount > 0 && (
              <Badge 
                variant="destructive" 
                className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs flex items-center justify-center"
              >
                {unreadCount > 99 ? '99+' : unreadCount}
              </Badge>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-96 p-0" align="end">
          <NotificationCenter
            userId={userId}
            compact={false}
            maxHeight="500px"
            showActivityFeed={false}
            showPreferences={false}
          />
        </PopoverContent>
      </Popover>
    );
  }

  return (
    <Card className="w-full" style={{ maxHeight }}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            <span>Notifications</span>
            {unreadCount > 0 && (
              <Badge variant="destructive">{unreadCount}</Badge>
            )}
          </div>
          
          <div className="flex items-center gap-1">
            {/* Connection Status */}
            <div className={`flex items-center gap-1 text-xs ${connectionStatus.color}`}>
              {connectionStatus.icon}
              <span>{connectionStatus.text}</span>
            </div>

            {/* Filter Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="h-auto p-1"
            >
              <Filter className="h-4 w-4" />
            </Button>

            {/* Mark All Read */}
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={markAllAsRead}
                className="h-auto p-1"
              >
                <CheckCheck className="h-4 w-4" />
              </Button>
            )}

            {/* Clear All */}
            {totalCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={dismissAll}
                className="h-auto p-1"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardTitle>

        {/* Filters */}
        {showFilters && (
          <div className="space-y-2 pt-2 border-t">
            <div className="text-sm font-medium">Filter by Category:</div>
            <div className="flex flex-wrap gap-1">
              {(['document', 'collaboration', 'system', 'security', 'workflow', 'ai_analysis'] as const).map(category => (
                <Button
                  key={category}
                  variant="outline"
                  size="sm"
                  onClick={() => filterByCategory(category)}
                  className="h-auto px-2 py-1 text-xs"
                >
                  {getCategoryIcon(category)}
                  <span className="ml-1 capitalize">{category.replace('_', ' ')}</span>
                </Button>
              ))}
            </div>
            
            <div className="text-sm font-medium">Filter by Priority:</div>
            <div className="flex flex-wrap gap-1">
              {(['urgent', 'high', 'medium', 'low'] as const).map(priority => (
                <Button
                  key={priority}
                  variant="outline"
                  size="sm"
                  onClick={() => filterByPriority(priority)}
                  className={`h-auto px-2 py-1 text-xs ${getPriorityColor(priority)}`}
                >
                  <span className="capitalize">{priority}</span>
                </Button>
              ))}
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              className="h-auto px-2 py-1 text-xs"
            >
              Clear Filters
            </Button>
          </div>
        )}
      </CardHeader>

      <CardContent className="p-0">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="notifications" className="relative">
              Notifications
              {unreadCount > 0 && (
                <Badge variant="destructive" className="ml-1 h-4 w-4 p-0 text-xs">
                  {unreadCount}
                </Badge>
              )}
            </TabsTrigger>
            {showActivityFeed && (
              <TabsTrigger value="activity">
                <Activity className="h-4 w-4 mr-1" />
                Activity
              </TabsTrigger>
            )}
            {showPreferences && (
              <TabsTrigger value="preferences">
                <Settings className="h-4 w-4 mr-1" />
                Settings
              </TabsTrigger>
            )}
          </TabsList>

          <TabsContent value="notifications" className="mt-0">
            <ScrollArea className="h-96">
              {isLoading ? (
                <div className="p-4 text-center text-sm text-muted-foreground">
                  Loading notifications...
                </div>
              ) : error ? (
                <div className="p-4 text-center text-sm text-red-600">
                  {error}
                </div>
              ) : notifications.length === 0 ? (
                <div className="p-8 text-center">
                  <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No notifications</h3>
                  <p className="text-gray-600">You're all caught up!</p>
                </div>
              ) : (
                <div className="divide-y">
                  {notifications.map((notification, index) => (
                    <NotificationItem
                      key={notification.id}
                      notification={notification}
                      onMarkAsRead={markAsRead}
                      onDismiss={dismissNotification}
                      onExecuteAction={executeAction}
                      isLast={index === notifications.length - 1}
                    />
                  ))}
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          {showActivityFeed && (
            <TabsContent value="activity" className="mt-0">
              <ScrollArea className="h-96">
                {activityFeed.length === 0 ? (
                  <div className="p-8 text-center">
                    <Activity className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No recent activity</h3>
                    <p className="text-gray-600">Activity will appear here as you work.</p>
                  </div>
                ) : (
                  <div className="divide-y">
                    {activityFeed.map((item, index) => (
                      <ActivityFeedItem
                        key={item.id}
                        item={item}
                        isLast={index === activityFeed.length - 1}
                      />
                    ))}
                  </div>
                )}
              </ScrollArea>
            </TabsContent>
          )}

          {showPreferences && (
            <TabsContent value="preferences" className="mt-0">
              <ScrollArea className="h-96">
                <div className="p-4">
                  <NotificationPreferences
                    preferences={preferences}
                    onUpdatePreferences={updatePreferences}
                  />
                </div>
              </ScrollArea>
            </TabsContent>
          )}
        </Tabs>
      </CardContent>
    </Card>
  );
}
