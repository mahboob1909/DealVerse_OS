// Collaboration types for real-time features
export interface UserPresence {
  user_id: string;
  user_name: string;
  user_email?: string;
  avatar_url?: string;
  status: 'online' | 'away' | 'busy' | 'offline';
  current_document?: string;
  current_location?: {
    page?: number;
    section?: string;
    element_id?: string;
  };
  cursor_position?: {
    x: number;
    y: number;
    element_id?: string;
  };
  last_activity: string;
  connection_id: string;
}

export interface CursorPosition {
  user_id: string;
  user_name: string;
  user_color: string;
  position: {
    x: number;
    y: number;
    element_id?: string;
    selection?: {
      start: number;
      end: number;
      text?: string;
    };
  };
  timestamp: string;
}

export interface LiveComment {
  id: string;
  content: string;
  author_id: string;
  author_name: string;
  author_avatar?: string;
  document_id: string;
  position?: {
    x: number;
    y: number;
    page?: number;
    element_id?: string;
  };
  thread_id?: string;
  parent_comment_id?: string;
  is_resolved: boolean;
  resolved_by?: string;
  resolved_at?: string;
  created_at: string;
  updated_at: string;
  reactions?: CommentReaction[];
  mentions?: string[];
}

export interface CommentReaction {
  user_id: string;
  user_name: string;
  emoji: string;
  created_at: string;
}

export interface DocumentEdit {
  id: string;
  document_id: string;
  user_id: string;
  user_name: string;
  edit_type: 'insert' | 'delete' | 'replace' | 'format' | 'annotation';
  position: {
    start: number;
    end?: number;
    page?: number;
    element_id?: string;
  };
  content?: string;
  previous_content?: string;
  metadata?: Record<string, any>;
  timestamp: string;
  applied: boolean;
  conflict?: boolean;
}

export interface CollaborationSession {
  document_id: string;
  session_id: string;
  participants: UserPresence[];
  active_editors: string[];
  document_version: number;
  last_sync: string;
  edit_queue: DocumentEdit[];
  conflict_resolution_mode: 'auto' | 'manual' | 'last_writer_wins';
}

export interface ConflictResolution {
  conflict_id: string;
  document_id: string;
  conflicting_edits: DocumentEdit[];
  resolution_strategy: 'merge' | 'choose_version' | 'manual_resolve';
  resolved_by?: string;
  resolved_at?: string;
  final_content?: string;
}

export interface LiveNotification {
  id: string;
  type: 'comment' | 'edit' | 'mention' | 'conflict' | 'system' | 'approval';
  title: string;
  message: string;
  document_id?: string;
  document_name?: string;
  from_user_id?: string;
  from_user_name?: string;
  to_user_id: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  read: boolean;
  action_url?: string;
  action_label?: string;
  metadata?: Record<string, any>;
  created_at: string;
  expires_at?: string;
}

export interface ActivityFeedItem {
  id: string;
  type: 'document_created' | 'document_updated' | 'comment_added' | 'user_joined' | 'analysis_completed' | 'approval_requested';
  title: string;
  description: string;
  user_id: string;
  user_name: string;
  user_avatar?: string;
  document_id?: string;
  document_name?: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

// WebSocket message types for collaboration
export interface CollaborationMessage {
  type: 'user_presence' | 'cursor_position' | 'document_edit' | 'comment_added' | 'comment_updated' | 'notification' | 'conflict_detected';
  data: UserPresence | CursorPosition | DocumentEdit | LiveComment | LiveNotification | ConflictResolution;
  document_id?: string;
  user_id: string;
  timestamp: string;
  message_id: string;
}

// Hook interfaces
export interface UseCollaborationOptions {
  document_id?: string;
  enable_cursor_tracking?: boolean;
  enable_live_comments?: boolean;
  enable_conflict_resolution?: boolean;
  auto_save_interval?: number;
}

export interface UseCollaborationReturn {
  // User presence
  activeUsers: UserPresence[];
  currentUser: UserPresence | null;
  
  // Cursor tracking
  cursors: CursorPosition[];
  updateCursorPosition: (position: CursorPosition['position']) => void;
  
  // Live comments
  liveComments: LiveComment[];
  addComment: (comment: Omit<LiveComment, 'id' | 'created_at' | 'updated_at'>) => Promise<void>;
  updateComment: (commentId: string, updates: Partial<LiveComment>) => Promise<void>;
  resolveComment: (commentId: string) => Promise<void>;
  addReaction: (commentId: string, emoji: string) => Promise<void>;
  
  // Document editing
  documentEdits: DocumentEdit[];
  applyEdit: (edit: Omit<DocumentEdit, 'id' | 'timestamp' | 'applied'>) => Promise<void>;
  
  // Conflict resolution
  conflicts: ConflictResolution[];
  resolveConflict: (conflictId: string, resolution: ConflictResolution['resolution_strategy'], content?: string) => Promise<void>;
  
  // Session management
  joinDocument: (documentId: string) => Promise<void>;
  leaveDocument: () => void;
  
  // Connection state
  isConnected: boolean;
  connectionError: string | null;
}
