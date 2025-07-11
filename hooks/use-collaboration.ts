"use client";

import { useState, useEffect, useCallback, useRef } from 'react';
import { useWebSocket } from './use-websocket';
import { useAuth } from '@/lib/auth-context';
import {
  UserPresence,
  CursorPosition,
  LiveComment,
  DocumentEdit,
  ConflictResolution,
  CollaborationMessage,
  UseCollaborationOptions,
  UseCollaborationReturn
} from '@/lib/types/collaboration';

const USER_COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
  '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
];

export function useCollaboration(options: UseCollaborationOptions = {}): UseCollaborationReturn {
  const { user } = useAuth();
  const [activeUsers, setActiveUsers] = useState<UserPresence[]>([]);
  const [currentUser, setCurrentUser] = useState<UserPresence | null>(null);
  const [cursors, setCursors] = useState<CursorPosition[]>([]);
  const [liveComments, setLiveComments] = useState<LiveComment[]>([]);
  const [documentEdits, setDocumentEdits] = useState<DocumentEdit[]>([]);
  const [conflicts, setConflicts] = useState<ConflictResolution[]>([]);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  const currentDocumentRef = useRef<string | null>(null);
  const userColorRef = useRef<string>('');
  const editQueueRef = useRef<DocumentEdit[]>([]);

  // Initialize user color
  useEffect(() => {
    if (user && !userColorRef.current) {
      const colorIndex = parseInt(user.id.slice(-2), 16) % USER_COLORS.length;
      userColorRef.current = USER_COLORS[colorIndex];
    }
  }, [user]);

  // WebSocket message handler
  const handleWebSocketMessage = useCallback((message: any) => {
    try {
      const collaborationMessage = message as CollaborationMessage;
      
      switch (collaborationMessage.type) {
        case 'user_presence':
          const presenceData = collaborationMessage.data as UserPresence;
          setActiveUsers(prev => {
            const filtered = prev.filter(u => u.user_id !== presenceData.user_id);
            return [...filtered, presenceData];
          });
          break;

        case 'cursor_position':
          const cursorData = collaborationMessage.data as CursorPosition;
          setCursors(prev => {
            const filtered = prev.filter(c => c.user_id !== cursorData.user_id);
            return [...filtered, cursorData];
          });
          break;

        case 'document_edit':
          const editData = collaborationMessage.data as DocumentEdit;
          setDocumentEdits(prev => [...prev, editData]);
          // Apply edit if it's not from current user
          if (editData.user_id !== user?.id) {
            applyRemoteEdit(editData);
          }
          break;

        case 'comment_added':
        case 'comment_updated':
          const commentData = collaborationMessage.data as LiveComment;
          setLiveComments(prev => {
            const filtered = prev.filter(c => c.id !== commentData.id);
            return [...filtered, commentData];
          });
          break;

        case 'conflict_detected':
          const conflictData = collaborationMessage.data as ConflictResolution;
          setConflicts(prev => [...prev, conflictData]);
          break;
      }
    } catch (error) {
      console.error('Error handling collaboration message:', error);
      setConnectionError('Failed to process collaboration message');
    }
  }, [user?.id]);

  // WebSocket connection
  const { isConnected, sendMessage, disconnect } = useWebSocket({
    onMessage: handleWebSocketMessage,
    onError: (error) => {
      console.error('WebSocket collaboration error:', error);
      setConnectionError('Connection error occurred');
    },
    onConnect: () => {
      setConnectionError(null);
      // Send initial presence
      if (user && currentDocumentRef.current) {
        updateUserPresence();
      }
    },
    onDisconnect: () => {
      setActiveUsers([]);
      setCursors([]);
    },
    enableHeartbeat: true,
    enableMessageQueue: true,
    enableMetrics: true
  });

  // Update user presence
  const updateUserPresence = useCallback(() => {
    if (!user || !isConnected) return;

    const presence: UserPresence = {
      user_id: user.id,
      user_name: user.full_name || user.email,
      user_email: user.email,
      status: 'online',
      current_document: currentDocumentRef.current || undefined,
      last_activity: new Date().toISOString(),
      connection_id: `${user.id}-${Date.now()}`
    };

    setCurrentUser(presence);
    
    sendMessage({
      type: 'user_presence',
      data: presence,
      document_id: currentDocumentRef.current || undefined,
      user_id: user.id,
      timestamp: new Date().toISOString(),
      message_id: `presence-${Date.now()}`
    });
  }, [user, isConnected, sendMessage]);

  // Update cursor position
  const updateCursorPosition = useCallback((position: CursorPosition['position']) => {
    if (!user || !isConnected || !currentDocumentRef.current) return;

    const cursorPosition: CursorPosition = {
      user_id: user.id,
      user_name: user.full_name || user.email,
      user_color: userColorRef.current,
      position,
      timestamp: new Date().toISOString()
    };

    sendMessage({
      type: 'cursor_position',
      data: cursorPosition,
      document_id: currentDocumentRef.current,
      user_id: user.id,
      timestamp: new Date().toISOString(),
      message_id: `cursor-${Date.now()}`
    });
  }, [user, isConnected, sendMessage]);

  // Add live comment
  const addComment = useCallback(async (comment: Omit<LiveComment, 'id' | 'created_at' | 'updated_at'>) => {
    if (!user || !isConnected) return;

    const newComment: LiveComment = {
      ...comment,
      id: `comment-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      author_id: user.id,
      author_name: user.full_name || user.email,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    // Optimistically add to local state
    setLiveComments(prev => [...prev, newComment]);

    // Send to other collaborators
    sendMessage({
      type: 'comment_added',
      data: newComment,
      document_id: comment.document_id,
      user_id: user.id,
      timestamp: new Date().toISOString(),
      message_id: `comment-add-${Date.now()}`
    });
  }, [user, isConnected, sendMessage]);

  // Update comment
  const updateComment = useCallback(async (commentId: string, updates: Partial<LiveComment>) => {
    if (!user || !isConnected) return;

    setLiveComments(prev => 
      prev.map(comment => 
        comment.id === commentId 
          ? { ...comment, ...updates, updated_at: new Date().toISOString() }
          : comment
      )
    );

    const updatedComment = liveComments.find(c => c.id === commentId);
    if (updatedComment) {
      sendMessage({
        type: 'comment_updated',
        data: { ...updatedComment, ...updates },
        document_id: updatedComment.document_id,
        user_id: user.id,
        timestamp: new Date().toISOString(),
        message_id: `comment-update-${Date.now()}`
      });
    }
  }, [user, isConnected, sendMessage, liveComments]);

  // Resolve comment
  const resolveComment = useCallback(async (commentId: string) => {
    await updateComment(commentId, {
      is_resolved: true,
      resolved_by: user?.id,
      resolved_at: new Date().toISOString()
    });
  }, [updateComment, user?.id]);

  // Add reaction to comment
  const addReaction = useCallback(async (commentId: string, emoji: string) => {
    if (!user) return;

    const comment = liveComments.find(c => c.id === commentId);
    if (!comment) return;

    const existingReactions = comment.reactions || [];
    const userReaction = existingReactions.find(r => r.user_id === user.id && r.emoji === emoji);

    let newReactions;
    if (userReaction) {
      // Remove reaction if it exists
      newReactions = existingReactions.filter(r => !(r.user_id === user.id && r.emoji === emoji));
    } else {
      // Add new reaction
      newReactions = [...existingReactions, {
        user_id: user.id,
        user_name: user.full_name || user.email,
        emoji,
        created_at: new Date().toISOString()
      }];
    }

    await updateComment(commentId, { reactions: newReactions });
  }, [user, liveComments, updateComment]);

  // Apply remote edit (placeholder for operational transformation)
  const applyRemoteEdit = useCallback((edit: DocumentEdit) => {
    // This would integrate with a rich text editor or document viewer
    // For now, we just track the edit
    console.log('Applying remote edit:', edit);
  }, []);

  // Apply document edit
  const applyEdit = useCallback(async (edit: Omit<DocumentEdit, 'id' | 'timestamp' | 'applied'>) => {
    if (!user || !isConnected) return;

    const newEdit: DocumentEdit = {
      ...edit,
      id: `edit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      user_id: user.id,
      user_name: user.full_name || user.email,
      timestamp: new Date().toISOString(),
      applied: false
    };

    // Add to edit queue for conflict detection
    editQueueRef.current.push(newEdit);
    setDocumentEdits(prev => [...prev, newEdit]);

    // Send to other collaborators
    sendMessage({
      type: 'document_edit',
      data: newEdit,
      document_id: edit.document_id,
      user_id: user.id,
      timestamp: new Date().toISOString(),
      message_id: `edit-${Date.now()}`
    });
  }, [user, isConnected, sendMessage]);

  // Resolve conflict
  const resolveConflict = useCallback(async (
    conflictId: string, 
    resolution: ConflictResolution['resolution_strategy'], 
    content?: string
  ) => {
    if (!user) return;

    const conflict = conflicts.find(c => c.conflict_id === conflictId);
    if (!conflict) return;

    const resolvedConflict: ConflictResolution = {
      ...conflict,
      resolution_strategy: resolution,
      resolved_by: user.id,
      resolved_at: new Date().toISOString(),
      final_content: content
    };

    setConflicts(prev => prev.filter(c => c.conflict_id !== conflictId));

    // Send resolution to other collaborators
    sendMessage({
      type: 'conflict_resolved',
      data: resolvedConflict,
      document_id: conflict.document_id,
      user_id: user.id,
      timestamp: new Date().toISOString(),
      message_id: `conflict-resolve-${Date.now()}`
    });
  }, [user, conflicts, sendMessage]);

  // Join document collaboration session
  const joinDocument = useCallback(async (documentId: string) => {
    currentDocumentRef.current = documentId;
    
    // Clear previous state
    setActiveUsers([]);
    setCursors([]);
    setLiveComments([]);
    setDocumentEdits([]);
    setConflicts([]);
    
    // Update presence
    updateUserPresence();
  }, [updateUserPresence]);

  // Leave document collaboration session
  const leaveDocument = useCallback(() => {
    currentDocumentRef.current = null;
    setActiveUsers([]);
    setCursors([]);
    setLiveComments([]);
    setDocumentEdits([]);
    setConflicts([]);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      leaveDocument();
      disconnect();
    };
  }, [leaveDocument, disconnect]);

  return {
    // User presence
    activeUsers,
    currentUser,
    
    // Cursor tracking
    cursors,
    updateCursorPosition,
    
    // Live comments
    liveComments,
    addComment,
    updateComment,
    resolveComment,
    addReaction,
    
    // Document editing
    documentEdits,
    applyEdit,
    
    // Conflict resolution
    conflicts,
    resolveConflict,
    
    // Session management
    joinDocument,
    leaveDocument,
    
    // Connection state
    isConnected,
    connectionError
  };
}
