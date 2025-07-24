/**
 * React hooks for PitchCraft Suite presentation management
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import { apiClient } from '@/lib/api-client';
import type {
  Presentation,
  PresentationSlide,
  PresentationTemplate,
  PresentationComment,
  PresentationCollaboration,
  CreatePresentationData,
  UpdatePresentationData,
  CreateSlideData,
  UpdateSlideData,
  CreateTemplateData,
  CreateCommentData,
  PresentationFilters,
  TemplateFilters,
  CommentFilters,
} from '@/lib/types/presentation';

// Presentations hook
export function usePresentations(filters?: PresentationFilters) {
  const [presentations, setPresentations] = useState<Presentation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Memoize filters to prevent unnecessary re-renders
  const memoizedFilters = useMemo(() => filters, [
    filters?.status,
    filters?.presentation_type,
    filters?.limit,
    filters?.skip
  ]);

  const fetchPresentations = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getPresentations(memoizedFilters);

      if (response.error) {
        // Check if it's a connection error and provide fallback
        if (response.error.includes('fetch') || response.error.includes('Failed to fetch')) {
          setError('Unable to connect to server. Please check your connection and try again.');
        } else {
          setError(response.error);
        }
        setPresentations([]);
      } else {
        setPresentations(Array.isArray(response) ? response as Presentation[] : (response.data || []) as Presentation[]);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch presentations';
      if (errorMessage.includes('fetch') || errorMessage.includes('NetworkError')) {
        setError('Unable to connect to server. Please check your connection and try again.');
      } else {
        setError(errorMessage);
      }
      setPresentations([]);
    } finally {
      setLoading(false);
    }
  }, [memoizedFilters]);

  useEffect(() => {
    // Debounce the fetch to prevent rapid API calls
    const timeoutId = setTimeout(() => {
      fetchPresentations();
    }, 100);

    return () => clearTimeout(timeoutId);
  }, [fetchPresentations]);

  const createPresentation = async (data: CreatePresentationData) => {
    try {
      const response = await apiClient.createPresentation(data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchPresentations(); // Refresh list
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  const updatePresentation = async (id: string, data: UpdatePresentationData) => {
    try {
      const response = await apiClient.updatePresentation(id, data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchPresentations(); // Refresh list
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  const deletePresentation = async (id: string) => {
    try {
      const response = await apiClient.deletePresentation(id);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchPresentations(); // Refresh list
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  const createVersion = async (id: string) => {
    try {
      const response = await apiClient.createPresentationVersion(id);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchPresentations(); // Refresh list
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  return {
    presentations,
    loading,
    error,
    refetch: fetchPresentations,
    createPresentation,
    updatePresentation,
    deletePresentation,
    createVersion,
  };
}

// Single presentation hook
export function usePresentation(id: string) {
  const [presentation, setPresentation] = useState<Presentation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPresentation = useCallback(async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getPresentation(id);
      
      if (response.error) {
        setError(response.error);
        setPresentation(null);
      } else {
        setPresentation((response.data || response || null) as Presentation | null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch presentation');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchPresentation();
  }, [fetchPresentation]);

  return {
    presentation,
    loading,
    error,
    refetch: fetchPresentation,
  };
}

// Presentation slides hook
export function usePresentationSlides(presentationId: string) {
  const [slides, setSlides] = useState<PresentationSlide[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSlides = useCallback(async () => {
    if (!presentationId) return;
    
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getPresentationSlides(presentationId);
      
      if (response.error) {
        setError(response.error);
        setSlides([]);
      } else {
        setSlides(Array.isArray(response) ? response as PresentationSlide[] : (response.data || []) as PresentationSlide[]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch slides');
    } finally {
      setLoading(false);
    }
  }, [presentationId]);

  useEffect(() => {
    fetchSlides();
  }, [fetchSlides]);

  const createSlide = async (data: CreateSlideData) => {
    try {
      const response = await apiClient.createSlide(presentationId, data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchSlides(); // Refresh list
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  const updateSlide = async (slideId: string, data: UpdateSlideData) => {
    try {
      const response = await apiClient.updateSlide(presentationId, slideId, data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchSlides(); // Refresh list
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  const deleteSlide = async (slideId: string) => {
    try {
      const response = await apiClient.deleteSlide(presentationId, slideId);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchSlides(); // Refresh list
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  const duplicateSlide = async (slideId: string, newSlideNumber: number) => {
    try {
      const response = await apiClient.duplicateSlide(presentationId, slideId, newSlideNumber);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchSlides(); // Refresh list
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  return {
    slides,
    loading,
    error,
    refetch: fetchSlides,
    createSlide,
    updateSlide,
    deleteSlide,
    duplicateSlide,
  };
}

// Presentation templates hook
export function usePresentationTemplates(filters?: TemplateFilters) {
  const [templates, setTemplates] = useState<PresentationTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Memoize filters to prevent unnecessary re-renders
  const memoizedFilters = useMemo(() => filters || {}, [
    filters?.public_only,
    filters?.category,
    filters?.limit,
    filters?.skip
  ]);

  const fetchTemplates = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getPresentationTemplates(memoizedFilters);

      if (response.error) {
        // Check if it's a connection error and provide fallback
        if (response.error.includes('fetch') || response.error.includes('Failed to fetch')) {
          setError('Unable to connect to server. Please check your connection and try again.');
        } else {
          setError(response.error);
        }
        setTemplates([]);
      } else {
        setTemplates(Array.isArray(response) ? response as PresentationTemplate[] : (response.data || []) as PresentationTemplate[]);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch templates';
      if (errorMessage.includes('fetch') || errorMessage.includes('NetworkError')) {
        setError('Unable to connect to server. Please check your connection and try again.');
      } else {
        setError(errorMessage);
      }
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  }, [memoizedFilters]);

  useEffect(() => {
    // Debounce the fetch to prevent rapid API calls
    const timeoutId = setTimeout(() => {
      fetchTemplates();
    }, 100);

    return () => clearTimeout(timeoutId);
  }, [fetchTemplates]);

  const createTemplate = async (data: CreateTemplateData) => {
    try {
      const response = await apiClient.createPresentationTemplate(data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchTemplates(); // Refresh list
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  const createFromTemplate = async (templateId: string, presentationData: any) => {
    try {
      const response = await apiClient.createPresentationFromTemplate(templateId, presentationData);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  return {
    templates,
    loading,
    error,
    refetch: fetchTemplates,
    createTemplate,
    createFromTemplate,
  };
}

// Presentation comments hook
export function usePresentationComments(presentationId: string, filters?: CommentFilters) {
  const [comments, setComments] = useState<PresentationComment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchComments = useCallback(async () => {
    if (!presentationId) return;
    
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getPresentationComments(presentationId, filters);
      
      if (response.error) {
        setError(response.error);
        setComments([]);
      } else {
        setComments(Array.isArray(response) ? response as PresentationComment[] : (response.data || []) as PresentationComment[]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch comments');
    } finally {
      setLoading(false);
    }
  }, [presentationId, filters]);

  useEffect(() => {
    fetchComments();
  }, [fetchComments]);

  const createComment = async (data: CreateCommentData) => {
    try {
      const response = await apiClient.createPresentationComment(presentationId, data);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchComments(); // Refresh list
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  const resolveComment = async (commentId: string) => {
    try {
      const response = await apiClient.resolvePresentationComment(presentationId, commentId);
      if (response.error) {
        throw new Error(response.error);
      }
      await fetchComments(); // Refresh list
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  return {
    comments,
    loading,
    error,
    refetch: fetchComments,
    createComment,
    resolveComment,
  };
}
