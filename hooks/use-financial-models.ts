"use client";

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';

export interface FinancialModel {
  id: string;
  name: string;
  description?: string;
  model_type: string;
  version: number;
  is_current: boolean;
  status: string;
  approval_status: string;
  model_data: any;
  assumptions: any;
  inputs: any;
  outputs: any;
  base_case: any;
  upside_case: any;
  downside_case: any;
  sensitivity_analysis: any;
  enterprise_value?: string;
  equity_value?: string;
  share_price?: string;
  valuation_multiple?: string;
  is_shared: boolean;
  access_level: string;
  collaborators: string[];
  tags: string[];
  notes?: string;
  organization_id: string;
  deal_id: string;
  created_by_id: string;
  parent_model_id?: string;
  created_at: string;
  updated_at: string;
  created_by?: any;
  deal?: any;
}

export interface ModelStatistics {
  total_models: number;
  active_models: number;
  models_in_review: number;
  draft_models: number;
  total_valuation?: string;
  avg_irr?: number;
  team_members?: number;
}

export interface UseFinancialModelsOptions {
  dealId?: string;
  modelType?: string;
  status?: string;
  autoFetch?: boolean;
}

export function useFinancialModels(options: UseFinancialModelsOptions = {}) {
  const [models, setModels] = useState<FinancialModel[]>([]);
  const [statistics, setStatistics] = useState<ModelStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchModels = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.getFinancialModels({
        deal_id: options.dealId,
        model_type: options.modelType,
        status: options.status,
        limit: 1000,
      });

      if (response.error) {
        throw new Error(response.error);
      }

      const modelsData = response.data || [];
      setModels(modelsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch financial models');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await apiClient.getModelStatistics();
      
      if (response.error) {
        throw new Error(response.error);
      }

      setStatistics(response.data);
    } catch (err) {
      console.error('Failed to fetch model statistics:', err);
    }
  };

  const createModel = async (modelData: {
    name: string;
    description?: string;
    model_type: string;
    deal_id?: string;
    model_data: any;
    assumptions?: any;
    inputs?: any;
  }) => {
    try {
      const response = await apiClient.createFinancialModel(modelData);
      
      if (response.error) {
        throw new Error(response.error);
      }

      // Refresh models after successful creation
      await fetchModels();
      await fetchStatistics();

      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to create financial model');
    }
  };

  const updateModel = async (modelId: string, updates: Partial<FinancialModel>) => {
    try {
      const response = await apiClient.updateFinancialModel(modelId, updates);
      
      if (response.error) {
        throw new Error(response.error);
      }

      // Update local state
      setModels(prev => 
        prev.map(model => 
          model.id === modelId ? { ...model, ...updates } : model
        )
      );

      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to update financial model');
    }
  };

  const deleteModel = async (modelId: string) => {
    try {
      const response = await apiClient.deleteFinancialModel(modelId);
      
      if (response.error) {
        throw new Error(response.error);
      }

      // Remove from local state
      setModels(prev => prev.filter(model => model.id !== modelId));
      await fetchStatistics();

      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to delete financial model');
    }
  };

  const createVersion = async (modelId: string, versionData: any) => {
    try {
      const response = await apiClient.createModelVersion(modelId, versionData);
      
      if (response.error) {
        throw new Error(response.error);
      }

      // Refresh models to get the new version
      await fetchModels();

      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to create model version');
    }
  };

  const getModelVersions = async (modelId: string) => {
    try {
      const response = await apiClient.getModelVersions(modelId);
      
      if (response.error) {
        throw new Error(response.error);
      }

      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to fetch model versions');
    }
  };

  // Helper functions for UI
  const getModelsByType = (type: string) => {
    return models.filter(model => model.model_type === type);
  };

  const getModelsByStatus = (status: string) => {
    return models.filter(model => model.status === status);
  };

  const getSharedModels = () => {
    return models.filter(model => model.is_shared);
  };

  const getRecentModels = (limit: number = 5) => {
    return [...models]
      .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
      .slice(0, limit);
  };

  const calculatePortfolioValue = () => {
    return models.reduce((total, model) => {
      if (model.enterprise_value) {
        const value = parseFloat(model.enterprise_value.replace(/[^0-9.-]+/g, ""));
        return total + (isNaN(value) ? 0 : value);
      }
      return total;
    }, 0);
  };

  const formatCurrency = (value: number): string => {
    if (value >= 1e9) {
      return `$${(value / 1e9).toFixed(1)}B`;
    } else if (value >= 1e6) {
      return `$${(value / 1e6).toFixed(1)}M`;
    } else if (value >= 1e3) {
      return `$${(value / 1e3).toFixed(1)}K`;
    }
    return `$${value.toFixed(0)}`;
  };

  // Auto-fetch on mount and when options change
  useEffect(() => {
    if (options.autoFetch !== false) {
      fetchModels();
      fetchStatistics();
    }
  }, [options.dealId, options.modelType, options.status]);

  return {
    models,
    statistics,
    loading,
    error,
    fetchModels,
    fetchStatistics,
    createModel,
    updateModel,
    deleteModel,
    createVersion,
    getModelVersions,
    // Helper functions
    getModelsByType,
    getModelsByStatus,
    getSharedModels,
    getRecentModels,
    calculatePortfolioValue,
    formatCurrency,
  };
}
