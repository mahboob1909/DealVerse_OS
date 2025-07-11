import { useState, useEffect, useCallback } from 'react';

export interface Deal {
  id: string;
  clientName: string;
  projectTitle: string;
  status: "negotiation" | "proposal" | "follow-up" | "won" | "lost";
  avatarUrl?: string;
  fallbackInitials: string;
  createdAt?: Date;
  value?: number;
  description?: string;
  clientId?: string;
  organizationId?: string;
}

interface UseDealsOptions {
  limit?: number;
  status?: string;
  clientId?: string;
  organizationId?: string;
}

interface UseDealsReturn {
  deals: Deal[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  createDeal: (deal: Omit<Deal, 'id' | 'createdAt'>) => Promise<Deal>;
  updateDeal: (id: string, updates: Partial<Deal>) => Promise<Deal>;
  deleteDeal: (id: string) => Promise<void>;
}

// Mock API functions - replace with actual API calls
const mockApiDelay = (ms: number = 1000) => new Promise(resolve => setTimeout(resolve, ms));

const mockDeals: Deal[] = [
  {
    id: "1",
    clientName: "Acme Corp",
    projectTitle: "Website Redesign",
    status: "negotiation",
    avatarUrl: "/avatars/01.png",
    fallbackInitials: "AC",
    createdAt: new Date("2024-01-15"),
    value: 15000,
    description: "Complete website redesign with modern UI/UX",
    clientId: "client-1",
    organizationId: "org-1",
  },
  {
    id: "2",
    clientName: "TechTron Inc.",
    projectTitle: "Mobile App Development",
    status: "proposal",
    avatarUrl: "/avatars/02.png",
    fallbackInitials: "TT",
    createdAt: new Date("2024-01-10"),
    value: 25000,
    description: "Native mobile app for iOS and Android",
    clientId: "client-2",
    organizationId: "org-1",
  },
  {
    id: "3",
    clientName: "Global Solutions",
    projectTitle: "Consulting Services",
    status: "follow-up",
    avatarUrl: "/avatars/03.png",
    fallbackInitials: "GS",
    createdAt: new Date("2024-01-08"),
    value: 8000,
    description: "Business process optimization consulting",
    clientId: "client-3",
    organizationId: "org-1",
  },
  {
    id: "4",
    clientName: "StartupXYZ",
    projectTitle: "Brand Identity",
    status: "won",
    avatarUrl: "/avatars/04.png",
    fallbackInitials: "SX",
    createdAt: new Date("2024-01-05"),
    value: 12000,
    description: "Complete brand identity package",
    clientId: "client-4",
    organizationId: "org-1",
  },
  {
    id: "5",
    clientName: "Enterprise Co",
    projectTitle: "System Integration",
    status: "lost",
    avatarUrl: "/avatars/05.png",
    fallbackInitials: "EC",
    createdAt: new Date("2024-01-03"),
    value: 50000,
    description: "Legacy system integration project",
    clientId: "client-5",
    organizationId: "org-1",
  },
];

// Mock API functions
const fetchDeals = async (options: UseDealsOptions = {}): Promise<Deal[]> => {
  await mockApiDelay(800);
  
  let filteredDeals = [...mockDeals];
  
  if (options.status && options.status !== 'all') {
    filteredDeals = filteredDeals.filter(deal => deal.status === options.status);
  }
  
  if (options.clientId) {
    filteredDeals = filteredDeals.filter(deal => deal.clientId === options.clientId);
  }
  
  if (options.organizationId) {
    filteredDeals = filteredDeals.filter(deal => deal.organizationId === options.organizationId);
  }
  
  if (options.limit) {
    filteredDeals = filteredDeals.slice(0, options.limit);
  }
  
  return filteredDeals;
};

const createDealApi = async (dealData: Omit<Deal, 'id' | 'createdAt'>): Promise<Deal> => {
  await mockApiDelay(500);
  
  const newDeal: Deal = {
    ...dealData,
    id: `deal-${Date.now()}`,
    createdAt: new Date(),
  };
  
  mockDeals.unshift(newDeal);
  return newDeal;
};

const updateDealApi = async (id: string, updates: Partial<Deal>): Promise<Deal> => {
  await mockApiDelay(500);
  
  const dealIndex = mockDeals.findIndex(deal => deal.id === id);
  if (dealIndex === -1) {
    throw new Error('Deal not found');
  }
  
  mockDeals[dealIndex] = { ...mockDeals[dealIndex], ...updates };
  return mockDeals[dealIndex];
};

const deleteDealApi = async (id: string): Promise<void> => {
  await mockApiDelay(500);
  
  const dealIndex = mockDeals.findIndex(deal => deal.id === id);
  if (dealIndex === -1) {
    throw new Error('Deal not found');
  }
  
  mockDeals.splice(dealIndex, 1);
};

export function useDeals(options: UseDealsOptions = {}): UseDealsReturn {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await fetchDeals(options);
      setDeals(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, [options.limit, options.status, options.clientId, options.organizationId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const createDeal = useCallback(async (dealData: Omit<Deal, 'id' | 'createdAt'>) => {
    try {
      const newDeal = await createDealApi(dealData);
      setDeals(prev => [newDeal, ...prev]);
      return newDeal;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create deal');
      throw err;
    }
  }, []);

  const updateDeal = useCallback(async (id: string, updates: Partial<Deal>) => {
    try {
      const updatedDeal = await updateDealApi(id, updates);
      setDeals(prev => prev.map(deal => deal.id === id ? updatedDeal : deal));
      return updatedDeal;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update deal');
      throw err;
    }
  }, []);

  const deleteDeal = useCallback(async (id: string) => {
    try {
      await deleteDealApi(id);
      setDeals(prev => prev.filter(deal => deal.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete deal');
      throw err;
    }
  }, []);

  return {
    deals,
    isLoading,
    error,
    refetch: fetchData,
    createDeal,
    updateDeal,
    deleteDeal,
  };
}
