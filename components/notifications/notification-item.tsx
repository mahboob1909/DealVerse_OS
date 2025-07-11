"use client";

import { useState } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Check,
  X,
  MoreHorizontal,
  ExternalLink,
  Clock,
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
  Users,
  FileText,
  Shield,
  Workflow,
  Brain,
  Settings,
  Bell
} from "lucide-react";
import { LiveNotification } from "@/lib/types/notifications";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";

interface NotificationItemProps {
  notification: LiveNotification;
  onMarkAsRead: (notificationId: string) => Promise<void>;
  onDismiss: (notificationId: string) => Promise<void>;
  onExecuteAction: (notificationId: string, actionId: string) => Promise<void>;
  isLast?: boolean;
  compact?: boolean;
}

export function NotificationItem({
  notification,
  onMarkAsRead,
  onDismiss,
  onExecuteAction,
  isLast = false,
  compact = false
}: NotificationItemProps) {
  const [isExecutingAction, setIsExecutingAction] = useState<string | null>(null);

  const getTypeIcon = () => {
    switch (notification.type) {
      case 'success': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'error': return <XCircle className="h-4 w-4 text-red-600" />;
      case 'collaboration': return <Users className="h-4 w-4 text-blue-600" />;
      case 'system': return <Settings className="h-4 w-4 text-gray-600" />;
      default: return <Info className="h-4 w-4 text-blue-600" />;
    }
  };

  const getCategoryIcon = () => {
    switch (notification.category) {
      case 'document': return <FileText className="h-3 w-3" />;
      case 'collaboration': return <Users className="h-3 w-3" />;
      case 'system': return <Settings className="h-3 w-3" />;
      case 'security': return <Shield className="h-3 w-3" />;
      case 'workflow': return <Workflow className="h-3 w-3" />;
      case 'ai_analysis': return <Brain className="h-3 w-3" />;
      default: return <Bell className="h-3 w-3" />;
    }
  };

  const getPriorityColor = () => {
    switch (notification.priority) {
      case 'urgent': return 'border-l-red-500 bg-red-50/50';
      case 'high': return 'border-l-orange-500 bg-orange-50/50';
      case 'medium': return 'border-l-yellow-500 bg-yellow-50/50';
      case 'low': return 'border-l-blue-500 bg-blue-50/50';
      default: return 'border-l-gray-500 bg-gray-50/50';
    }
  };

  const getPriorityBadgeColor = () => {
    switch (notification.priority) {
      case 'urgent': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleActionClick = async (actionId: string) => {
    setIsExecutingAction(actionId);
    try {
      await onExecuteAction(notification.id, actionId);
    } catch (error) {
      console.error('Failed to execute action:', error);
    } finally {
      setIsExecutingAction(null);
    }
  };

  const isUnread = !notification.read_at;
  const isExpired = notification.expires_at && new Date(notification.expires_at) < new Date();

  return (
    <div
      className={cn(
        "relative p-4 hover:bg-gray-50 transition-colors border-l-4",
        getPriorityColor(),
        isUnread && "bg-blue-50/30",
        isExpired && "opacity-60",
        compact && "p-3"
      )}
    >
      {/* Unread Indicator */}
      {isUnread && (
        <div className="absolute top-4 right-4 h-2 w-2 bg-blue-600 rounded-full" />
      )}

      <div className="flex gap-3">
        {/* Avatar/Icon */}
        <div className="flex-shrink-0">
          {notification.avatar_url ? (
            <Avatar className={cn("border", compact ? "h-8 w-8" : "h-10 w-10")}>
              <AvatarImage src={notification.avatar_url} alt="Notification" />
              <AvatarFallback>{getTypeIcon()}</AvatarFallback>
            </Avatar>
          ) : (
            <div className={cn(
              "flex items-center justify-center rounded-full border bg-white",
              compact ? "h-8 w-8" : "h-10 w-10"
            )}>
              {getTypeIcon()}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <h4 className={cn(
                "font-medium text-gray-900 truncate",
                compact ? "text-sm" : "text-base"
              )}>
                {notification.title}
              </h4>
              <p className={cn(
                "text-gray-600 mt-1",
                compact ? "text-xs" : "text-sm"
              )}>
                {notification.message}
              </p>
            </div>

            {/* Actions Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-auto p-1">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {!isUnread ? (
                  <DropdownMenuItem onClick={() => onMarkAsRead(notification.id)}>
                    <Check className="h-4 w-4 mr-2" />
                    Mark as Read
                  </DropdownMenuItem>
                ) : null}
                <DropdownMenuItem onClick={() => onDismiss(notification.id)}>
                  <X className="h-4 w-4 mr-2" />
                  Dismiss
                </DropdownMenuItem>
                {notification.action_url && (
                  <DropdownMenuItem asChild>
                    <a href={notification.action_url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Open Link
                    </a>
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Metadata */}
          <div className="flex items-center gap-2 mt-2">
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>{formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}</span>
            </div>

            <Badge variant="outline" className={cn("text-xs", getPriorityBadgeColor())}>
              {notification.priority}
            </Badge>

            <Badge variant="outline" className="text-xs">
              {getCategoryIcon()}
              <span className="ml-1 capitalize">{notification.category.replace('_', ' ')}</span>
            </Badge>

            {isExpired && (
              <Badge variant="outline" className="text-xs text-red-600">
                Expired
              </Badge>
            )}
          </div>

          {/* Thumbnail */}
          {notification.thumbnail_url && (
            <div className="mt-2">
              <img
                src={notification.thumbnail_url}
                alt="Notification thumbnail"
                className="h-16 w-24 object-cover rounded border"
              />
            </div>
          )}

          {/* Actions */}
          {notification.actions && notification.actions.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {notification.actions.map((action) => (
                <Button
                  key={action.id}
                  variant={action.style === 'primary' ? 'default' : action.style === 'destructive' ? 'destructive' : 'outline'}
                  size="sm"
                  onClick={() => handleActionClick(action.id)}
                  disabled={isExecutingAction === action.id}
                  className="h-auto px-3 py-1 text-xs"
                >
                  {isExecutingAction === action.id ? (
                    <div className="h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent mr-1" />
                  ) : action.icon ? (
                    <span className="mr-1">{action.icon}</span>
                  ) : null}
                  {action.label}
                </Button>
              ))}
            </div>
          )}

          {/* Primary Action Button */}
          {notification.action_url && notification.action_label && (
            <div className="mt-3">
              <Button
                variant="outline"
                size="sm"
                asChild
                className="h-auto px-3 py-1 text-xs"
              >
                <a href={notification.action_url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-3 w-3 mr-1" />
                  {notification.action_label}
                </a>
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Separator */}
      {!isLast && <Separator className="mt-4" />}
    </div>
  );
}
