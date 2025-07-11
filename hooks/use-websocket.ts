"use client";

import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/lib/auth-context';

interface WebSocketOptions {
  onMessage?: (message: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  onConnectionEstablished?: (connectionInfo: any) => void;
  onPing?: (timestamp: string) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
  enableHeartbeat?: boolean;
  heartbeatInterval?: number;
  enableMessageQueue?: boolean;
  enableMetrics?: boolean;
}

interface ConnectionMetrics {
  messagesSent: number;
  messagesReceived: number;
  bytesTransferred: number;
  connectionTime: number;
  reconnectCount: number;
  lastActivity: Date;
}

interface WebSocketHook {
  isConnected: boolean;
  connectionId: string | null;
  sendMessage: (message: any) => void;
  disconnect: () => void;
  reconnect: () => void;
  getMetrics: () => ConnectionMetrics;
  getConnectionInfo: () => any;
}

export function useWebSocket(options: WebSocketOptions = {}): WebSocketHook {
  const { user } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const metricsRef = useRef<ConnectionMetrics>({
    messagesSent: 0,
    messagesReceived: 0,
    bytesTransferred: 0,
    connectionTime: 0,
    reconnectCount: 0,
    lastActivity: new Date()
  });
  const connectionInfoRef = useRef<any>(null);
  const messageQueueRef = useRef<any[]>([]);

  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    onConnectionEstablished,
    onPing,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
    enableHeartbeat = true,
    heartbeatInterval = 30000,
    enableMessageQueue = true,
    enableMetrics = true
  } = options;

  const connect = useCallback(() => {
    if (!user?.id || !user?.organization_id) {
      console.log('WebSocket: User not authenticated, skipping connection');
      return;
    }

    try {
      // Construct WebSocket URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = process.env.NODE_ENV === 'production' 
        ? window.location.host 
        : 'localhost:8000';
      
      const wsUrl = `${wsProtocol}//${wsHost}/api/v1/ws/ws/${user.id}?organization_id=${user.organization_id}&user_name=${encodeURIComponent(user.first_name + ' ' + user.last_name)}`;
      
      console.log('WebSocket: Connecting to', wsUrl);
      
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket: Connected');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;

        // Update metrics
        if (enableMetrics) {
          metricsRef.current.connectionTime = Date.now();
          metricsRef.current.lastActivity = new Date();
          if (reconnectAttemptsRef.current > 0) {
            metricsRef.current.reconnectCount++;
          }
        }

        // Start heartbeat if enabled
        if (enableHeartbeat) {
          startHeartbeat();
        }

        // Send queued messages if any
        if (enableMessageQueue && messageQueueRef.current.length > 0) {
          console.log(`WebSocket: Sending ${messageQueueRef.current.length} queued messages`);
          messageQueueRef.current.forEach(queuedMessage => {
            sendMessage(queuedMessage);
          });
          messageQueueRef.current = [];
        }

        onConnect?.();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('WebSocket: Message received', message);

          // Update metrics
          if (enableMetrics) {
            metricsRef.current.messagesReceived++;
            metricsRef.current.bytesTransferred += event.data.length;
            metricsRef.current.lastActivity = new Date();
          }

          // Handle special message types
          if (message.type === 'connection_established') {
            setConnectionId(message.connection_id);
            connectionInfoRef.current = message;
            onConnectionEstablished?.(message);
          } else if (message.type === 'ping') {
            // Respond to server ping with pong
            sendMessage({
              type: 'pong',
              timestamp: message.timestamp
            });
            onPing?.(message.timestamp);
          } else if (message.type === 'pong') {
            // Server responded to our ping
            console.log('WebSocket: Pong received');
          } else {
            // Regular message
            onMessage?.(message);
          }
        } catch (error) {
          console.error('WebSocket: Failed to parse message', error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket: Disconnected', event.code, event.reason);
        setIsConnected(false);
        setConnectionId(null);

        // Stop heartbeat
        stopHeartbeat();

        onDisconnect?.();

        // Attempt to reconnect if not manually closed
        if (event.code !== 1000 && reconnectAttemptsRef.current < reconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`WebSocket: Reconnecting attempt ${reconnectAttemptsRef.current}/${reconnectAttempts}`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket: Error', error);
        onError?.(error);
      };

    } catch (error) {
      console.error('WebSocket: Connection failed', error);
    }
  }, [user, onMessage, onConnect, onDisconnect, onError, onConnectionEstablished, onPing, reconnectAttempts, reconnectInterval, enableHeartbeat, enableMessageQueue, enableMetrics]);

  const startHeartbeat = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
    }

    const sendHeartbeat = () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        sendMessage({
          type: 'ping',
          timestamp: new Date().toISOString()
        });

        heartbeatTimeoutRef.current = setTimeout(sendHeartbeat, heartbeatInterval);
      }
    };

    heartbeatTimeoutRef.current = setTimeout(sendHeartbeat, heartbeatInterval);
  }, [heartbeatInterval]);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    stopHeartbeat();

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setIsConnected(false);
    setConnectionId(null);
  }, [stopHeartbeat]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        const messageString = JSON.stringify(message);
        wsRef.current.send(messageString);
        console.log('WebSocket: Message sent', message);

        // Update metrics
        if (enableMetrics) {
          metricsRef.current.messagesSent++;
          metricsRef.current.bytesTransferred += messageString.length;
          metricsRef.current.lastActivity = new Date();
        }
      } catch (error) {
        console.error('WebSocket: Failed to send message', error);
      }
    } else {
      console.warn('WebSocket: Cannot send message, connection not open');

      // Queue message if enabled and not connected
      if (enableMessageQueue && message.type !== 'ping' && message.type !== 'pong') {
        messageQueueRef.current.push(message);
        console.log('WebSocket: Message queued for later delivery');
      }
    }
  }, [enableMetrics, enableMessageQueue]);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    connect();
  }, [disconnect, connect]);

  const getMetrics = useCallback((): ConnectionMetrics => {
    return { ...metricsRef.current };
  }, []);

  const getConnectionInfo = useCallback(() => {
    return connectionInfoRef.current;
  }, []);

  // Connect on mount and when user changes
  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (heartbeatTimeoutRef.current) {
        clearTimeout(heartbeatTimeoutRef.current);
      }
    };
  }, []);

  return {
    isConnected,
    connectionId,
    sendMessage,
    disconnect,
    reconnect,
    getMetrics,
    getConnectionInfo
  };
}
