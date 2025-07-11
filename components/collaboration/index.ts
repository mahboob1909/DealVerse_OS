// Collaboration Components Export Index
export { UserPresenceIndicator } from './user-presence';
export { LiveCursors, CollaborativeCursors, useCursorTracking } from './live-cursors';
export { LiveComments } from './live-comments';
export { ConflictResolution } from './conflict-resolution';
export { CollaborativeEditor } from './collaborative-editor';

// Re-export collaboration types for convenience
export type {
  UserPresence,
  CursorPosition,
  LiveComment,
  DocumentEdit,
  ConflictResolution as ConflictType,
  CollaborationMessage,
  UseCollaborationOptions,
  UseCollaborationReturn
} from '@/lib/types/collaboration';

// Re-export collaboration hook
export { useCollaboration } from '@/hooks/use-collaboration';
