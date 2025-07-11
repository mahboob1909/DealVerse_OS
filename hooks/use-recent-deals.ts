import React from 'react';
import { useDeals, Deal } from './use-deals';

interface UseRecentDealsOptions {
  limit?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseRecentDealsReturn {
  deals: Deal[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useRecentDeals(options: UseRecentDealsOptions = {}): UseRecentDealsReturn {
  const {
    limit = 5,
    autoRefresh = false,
    refreshInterval = 30000, // 30 seconds
  } = options;

  const { deals, isLoading, error, refetch } = useDeals({
    limit,
  });

  // Auto-refresh functionality
  React.useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      refetch();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, refetch]);

  // Sort deals by creation date (most recent first)
  const sortedDeals = React.useMemo(() => {
    return [...deals].sort((a, b) => {
      if (!a.createdAt || !b.createdAt) return 0;
      return b.createdAt.getTime() - a.createdAt.getTime();
    });
  }, [deals]);

  return {
    deals: sortedDeals,
    isLoading,
    error,
    refetch,
  };
}

// Hook for deal statistics
export function useDealStats() {
  const { deals, isLoading } = useDeals();

  const stats = React.useMemo(() => {
    if (!deals.length) {
      return {
        total: 0,
        won: 0,
        lost: 0,
        active: 0,
        totalValue: 0,
        averageValue: 0,
        winRate: 0,
      };
    }

    const total = deals.length;
    const won = deals.filter(deal => deal.status === 'won').length;
    const lost = deals.filter(deal => deal.status === 'lost').length;
    const active = deals.filter(deal => 
      ['negotiation', 'proposal', 'follow-up'].includes(deal.status)
    ).length;

    const totalValue = deals.reduce((sum, deal) => sum + (deal.value || 0), 0);
    const averageValue = totalValue / total;
    const winRate = total > 0 ? (won / (won + lost)) * 100 : 0;

    return {
      total,
      won,
      lost,
      active,
      totalValue,
      averageValue,
      winRate,
    };
  }, [deals]);

  return {
    stats,
    isLoading,
  };
}
