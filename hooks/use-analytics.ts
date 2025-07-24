"use client";

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';

// Analytics interfaces
export interface DashboardAnalytics {
  deals: {
    total_deals: number;
    active_deals: number;
    won_deals: number;
    lost_deals: number;
    total_value: number;
    average_deal_size: number;
    conversion_rate: number;
    pipeline_value: number;
    deals_by_stage: Record<string, number>;
    deals_by_month: Array<{
      month: string;
      count: number;
      value: number;
      pipeline: number;
    }>;
  };
  clients: {
    total_clients: number;
    active_clients: number;
    prospects: number;
    conversion_rate: number;
    clients_by_industry: Record<string, number>;
    clients_by_source: Record<string, number>;
    clients_by_type: Record<string, number>;
    recent_clients: Array<{
      id: string;
      name: string;
      type: string;
      created_at: string;
    }>;
  };
  team: {
    total_users: number;
    active_users: number;
    roles: Record<string, number>;
  };
  recent_deals: Array<{
    id: string;
    client_name: string;
    project_title: string;
    status: string;
    value: number;
    created_at: string;
  }>;
}

export interface DealsPerformance {
  period_stats: {
    total_deals: number;
    won_deals: number;
    lost_deals: number;
    total_value: number;
    average_deal_size: number;
    conversion_rate: number;
  };
  trend_data: Array<{
    date: string;
    deals_count: number;
    deals_value: number;
    won_count: number;
    lost_count: number;
    pipeline_value: number;
  }>;
  stage_distribution: Array<{
    stage: string;
    count: number;
    value: number;
    percentage: number;
  }>;
  top_performers: Array<{
    user_id: string;
    user_name: string;
    deals_count: number;
    total_value: number;
  }>;
}

export interface ClientInsights {
  total_clients: number;
  client_acquisition: {
    prospects: number;
    active_clients: number;
    conversion_rate: number;
  };
  industry_breakdown: Record<string, number>;
  source_analysis: Record<string, number>;
  relationship_status: Record<string, number>;
  recent_activity: Array<{
    id: string;
    name: string;
    activity_type: string;
    date: string;
  }>;
  growth_trends: Array<{
    month: string;
    new_clients: number;
    total_clients: number;
    churn_rate: number;
  }>;
}

export interface TeamProductivity {
  team_size: number;
  active_members: number;
  role_distribution: Record<string, number>;
  recent_activity: Array<{
    user_id: string;
    user_name: string;
    activity_type: string;
    timestamp: string;
  }>;
  performance_indicators: {
    deals_per_user: number;
    clients_per_user: number;
    average_deal_value: number;
  };
  productivity_trends: Array<{
    month: string;
    active_users: number;
    deals_closed: number;
    revenue_generated: number;
  }>;
}

export interface ExecutiveSummary {
  overview: {
    total_revenue: number;
    total_deals: number;
    total_clients: number;
    team_size: number;
    growth_rate: number;
  };
  key_metrics: {
    monthly_recurring_revenue: number;
    customer_acquisition_cost: number;
    lifetime_value: number;
    churn_rate: number;
  };
  performance_highlights: Array<{
    metric: string;
    value: string;
    change: number;
    trend: 'up' | 'down' | 'stable';
  }>;
  recommendations: Array<{
    category: string;
    priority: 'high' | 'medium' | 'low';
    description: string;
    impact: string;
  }>;
}

export interface UseAnalyticsOptions {
  autoFetch?: boolean;
  refreshInterval?: number;
  enableRealTime?: boolean;
}

export interface UseAnalyticsReturn {
  // Data
  dashboardAnalytics: DashboardAnalytics | null;
  dealsPerformance: DealsPerformance | null;
  clientInsights: ClientInsights | null;
  teamProductivity: TeamProductivity | null;
  executiveSummary: ExecutiveSummary | null;
  
  // Loading states
  loading: boolean;
  dashboardLoading: boolean;
  dealsLoading: boolean;
  clientsLoading: boolean;
  teamLoading: boolean;
  executiveLoading: boolean;
  
  // Error states
  error: string | null;
  
  // Actions
  fetchDashboardAnalytics: () => Promise<void>;
  fetchDealsPerformance: (days?: number) => Promise<void>;
  fetchClientInsights: () => Promise<void>;
  fetchTeamProductivity: () => Promise<void>;
  fetchExecutiveSummary: () => Promise<void>;
  refreshAll: () => Promise<void>;
  
  // Utilities
  clearError: () => void;
  getRevenueGrowth: () => number;
  getConversionRate: () => number;
  getTopPerformers: () => Array<{ name: string; value: number }>;
  formatCurrency: (value: number) => string;
  formatPercentage: (value: number) => string;
}

export function useAnalytics(options: UseAnalyticsOptions = {}): UseAnalyticsReturn {
  const [dashboardAnalytics, setDashboardAnalytics] = useState<DashboardAnalytics | null>(null);
  const [dealsPerformance, setDealsPerformance] = useState<DealsPerformance | null>(null);
  const [clientInsights, setClientInsights] = useState<ClientInsights | null>(null);
  const [teamProductivity, setTeamProductivity] = useState<TeamProductivity | null>(null);
  const [executiveSummary, setExecutiveSummary] = useState<ExecutiveSummary | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [dealsLoading, setDealsLoading] = useState(false);
  const [clientsLoading, setClientsLoading] = useState(false);
  const [teamLoading, setTeamLoading] = useState(false);
  const [executiveLoading, setExecutiveLoading] = useState(false);
  
  const [error, setError] = useState<string | null>(null);

  // Fetch dashboard analytics
  const fetchDashboardAnalytics = useCallback(async () => {
    setDashboardLoading(true);
    setError(null);

    try {
      const response = await apiClient.getDashboardAnalytics();
      
      if (response.error) {
        throw new Error(response.error);
      }

      setDashboardAnalytics(response.data as DashboardAnalytics);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch dashboard analytics';
      setError(errorMessage);
      throw err;
    } finally {
      setDashboardLoading(false);
    }
  }, []);

  // Fetch deals performance
  const fetchDealsPerformance = useCallback(async (days: number = 30) => {
    setDealsLoading(true);
    setError(null);

    try {
      const response = await apiClient.getDealsPerformance(days);
      
      if (response.error) {
        throw new Error(response.error);
      }

      setDealsPerformance(response.data as DealsPerformance);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch deals performance';
      setError(errorMessage);
      throw err;
    } finally {
      setDealsLoading(false);
    }
  }, []);

  // Fetch client insights
  const fetchClientInsights = useCallback(async () => {
    setClientsLoading(true);
    setError(null);

    try {
      const response = await apiClient.getClientInsights();
      
      if (response.error) {
        throw new Error(response.error);
      }

      setClientInsights(response.data as ClientInsights);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch client insights';
      setError(errorMessage);
      throw err;
    } finally {
      setClientsLoading(false);
    }
  }, []);

  // Fetch team productivity
  const fetchTeamProductivity = useCallback(async () => {
    setTeamLoading(true);
    setError(null);

    try {
      const response = await apiClient.getTeamProductivity();
      
      if (response.error) {
        throw new Error(response.error);
      }

      setTeamProductivity(response.data as TeamProductivity);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch team productivity';
      setError(errorMessage);
      throw err;
    } finally {
      setTeamLoading(false);
    }
  }, []);

  // Fetch executive summary
  const fetchExecutiveSummary = useCallback(async () => {
    setExecutiveLoading(true);
    setError(null);

    try {
      const response = await apiClient.getExecutiveSummary();
      
      if (response.error) {
        throw new Error(response.error);
      }

      setExecutiveSummary(response.data as ExecutiveSummary);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch executive summary';
      setError(errorMessage);
      throw err;
    } finally {
      setExecutiveLoading(false);
    }
  }, []);

  // Refresh all analytics data
  const refreshAll = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchDashboardAnalytics(),
        fetchDealsPerformance(),
        fetchClientInsights(),
        fetchTeamProductivity(),
        fetchExecutiveSummary()
      ]);
    } finally {
      setLoading(false);
    }
  }, [fetchDashboardAnalytics, fetchDealsPerformance, fetchClientInsights, fetchTeamProductivity, fetchExecutiveSummary]);

  // Utility functions
  const clearError = useCallback(() => setError(null), []);

  const getRevenueGrowth = useCallback(() => {
    if (!dashboardAnalytics?.deals?.deals_by_month || dashboardAnalytics.deals.deals_by_month.length < 2) {
      return 0;
    }
    
    const months = dashboardAnalytics.deals.deals_by_month;
    const currentMonth = months[months.length - 1];
    const previousMonth = months[months.length - 2];
    
    if (previousMonth.value === 0) return 0;
    
    return ((currentMonth.value - previousMonth.value) / previousMonth.value) * 100;
  }, [dashboardAnalytics]);

  const getConversionRate = useCallback(() => {
    return dashboardAnalytics?.deals?.conversion_rate || 0;
  }, [dashboardAnalytics]);

  const getTopPerformers = useCallback(() => {
    if (!dealsPerformance?.top_performers) return [];
    
    return dealsPerformance.top_performers.map(performer => ({
      name: performer.user_name,
      value: performer.total_value
    }));
  }, [dealsPerformance]);

  const formatCurrency = useCallback((value: number): string => {
    if (value >= 1e9) {
      return `$${(value / 1e9).toFixed(1)}B`;
    } else if (value >= 1e6) {
      return `$${(value / 1e6).toFixed(1)}M`;
    } else if (value >= 1e3) {
      return `$${(value / 1e3).toFixed(1)}K`;
    }
    return `$${value.toFixed(0)}`;
  }, []);

  const formatPercentage = useCallback((value: number): string => {
    return `${value.toFixed(1)}%`;
  }, []);

  // Auto-fetch on mount
  useEffect(() => {
    if (options.autoFetch !== false) {
      refreshAll();
    }
  }, [refreshAll, options.autoFetch]);

  // Set up refresh interval
  useEffect(() => {
    if (options.refreshInterval && options.refreshInterval > 0) {
      const interval = setInterval(() => {
        refreshAll();
      }, options.refreshInterval);

      return () => clearInterval(interval);
    }
  }, [refreshAll, options.refreshInterval]);

  return {
    // Data
    dashboardAnalytics,
    dealsPerformance,
    clientInsights,
    teamProductivity,
    executiveSummary,
    
    // Loading states
    loading,
    dashboardLoading,
    dealsLoading,
    clientsLoading,
    teamLoading,
    executiveLoading,
    
    // Error states
    error,
    
    // Actions
    fetchDashboardAnalytics,
    fetchDealsPerformance,
    fetchClientInsights,
    fetchTeamProductivity,
    fetchExecutiveSummary,
    refreshAll,
    
    // Utilities
    clearError,
    getRevenueGrowth,
    getConversionRate,
    getTopPerformers,
    formatCurrency,
    formatPercentage,
  };
}
