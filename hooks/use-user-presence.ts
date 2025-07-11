"use client";

import { useState, useEffect, useRef, useCallback } from 'react';
import { useWebSocket } from './use-websocket';
import { useAuth } from '@/lib/auth-context';

interface UserPresence {
  user_id: string;
  user_name: string;
  avatar_url?: string;
  status: 'online' | 'away' | 'busy' | 'offline';
  current_module?: string;
  current_page?: string;
  last_activity: string;
  cursor_position?: {
    x: number;
    y: number;
    element?: string;
  };
}

interface UseUserPresenceOptions {
  module?: string;
  page?: string;
  trackCursor?: boolean;
  trackActivity?: boolean;
  presenceTimeout?: number; // milliseconds
  onUserJoined?: (user: UserPresence) => void;
  onUserLeft?: (user: UserPresence) => void;
  onUserUpdated?: (user: UserPresence) => void;
}

interface UseUserPresenceReturn {
  activeUsers: UserPresence[];
  currentUser: UserPresence | null;
  isConnected: boolean;
  updatePresence: (updates: Partial<UserPresence>) => void;
  updateCursorPosition: (x: number, y: number, element?: string) => void;
  setStatus: (status: UserPresence['status']) => void;
  getUsersInModule: (module: string) => UserPresence[];
  getUsersOnPage: (page: string) => UserPresence[];
  isUserActive: (userId: string) => boolean;
}

export function useUserPresence(
  options: UseUserPresenceOptions = {}
): UseUserPresenceReturn {
  const { user } = useAuth();
  const [activeUsers, setActiveUsers] = useState<UserPresence[]>([]);
  const [currentUser, setCurrentUser] = useState<UserPresence | null>(null);
  const currentUserRef = useRef<UserPresence | null>(null);
  const activityTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const cursorTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const {
    module = 'dashboard',
    page = 'overview',
    trackCursor = true,
    trackActivity = true,
    presenceTimeout = 300000, // 5 minutes
    onUserJoined,
    onUserLeft,
    onUserUpdated
  } = options;

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((message: any) => {
    try {
      switch (message.type) {
        case 'user_presence_update':
          const updatedUser: UserPresence = {
            user_id: message.user_id,
            user_name: message.user_name,
            avatar_url: message.avatar_url,
            status: message.status,
            current_module: message.current_module,
            current_page: message.current_page,
            last_activity: message.last_activity,
            cursor_position: message.cursor_position
          };

          setActiveUsers(prev => {
            const filtered = prev.filter(u => u.user_id !== updatedUser.user_id);
            const updated = [...filtered, updatedUser];
            
            // Check if this is a new user
            const existingUser = prev.find(u => u.user_id === updatedUser.user_id);
            if (!existingUser) {
              onUserJoined?.(updatedUser);
            } else {
              onUserUpdated?.(updatedUser);
            }
            
            return updated;
          });
          break;

        case 'user_presence_left':
          const leftUser: UserPresence = {
            user_id: message.user_id,
            user_name: message.user_name,
            avatar_url: message.avatar_url,
            status: 'offline',
            current_module: message.current_module,
            current_page: message.current_page,
            last_activity: message.last_activity
          };

          setActiveUsers(prev => {
            const updated = prev.filter(u => u.user_id !== message.user_id);
            onUserLeft?.(leftUser);
            return updated;
          });
          break;

        case 'cursor_position':
          setActiveUsers(prev => prev.map(user => 
            user.user_id === message.user_id 
              ? { 
                  ...user, 
                  cursor_position: message.position,
                  last_activity: message.timestamp 
                }
              : user
          ));
          break;

        default:
          // Handle other message types
          break;
      }
    } catch (error) {
      console.error('Error handling presence message:', error);
    }
  }, [onUserJoined, onUserLeft, onUserUpdated]);

  // WebSocket connection
  const { isConnected, sendMessage } = useWebSocket({
    onMessage: handleWebSocketMessage,
    onError: (error) => {
      console.error('WebSocket presence error:', error);
    },
    onConnect: () => {
      // Send initial presence when connected
      if (user) {
        updatePresence({
          status: 'online',
          current_module: module,
          current_page: page
        });
      }
    },
    onDisconnect: () => {
      setActiveUsers([]);
      setCurrentUser(null);
    },
    enableHeartbeat: true,
    enableMessageQueue: true
  });

  // Update presence information
  const updatePresence = useCallback((updates: Partial<UserPresence>) => {
    if (!isConnected || !user) return;

    const presenceUpdate = {
      user_id: user.id,
      user_name: `${user.first_name} ${user.last_name}`,
      avatar_url: user.avatar_url,
      status: 'online',
      current_module: module,
      current_page: page,
      last_activity: new Date().toISOString(),
      ...updates
    };

    // Update current user state
    setCurrentUser(presenceUpdate as UserPresence);
    currentUserRef.current = presenceUpdate as UserPresence;

    // Send presence update
    sendMessage({
      type: 'user_presence_update',
      ...presenceUpdate,
      timestamp: new Date().toISOString()
    });
  }, [isConnected, user, module, page, sendMessage]);

  // Update cursor position
  const updateCursorPosition = useCallback((x: number, y: number, element?: string) => {
    if (!isConnected || !user || !trackCursor) return;

    // Throttle cursor updates
    if (cursorTimeoutRef.current) {
      clearTimeout(cursorTimeoutRef.current);
    }

    cursorTimeoutRef.current = setTimeout(() => {
      sendMessage({
        type: 'cursor_position',
        user_id: user.id,
        position: { x, y, element },
        current_module: module,
        current_page: page,
        timestamp: new Date().toISOString()
      });
    }, 100); // Throttle to 10 updates per second
  }, [isConnected, user, trackCursor, module, page, sendMessage]);

  // Set user status
  const setStatus = useCallback((status: UserPresence['status']) => {
    updatePresence({ status });
  }, [updatePresence]);

  // Get users in specific module
  const getUsersInModule = useCallback((targetModule: string) => {
    return activeUsers.filter(user => user.current_module === targetModule);
  }, [activeUsers]);

  // Get users on specific page
  const getUsersOnPage = useCallback((targetPage: string) => {
    return activeUsers.filter(user => user.current_page === targetPage);
  }, [activeUsers]);

  // Check if user is active (last activity within timeout)
  const isUserActive = useCallback((userId: string) => {
    const user = activeUsers.find(u => u.user_id === userId);
    if (!user) return false;
    
    const lastActivity = new Date(user.last_activity);
    const now = new Date();
    const diffMs = now.getTime() - lastActivity.getTime();
    
    return diffMs < presenceTimeout;
  }, [activeUsers, presenceTimeout]);

  // Track mouse movement for cursor position
  useEffect(() => {
    if (!trackCursor || !isConnected) return;

    const handleMouseMove = (event: MouseEvent) => {
      updateCursorPosition(event.clientX, event.clientY);
    };

    document.addEventListener('mousemove', handleMouseMove);
    return () => document.removeEventListener('mousemove', handleMouseMove);
  }, [trackCursor, isConnected, updateCursorPosition]);

  // Track user activity
  useEffect(() => {
    if (!trackActivity || !isConnected) return;

    const handleActivity = () => {
      if (activityTimeoutRef.current) {
        clearTimeout(activityTimeoutRef.current);
      }

      // Update presence on activity
      updatePresence({ last_activity: new Date().toISOString() });

      // Set away status after inactivity
      activityTimeoutRef.current = setTimeout(() => {
        updatePresence({ status: 'away' });
      }, presenceTimeout);
    };

    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => document.addEventListener(event, handleActivity));

    // Initial activity
    handleActivity();

    return () => {
      events.forEach(event => document.removeEventListener(event, handleActivity));
      if (activityTimeoutRef.current) {
        clearTimeout(activityTimeoutRef.current);
      }
    };
  }, [trackActivity, isConnected, updatePresence, presenceTimeout]);

  // Update presence when module/page changes
  useEffect(() => {
    if (isConnected && user) {
      updatePresence({
        current_module: module,
        current_page: page
      });
    }
  }, [module, page, isConnected, user, updatePresence]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (cursorTimeoutRef.current) {
        clearTimeout(cursorTimeoutRef.current);
      }
      if (activityTimeoutRef.current) {
        clearTimeout(activityTimeoutRef.current);
      }
      
      // Send offline status
      if (isConnected && user) {
        sendMessage({
          type: 'user_presence_update',
          user_id: user.id,
          status: 'offline',
          timestamp: new Date().toISOString()
        });
      }
    };
  }, [isConnected, user, sendMessage]);

  return {
    activeUsers,
    currentUser,
    isConnected,
    updatePresence,
    updateCursorPosition,
    setStatus,
    getUsersInModule,
    getUsersOnPage,
    isUserActive
  };
}
