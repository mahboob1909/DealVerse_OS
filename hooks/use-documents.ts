"use client";

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';

export interface Document {
  id: string;
  title: string;
  filename: string;
  file_path: string;
  file_size: number;
  file_type: string;
  file_extension: string;
  document_type: string;
  category?: string;
  subcategory?: string;
  status: string;
  is_confidential: boolean;
  is_archived: boolean;
  version: string;
  is_latest_version: boolean;
  ai_analysis?: any;
  risk_score?: string;
  key_findings?: string[];
  extracted_data?: any;
  compliance_status: string;
  review_status: string;
  reviewer_notes?: string;
  description?: string;
  tags?: string[];
  keywords?: string[];
  access_level: string;
  allowed_roles?: string[];
  organization_id: string;
  deal_id?: string;
  client_id?: string;
  uploaded_by_id: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentTreeNode {
  id: string;
  name: string;
  type: 'folder' | 'file';
  progress?: number;
  totalFiles?: number;
  completedFiles?: number;
  status?: string;
  riskLevel?: string;
  size?: string;
  lastModified?: string;
  annotations?: number;
  children?: DocumentTreeNode[];
  document?: Document;
}

export interface UseDocumentsOptions {
  dealId?: string;
  documentType?: string;
  status?: string;
  autoFetch?: boolean;
}

export function useDocuments(options: UseDocumentsOptions = {}) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [documentTree, setDocumentTree] = useState<DocumentTreeNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.getDocuments({
        deal_id: options.dealId,
        document_type: options.documentType,
        status: options.status,
        limit: 1000, // Get all documents for tree structure
      });

      if (response.error) {
        throw new Error(response.error);
      }

      const docs = (response.data || []) as Document[];
      setDocuments(docs);
      
      // Transform documents into tree structure
      const tree = buildDocumentTree(docs);
      setDocumentTree(tree);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const uploadDocument = async (
    file: File,
    metadata: {
      title: string;
      document_type?: string;
      deal_id?: string;
      client_id?: string;
      is_confidential?: boolean;
    }
  ) => {
    const uploadId = `${file.name}-${Date.now()}`;
    setUploadProgress(prev => ({ ...prev, [uploadId]: 0 }));

    try {
      // Simulate upload progress (in real implementation, you'd track actual progress)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          const current = prev[uploadId] || 0;
          if (current >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return { ...prev, [uploadId]: current + 10 };
        });
      }, 200);

      const response = await apiClient.uploadDocument(file, metadata);

      clearInterval(progressInterval);
      setUploadProgress(prev => ({ ...prev, [uploadId]: 100 }));

      if (response.error) {
        throw new Error(response.error);
      }

      // Refresh documents after successful upload
      await fetchDocuments();

      // Clean up progress tracking
      setTimeout(() => {
        setUploadProgress(prev => {
          const { [uploadId]: _, ...rest } = prev;
          return rest;
        });
      }, 2000);

      return response.data;
    } catch (err) {
      setUploadProgress(prev => {
        const { [uploadId]: _, ...rest } = prev;
        return rest;
      });
      throw err;
    }
  };

  const analyzeDocument = async (documentId: string) => {
    try {
      const response = await apiClient.analyzeDocument(documentId);
      
      if (response.error) {
        throw new Error(response.error);
      }

      // Refresh documents to get updated analysis
      await fetchDocuments();
      
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to analyze document');
    }
  };

  const updateDocument = async (documentId: string, updates: Partial<Document>) => {
    try {
      const response = await apiClient.updateDocument(documentId, updates);
      
      if (response.error) {
        throw new Error(response.error);
      }

      // Update local state
      setDocuments(prev => 
        prev.map(doc => 
          doc.id === documentId ? { ...doc, ...updates } : doc
        )
      );

      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to update document');
    }
  };

  const deleteDocument = async (documentId: string) => {
    try {
      const response = await apiClient.deleteDocument(documentId);
      
      if (response.error) {
        throw new Error(response.error);
      }

      // Remove from local state
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
      
      // Rebuild tree
      const updatedDocs = documents.filter(doc => doc.id !== documentId);
      const tree = buildDocumentTree(updatedDocs);
      setDocumentTree(tree);

      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to delete document');
    }
  };

  // Build hierarchical tree structure from flat document list
  const buildDocumentTree = (docs: Document[]): DocumentTreeNode[] => {
    const folders: Record<string, DocumentTreeNode> = {};
    
    // Group documents by type/category
    docs.forEach(doc => {
      const folderKey = doc.document_type || 'General';
      
      if (!folders[folderKey]) {
        folders[folderKey] = {
          id: folderKey.toLowerCase().replace(/\s+/g, '-'),
          name: folderKey.charAt(0).toUpperCase() + folderKey.slice(1) + ' Documents',
          type: 'folder',
          children: [],
          totalFiles: 0,
          completedFiles: 0,
          progress: 0,
        };
      }

      const fileNode: DocumentTreeNode = {
        id: doc.id,
        name: doc.title,
        type: 'file',
        status: doc.status,
        riskLevel: doc.risk_score ? (
          parseInt(doc.risk_score) > 70 ? 'high' :
          parseInt(doc.risk_score) > 40 ? 'medium' : 'low'
        ) : 'low',
        size: formatFileSize(doc.file_size),
        lastModified: formatDate(doc.updated_at),
        annotations: doc.key_findings?.length || 0,
        document: doc,
      };

      folders[folderKey].children!.push(fileNode);
      folders[folderKey].totalFiles!++;
      
      if (doc.status === 'analyzed' || doc.status === 'approved') {
        folders[folderKey].completedFiles!++;
      }
    });

    // Calculate progress for each folder
    Object.values(folders).forEach(folder => {
      if (folder.totalFiles! > 0) {
        folder.progress = Math.round((folder.completedFiles! / folder.totalFiles!) * 100);
      }
    });

    return Object.values(folders);
  };

  // Helper functions
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  // Auto-fetch on mount and when options change
  useEffect(() => {
    if (options.autoFetch !== false) {
      fetchDocuments();
    }
  }, [options.dealId, options.documentType, options.status]);

  return {
    documents,
    documentTree,
    loading,
    error,
    uploadProgress,
    fetchDocuments,
    uploadDocument,
    analyzeDocument,
    updateDocument,
    deleteDocument,
  };
}
