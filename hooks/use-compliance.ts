"use client";

import { useState, useEffect, useCallback, useMemo } from 'react';
import { apiClient } from '@/lib/api-client';

// Types for Compliance Guardian
export interface ComplianceCategory {
  id: string;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  organization_id: string;
}

export interface ComplianceRequirement {
  id: string;
  title: string;
  description?: string;
  requirement_code?: string;
  is_mandatory: boolean;
  risk_level: string;
  required_documents: string[];
  evidence_requirements?: string;
  review_frequency_days: number;
  due_date?: string;
  last_review_date?: string;
  next_review_date?: string;
  status: string;
  completion_percentage: number;
  category_id: string;
  organization_id: string;
  created_at: string;
  updated_at: string;
}

export interface ComplianceAssessment {
  id: string;
  assessment_type: string;
  status: string;
  score?: number;
  findings?: string;
  recommendations?: string;
  risk_level: string;
  impact_assessment?: string;
  evidence_provided: string[];
  supporting_documents: string[];
  action_items: any[];
  remediation_plan?: string;
  category_id?: string;
  requirement_id?: string;
  organization_id: string;
  assessed_by_id: string;
  target_completion_date?: string;
  created_at: string;
  updated_at: string;
}

export interface RegulatoryUpdate {
  id: string;
  title: string;
  description?: string;
  regulation_type: string;
  impact_level: string;
  effective_date?: string;
  deadline?: string;
  source: string;
  content?: string;
  source_url?: string;
  document_references: string[];
  is_reviewed: boolean;
  review_notes?: string;
  reviewed_by_id?: string;
  reviewed_at?: string;
  organization_id: string;
  created_at: string;
  updated_at: string;
}

export interface ComplianceDashboardSummary {
  overall_score: number;
  total_requirements: number;
  completed_requirements: number;
  pending_requirements: number;
  overdue_requirements: number;
  upcoming_deadlines: Array<{
    requirement: string;
    deadline: string;
    status: string;
    priority: string;
  }>;
  compliance_categories: Array<{
    category: string;
    score: number;
    status: string;
    last_review: string;
    next_review: string;
  }>;
  recent_assessments: Array<{
    assessment_type: string;
    score: number;
    date: string;
    status: string;
  }>;
  regulatory_alerts: Array<{
    title: string;
    impact: string;
    deadline: string;
    status: string;
  }>;
}

export interface UseComplianceOptions {
  autoFetch?: boolean;
  filters?: {
    status?: string;
    category_id?: string;
    risk_level?: string;
    assessment_type?: string;
  };
  limit?: number;
}

export interface UseComplianceReturn {
  // Data
  dashboard: ComplianceDashboardSummary | null;
  categories: ComplianceCategory[];
  requirements: ComplianceRequirement[];
  assessments: ComplianceAssessment[];
  regulatoryUpdates: RegulatoryUpdate[];
  
  // Loading states
  loading: boolean;
  dashboardLoading: boolean;
  categoriesLoading: boolean;
  requirementsLoading: boolean;
  assessmentsLoading: boolean;
  updatesLoading: boolean;
  
  // Error states
  error: string | null;
  
  // Actions
  fetchDashboard: () => Promise<void>;
  fetchCategories: () => Promise<void>;
  fetchRequirements: () => Promise<void>;
  fetchAssessments: () => Promise<void>;
  fetchRegulatoryUpdates: () => Promise<void>;
  refreshAll: () => Promise<void>;
  
  // CRUD operations
  createCategory: (data: any) => Promise<ComplianceCategory>;
  updateCategory: (id: string, data: any) => Promise<ComplianceCategory>;
  deleteCategory: (id: string) => Promise<void>;
  
  createRequirement: (data: any) => Promise<ComplianceRequirement>;
  updateRequirement: (id: string, data: any) => Promise<ComplianceRequirement>;
  deleteRequirement: (id: string) => Promise<void>;
  
  createAssessment: (data: any) => Promise<ComplianceAssessment>;
  updateAssessment: (id: string, data: any) => Promise<ComplianceAssessment>;
  
  createRegulatoryUpdate: (data: any) => Promise<RegulatoryUpdate>;
  updateRegulatoryUpdate: (id: string, data: any) => Promise<RegulatoryUpdate>;
  markUpdateAsReviewed: (id: string, notes?: string) => Promise<void>;
  
  // Specialized operations
  getUpcomingReviews: (daysAhead?: number) => Promise<ComplianceRequirement[]>;
  generateAuditTrail: (params: any) => Promise<any>;
  runComplianceCheck: (categoryId?: string) => Promise<any>;
}

export function useCompliance(options: UseComplianceOptions = {}): UseComplianceReturn {
  const [dashboard, setDashboard] = useState<ComplianceDashboardSummary | null>(null);
  const [categories, setCategories] = useState<ComplianceCategory[]>([]);
  const [requirements, setRequirements] = useState<ComplianceRequirement[]>([]);
  const [assessments, setAssessments] = useState<ComplianceAssessment[]>([]);
  const [regulatoryUpdates, setRegulatoryUpdates] = useState<RegulatoryUpdate[]>([]);
  
  const [loading, setLoading] = useState(false);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [categoriesLoading, setCategoriesLoading] = useState(false);
  const [requirementsLoading, setRequirementsLoading] = useState(false);
  const [assessmentsLoading, setAssessmentsLoading] = useState(false);
  const [updatesLoading, setUpdatesLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch dashboard summary
  const fetchDashboard = useCallback(async () => {
    try {
      setDashboardLoading(true);
      setError(null);
      const response = await apiClient.getComplianceDashboard();
      if (response.error) {
        throw new Error(response.error);
      }
      setDashboard(response.data || response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch compliance dashboard');
    } finally {
      setDashboardLoading(false);
    }
  }, []);

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      setCategoriesLoading(true);
      setError(null);
      const response = await apiClient.getComplianceCategories();
      if (response.error) {
        throw new Error(response.error);
      }
      setCategories(response.data || response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch compliance categories');
    } finally {
      setCategoriesLoading(false);
    }
  }, []);

  // Fetch requirements
  const fetchRequirements = useCallback(async () => {
    try {
      setRequirementsLoading(true);
      setError(null);
      const params = {
        limit: options.limit || 100,
        ...options.filters
      };
      const response = await apiClient.getComplianceRequirements(params);
      if (response.error) {
        throw new Error(response.error);
      }
      setRequirements(response.data || response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch compliance requirements');
    } finally {
      setRequirementsLoading(false);
    }
  }, [options.filters, options.limit]);

  // Fetch assessments
  const fetchAssessments = useCallback(async () => {
    try {
      setAssessmentsLoading(true);
      setError(null);
      const params = {
        limit: options.limit || 100,
        assessment_type: options.filters?.assessment_type
      };
      const response = await apiClient.getComplianceAssessments(params);
      if (response.error) {
        throw new Error(response.error);
      }
      setAssessments(response.data || response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch compliance assessments');
    } finally {
      setAssessmentsLoading(false);
    }
  }, [options.filters?.assessment_type, options.limit]);

  // Fetch regulatory updates
  const fetchRegulatoryUpdates = useCallback(async () => {
    try {
      setUpdatesLoading(true);
      setError(null);
      const response = await apiClient.getRegulatoryUpdates();
      if (response.error) {
        throw new Error(response.error);
      }
      setRegulatoryUpdates(response.data || response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch regulatory updates');
    } finally {
      setUpdatesLoading(false);
    }
  }, []);

  // Refresh all data
  const refreshAll = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchDashboard(),
        fetchCategories(),
        fetchRequirements(),
        fetchAssessments(),
        fetchRegulatoryUpdates()
      ]);
    } finally {
      setLoading(false);
    }
  }, [fetchDashboard, fetchCategories, fetchRequirements, fetchAssessments, fetchRegulatoryUpdates]);

  // Auto-fetch on mount
  useEffect(() => {
    if (options.autoFetch !== false) {
      refreshAll();
    }
  }, [refreshAll, options.autoFetch]);

  // CRUD operations for categories
  const createCategory = async (data: any): Promise<ComplianceCategory> => {
    const response = await apiClient.createComplianceCategory(data);
    if (response.error) {
      throw new Error(response.error);
    }
    await fetchCategories(); // Refresh list
    return response.data || response;
  };

  const updateCategory = async (id: string, data: any): Promise<ComplianceCategory> => {
    const response = await apiClient.updateComplianceCategory(id, data);
    if (response.error) {
      throw new Error(response.error);
    }
    await fetchCategories(); // Refresh list
    return response.data || response;
  };

  const deleteCategory = async (id: string): Promise<void> => {
    const response = await apiClient.deleteComplianceCategory(id);
    if (response.error) {
      throw new Error(response.error);
    }
    await fetchCategories(); // Refresh list
  };

  return {
    // Data
    dashboard,
    categories,
    requirements,
    assessments,
    regulatoryUpdates,
    
    // Loading states
    loading,
    dashboardLoading,
    categoriesLoading,
    requirementsLoading,
    assessmentsLoading,
    updatesLoading,
    
    // Error states
    error,
    
    // Actions
    fetchDashboard,
    fetchCategories,
    fetchRequirements,
    fetchAssessments,
    fetchRegulatoryUpdates,
    refreshAll,
    
    // CRUD operations
    createCategory,
    updateCategory,
    deleteCategory,
    
    // CRUD operations for requirements
    createRequirement: async (data: any): Promise<ComplianceRequirement> => {
      const response = await apiClient.createComplianceRequirement(data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchRequirements(); // Refresh list
      return response.data || response;
    },

    updateRequirement: async (id: string, data: any): Promise<ComplianceRequirement> => {
      const response = await apiClient.updateComplianceRequirement(id, data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchRequirements(); // Refresh list
      return response.data || response;
    },

    deleteRequirement: async (id: string): Promise<void> => {
      const response = await apiClient.deleteComplianceRequirement(id);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchRequirements(); // Refresh list
    },

    // CRUD operations for assessments
    createAssessment: async (data: any): Promise<ComplianceAssessment> => {
      const response = await apiClient.createComplianceAssessment(data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchAssessments(); // Refresh list
      return response.data || response;
    },

    updateAssessment: async (id: string, data: any): Promise<ComplianceAssessment> => {
      const response = await apiClient.updateComplianceAssessment(id, data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchAssessments(); // Refresh list
      return response.data || response;
    },

    // CRUD operations for regulatory updates
    createRegulatoryUpdate: async (data: any): Promise<RegulatoryUpdate> => {
      const response = await apiClient.createRegulatoryUpdate(data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchRegulatoryUpdates(); // Refresh list
      return response.data || response;
    },

    updateRegulatoryUpdate: async (id: string, data: any): Promise<RegulatoryUpdate> => {
      const response = await apiClient.updateRegulatoryUpdate(id, data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchRegulatoryUpdates(); // Refresh list
      return response.data || response;
    },

    markUpdateAsReviewed: async (id: string, notes?: string): Promise<void> => {
      const response = await apiClient.markRegulatoryUpdateAsReviewed(id, notes);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchRegulatoryUpdates(); // Refresh list
    },

    // Specialized operations
    getUpcomingReviews: async (daysAhead: number = 30): Promise<ComplianceRequirement[]> => {
      const response = await apiClient.getUpcomingComplianceReviews({ days_ahead: daysAhead });
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data || response;
    },

    generateAuditTrail: async (params: any): Promise<any> => {
      const response = await apiClient.generateComplianceAuditTrail(params);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data || response;
    },

    runComplianceCheck: async (categoryId?: string): Promise<any> => {
      const response = await apiClient.runComplianceCheck(categoryId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data || response;
    },
  };
}
