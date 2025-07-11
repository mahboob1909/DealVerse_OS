"use client";

import { useState } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import {
  Users,
  Circle,
  Clock,
  Eye,
  Edit,
  MessageCircle,
  ChevronDown
} from "lucide-react";
import { UserPresence } from "@/lib/types/collaboration";
import { formatDistanceToNow } from "date-fns";

interface UserPresenceProps {
  activeUsers: UserPresence[];
  currentUser: UserPresence | null;
  maxVisible?: number;
  showDetails?: boolean;
  compact?: boolean;
}

export function UserPresenceIndicator({ 
  activeUsers, 
  currentUser, 
  maxVisible = 5,
  showDetails = true,
  compact = false
}: UserPresenceProps) {
  const [showAllUsers, setShowAllUsers] = useState(false);

  // Filter out current user from active users display
  const otherUsers = activeUsers.filter(user => user.user_id !== currentUser?.user_id);
  const visibleUsers = showAllUsers ? otherUsers : otherUsers.slice(0, maxVisible);
  const hiddenCount = Math.max(0, otherUsers.length - maxVisible);

  const getStatusColor = (status: UserPresence['status']) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'away': return 'bg-yellow-500';
      case 'busy': return 'bg-red-500';
      case 'offline': return 'bg-gray-400';
      default: return 'bg-gray-400';
    }
  };

  const getStatusLabel = (status: UserPresence['status']) => {
    switch (status) {
      case 'online': return 'Online';
      case 'away': return 'Away';
      case 'busy': return 'Busy';
      case 'offline': return 'Offline';
      default: return 'Unknown';
    }
  };

  const getUserInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getActivityDescription = (user: UserPresence) => {
    if (user.current_location?.section) {
      return `Viewing ${user.current_location.section}`;
    }
    if (user.current_location?.page) {
      return `On page ${user.current_location.page}`;
    }
    return 'In document';
  };

  if (compact) {
    return (
      <div className="flex items-center gap-1">
        <TooltipProvider>
          <div className="flex -space-x-2">
            {visibleUsers.map((user) => (
              <Tooltip key={user.user_id}>
                <TooltipTrigger asChild>
                  <div className="relative">
                    <Avatar className="h-8 w-8 border-2 border-white">
                      <AvatarImage src={user.avatar_url} alt={user.user_name} />
                      <AvatarFallback className="text-xs">
                        {getUserInitials(user.user_name)}
                      </AvatarFallback>
                    </Avatar>
                    <div className={`absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white ${getStatusColor(user.status)}`} />
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <div className="text-sm">
                    <div className="font-medium">{user.user_name}</div>
                    <div className="text-muted-foreground">{getStatusLabel(user.status)}</div>
                    <div className="text-muted-foreground">{getActivityDescription(user)}</div>
                  </div>
                </TooltipContent>
              </Tooltip>
            ))}
            
            {hiddenCount > 0 && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-white bg-gray-100 text-xs font-medium text-gray-600">
                    +{hiddenCount}
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <div className="text-sm">
                    {hiddenCount} more user{hiddenCount > 1 ? 's' : ''} online
                  </div>
                </TooltipContent>
              </Tooltip>
            )}
          </div>
        </TooltipProvider>
        
        <span className="ml-2 text-sm text-muted-foreground">
          {otherUsers.length} online
        </span>
      </div>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            <span>Active Collaborators</span>
            <Badge variant="secondary" className="text-xs">
              {otherUsers.length}
            </Badge>
          </div>
          
          {hiddenCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAllUsers(!showAllUsers)}
              className="h-auto p-1"
            >
              <ChevronDown className={`h-3 w-3 transition-transform ${showAllUsers ? 'rotate-180' : ''}`} />
            </Button>
          )}
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {/* Current User */}
        {currentUser && (
          <>
            <div className="flex items-center gap-3 p-2 bg-blue-50 rounded-lg">
              <div className="relative">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={currentUser.avatar_url} alt={currentUser.user_name} />
                  <AvatarFallback className="text-xs">
                    {getUserInitials(currentUser.user_name)}
                  </AvatarFallback>
                </Avatar>
                <div className={`absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white ${getStatusColor(currentUser.status)}`} />
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium truncate">
                    {currentUser.user_name} (You)
                  </span>
                  <Badge variant="outline" className="text-xs">
                    {getStatusLabel(currentUser.status)}
                  </Badge>
                </div>
                {showDetails && (
                  <div className="text-xs text-muted-foreground">
                    {getActivityDescription(currentUser)}
                  </div>
                )}
              </div>
            </div>
            
            {otherUsers.length > 0 && <Separator />}
          </>
        )}

        {/* Other Users */}
        {visibleUsers.length > 0 ? (
          <div className="space-y-2">
            {visibleUsers.map((user) => (
              <div key={user.user_id} className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded-lg transition-colors">
                <div className="relative">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user.avatar_url} alt={user.user_name} />
                    <AvatarFallback className="text-xs">
                      {getUserInitials(user.user_name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className={`absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white ${getStatusColor(user.status)}`} />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium truncate">
                      {user.user_name}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      {getStatusLabel(user.status)}
                    </Badge>
                  </div>
                  
                  {showDetails && (
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        {getActivityDescription(user)}
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDistanceToNow(new Date(user.last_activity), { addSuffix: true })}
                      </div>
                    </div>
                  )}
                </div>

                {/* Activity Indicators */}
                <div className="flex items-center gap-1">
                  {user.cursor_position && (
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <span className="text-xs">Currently editing</span>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-4 text-sm text-muted-foreground">
            No other collaborators online
          </div>
        )}

        {/* Show More Button */}
        {hiddenCount > 0 && !showAllUsers && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowAllUsers(true)}
            className="w-full text-xs"
          >
            Show {hiddenCount} more user{hiddenCount > 1 ? 's' : ''}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
