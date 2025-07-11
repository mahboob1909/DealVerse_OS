"use client";

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Users, Activity, Clock, Wifi, WifiOff } from 'lucide-react';

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

interface UserPresenceIndicatorProps {
  users: UserPresence[];
  currentModule?: string;
  currentPage?: string;
  isConnected: boolean;
  maxVisible?: number;
  showStatus?: boolean;
  showModule?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const statusColors = {
  online: 'bg-green-500',
  away: 'bg-yellow-500',
  busy: 'bg-red-500',
  offline: 'bg-gray-400'
};

const statusLabels = {
  online: 'Online',
  away: 'Away',
  busy: 'Busy',
  offline: 'Offline'
};

const sizeClasses = {
  sm: 'w-6 h-6 text-xs',
  md: 'w-8 h-8 text-sm',
  lg: 'w-10 h-10 text-base'
};

export function UserPresenceIndicator({
  users,
  currentModule,
  currentPage,
  isConnected,
  maxVisible = 5,
  showStatus = true,
  showModule = false,
  size = 'md',
  className = ''
}: UserPresenceIndicatorProps) {
  // Filter users based on current context
  const relevantUsers = users.filter(user => {
    if (currentModule && user.current_module !== currentModule) return false;
    if (currentPage && user.current_page !== currentPage) return false;
    return user.status !== 'offline';
  });

  const visibleUsers = relevantUsers.slice(0, maxVisible);
  const hiddenCount = Math.max(0, relevantUsers.length - maxVisible);

  const formatLastActivity = (lastActivity: string) => {
    const now = new Date();
    const activity = new Date(lastActivity);
    const diffMs = now.getTime() - activity.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  if (relevantUsers.length === 0) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="flex items-center space-x-1 text-gray-500">
          {isConnected ? (
            <Wifi className="h-4 w-4" />
          ) : (
            <WifiOff className="h-4 w-4" />
          )}
          <span className="text-sm">
            {isConnected ? 'No active users' : 'Disconnected'}
          </span>
        </div>
      </div>
    );
  }

  return (
    <TooltipProvider>
      <div className={`flex items-center space-x-2 ${className}`}>
        {/* Connection Status */}
        <div className="flex items-center space-x-1">
          {isConnected ? (
            <Wifi className="h-4 w-4 text-green-500" />
          ) : (
            <WifiOff className="h-4 w-4 text-red-500" />
          )}
        </div>

        {/* User Avatars */}
        <div className="flex -space-x-2">
          {visibleUsers.map((user) => (
            <Tooltip key={user.user_id}>
              <TooltipTrigger asChild>
                <div className="relative">
                  <Avatar className={`${sizeClasses[size]} border-2 border-white hover:z-10 transition-transform hover:scale-110`}>
                    <AvatarImage src={user.avatar_url} alt={user.user_name} />
                    <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-medium">
                      {user.user_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  
                  {/* Status Indicator */}
                  {showStatus && (
                    <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white ${statusColors[user.status]}`} />
                  )}
                </div>
              </TooltipTrigger>
              <TooltipContent side="bottom" className="max-w-xs">
                <div className="space-y-1">
                  <div className="font-medium">{user.user_name}</div>
                  <div className="flex items-center space-x-2 text-sm">
                    <div className={`w-2 h-2 rounded-full ${statusColors[user.status]}`} />
                    <span>{statusLabels[user.status]}</span>
                  </div>
                  <div className="flex items-center space-x-1 text-xs text-gray-500">
                    <Clock className="h-3 w-3" />
                    <span>{formatLastActivity(user.last_activity)}</span>
                  </div>
                  {showModule && user.current_module && (
                    <div className="text-xs text-gray-500">
                      In: {user.current_module}
                      {user.current_page && ` > ${user.current_page}`}
                    </div>
                  )}
                </div>
              </TooltipContent>
            </Tooltip>
          ))}
          
          {/* Hidden Users Count */}
          {hiddenCount > 0 && (
            <Tooltip>
              <TooltipTrigger asChild>
                <div className={`${sizeClasses[size]} rounded-full bg-gray-200 border-2 border-white flex items-center justify-center text-gray-600 font-medium hover:z-10 transition-transform hover:scale-110`}>
                  +{hiddenCount}
                </div>
              </TooltipTrigger>
              <TooltipContent side="bottom">
                <div className="space-y-1">
                  <div className="font-medium">Additional Users</div>
                  {users.slice(maxVisible).map((user) => (
                    <div key={user.user_id} className="flex items-center space-x-2 text-sm">
                      <div className={`w-2 h-2 rounded-full ${statusColors[user.status]}`} />
                      <span>{user.user_name}</span>
                    </div>
                  ))}
                </div>
              </TooltipContent>
            </Tooltip>
          )}
        </div>

        {/* Summary */}
        <div className="flex items-center space-x-1 text-sm text-gray-600">
          <Users className="h-4 w-4" />
          <span>
            {relevantUsers.length} active
            {currentModule && ` in ${currentModule}`}
          </span>
        </div>
      </div>
    </TooltipProvider>
  );
}

// Simplified version for compact spaces
export function CompactUserPresence({
  users,
  isConnected,
  className = ''
}: {
  users: UserPresence[];
  isConnected: boolean;
  className?: string;
}) {
  const activeUsers = users.filter(u => u.status !== 'offline');
  
  return (
    <div className={`flex items-center space-x-1 ${className}`}>
      {isConnected ? (
        <Activity className="h-4 w-4 text-green-500" />
      ) : (
        <Activity className="h-4 w-4 text-gray-400" />
      )}
      <span className="text-sm text-gray-600">
        {activeUsers.length}
      </span>
    </div>
  );
}

// Real-time cursor overlay component
export function CursorOverlay({
  users,
  currentModule,
  currentPage
}: {
  users: UserPresence[];
  currentModule?: string;
  currentPage?: string;
}) {
  const usersWithCursors = users.filter(user => 
    user.cursor_position && 
    user.status !== 'offline' &&
    (!currentModule || user.current_module === currentModule) &&
    (!currentPage || user.current_page === currentPage)
  );

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {usersWithCursors.map((user) => (
        <div
          key={user.user_id}
          className="absolute transition-all duration-100 ease-out"
          style={{
            left: user.cursor_position!.x,
            top: user.cursor_position!.y,
            transform: 'translate(-50%, -50%)'
          }}
        >
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full border border-white shadow-lg" />
            <div className="bg-blue-500 text-white text-xs px-2 py-1 rounded shadow-lg whitespace-nowrap">
              {user.user_name}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
