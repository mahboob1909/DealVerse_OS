// Live Notifications System Types

export interface LiveNotification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error' | 'collaboration' | 'system';
  title: string;
  message: string;
  user_id: string;
  document_id?: string;
  project_id?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: 'document' | 'collaboration' | 'system' | 'security' | 'workflow' | 'ai_analysis';
  
  // Metadata
  created_at: string;
  read_at?: string;
  dismissed_at?: string;
  expires_at?: string;
  
  // Actions
  action_url?: string;
  action_label?: string;
  actions?: NotificationAction[];
  
  // Rich content
  avatar_url?: string;
  thumbnail_url?: string;
  metadata?: Record<string, any>;
  
  // Delivery settings
  channels: NotificationChannel[];
  delivery_status: NotificationDeliveryStatus;
  
  // Grouping
  group_key?: string;
  thread_id?: string;
}

export interface NotificationAction {
  id: string;
  label: string;
  action_type: 'navigate' | 'api_call' | 'dismiss' | 'mark_read' | 'custom';
  action_data: Record<string, any>;
  style?: 'primary' | 'secondary' | 'destructive';
  icon?: string;
}

export interface NotificationChannel {
  type: 'in_app' | 'email' | 'push' | 'sms' | 'webhook';
  enabled: boolean;
  delivered_at?: string;
  delivery_error?: string;
}

export interface NotificationDeliveryStatus {
  in_app: 'pending' | 'delivered' | 'read' | 'dismissed' | 'failed';
  email?: 'pending' | 'sent' | 'delivered' | 'bounced' | 'failed';
  push?: 'pending' | 'sent' | 'delivered' | 'failed';
  sms?: 'pending' | 'sent' | 'delivered' | 'failed';
}

export interface NotificationPreferences {
  user_id: string;
  
  // Channel preferences
  email_enabled: boolean;
  push_enabled: boolean;
  sms_enabled: boolean;
  in_app_enabled: boolean;
  
  // Category preferences
  document_notifications: boolean;
  collaboration_notifications: boolean;
  system_notifications: boolean;
  security_notifications: boolean;
  workflow_notifications: boolean;
  ai_analysis_notifications: boolean;
  
  // Timing preferences
  quiet_hours_enabled: boolean;
  quiet_hours_start?: string; // HH:MM format
  quiet_hours_end?: string;   // HH:MM format
  timezone: string;
  
  // Frequency preferences
  digest_enabled: boolean;
  digest_frequency: 'daily' | 'weekly' | 'monthly';
  digest_time?: string; // HH:MM format
  
  // Priority filtering
  minimum_priority: 'low' | 'medium' | 'high' | 'urgent';
  
  // Advanced settings
  group_similar_notifications: boolean;
  auto_dismiss_read: boolean;
  max_notifications_per_day?: number;
  
  updated_at: string;
}

export interface ActivityFeedItem {
  id: string;
  type: 'document_created' | 'document_updated' | 'comment_added' | 'user_joined' | 
        'analysis_completed' | 'workflow_updated' | 'collaboration_started' | 'system_event';
  
  // Core data
  title: string;
  description: string;
  user_id: string;
  user_name: string;
  user_avatar?: string;
  
  // Context
  document_id?: string;
  document_name?: string;
  project_id?: string;
  project_name?: string;
  
  // Metadata
  created_at: string;
  metadata?: Record<string, any>;
  
  // Visual
  icon?: string;
  color?: string;
  thumbnail_url?: string;
  
  // Actions
  action_url?: string;
  action_label?: string;
}

export interface NotificationTemplate {
  id: string;
  name: string;
  type: LiveNotification['type'];
  category: LiveNotification['category'];
  
  // Template content
  title_template: string;
  message_template: string;
  
  // Default settings
  default_priority: LiveNotification['priority'];
  default_channels: NotificationChannel['type'][];
  default_actions?: Omit<NotificationAction, 'id'>[];
  
  // Conditions
  conditions?: NotificationCondition[];
  
  // Metadata
  created_at: string;
  updated_at: string;
  created_by: string;
  is_active: boolean;
}

export interface NotificationCondition {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than';
  value: any;
  logic?: 'and' | 'or';
}

export interface NotificationRule {
  id: string;
  name: string;
  description: string;
  
  // Trigger conditions
  event_type: string;
  conditions: NotificationCondition[];
  
  // Template to use
  template_id: string;
  
  // Override settings
  priority_override?: LiveNotification['priority'];
  channel_overrides?: NotificationChannel['type'][];
  
  // Targeting
  target_users?: string[];
  target_roles?: string[];
  target_conditions?: NotificationCondition[];
  
  // Rate limiting
  rate_limit?: {
    max_per_hour?: number;
    max_per_day?: number;
    cooldown_minutes?: number;
  };
  
  // Metadata
  created_at: string;
  updated_at: string;
  created_by: string;
  is_active: boolean;
}

export interface NotificationDigest {
  id: string;
  user_id: string;
  period_start: string;
  period_end: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  
  // Content
  total_notifications: number;
  unread_notifications: number;
  notifications_by_category: Record<string, number>;
  top_notifications: LiveNotification[];
  activity_summary: ActivityFeedItem[];
  
  // Delivery
  generated_at: string;
  sent_at?: string;
  delivery_status: 'pending' | 'sent' | 'delivered' | 'failed';
  delivery_error?: string;
}

export interface UseNotificationsOptions {
  user_id?: string;
  auto_mark_read?: boolean;
  real_time_updates?: boolean;
  max_notifications?: number;
  categories?: LiveNotification['category'][];
  priorities?: LiveNotification['priority'][];
}

export interface UseNotificationsReturn {
  // Notifications state
  notifications: LiveNotification[];
  unreadCount: number;
  totalCount: number;
  isLoading: boolean;
  error: string | null;
  
  // Activity feed
  activityFeed: ActivityFeedItem[];
  
  // Actions
  markAsRead: (notificationId: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  dismissNotification: (notificationId: string) => Promise<void>;
  dismissAll: () => Promise<void>;
  executeAction: (notificationId: string, actionId: string) => Promise<void>;
  
  // Filtering
  filterByCategory: (category: LiveNotification['category']) => void;
  filterByPriority: (priority: LiveNotification['priority']) => void;
  clearFilters: () => void;
  
  // Preferences
  preferences: NotificationPreferences | null;
  updatePreferences: (updates: Partial<NotificationPreferences>) => Promise<void>;
  
  // Real-time
  isConnected: boolean;
}

export interface NotificationContextType {
  // Global notification state
  notifications: LiveNotification[];
  unreadCount: number;
  
  // Global actions
  addNotification: (notification: Omit<LiveNotification, 'id' | 'created_at'>) => void;
  removeNotification: (notificationId: string) => void;
  clearAllNotifications: () => void;
  
  // Toast notifications
  showToast: (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;
  
  // Preferences
  preferences: NotificationPreferences | null;
  updatePreferences: (updates: Partial<NotificationPreferences>) => Promise<void>;
}
