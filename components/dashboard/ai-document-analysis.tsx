"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Brain,
  FileText,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Shield,
  Users,
  Calendar,
  DollarSign,
  MapPin,
  Loader2,
  RefreshCw,
  Eye,
  Download
} from "lucide-react";
import { useDocumentAnalysis, type DocumentAnalysisResult } from "@/hooks/use-document-analysis";
import { type Document } from "@/hooks/use-documents";

interface AIDocumentAnalysisProps {
  document: Document;
  onAnalysisComplete?: (result: DocumentAnalysisResult) => void;
}

export function AIDocumentAnalysis({ document, onAnalysisComplete }: AIDocumentAnalysisProps) {
  const {
    analysisResults,
    loading,
    error,
    analyzeDocument,
    getDocumentAnalysis,
    isAnalyzing,
    hasAnalysis,
    getAnalysisForDocument,
    clearError
  } = useDocumentAnalysis();

  const [selectedAnalysisType, setSelectedAnalysisType] = useState<string>('full');
  const [selectedFocusAreas, setSelectedFocusAreas] = useState<string[]>(['financial', 'legal', 'risk']);

  const analysis = getAnalysisForDocument(document.id);
  const isLoading = isAnalyzing(document.id);

  useEffect(() => {
    // Try to fetch existing analysis on mount
    if (!hasAnalysis(document.id) && !isLoading) {
      getDocumentAnalysis(document.id).catch(() => {
        // Ignore errors for missing analysis
      });
    }
  }, [document.id, hasAnalysis, isLoading, getDocumentAnalysis]);

  const handleAnalyze = async () => {
    try {
      clearError();
      const result = await analyzeDocument(document.id, selectedAnalysisType, selectedFocusAreas);
      onAnalysisComplete?.(result);
    } catch (err) {
      // Error is handled by the hook
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 0.7) return 'text-red-600 bg-red-50 border-red-200';
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-green-600 bg-green-50 border-green-200';
  };

  const getRiskLabel = (score: number) => {
    if (score >= 0.7) return 'High Risk';
    if (score >= 0.4) return 'Medium Risk';
    return 'Low Risk';
  };

  return (
    <div className="space-y-6">
      {/* Analysis Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-dealverse-blue" />
            AI Document Analysis
          </CardTitle>
          <CardDescription>
            Powered by DeepSeek AI through OpenRouter - Advanced document analysis and risk assessment
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Analysis Type Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Analysis Type</label>
            <div className="flex gap-2 flex-wrap">
              {[
                { value: 'full', label: 'Full Analysis' },
                { value: 'risk_only', label: 'Risk Only' },
                { value: 'financial_only', label: 'Financial Only' },
                { value: 'legal_only', label: 'Legal Only' },
                { value: 'compliance_only', label: 'Compliance Only' }
              ].map((type) => (
                <Button
                  key={type.value}
                  variant={selectedAnalysisType === type.value ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedAnalysisType(type.value)}
                  disabled={isLoading}
                >
                  {type.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Focus Areas Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Focus Areas</label>
            <div className="flex gap-2 flex-wrap">
              {[
                { value: 'financial', label: 'Financial' },
                { value: 'legal', label: 'Legal' },
                { value: 'risk', label: 'Risk' },
                { value: 'compliance', label: 'Compliance' },
                { value: 'operational', label: 'Operational' }
              ].map((area) => (
                <Button
                  key={area.value}
                  variant={selectedFocusAreas.includes(area.value) ? "default" : "outline"}
                  size="sm"
                  onClick={() => {
                    setSelectedFocusAreas(prev => 
                      prev.includes(area.value)
                        ? prev.filter(a => a !== area.value)
                        : [...prev, area.value]
                    );
                  }}
                  disabled={isLoading}
                >
                  {area.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button 
              onClick={handleAnalyze} 
              disabled={isLoading || selectedFocusAreas.length === 0}
              className="bg-dealverse-blue hover:bg-dealverse-blue/90"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4 mr-2" />
                  {analysis ? 'Re-analyze' : 'Analyze Document'}
                </>
              )}
            </Button>
            
            {analysis && (
              <Button variant="outline" onClick={() => getDocumentAnalysis(document.id)}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysis && (
        <Tabs defaultValue="summary" className="space-y-4">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="summary">Summary</TabsTrigger>
            <TabsTrigger value="risk">Risk Assessment</TabsTrigger>
            <TabsTrigger value="financial">Financial</TabsTrigger>
            <TabsTrigger value="entities">Entities</TabsTrigger>
            <TabsTrigger value="compliance">Compliance</TabsTrigger>
          </TabsList>

          {/* Summary Tab */}
          <TabsContent value="summary" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Executive Summary</span>
                  <Badge className={getRiskColor(analysis.risk_assessment.overall_risk_score)}>
                    {getRiskLabel(analysis.risk_assessment.overall_risk_score)}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">{analysis.executive_summary}</p>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Confidence Score</label>
                    <div className="flex items-center gap-2">
                      <Progress value={analysis.confidence_score * 100} className="flex-1" />
                      <span className="text-sm font-medium">{Math.round(analysis.confidence_score * 100)}%</span>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Risk Score</label>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={analysis.risk_assessment.overall_risk_score * 100} 
                        className="flex-1"
                      />
                      <span className="text-sm font-medium">
                        {Math.round(analysis.risk_assessment.overall_risk_score * 100)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Key Findings</label>
                  <ul className="space-y-1">
                    {analysis.key_findings.map((finding, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        {finding}
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Risk Assessment Tab */}
          <TabsContent value="risk" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-red-600" />
                  Risk Assessment
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysis.risk_assessment.risk_factors.map((factor, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{factor.category}</span>
                      <Badge variant={factor.severity === 'high' ? 'destructive' : factor.severity === 'medium' ? 'default' : 'secondary'}>
                        {factor.severity}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{factor.description}</p>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">Confidence:</span>
                      <Progress value={factor.confidence * 100} className="flex-1 h-2" />
                      <span className="text-xs">{Math.round(factor.confidence * 100)}%</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Financial Tab */}
          <TabsContent value="financial" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  Financial Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                {analysis.financial_analysis ? (
                  <div className="space-y-4">
                    {Object.entries(analysis.financial_analysis).map(([key, value]) => (
                      <div key={key} className="border rounded-lg p-4">
                        <h4 className="font-medium capitalize mb-2">{key.replace(/_/g, ' ')}</h4>
                        <pre className="text-sm text-muted-foreground whitespace-pre-wrap">
                          {JSON.stringify(value, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No financial analysis available for this document.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Entities Tab */}
          <TabsContent value="entities" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(analysis.entity_extraction).map(([type, entities]) => (
                <Card key={type}>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-sm">
                      {type === 'companies' && <Users className="h-4 w-4" />}
                      {type === 'people' && <Users className="h-4 w-4" />}
                      {type === 'dates' && <Calendar className="h-4 w-4" />}
                      {type === 'amounts' && <DollarSign className="h-4 w-4" />}
                      {type === 'locations' && <MapPin className="h-4 w-4" />}
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-1">
                      {entities.length > 0 ? (
                        entities.map((entity, index) => (
                          <Badge key={index} variant="outline" className="mr-1 mb-1">
                            {entity}
                          </Badge>
                        ))
                      ) : (
                        <p className="text-sm text-muted-foreground">None found</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Compliance Tab */}
          <TabsContent value="compliance" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-blue-600" />
                  Compliance Notes
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysis.compliance_notes.length > 0 ? (
                  <ul className="space-y-2">
                    {analysis.compliance_notes.map((note, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        {note}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">No compliance notes available.</p>
                )}

                <div className="border-t pt-4">
                  <h4 className="font-medium mb-2">Recommendations</h4>
                  {analysis.recommendations.length > 0 ? (
                    <ul className="space-y-2">
                      {analysis.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm">
                          <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-muted-foreground">No recommendations available.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
