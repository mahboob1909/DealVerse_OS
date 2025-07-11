"use client";

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  X,
  CheckCircle,
  AlertTriangle,
  Info,
  XCircle,
  ExternalLink
} from "lucide-react";
import { LiveNotification } from "@/lib/types/notifications";
import { cn } from "@/lib/utils";

interface ToastNotificationProps {
  notification: LiveNotification;
  onDismiss: (id: string) => void;
  onAction?: (id: string, actionId: string) => void;
  duration?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  showProgress?: boolean;
}

export function ToastNotification({
  notification,
  onDismiss,
  onAction,
  duration = 5000,
  position = 'top-right',
  showProgress = true
}: ToastNotificationProps) {
  const [progress, setProgress] = useState(100);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    if (isPaused || duration <= 0) return;

    const interval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev - (100 / (duration / 100));
        if (newProgress <= 0) {
          onDismiss(notification.id);
          return 0;
        }
        return newProgress;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [notification.id, onDismiss, duration, isPaused]);

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'info':
      default:
        return <Info className="h-5 w-5 text-blue-600" />;
    }
  };

  const getColorClasses = () => {
    switch (notification.type) {
      case 'success':
        return 'border-l-green-500 bg-green-50';
      case 'warning':
        return 'border-l-yellow-500 bg-yellow-50';
      case 'error':
        return 'border-l-red-500 bg-red-50';
      case 'info':
      default:
        return 'border-l-blue-500 bg-blue-50';
    }
  };

  const getProgressColor = () => {
    switch (notification.type) {
      case 'success':
        return 'bg-green-600';
      case 'warning':
        return 'bg-yellow-600';
      case 'error':
        return 'bg-red-600';
      case 'info':
      default:
        return 'bg-blue-600';
    }
  };

  const getPositionClasses = () => {
    switch (position) {
      case 'top-left':
        return 'top-4 left-4';
      case 'top-center':
        return 'top-4 left-1/2 transform -translate-x-1/2';
      case 'top-right':
        return 'top-4 right-4';
      case 'bottom-left':
        return 'bottom-4 left-4';
      case 'bottom-center':
        return 'bottom-4 left-1/2 transform -translate-x-1/2';
      case 'bottom-right':
        return 'bottom-4 right-4';
      default:
        return 'top-4 right-4';
    }
  };

  const handleActionClick = (actionId: string) => {
    if (onAction) {
      onAction(notification.id, actionId);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.95 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className={cn(
        "fixed z-50 w-96 max-w-[calc(100vw-2rem)]",
        getPositionClasses()
      )}
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <Card className={cn(
        "border-l-4 shadow-lg",
        getColorClasses()
      )}>
        <div className="p-4">
          <div className="flex items-start gap-3">
            {/* Icon */}
            <div className="flex-shrink-0 mt-0.5">
              {getIcon()}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h4 className="font-medium text-gray-900 text-sm">
                {notification.title}
              </h4>
              <p className="text-gray-600 text-sm mt-1">
                {notification.message}
              </p>

              {/* Actions */}
              {notification.actions && notification.actions.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {notification.actions.slice(0, 2).map((action) => (
                    <Button
                      key={action.id}
                      variant={action.style === 'primary' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => handleActionClick(action.id)}
                      className="h-auto px-3 py-1 text-xs"
                    >
                      {action.label}
                    </Button>
                  ))}
                </div>
              )}

              {/* Primary Action */}
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

            {/* Dismiss Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDismiss(notification.id)}
              className="h-auto p-1 text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Progress Bar */}
          {showProgress && duration > 0 && (
            <div className="mt-3">
              <div className="w-full bg-gray-200 rounded-full h-1">
                <div
                  className={cn("h-1 rounded-full transition-all duration-100", getProgressColor())}
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  );
}

interface ToastContainerProps {
  notifications: LiveNotification[];
  onDismiss: (id: string) => void;
  onAction?: (id: string, actionId: string) => void;
  maxToasts?: number;
  position?: ToastNotificationProps['position'];
  duration?: number;
}

export function ToastContainer({
  notifications,
  onDismiss,
  onAction,
  maxToasts = 5,
  position = 'top-right',
  duration = 5000
}: ToastContainerProps) {
  // Only show recent notifications as toasts
  const toastNotifications = notifications
    .filter(n => !n.read_at && !n.dismissed_at)
    .slice(0, maxToasts);

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      <AnimatePresence mode="popLayout">
        {toastNotifications.map((notification, index) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0 }}
            animate={{ 
              opacity: 1,
              y: index * 110 // Stack toasts vertically
            }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="pointer-events-auto"
          >
            <ToastNotification
              notification={notification}
              onDismiss={onDismiss}
              onAction={onAction}
              position={position}
              duration={duration}
              showProgress={true}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
