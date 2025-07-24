"use client";

import { useState, useEffect, useCallback, useRef } from 'react';
import { useWebSocket } from './use-websocket';
import { useAuth } from '@/lib/auth-context';
import {
  LiveNotification,
  ActivityFeedItem,
  NotificationPreferences,
  UseNotificationsOptions,
  UseNotificationsReturn
} from '@/lib/types/notifications';

const DEFAULT_PREFERENCES: Partial<NotificationPreferences> = {
  email_enabled: true,
  push_enabled: true,
  sms_enabled: false,
  in_app_enabled: true,
  document_notifications: true,
  collaboration_notifications: true,
  system_notifications: true,
  security_notifications: true,
  workflow_notifications: true,
  ai_analysis_notifications: true,
  quiet_hours_enabled: false,
  digest_enabled: true,
  digest_frequency: 'daily',
  minimum_priority: 'low',
  group_similar_notifications: true,
  auto_dismiss_read: false,
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
};

export function useNotifications(options: UseNotificationsOptions = {}): UseNotificationsReturn {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<LiveNotification[]>([]);
  const [activityFeed, setActivityFeed] = useState<ActivityFeedItem[]>([]);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<{
    categories?: LiveNotification['category'][];
    priorities?: LiveNotification['priority'][];
  }>({});

  const notificationTimeoutRefs = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // WebSocket message handler for real-time notifications
  const handleWebSocketMessage = useCallback((message: any) => {
    try {
      switch (message.type) {
        case 'notification':
          const notification = message.data as LiveNotification;
          setNotifications(prev => {
            // Avoid duplicates
            const filtered = prev.filter(n => n.id !== notification.id);
            return [notification, ...filtered].slice(0, options.max_notifications || 100);
          });
          
          // Auto-dismiss if configured
          if (notification.expires_at) {
            const expiresIn = new Date(notification.expires_at).getTime() - Date.now();
            if (expiresIn > 0) {
              const timeout = setTimeout(() => {
                dismissNotification(notification.id);
              }, expiresIn);
              notificationTimeoutRefs.current.set(notification.id, timeout);
            }
          }
          break;

        case 'activity_feed_item':
          const activityItem = message.data as ActivityFeedItem;
          setActivityFeed(prev => {
            const filtered = prev.filter(item => item.id !== activityItem.id);
            return [activityItem, ...filtered].slice(0, 50); // Keep last 50 items
          });
          break;

        case 'notification_read':
          const { notification_id } = message.data;
          setNotifications(prev => 
            prev.map(n => 
              n.id === notification_id 
                ? { ...n, read_at: new Date().toISOString() }
                : n
            )
          );
          break;

        case 'notification_dismissed':
          const { notification_id: dismissedId } = message.data;
          setNotifications(prev => prev.filter(n => n.id !== dismissedId));
          break;

        case 'preferences_updated':
          const updatedPreferences = message.data as NotificationPreferences;
          setPreferences(updatedPreferences);
          break;
      }
    } catch (error) {
      console.error('Error handling notification message:', error);
      setError('Failed to process notification');
    }
  }, [options.max_notifications]);

  // WebSocket connection for real-time updates
  const { isConnected, sendMessage } = useWebSocket({
    onMessage: handleWebSocketMessage,
    onError: (error) => {
      console.error('WebSocket notification error:', error);
      setError('Connection error occurred');
    },
    onConnect: () => {
      setError(null);
      // Subscribe to user's notifications
      if (user) {
        sendMessage({
          type: 'subscribe_notifications',
          user_id: user.id,
          categories: options.categories,
          priorities: options.priorities
        });
      }
    },
    enableHeartbeat: true,
    enableMessageQueue: true
  });

  // Load initial notifications and preferences
  useEffect(() => {
    if (!user) return;

    const loadNotifications = async () => {
      setIsLoading(true);
      try {
        // Load notifications
        const notificationsResponse = await fetch(`/api/notifications?user_id=${user.id}&limit=${options.max_notifications || 50}`);
        if (notificationsResponse.ok) {
          const notificationsData = await notificationsResponse.json();
          setNotifications(notificationsData.notifications || []);
        }

        // Load activity feed
        const activityResponse = await fetch(`/api/notifications/activity-feed?user_id=${user.id}&limit=50`);
        if (activityResponse.ok) {
          const activityData = await activityResponse.json();
          setActivityFeed(activityData.activity_feed || []);
        }

        // Load preferences
        const preferencesResponse = await fetch(`/api/notifications/preferences?user_id=${user.id}`);
        if (preferencesResponse.ok) {
          const preferencesData = await preferencesResponse.json();
          setPreferences({ ...DEFAULT_PREFERENCES, ...preferencesData.preferences } as NotificationPreferences);
        } else {
          // Create default preferences
          setPreferences({ ...DEFAULT_PREFERENCES, user_id: user.id } as NotificationPreferences);
        }
      } catch (error) {
        console.error('Failed to load notifications:', error);
        setError('Failed to load notifications');
      } finally {
        setIsLoading(false);
      }
    };

    loadNotifications();
  }, [user, options.max_notifications]);

  // Mark notification as read
  const markAsRead = useCallback(async (notificationId: string) => {
    if (!user) return;

    try {
      const response = await fetch(`/api/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id })
      });

      if (response.ok) {
        setNotifications(prev => 
          prev.map(n => 
            n.id === notificationId 
              ? { ...n, read_at: new Date().toISOString() }
              : n
          )
        );

        // Send real-time update
        sendMessage({
          type: 'notification_read',
          notification_id: notificationId,
          user_id: user.id
        });
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  }, [user, sendMessage]);

  // Mark all notifications as read
  const markAllAsRead = useCallback(async () => {
    if (!user) return;

    try {
      const response = await fetch('/api/notifications/read-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id })
      });

      if (response.ok) {
        const now = new Date().toISOString();
        setNotifications(prev => 
          prev.map(n => ({ ...n, read_at: n.read_at || now }))
        );
      }
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  }, [user]);

  // Dismiss notification
  const dismissNotification = useCallback(async (notificationId: string) => {
    if (!user) return;

    try {
      const response = await fetch(`/api/notifications/${notificationId}/dismiss`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id })
      });

      if (response.ok) {
        setNotifications(prev => prev.filter(n => n.id !== notificationId));
        
        // Clear timeout if exists
        const timeout = notificationTimeoutRefs.current.get(notificationId);
        if (timeout) {
          clearTimeout(timeout);
          notificationTimeoutRefs.current.delete(notificationId);
        }

        // Send real-time update
        sendMessage({
          type: 'notification_dismissed',
          notification_id: notificationId,
          user_id: user.id
        });
      }
    } catch (error) {
      console.error('Failed to dismiss notification:', error);
    }
  }, [user, sendMessage]);

  // Dismiss all notifications
  const dismissAll = useCallback(async () => {
    if (!user) return;

    try {
      const response = await fetch('/api/notifications/dismiss-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id })
      });

      if (response.ok) {
        setNotifications([]);
        
        // Clear all timeouts
        notificationTimeoutRefs.current.forEach(timeout => clearTimeout(timeout));
        notificationTimeoutRefs.current.clear();
      }
    } catch (error) {
      console.error('Failed to dismiss all notifications:', error);
    }
  }, [user]);

  // Execute notification action
  const executeAction = useCallback(async (notificationId: string, actionId: string) => {
    if (!user) return;

    try {
      const response = await fetch(`/api/notifications/${notificationId}/actions/${actionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Handle different action types
        if (result.action_type === 'navigate' && result.url) {
          window.location.href = result.url;
        } else if (result.action_type === 'dismiss') {
          await dismissNotification(notificationId);
        } else if (result.action_type === 'mark_read') {
          await markAsRead(notificationId);
        }
      }
    } catch (error) {
      console.error('Failed to execute notification action:', error);
    }
  }, [user, dismissNotification, markAsRead]);

  // Filter notifications
  const filterByCategory = useCallback((category: LiveNotification['category']) => {
    setFilters(prev => ({
      ...prev,
      categories: prev.categories?.includes(category) 
        ? prev.categories.filter(c => c !== category)
        : [...(prev.categories || []), category]
    }));
  }, []);

  const filterByPriority = useCallback((priority: LiveNotification['priority']) => {
    setFilters(prev => ({
      ...prev,
      priorities: prev.priorities?.includes(priority)
        ? prev.priorities.filter(p => p !== priority)
        : [...(prev.priorities || []), priority]
    }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  // Update preferences
  const updatePreferences = useCallback(async (updates: Partial<NotificationPreferences>) => {
    if (!user || !preferences) return;

    try {
      const updatedPreferences = { ...preferences, ...updates, updated_at: new Date().toISOString() };
      
      const response = await fetch('/api/notifications/preferences', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedPreferences)
      });

      if (response.ok) {
        setPreferences(updatedPreferences);
        
        // Send real-time update
        sendMessage({
          type: 'preferences_updated',
          data: updatedPreferences,
          user_id: user.id
        });
      }
    } catch (error) {
      console.error('Failed to update preferences:', error);
    }
  }, [user, preferences, sendMessage]);

  // Apply filters to notifications
  const filteredNotifications = notifications.filter(notification => {
    if (filters.categories && !filters.categories.includes(notification.category)) {
      return false;
    }
    if (filters.priorities && !filters.priorities.includes(notification.priority)) {
      return false;
    }
    return true;
  });

  // Calculate unread count
  const unreadCount = filteredNotifications.filter(n => !n.read_at).length;

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      notificationTimeoutRefs.current.forEach(timeout => clearTimeout(timeout));
      notificationTimeoutRefs.current.clear();
    };
  }, []);

  return {
    // State
    notifications: filteredNotifications,
    unreadCount,
    totalCount: filteredNotifications.length,
    isLoading,
    error,
    activityFeed,

    // Actions
    markAsRead,
    markAllAsRead,
    dismissNotification,
    dismissAll,
    executeAction,

    // Filtering
    filterByCategory,
    filterByPriority,
    clearFilters,

    // Preferences
    preferences,
    updatePreferences,

    // Connection
    isConnected
  };
}
