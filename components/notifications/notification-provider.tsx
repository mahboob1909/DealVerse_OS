"use client";

import { createContext, useContext, useCallback, useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useNotifications } from '@/hooks/use-notifications';
import { ToastContainer } from './toast-notification';
import {
  LiveNotification,
  NotificationPreferences,
  NotificationContextType
} from '@/lib/types/notifications';

const NotificationContext = createContext<NotificationContextType | null>(null);

interface NotificationProviderProps {
  children: React.ReactNode;
  enableToasts?: boolean;
  toastPosition?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  toastDuration?: number;
  maxToasts?: number;
}

export function NotificationProvider({
  children,
  enableToasts = true,
  toastPosition = 'top-right',
  toastDuration = 5000,
  maxToasts = 5
}: NotificationProviderProps) {
  const { user } = useAuth();
  const [toastNotifications, setToastNotifications] = useState<LiveNotification[]>([]);

  const {
    notifications,
    unreadCount,
    dismissNotification,
    preferences,
    updatePreferences,
    executeAction
  } = useNotifications({
    user_id: user?.id,
    real_time_updates: true,
    max_notifications: 100
  });

  // Add new notification (for programmatic use)
  const addNotification = useCallback((notification: Omit<LiveNotification, 'id' | 'created_at'>) => {
    const newNotification: LiveNotification = {
      ...notification,
      id: `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      created_at: new Date().toISOString(),
      delivery_status: {
        in_app: 'delivered'
      }
    };

    // Add to toast notifications if enabled
    if (enableToasts) {
      setToastNotifications(prev => [newNotification, ...prev.slice(0, maxToasts - 1)]);
    }
  }, [enableToasts, maxToasts]);

  // Remove notification
  const removeNotification = useCallback((notificationId: string) => {
    setToastNotifications(prev => prev.filter(n => n.id !== notificationId));
    dismissNotification(notificationId);
  }, [dismissNotification]);

  // Clear all notifications
  const clearAllNotifications = useCallback(() => {
    setToastNotifications([]);
  }, []);

  // Show toast notification
  const showToast = useCallback((
    message: string, 
    type: 'info' | 'success' | 'warning' | 'error' = 'info'
  ) => {
    if (!enableToasts) return;

    const notification: Omit<LiveNotification, 'id' | 'created_at'> = {
      type,
      title: type.charAt(0).toUpperCase() + type.slice(1),
      message,
      user_id: user?.id || 'anonymous',
      priority: type === 'error' ? 'high' : type === 'warning' ? 'medium' : 'low',
      category: 'system',
      channels: [{ type: 'in_app', enabled: true }],
      delivery_status: { in_app: 'delivered' }
    };

    addNotification(notification);
  }, [enableToasts, user?.id, addNotification]);

  // Update toast notifications when main notifications change
  useEffect(() => {
    if (!enableToasts) return;

    // Add new unread notifications to toast list
    const newToasts = notifications
      .filter(n => !n.read_at && !n.dismissed_at)
      .filter(n => !toastNotifications.some(t => t.id === n.id))
      .slice(0, maxToasts);

    if (newToasts.length > 0) {
      setToastNotifications(prev => [...newToasts, ...prev].slice(0, maxToasts));
    }
  }, [notifications, enableToasts, maxToasts, toastNotifications]);

  // Handle toast dismissal
  const handleToastDismiss = useCallback((notificationId: string) => {
    setToastNotifications(prev => prev.filter(n => n.id !== notificationId));
    
    // Also dismiss from main notifications if it exists there
    const mainNotification = notifications.find(n => n.id === notificationId);
    if (mainNotification) {
      dismissNotification(notificationId);
    }
  }, [notifications, dismissNotification]);

  // Handle toast action execution
  const handleToastAction = useCallback(async (notificationId: string, actionId: string) => {
    try {
      await executeAction(notificationId, actionId);
      
      // Remove from toast after action execution
      setToastNotifications(prev => prev.filter(n => n.id !== notificationId));
    } catch (error) {
      console.error('Failed to execute toast action:', error);
      showToast('Failed to execute action', 'error');
    }
  }, [executeAction, showToast]);

  const contextValue: NotificationContextType = {
    // Global state
    notifications,
    unreadCount,
    
    // Global actions
    addNotification,
    removeNotification,
    clearAllNotifications,
    
    // Toast notifications
    showToast,
    
    // Preferences
    preferences,
    updatePreferences
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
      
      {/* Toast Container */}
      {enableToasts && (
        <ToastContainer
          notifications={toastNotifications}
          onDismiss={handleToastDismiss}
          onAction={handleToastAction}
          position={toastPosition}
          duration={toastDuration}
          maxToasts={maxToasts}
        />
      )}
    </NotificationContext.Provider>
  );
}

export function useNotificationContext(): NotificationContextType {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotificationContext must be used within a NotificationProvider');
  }
  return context;
}

// Convenience hooks for common operations
export function useToast() {
  const { showToast } = useNotificationContext();
  
  return {
    toast: showToast,
    success: (message: string) => showToast(message, 'success'),
    error: (message: string) => showToast(message, 'error'),
    warning: (message: string) => showToast(message, 'warning'),
    info: (message: string) => showToast(message, 'info')
  };
}

export function useNotificationActions() {
  const { 
    addNotification, 
    removeNotification, 
    clearAllNotifications,
    notifications,
    unreadCount
  } = useNotificationContext();
  
  return {
    addNotification,
    removeNotification,
    clearAllNotifications,
    notifications,
    unreadCount
  };
}
