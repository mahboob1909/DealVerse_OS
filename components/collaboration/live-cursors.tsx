"use client";

import { useEffect, useState, useRef } from 'react';
import { CursorPosition } from "@/lib/types/collaboration";
import { motion, AnimatePresence } from "framer-motion";

interface LiveCursorsProps {
  cursors: CursorPosition[];
  containerRef?: React.RefObject<HTMLElement>;
  showLabels?: boolean;
  fadeTimeout?: number;
}

interface CursorWithTimeout extends CursorPosition {
  lastSeen: number;
}

export function LiveCursors({ 
  cursors, 
  containerRef,
  showLabels = true,
  fadeTimeout = 3000 
}: LiveCursorsProps) {
  const [activeCursors, setActiveCursors] = useState<CursorWithTimeout[]>([]);
  const timeoutRefs = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Update cursors with timeout tracking
  useEffect(() => {
    const now = Date.now();
    
    cursors.forEach(cursor => {
      // Clear existing timeout for this user
      const existingTimeout = timeoutRefs.current.get(cursor.user_id);
      if (existingTimeout) {
        clearTimeout(existingTimeout);
      }

      // Update cursor with current timestamp
      setActiveCursors(prev => {
        const filtered = prev.filter(c => c.user_id !== cursor.user_id);
        return [...filtered, { ...cursor, lastSeen: now }];
      });

      // Set new timeout to remove cursor
      const timeout = setTimeout(() => {
        setActiveCursors(prev => prev.filter(c => c.user_id !== cursor.user_id));
        timeoutRefs.current.delete(cursor.user_id);
      }, fadeTimeout);

      timeoutRefs.current.set(cursor.user_id, timeout);
    });
  }, [cursors, fadeTimeout]);

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      timeoutRefs.current.forEach(timeout => clearTimeout(timeout));
      timeoutRefs.current.clear();
    };
  }, []);

  // Get container bounds for positioning
  const getContainerBounds = () => {
    if (containerRef?.current) {
      return containerRef.current.getBoundingClientRect();
    }
    return { left: 0, top: 0, width: window.innerWidth, height: window.innerHeight };
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
    <div className="pointer-events-none fixed inset-0 z-50">
      <AnimatePresence>
        {activeCursors.map((cursor) => {
          const containerBounds = getContainerBounds();
          const x = containerBounds.left + cursor.position.x;
          const y = containerBounds.top + cursor.position.y;

          return (
            <motion.div
              key={cursor.user_id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.2 }}
              className="absolute"
              style={{
                left: x,
                top: y,
                transform: 'translate(-2px, -2px)',
              }}
            >
              {/* Cursor SVG */}
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="drop-shadow-sm"
              >
                <path
                  d="M2 2L18 8L8 12L2 18V2Z"
                  fill={cursor.user_color}
                  stroke="white"
                  strokeWidth="1"
                />
              </svg>

              {/* User Label */}
              {showLabels && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ delay: 0.1 }}
                  className="absolute left-5 top-0 flex items-center gap-1 pointer-events-auto"
                >
                  <div
                    className="px-2 py-1 rounded-md text-white text-xs font-medium shadow-lg max-w-32 truncate"
                    style={{ backgroundColor: cursor.user_color }}
                  >
                    {cursor.user_name}
                  </div>
                </motion.div>
              )}

              {/* Selection Highlight */}
              {cursor.position.selection && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 0.3 }}
                  exit={{ opacity: 0 }}
                  className="absolute pointer-events-none"
                  style={{
                    backgroundColor: cursor.user_color,
                    left: cursor.position.selection.start,
                    width: cursor.position.selection.end - cursor.position.selection.start,
                    height: '1.2em',
                    top: '-0.1em',
                  }}
                />
              )}
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}

// Hook for tracking mouse position and sending cursor updates
export function useCursorTracking(
  updateCursorPosition: (position: CursorPosition['position']) => void,
  containerRef?: React.RefObject<HTMLElement>,
  enabled: boolean = true
) {
  const lastPositionRef = useRef<{ x: number; y: number } | null>(null);
  const throttleRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!enabled) return;

    const handleMouseMove = (event: MouseEvent) => {
      const container = containerRef?.current || document.body;
      const containerBounds = container.getBoundingClientRect();
      
      const x = event.clientX - containerBounds.left;
      const y = event.clientY - containerBounds.top;

      // Throttle updates to avoid overwhelming the WebSocket
      if (throttleRef.current) {
        clearTimeout(throttleRef.current);
      }

      throttleRef.current = setTimeout(() => {
        // Only send update if position changed significantly
        if (
          !lastPositionRef.current ||
          Math.abs(lastPositionRef.current.x - x) > 5 ||
          Math.abs(lastPositionRef.current.y - y) > 5
        ) {
          lastPositionRef.current = { x, y };
          
          updateCursorPosition({
            x,
            y,
            element_id: (event.target as HTMLElement)?.id || undefined
          });
        }
      }, 50); // Throttle to 20fps
    };

    const handleMouseLeave = () => {
      // Clear cursor when mouse leaves the container
      if (throttleRef.current) {
        clearTimeout(throttleRef.current);
      }
    };

    const container = containerRef?.current || document;
    container.addEventListener('mousemove', handleMouseMove);
    container.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      container.removeEventListener('mousemove', handleMouseMove);
      container.removeEventListener('mouseleave', handleMouseLeave);
      if (throttleRef.current) {
        clearTimeout(throttleRef.current);
      }
    };
  }, [updateCursorPosition, containerRef, enabled]);

  return {
    // Could return cursor tracking state if needed
  };
}

// Component that combines cursor display and tracking
export function CollaborativeCursors({
  cursors,
  updateCursorPosition,
  containerRef,
  showLabels = true,
  enableTracking = true,
  fadeTimeout = 3000
}: LiveCursorsProps & {
  updateCursorPosition: (position: CursorPosition['position']) => void;
  enableTracking?: boolean;
}) {
  // Track current user's cursor
  useCursorTracking(updateCursorPosition, containerRef, enableTracking);

  return (
    <LiveCursors
      cursors={cursors}
      containerRef={containerRef}
      showLabels={showLabels}
      fadeTimeout={fadeTimeout}
    />
  );
}
