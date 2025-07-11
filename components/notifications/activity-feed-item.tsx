"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  FileText,
  Edit3,
  MessageCircle,
  UserPlus,
  CheckCircle,
  Workflow,
  Users,
  Settings,
  Clock,
  ExternalLink
} from "lucide-react";
import { ActivityFeedItem as ActivityItem } from "@/lib/types/notifications";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";

interface ActivityFeedItemProps {
  item: ActivityItem;
  isLast?: boolean;
  compact?: boolean;
}

export function ActivityFeedItem({
  item,
  isLast = false,
  compact = false
}: ActivityFeedItemProps) {
  const getActivityIcon = () => {
    switch (item.type) {
      case 'document_created':
        return <FileText className="h-4 w-4 text-blue-600" />;
      case 'document_updated':
        return <Edit3 className="h-4 w-4 text-green-600" />;
      case 'comment_added':
        return <MessageCircle className="h-4 w-4 text-purple-600" />;
      case 'user_joined':
        return <UserPlus className="h-4 w-4 text-blue-600" />;
      case 'analysis_completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'workflow_updated':
        return <Workflow className="h-4 w-4 text-orange-600" />;
      case 'collaboration_started':
        return <Users className="h-4 w-4 text-blue-600" />;
      case 'system_event':
        return <Settings className="h-4 w-4 text-gray-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getActivityColor = () => {
    switch (item.type) {
      case 'document_created':
      case 'user_joined':
      case 'collaboration_started':
        return 'text-blue-600';
      case 'document_updated':
      case 'analysis_completed':
        return 'text-green-600';
      case 'comment_added':
        return 'text-purple-600';
      case 'workflow_updated':
        return 'text-orange-600';
      case 'system_event':
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  const getActivityTypeLabel = () => {
    switch (item.type) {
      case 'document_created': return 'Created Document';
      case 'document_updated': return 'Updated Document';
      case 'comment_added': return 'Added Comment';
      case 'user_joined': return 'Joined Project';
      case 'analysis_completed': return 'Completed Analysis';
      case 'workflow_updated': return 'Updated Workflow';
      case 'collaboration_started': return 'Started Collaboration';
      case 'system_event': return 'System Event';
      default: return 'Activity';
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

  return (
    <div className={cn("relative p-4 hover:bg-gray-50 transition-colors", compact && "p-3")}>
      <div className="flex gap-3">
        {/* Timeline indicator */}
        <div className="flex flex-col items-center">
          <div className={cn(
            "flex items-center justify-center rounded-full border-2 border-white bg-white shadow-sm",
            compact ? "h-8 w-8" : "h-10 w-10"
          )}>
            {item.user_avatar ? (
              <Avatar className={cn(compact ? "h-6 w-6" : "h-8 w-8")}>
                <AvatarImage src={item.user_avatar} alt={item.user_name} />
                <AvatarFallback className="text-xs">
                  {getUserInitials(item.user_name)}
                </AvatarFallback>
              </Avatar>
            ) : (
              getActivityIcon()
            )}
          </div>
          
          {/* Timeline line */}
          {!isLast && (
            <div className="w-px h-full bg-gray-200 mt-2" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h4 className={cn(
                  "font-medium text-gray-900",
                  compact ? "text-sm" : "text-base"
                )}>
                  {item.title}
                </h4>
                
                <Badge variant="outline" className={cn("text-xs", getActivityColor())}>
                  {getActivityIcon()}
                  <span className="ml-1">{getActivityTypeLabel()}</span>
                </Badge>
              </div>

              <p className={cn(
                "text-gray-600",
                compact ? "text-xs" : "text-sm"
              )}>
                {item.description}
              </p>

              {/* Context information */}
              <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                <span className="font-medium">{item.user_name}</span>
                
                {item.document_name && (
                  <>
                    <span>•</span>
                    <span>{item.document_name}</span>
                  </>
                )}
                
                {item.project_name && (
                  <>
                    <span>•</span>
                    <span>{item.project_name}</span>
                  </>
                )}
                
                <span>•</span>
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  <span>{formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}</span>
                </div>
              </div>

              {/* Thumbnail */}
              {item.thumbnail_url && (
                <div className="mt-2">
                  <img
                    src={item.thumbnail_url}
                    alt="Activity thumbnail"
                    className="h-12 w-16 object-cover rounded border"
                  />
                </div>
              )}

              {/* Action button */}
              {item.action_url && item.action_label && (
                <div className="mt-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    asChild
                    className="h-auto px-2 py-1 text-xs"
                  >
                    <a href={item.action_url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-3 w-3 mr-1" />
                      {item.action_label}
                    </a>
                  </Button>
                </div>
              )}

              {/* Metadata */}
              {item.metadata && Object.keys(item.metadata).length > 0 && (
                <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                  {Object.entries(item.metadata).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="font-medium capitalize">{key.replace('_', ' ')}:</span>
                      <span className="text-muted-foreground">{String(value)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Separator */}
      {!isLast && <Separator className="mt-4" />}
    </div>
  );
}
