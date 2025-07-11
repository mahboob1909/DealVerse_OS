// Notifications Components Export Index

// Main Components
export { NotificationCenter } from './notification-center';
export { NotificationItem } from './notification-item';
export { ActivityFeedItem } from './activity-feed-item';
export { NotificationPreferences } from './notification-preferences';
export { ToastNotification, ToastContainer } from './toast-notification';

// Context and Providers
export { 
  NotificationProvider, 
  useNotificationContext, 
  useToast, 
  useNotificationActions 
} from './notification-provider';

// Re-export notification types for convenience
export type {
  LiveNotification,
  ActivityFeedItem as ActivityItem,
  NotificationPreferences as PreferencesType,
  NotificationAction,
  NotificationChannel,
  NotificationDeliveryStatus,
  NotificationTemplate,
  NotificationRule,
  NotificationDigest,
  UseNotificationsOptions,
  UseNotificationsReturn,
  NotificationContextType
} from '@/lib/types/notifications';

// Re-export notification hook
export { useNotifications } from '@/hooks/use-notifications';
