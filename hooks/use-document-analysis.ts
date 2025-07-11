"use client";

import { useState, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';

export interface DocumentAnalysisResult {
  id: string;
  document_id: string;
  analysis_type: string;
  status: string;
  confidence_score: number;
  executive_summary: string;
  key_findings: string[];
  financial_analysis?: {
    revenue_trends?: any;
    profitability_metrics?: any;
    liquidity_ratios?: any;
    debt_analysis?: any;
  };
  risk_assessment: {
    overall_risk_score: number;
    risk_factors: Array<{
      category: string;
      severity: string;
      description: string;
      confidence: number;
    }>;
  };
  entity_extraction: {
    companies: string[];
    people: string[];
    dates: string[];
    amounts: string[];
    locations: string[];
  };
  compliance_notes: string[];
  recommendations: string[];
  created_at: string;
  updated_at: string;
}

export interface RiskAssessment {
  id: string;
  assessment_type: string;
  document_ids: string[];
  overall_risk_score: number;
  risk_categories: Array<{
    category: string;
    score: number;
    findings: string[];
  }>;
  recommendations: string[];
  created_at: string;
}

export interface DocumentAnalytics {
  total_documents: number;
  analyzed_documents: number;
  pending_analysis: number;
  high_risk_documents: number;
  average_risk_score: number;
  analysis_completion_rate: number;
  risk_distribution: {
    low: number;
    medium: number;
    high: number;
  };
  recent_analyses: Array<{
    document_id: string;
    document_title: string;
    analysis_date: string;
    risk_score: number;
  }>;
}

export function useDocumentAnalysis() {
  const [analysisResults, setAnalysisResults] = useState<Record<string, DocumentAnalysisResult>>({});
  const [riskAssessments, setRiskAssessments] = useState<RiskAssessment[]>([]);
  const [analytics, setAnalytics] = useState<DocumentAnalytics | null>(null);
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);

  const analyzeDocument = useCallback(async (
    documentId: string, 
    analysisType: string = 'full',
    focusAreas: string[] = ['financial', 'legal', 'risk']
  ) => {
    setLoading(prev => ({ ...prev, [`analyze_${documentId}`]: true }));
    setError(null);

    try {
      const response = await apiClient.analyzeDocument(documentId, analysisType, focusAreas);
      
      if (response.error) {
        throw new Error(response.error);
      }

      // Poll for analysis completion
      const pollForResult = async (): Promise<DocumentAnalysisResult> => {
        const resultResponse = await apiClient.getDocumentAnalysis(documentId);
        
        if (resultResponse.error) {
          throw new Error(resultResponse.error);
        }

        const result = resultResponse.data;
        
        if (result.status === 'completed') {
          return result;
        } else if (result.status === 'failed') {
          throw new Error('Analysis failed');
        }

        // Wait 2 seconds before polling again
        await new Promise(resolve => setTimeout(resolve, 2000));
        return pollForResult();
      };

      const result = await pollForResult();
      
      setAnalysisResults(prev => ({
        ...prev,
        [documentId]: result
      }));

      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, [`analyze_${documentId}`]: false }));
    }
  }, []);

  const getDocumentAnalysis = useCallback(async (documentId: string) => {
    setLoading(prev => ({ ...prev, [`get_${documentId}`]: true }));
    setError(null);

    try {
      const response = await apiClient.getDocumentAnalysis(documentId);
      
      if (response.error) {
        throw new Error(response.error);
      }

      const result = response.data;
      setAnalysisResults(prev => ({
        ...prev,
        [documentId]: result
      }));

      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get analysis';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, [`get_${documentId}`]: false }));
    }
  }, []);

  const assessRisk = useCallback(async (
    documentIds: string[],
    assessmentType: string = 'comprehensive'
  ) => {
    setLoading(prev => ({ ...prev, 'risk_assessment': true }));
    setError(null);

    try {
      const response = await apiClient.assessDocumentRisk(documentIds, assessmentType);
      
      if (response.error) {
        throw new Error(response.error);
      }

      const assessment = response.data;
      setRiskAssessments(prev => [assessment, ...prev]);

      return assessment;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Risk assessment failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, 'risk_assessment': false }));
    }
  }, []);

  const fetchAnalytics = useCallback(async () => {
    setLoading(prev => ({ ...prev, 'analytics': true }));
    setError(null);

    try {
      const response = await apiClient.getDocumentAnalytics();
      
      if (response.error) {
        throw new Error(response.error);
      }

      setAnalytics(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch analytics';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, 'analytics': false }));
    }
  }, []);

  const fetchRiskAssessments = useCallback(async (params?: { skip?: number; limit?: number }) => {
    setLoading(prev => ({ ...prev, 'risk_assessments': true }));
    setError(null);

    try {
      const response = await apiClient.getRiskAssessments(params);
      
      if (response.error) {
        throw new Error(response.error);
      }

      setRiskAssessments(response.data || []);
      return response.data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch risk assessments';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, 'risk_assessments': false }));
    }
  }, []);

  const categorizeDocument = useCallback(async (documentId: string) => {
    setLoading(prev => ({ ...prev, [`categorize_${documentId}`]: true }));
    setError(null);

    try {
      const response = await apiClient.categorizeDocument(documentId);
      
      if (response.error) {
        throw new Error(response.error);
      }

      return response.data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Categorization failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, [`categorize_${documentId}`]: false }));
    }
  }, []);

  const getHighRiskDocuments = useCallback(async (params?: { 
    skip?: number; 
    limit?: number; 
    risk_threshold?: number 
  }) => {
    setLoading(prev => ({ ...prev, 'high_risk': true }));
    setError(null);

    try {
      const response = await apiClient.getHighRiskDocuments(params);
      
      if (response.error) {
        throw new Error(response.error);
      }

      return response.data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch high-risk documents';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, 'high_risk': false }));
    }
  }, []);

  return {
    // State
    analysisResults,
    riskAssessments,
    analytics,
    loading,
    error,
    
    // Actions
    analyzeDocument,
    getDocumentAnalysis,
    assessRisk,
    fetchAnalytics,
    fetchRiskAssessments,
    categorizeDocument,
    getHighRiskDocuments,
    
    // Utilities
    clearError: () => setError(null),
    isAnalyzing: (documentId: string) => loading[`analyze_${documentId}`] || false,
    hasAnalysis: (documentId: string) => !!analysisResults[documentId],
    getAnalysisForDocument: (documentId: string) => analysisResults[documentId] || null,
  };
}
