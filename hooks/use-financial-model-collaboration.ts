"use client";

import { useState, useEffect, useRef, useCallback } from 'react';
import { useWebSocket } from './use-websocket';
import { useAuth } from '@/lib/auth-context';

interface FinancialModelUpdate {
  type: 'cell_update' | 'formula_update' | 'structure_update';
  cellId?: string;
  value?: any;
  formula?: string;
  range?: string;
  metadata?: any;
}

interface ModelUser {
  user_id: string;
  user_name: string;
  cursor_position?: {
    cell: string;
    sheet: string;
  };
  last_activity: string;
}

interface ScenarioData {
  name: string;
  assumptions: Record<string, any>;
  results: Record<string, any>;
  metadata?: any;
}

interface UseFinancialModelCollaborationOptions {
  modelId: string;
  onModelUpdate?: (update: FinancialModelUpdate, user: ModelUser) => void;
  onUserJoined?: (user: ModelUser) => void;
  onUserLeft?: (user: ModelUser) => void;
  onScenarioUpdate?: (scenario: ScenarioData, user: ModelUser) => void;
  onConnectionError?: (error: string) => void;
  enableAutoSave?: boolean;
  autoSaveInterval?: number;
}

interface UseFinancialModelCollaborationReturn {
  activeUsers: ModelUser[];
  isConnected: boolean;
  connectionError: string | null;
  sendModelUpdate: (update: FinancialModelUpdate) => void;
  sendScenarioUpdate: (scenario: ScenarioData) => void;
  joinModel: () => void;
  leaveModel: () => void;
  updateCursorPosition: (position: { cell: string; sheet: string }) => void;
  getModelVersion: () => number;
  isUserActive: (userId: string) => boolean;
}

export function useFinancialModelCollaboration(
  options: UseFinancialModelCollaborationOptions
): UseFinancialModelCollaborationReturn {
  const { user } = useAuth();
  const [activeUsers, setActiveUsers] = useState<ModelUser[]>([]);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [modelVersion, setModelVersion] = useState(1);
  const currentModelRef = useRef<string | null>(null);
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const {
    modelId,
    onModelUpdate,
    onUserJoined,
    onUserLeft,
    onScenarioUpdate,
    onConnectionError,
    enableAutoSave = true,
    autoSaveInterval = 5000
  } = options;

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((message: any) => {
    try {
      switch (message.type) {
        case 'financial_model_update':
          if (message.model_id === modelId) {
            const update: FinancialModelUpdate = {
              type: message.update_type,
              ...message.update_data
            };
            const user: ModelUser = {
              user_id: message.user_id,
              user_name: message.user_name,
              last_activity: message.timestamp
            };
            
            setModelVersion(prev => prev + 1);
            onModelUpdate?.(update, user);
          }
          break;

        case 'user_joined_model':
          if (message.model_id === modelId) {
            const newUser: ModelUser = {
              user_id: message.user_id,
              user_name: message.user_name,
              last_activity: message.timestamp
            };
            
            setActiveUsers(prev => {
              const filtered = prev.filter(u => u.user_id !== newUser.user_id);
              return [...filtered, newUser];
            });
            
            onUserJoined?.(newUser);
          }
          break;

        case 'user_left_model':
          if (message.model_id === modelId) {
            const leftUser: ModelUser = {
              user_id: message.user_id,
              user_name: message.user_name,
              last_activity: message.timestamp
            };
            
            setActiveUsers(prev => prev.filter(u => u.user_id !== message.user_id));
            onUserLeft?.(leftUser);
          }
          break;

        case 'scenario_update':
          if (message.model_id === modelId) {
            const scenario: ScenarioData = {
              name: message.scenario_name,
              assumptions: message.scenario_data.assumptions || {},
              results: message.scenario_data.results || {},
              metadata: message.scenario_data.metadata
            };
            const user: ModelUser = {
              user_id: message.user_id,
              user_name: message.user_name,
              last_activity: message.timestamp
            };
            
            onScenarioUpdate?.(scenario, user);
          }
          break;

        case 'model_state':
          if (message.model_id === modelId) {
            console.log('Received model state:', message);
            // Handle initial model state when joining
          }
          break;

        case 'cursor_position':
          if (message.model_id === modelId) {
            setActiveUsers(prev => prev.map(user => 
              user.user_id === message.user_id 
                ? { ...user, cursor_position: message.position, last_activity: message.timestamp }
                : user
            ));
          }
          break;

        default:
          // Handle other message types
          break;
      }
    } catch (error) {
      console.error('Error handling financial model message:', error);
      setConnectionError('Failed to process collaboration message');
    }
  }, [modelId, onModelUpdate, onUserJoined, onUserLeft, onScenarioUpdate]);

  // WebSocket connection
  const { isConnected, sendMessage } = useWebSocket({
    onMessage: handleWebSocketMessage,
    onError: (error) => {
      console.error('WebSocket financial model error:', error);
      setConnectionError('Connection error occurred');
      onConnectionError?.('Connection error occurred');
    },
    onConnect: () => {
      setConnectionError(null);
      // Auto-join model when connected
      if (modelId && user) {
        joinModel();
      }
    },
    onDisconnect: () => {
      setActiveUsers([]);
    },
    enableHeartbeat: true,
    enableMessageQueue: true,
    enableMetrics: true
  });

  // Join financial model collaboration
  const joinModel = useCallback(() => {
    if (!isConnected || !modelId || !user) return;

    currentModelRef.current = modelId;
    sendMessage({
      type: 'join_financial_model',
      model_id: modelId,
      timestamp: new Date().toISOString()
    });
  }, [isConnected, modelId, user, sendMessage]);

  // Leave financial model collaboration
  const leaveModel = useCallback(() => {
    if (!isConnected || !modelId || !user) return;

    sendMessage({
      type: 'leave_financial_model',
      model_id: modelId,
      timestamp: new Date().toISOString()
    });

    currentModelRef.current = null;
    setActiveUsers([]);
  }, [isConnected, modelId, user, sendMessage]);

  // Send model update
  const sendModelUpdate = useCallback((update: FinancialModelUpdate) => {
    if (!isConnected || !modelId || !user) return;

    sendMessage({
      type: 'financial_model_update',
      model_id: modelId,
      update_type: update.type,
      update_data: {
        cellId: update.cellId,
        value: update.value,
        formula: update.formula,
        range: update.range,
        metadata: update.metadata
      },
      version: modelVersion,
      timestamp: new Date().toISOString()
    });

    setModelVersion(prev => prev + 1);
  }, [isConnected, modelId, user, sendMessage, modelVersion]);

  // Send scenario update
  const sendScenarioUpdate = useCallback((scenario: ScenarioData) => {
    if (!isConnected || !modelId || !user) return;

    sendMessage({
      type: 'scenario_update',
      model_id: modelId,
      scenario_name: scenario.name,
      scenario_data: {
        assumptions: scenario.assumptions,
        results: scenario.results,
        metadata: scenario.metadata
      },
      timestamp: new Date().toISOString()
    });
  }, [isConnected, modelId, user, sendMessage]);

  // Update cursor position
  const updateCursorPosition = useCallback((position: { cell: string; sheet: string }) => {
    if (!isConnected || !modelId || !user) return;

    sendMessage({
      type: 'cursor_position',
      model_id: modelId,
      position: position,
      timestamp: new Date().toISOString()
    });
  }, [isConnected, modelId, user, sendMessage]);

  // Check if user is active (last activity within 5 minutes)
  const isUserActive = useCallback((userId: string) => {
    const user = activeUsers.find(u => u.user_id === userId);
    if (!user) return false;
    
    const lastActivity = new Date(user.last_activity);
    const now = new Date();
    const diffMinutes = (now.getTime() - lastActivity.getTime()) / (1000 * 60);
    
    return diffMinutes < 5;
  }, [activeUsers]);

  // Auto-join model when modelId changes
  useEffect(() => {
    if (modelId && isConnected && user) {
      joinModel();
    }

    return () => {
      if (currentModelRef.current) {
        leaveModel();
      }
    };
  }, [modelId, isConnected, user, joinModel, leaveModel]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
      if (currentModelRef.current) {
        leaveModel();
      }
    };
  }, [leaveModel]);

  return {
    activeUsers,
    isConnected,
    connectionError,
    sendModelUpdate,
    sendScenarioUpdate,
    joinModel,
    leaveModel,
    updateCursorPosition,
    getModelVersion: () => modelVersion,
    isUserActive
  };
}
