"use client";

import { useState, useEffect, useCallback, useMemo } from 'react';
import { apiClient } from '@/lib/api-client';

// Types for Prospect AI
export interface Prospect {
  id: string;
  company_name: string;
  industry: string;
  location: string;
  deal_size?: string;
  ai_score: number;
  confidence: string;
  last_activity: string;
  stage: string;
  description?: string;
  market_cap?: string;
  revenue?: string;
  employees?: string;
  risk_factors: string[];
  opportunities: string[];
  status: string;
  priority: string;
  assigned_to_id?: string;
  created_at: string;
  updated_at: string;
}

export interface ProspectAnalysisRequest {
  company_name: string;
  industry: string;
  location?: string;
  market_cap?: number;
  revenue?: number;
  employees?: number;
  financial_data?: Record<string, any>;
  business_model?: string;
  target_market?: string;
  competitive_landscape?: string;
}

export interface ProspectAnalysisResponse {
  ai_score: number;
  confidence_level: string;
  deal_probability: number;
  estimated_deal_size: string;
  risk_factors: string[];
  opportunities: string[];
  recommended_approach: string;
  analysis_details: {
    financial_health: number;
    market_position: number;
    growth_potential: number;
    strategic_fit: number;
  };
  processing_time: number;
}

export interface ProspectScoringRequest {
  prospects: Array<Record<string, any>>;
  scoring_criteria: {
    financial_weight: number;
    market_weight: number;
    strategic_weight: number;
    risk_weight: number;
  };
}

export interface MarketIntelligenceResponse {
  market_overview: {
    total_market_size: string;
    growth_rate: string;
    key_trends: string[];
    market_sentiment: string;
  };
  industry_trends: Array<{
    trend: string;
    impact: string;
    confidence: number;
  }>;
  recent_transactions: Array<{
    company: string;
    deal_size: string;
    deal_type: string;
    date: string;
    multiple: string;
  }>;
  market_alerts: Array<{
    type: string;
    message: string;
    severity: string;
    date: string;
  }>;
}

export interface ProspectStatistics {
  total_prospects: number;
  high_score_prospects: number;
  active_prospects: number;
  ai_accuracy: number;
  average_score: number;
  prospects_by_stage: Record<string, number>;
  prospects_by_industry: Record<string, number>;
  recent_activity_count: number;
}

export interface ProspectFilters {
  query?: string;
  industry?: string;
  location?: string;
  min_revenue?: number;
  max_revenue?: number;
  min_ai_score?: number;
  status?: string;
  stage?: string;
  priority?: string;
  assigned_to_id?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

interface UseProspectsOptions {
  autoFetch?: boolean;
  filters?: ProspectFilters;
  limit?: number;
  skip?: number;
}

interface UseProspectsReturn {
  prospects: Prospect[];
  statistics: ProspectStatistics | null;
  loading: boolean;
  error: string | null;
  total: number;
  hasMore: boolean;
  // Core functions
  fetchProspects: () => Promise<void>;
  fetchStatistics: () => Promise<void>;
  createProspect: (data: Omit<Prospect, 'id' | 'created_at' | 'updated_at'>) => Promise<Prospect>;
  updateProspect: (id: string, data: Partial<Prospect>) => Promise<Prospect>;
  deleteProspect: (id: string) => Promise<void>;
  // AI functions
  analyzeProspect: (request: ProspectAnalysisRequest) => Promise<ProspectAnalysisResponse>;
  scoreProspects: (request: ProspectScoringRequest) => Promise<any>;
  getMarketIntelligence: (params?: {
    industry?: string;
    region?: string;
    time_period?: string;
    deal_type?: string;
  }) => Promise<MarketIntelligenceResponse>;
  // Helper functions
  getProspectsByScore: (minScore: number) => Prospect[];
  getProspectsByStage: (stage: string) => Prospect[];
  getProspectsByIndustry: (industry: string) => Prospect[];
  getHighPriorityProspects: () => Prospect[];
  refreshData: () => Promise<void>;
}

export function useProspects(options: UseProspectsOptions = {}): UseProspectsReturn {
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [statistics, setStatistics] = useState<ProspectStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  const { autoFetch = true, filters = {}, limit = 50, skip = 0 } = options;

  const fetchProspects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.getProspects({
        ...filters,
        limit,
        skip
      });

      if (response.error) {
        setError(response.error);
        return;
      }

      const data = response.data || response;
      setProspects(data.prospects || []);
      setTotal(data.total || 0);
      setHasMore(data.has_more || false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch prospects');
    } finally {
      setLoading(false);
    }
  }, [filters, limit, skip]);

  const fetchStatistics = useCallback(async () => {
    try {
      const response = await apiClient.getProspectStatistics();
      
      if (response.error) {
        console.error('Failed to fetch prospect statistics:', response.error);
        return;
      }

      setStatistics(response.data || response);
    } catch (err) {
      console.error('Failed to fetch prospect statistics:', err);
    }
  }, []);

  const createProspect = async (data: Omit<Prospect, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const response = await apiClient.createProspect(data);
      
      if (response.error) {
        throw new Error(response.error);
      }

      await fetchProspects(); // Refresh list
      return response.data || response;
    } catch (err) {
      throw err;
    }
  };

  const updateProspect = async (id: string, data: Partial<Prospect>) => {
    try {
      const response = await apiClient.updateProspect(id, data);
      
      if (response.error) {
        throw new Error(response.error);
      }

      await fetchProspects(); // Refresh list
      return response.data || response;
    } catch (err) {
      throw err;
    }
  };

  const deleteProspect = async (id: string) => {
    try {
      const response = await apiClient.deleteProspect(id);
      
      if (response.error) {
        throw new Error(response.error);
      }

      await fetchProspects(); // Refresh list
    } catch (err) {
      throw err;
    }
  };

  const analyzeProspect = async (request: ProspectAnalysisRequest): Promise<ProspectAnalysisResponse> => {
    try {
      const response = await apiClient.analyzeProspect(request);
      
      if (response.error) {
        throw new Error(response.error);
      }

      return response.data || response;
    } catch (err) {
      throw err;
    }
  };

  const scoreProspects = async (request: ProspectScoringRequest) => {
    try {
      const response = await apiClient.scoreProspects(request);
      
      if (response.error) {
        throw new Error(response.error);
      }

      return response.data || response;
    } catch (err) {
      throw err;
    }
  };

  const getMarketIntelligence = async (params?: {
    industry?: string;
    region?: string;
    time_period?: string;
    deal_type?: string;
  }): Promise<MarketIntelligenceResponse> => {
    try {
      const response = await apiClient.getMarketIntelligence(params);
      
      if (response.error) {
        throw new Error(response.error);
      }

      return response.data || response;
    } catch (err) {
      throw err;
    }
  };

  // Helper functions
  const getProspectsByScore = useMemo(() => {
    return (minScore: number) => prospects.filter(p => p.ai_score >= minScore);
  }, [prospects]);

  const getProspectsByStage = useMemo(() => {
    return (stage: string) => prospects.filter(p => p.stage === stage);
  }, [prospects]);

  const getProspectsByIndustry = useMemo(() => {
    return (industry: string) => prospects.filter(p => p.industry === industry);
  }, [prospects]);

  const getHighPriorityProspects = useMemo(() => {
    return () => prospects.filter(p => p.priority === 'high' || p.ai_score >= 80);
  }, [prospects]);

  const refreshData = useCallback(async () => {
    await Promise.all([fetchProspects(), fetchStatistics()]);
  }, [fetchProspects, fetchStatistics]);

  // Auto-fetch on mount and when options change
  useEffect(() => {
    if (autoFetch) {
      fetchProspects();
      fetchStatistics();
    }
  }, [autoFetch, fetchProspects, fetchStatistics]);

  return {
    prospects,
    statistics,
    loading,
    error,
    total,
    hasMore,
    fetchProspects,
    fetchStatistics,
    createProspect,
    updateProspect,
    deleteProspect,
    analyzeProspect,
    scoreProspects,
    getMarketIntelligence,
    getProspectsByScore,
    getProspectsByStage,
    getProspectsByIndustry,
    getHighPriorityProspects,
    refreshData,
  };
}
