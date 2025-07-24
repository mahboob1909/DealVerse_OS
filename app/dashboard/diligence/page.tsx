"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Search,
  FileText,
  FolderOpen,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  Download,
  Upload,
  Shield,
  AlertCircle,
  TrendingUp,
  FileCheck,
  XCircle,
  Loader2,
  RefreshCw,
  Plus,
  Filter,
  BarChart3,
  Brain
} from "lucide-react";
import { useState, useRef, useEffect, useCallback } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";
import { useDocuments, type Document, type DocumentTreeNode } from "@/hooks/use-documents";
import { useAuth } from "@/lib/auth-context";
import { DocumentPreview } from "@/components/dashboard/document-preview";
import { AIDocumentAnalysis } from "@/components/dashboard/ai-document-analysis";
import { useDocumentAnalysis, type DocumentAnalytics, type RiskAssessment } from "@/hooks/use-document-analysis";
import { useToast } from "@/hooks/use-toast";

// Document categories for organization
const DOCUMENT_CATEGORIES = [
  { id: 'financial', name: 'Financial Documents', icon: TrendingUp },
  { id: 'legal', name: 'Legal Documents', icon: Shield },
  { id: 'operational', name: 'Operational Documents', icon: FileCheck },
  { id: 'compliance', name: 'Compliance Documents', icon: CheckCircle },
  { id: 'other', name: 'Other Documents', icon: FileText }
];

// Risk level configurations
const RISK_LEVELS = {
  low: { color: 'text-green-600 bg-green-50 border-green-200', label: 'Low Risk' },
  medium: { color: 'text-yellow-600 bg-yellow-50 border-yellow-200', label: 'Medium Risk' },
  high: { color: 'text-red-600 bg-red-50 border-red-200', label: 'High Risk' }
};

// Status configurations
const STATUS_CONFIG = {
  pending: { color: 'text-gray-600 bg-gray-50 border-gray-200', label: 'Pending', icon: Clock },
  analyzing: { color: 'text-blue-600 bg-blue-50 border-blue-200', label: 'Analyzing', icon: Brain },
  completed: { color: 'text-green-600 bg-green-50 border-green-200', label: 'Completed', icon: CheckCircle },
  failed: { color: 'text-red-600 bg-red-50 border-red-200', label: 'Failed', icon: XCircle },
  review: { color: 'text-yellow-600 bg-yellow-50 border-yellow-200', label: 'Review Required', icon: AlertTriangle }
};
export default function DiligenceNavigatorPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const {
    documents,
    loading: documentsLoading,
    error: documentsError,
    fetchDocuments,
    uploadDocument,
    deleteDocument
  } = useDocuments();

  const {
    analytics,
    riskAssessments,
    loading: analysisLoading,
    error: analysisError,
    fetchAnalytics,
    fetchRiskAssessments,
    assessRisk,
    getHighRiskDocuments,
    clearError
  } = useDocumentAnalysis();

  // Local state
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [highRiskDocs, setHighRiskDocs] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load high-risk documents
  const loadHighRiskDocuments = useCallback(async () => {
    try {
      // Filter documents with high risk scores
      const highRisk = documents.filter(doc => {
        const riskScore = parseInt(doc.risk_score || '0');
        return riskScore >= 70;
      });
      setHighRiskDocs(highRisk || []);
    } catch (error) {
      console.error('Failed to load high-risk documents:', error);
    }
  }, [documents]);

  // Load data on component mount
  useEffect(() => {
    if (user?.organization_id) {
      fetchDocuments();
      fetchAnalytics();
      fetchRiskAssessments();
      loadHighRiskDocuments();
    }
  }, [user?.organization_id, fetchDocuments, fetchAnalytics, fetchRiskAssessments, loadHighRiskDocuments]);

  // Mock statistics
  const stats = {
    documentsReviewed: documents.filter(doc => doc.review_status === 'completed').length,
    totalDocuments: documents.length,
    riskFlags: documents.filter(doc => parseInt(doc.risk_score || '0') >= 70).length,
    missingDocs: 3, // Mock value
    completionPercentage: documents.length > 0 ? Math.round((documents.filter(doc => doc.review_status === 'completed').length / documents.length) * 100) : 0
  };

  // Filter documents based on search and category
  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Group documents by category
  const documentsByCategory = DOCUMENT_CATEGORIES.reduce((acc, category) => {
    acc[category.id] = filteredDocuments.filter(doc =>
      doc.category === category.id || (category.id === 'other' && !doc.category)
    );
    return acc;
  }, {} as Record<string, Document[]>);

  // Handle file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    try {
      for (const file of Array.from(files)) {
        await uploadDocument(file, {
          title: file.name,
          document_type: selectedCategory !== 'all' ? selectedCategory : 'other',
          is_confidential: false
        });
      }

      // Refresh data after upload
      fetchDocuments();
      fetchAnalytics();

      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      toast({
        title: "Upload Successful",
        description: `${files.length} document(s) uploaded successfully`,
      });
    } catch (error) {
      console.error('Upload failed:', error);
      toast({
        title: "Upload Failed",
        description: "Failed to upload documents. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsUploading(false);
    }
  };

  // Handle document selection
  const handleDocumentSelect = (document: Document) => {
    setSelectedDocument(document);
  };

  // Handle document deletion
  const handleDocumentDelete = async (documentId: string) => {
    try {
      await deleteDocument(documentId);
      fetchDocuments();
      fetchAnalytics();

      // Clear selection if deleted document was selected
      if (selectedDocument?.id === documentId) {
        setSelectedDocument(null);
      }
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  // Get risk level for document
  const getDocumentRiskLevel = (document: Document): 'low' | 'medium' | 'high' => {
    // This would typically come from analysis results
    // For now, use a simple heuristic based on document type
    if (document.category === 'legal' || document.title.toLowerCase().includes('litigation')) {
      return 'high';
    }
    if (document.category === 'compliance' || document.title.toLowerCase().includes('contract')) {
      return 'medium';
    }
    return 'low';
  };

  // Get document status
  const getDocumentStatus = (document: Document): keyof typeof STATUS_CONFIG => {
    // This would typically come from analysis results
    // For now, use review_status or default to pending
    return (document.review_status as keyof typeof STATUS_CONFIG) || 'pending';
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Format date
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
  // Component render starts here
  if (documentsLoading && documents.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-dealverse-blue mx-auto mb-4" />
          <p className="text-dealverse-medium-gray">Loading documents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-dealverse-navy">Diligence Navigator</h1>
          <p className="text-dealverse-medium-gray">AI-powered document analysis and risk assessment</p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={() => fileInputRef.current?.click()}
            className="bg-dealverse-blue hover:bg-dealverse-blue/90"
          >
            <Upload className="h-4 w-4 mr-2" />
            Upload Documents
          </Button>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.xls,.xlsx,.txt"
            onChange={handleFileUpload}
            className="hidden"
          />

          <Button
            variant="outline"
            onClick={() => {
              fetchDocuments();
              fetchAnalytics();
            }}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {(documentsError || analysisError) && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {documentsError || analysisError}
            <Button
              variant="ghost"
              size="sm"
              onClick={clearError}
              className="ml-2"
            >
              Dismiss
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Analytics Overview */}
      {analytics && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-dealverse-medium-gray">Total Documents</p>
                  <p className="text-2xl font-bold text-dealverse-navy">{analytics.total_documents}</p>
                </div>
                <FileText className="h-8 w-8 text-dealverse-blue" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-dealverse-medium-gray">Analyzed</p>
                  <p className="text-2xl font-bold text-dealverse-navy">{analytics.analyzed_documents}</p>
                </div>
                <Brain className="h-8 w-8 text-dealverse-green" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-dealverse-medium-gray">High Risk</p>
                  <p className="text-2xl font-bold text-dealverse-navy">{analytics.high_risk_documents}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-dealverse-medium-gray">Avg Risk Score</p>
                  <p className="text-2xl font-bold text-dealverse-navy">{analytics.average_risk_score.toFixed(1)}</p>
                </div>
                <BarChart3 className="h-8 w-8 text-dealverse-blue" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-dealverse-medium-gray" />
            <Input
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <div className="flex gap-2">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-dealverse-blue"
          >
            <option value="all">All Categories</option>
            {DOCUMENT_CATEGORIES.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setViewMode(viewMode === 'list' ? 'grid' : 'list')}
          >
            {viewMode === 'list' ? 'Grid View' : 'List View'}
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Document Repository */}
        <div className="lg:col-span-1 space-y-6">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-dealverse-navy">Document Repository</CardTitle>
              <CardDescription className="text-dealverse-medium-gray">
                Organized by category with AI analysis status
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {DOCUMENT_CATEGORIES.map(category => {
                const categoryDocs = documentsByCategory[category.id] || [];
                const Icon = category.icon;

                if (categoryDocs.length === 0 && selectedCategory !== 'all' && selectedCategory !== category.id) {
                  return null;
                }

                return (
                  <div key={category.id} className="space-y-2">
                    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Icon className="h-4 w-4 text-dealverse-blue" />
                        <span className="font-medium text-dealverse-navy">{category.name}</span>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {categoryDocs.length}
                      </Badge>
                    </div>

                    {categoryDocs.length > 0 && (
                      <div className="space-y-1 ml-6">
                        {categoryDocs.map(document => {
                          const status = getDocumentStatus(document);
                          const riskLevel = getDocumentRiskLevel(document);
                          const statusConfig = STATUS_CONFIG[status];
                          const riskConfig = RISK_LEVELS[riskLevel];

                          return (
                            <div
                              key={document.id}
                              onClick={() => handleDocumentSelect(document)}
                              className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                                selectedDocument?.id === document.id
                                  ? 'border-dealverse-blue bg-dealverse-blue/5'
                                  : 'border-gray-200 hover:border-gray-300'
                              }`}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                  <p className="font-medium text-sm text-dealverse-navy truncate">
                                    {document.title}
                                  </p>
                                  <div className="flex items-center gap-2 mt-1">
                                    <Badge className={`text-xs ${statusConfig.color}`}>
                                      {statusConfig.label}
                                    </Badge>
                                    <Badge className={`text-xs ${riskConfig.color}`}>
                                      {riskConfig.label}
                                    </Badge>
                                  </div>
                                  <p className="text-xs text-dealverse-medium-gray mt-1">
                                    {document.file_size ? formatFileSize(document.file_size) : 'Unknown size'} • {formatDate(document.created_at)}
                                  </p>
                                </div>

                                <div className="flex items-center gap-1 ml-2">
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleDocumentDelete(document.id);
                                    }}
                                  >
                                    <XCircle className="h-4 w-4 text-red-600" />
                                  </Button>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {categoryDocs.length === 0 && selectedCategory === category.id && (
                      <p className="text-sm text-dealverse-medium-gray ml-6 py-2">
                        No documents in this category
                      </p>
                    )}
                  </div>
                );
              })}

              {filteredDocuments.length === 0 && searchQuery && (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-dealverse-medium-gray mx-auto mb-4" />
                  <p className="text-dealverse-medium-gray">No documents found matching "{searchQuery}"</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
        {/* Document Analysis Panel */}
        <div className="lg:col-span-2 space-y-6">
          {selectedDocument ? (
            <AIDocumentAnalysis
              document={selectedDocument}
              onAnalysisComplete={(result) => {
                // Update document status and refresh data
                console.log('Analysis completed:', result);
                // Optionally refresh documents list
                fetchDocuments();
                fetchAnalytics();
              }}
            />
          ) : (
            <Card className="border-0 shadow-lg">
              <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                <FileText className="h-12 w-12 text-dealverse-medium-gray mb-4" />
                <h3 className="text-lg font-semibold text-dealverse-navy mb-2">
                  Select a Document
                </h3>
                <p className="text-dealverse-medium-gray">
                  Choose a document from the repository to view AI-powered analysis and insights.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Risk Assessment & Analytics */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Risk Assessment */}
        <Card className="border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-dealverse-navy flex items-center gap-2">
              <Shield className="h-5 w-5 text-red-600" />
              Risk Assessment
            </CardTitle>
            <CardDescription className="text-dealverse-medium-gray">
              AI-powered risk analysis across all documents
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {analysisLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-6 w-6 animate-spin text-dealverse-blue" />
              </div>
            ) : riskAssessments.length > 0 ? (
              riskAssessments.slice(0, 3).map((assessment, index) => (
                <div key={assessment.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h5 className="font-medium text-dealverse-navy">
                      {assessment.assessment_type.charAt(0).toUpperCase() + assessment.assessment_type.slice(1)} Assessment
                    </h5>
                    <Badge
                      className={`${
                        assessment.overall_risk_score > 70 ? 'text-red-600 bg-red-50 border-red-200' :
                        assessment.overall_risk_score > 40 ? 'text-yellow-600 bg-yellow-50 border-yellow-200' :
                        'text-green-600 bg-green-50 border-green-200'
                      } border-current`}
                      variant="outline"
                    >
                      {assessment.overall_risk_score > 70 ? 'High' :
                       assessment.overall_risk_score > 40 ? 'Medium' : 'Low'} Risk
                    </Badge>
                  </div>
                  <Progress value={assessment.overall_risk_score} className="h-2" />
                  <div className="space-y-1">
                    {assessment.risk_categories.slice(0, 2).map((category, categoryIndex) => (
                      <div key={categoryIndex} className="flex items-start text-xs">
                        <AlertCircle className="h-3 w-3 text-dealverse-coral mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-dealverse-medium-gray">
                          {category.category}: {category.score}/100
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Shield className="h-12 w-12 text-dealverse-medium-gray mx-auto mb-4" />
                <p className="text-dealverse-medium-gray">No risk assessments available</p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  onClick={() => assessRisk(documents.map(d => d.id))}
                  disabled={documents.length === 0}
                >
                  Run Risk Assessment
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* High-Risk Documents */}
        <Card className="border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-dealverse-navy flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              High-Risk Documents
            </CardTitle>
            <CardDescription className="text-dealverse-medium-gray">
              Documents requiring immediate attention
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {highRiskDocs.length > 0 ? (
              highRiskDocs.slice(0, 5).map((document) => (
                <div
                  key={document.id}
                  onClick={() => handleDocumentSelect(document)}
                  className="p-3 border border-red-200 rounded-lg cursor-pointer hover:bg-red-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm text-dealverse-navy truncate">
                        {document.title}
                      </p>
                      <p className="text-xs text-dealverse-medium-gray">
                        {document.category} • {formatDate(document.created_at)}
                      </p>
                    </div>
                    <Badge className="text-red-600 bg-red-50 border-red-200">
                      High Risk
                    </Badge>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <p className="text-dealverse-medium-gray">No high-risk documents identified</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Dashboard Statistics */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 bg-gradient-to-br from-dealverse-blue/10 to-dealverse-blue/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Documents Reviewed</CardTitle>
            <FileCheck className="h-4 w-4 text-dealverse-blue" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {documentsLoading ? <Loader2 className="h-6 w-6 animate-spin" /> : stats.documentsReviewed}
            </div>
            <p className="text-xs text-dealverse-medium-gray">of {stats.totalDocuments} total</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-coral/10 to-dealverse-coral/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Risk Flags</CardTitle>
            <AlertTriangle className="h-4 w-4 text-dealverse-coral" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {documentsLoading ? <Loader2 className="h-6 w-6 animate-spin" /> : stats.riskFlags}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Require attention</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-amber/10 to-dealverse-amber/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Missing Docs</CardTitle>
            <XCircle className="h-4 w-4 text-dealverse-amber" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {documentsLoading ? <Loader2 className="h-6 w-6 animate-spin" /> : stats.missingDocs}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Critical items</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-green/10 to-dealverse-green/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Completion</CardTitle>
            <TrendingUp className="h-4 w-4 text-dealverse-green" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {documentsLoading ? <Loader2 className="h-6 w-6 animate-spin" /> : `${stats.completionPercentage}%`}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Overall progress</p>
          </CardContent>
        </Card>
      </div>

      {/* File Upload Section */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl font-semibold text-dealverse-navy">Document Upload</CardTitle>
              <CardDescription className="text-dealverse-medium-gray">
                Upload documents for AI-powered analysis
              </CardDescription>
            </div>
            <div className="flex space-x-2">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt"
                onChange={handleFileUpload}
                className="hidden"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
              >
                {isUploading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Upload className="h-4 w-4 mr-2" />
                )}
                Upload Documents
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchDocuments}
                disabled={documentsLoading}
              >
                {documentsLoading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {documentsError && (
            <Alert className="mb-4">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{documentsError}</AlertDescription>
            </Alert>
          )}

          {isUploading && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-6 w-6 animate-spin text-dealverse-blue mr-2" />
              <span className="text-dealverse-medium-gray">Uploading documents...</span>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

