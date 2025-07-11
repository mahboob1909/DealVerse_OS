"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Eye,
  Download,
  Shield,
  AlertCircle,
  Star,
  Calendar,
  User,
  FileCheck,
  XCircle,
  Loader2
} from "lucide-react";
import { Document } from "@/hooks/use-documents";

interface DocumentPreviewProps {
  document: Document | null;
  onAnalyze?: (documentId: string) => void;
  onUpdate?: (documentId: string, updates: Partial<Document>) => void;
  isAnalyzing?: boolean;
}

export function DocumentPreview({ 
  document, 
  onAnalyze, 
  onUpdate, 
  isAnalyzing = false 
}: DocumentPreviewProps) {
  if (!document) {
    return (
      <Card className="border-0 shadow-lg h-full">
        <CardContent className="flex items-center justify-center h-full min-h-[400px]">
          <div className="text-center">
            <FileText className="h-12 w-12 text-dealverse-medium-gray mx-auto mb-4" />
            <p className="text-dealverse-medium-gray">
              Select a document to view details and analysis
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "analyzed":
      case "approved": 
        return <CheckCircle className="h-4 w-4 text-dealverse-green" />;
      case "processing": 
        return <Clock className="h-4 w-4 text-dealverse-amber" />;
      case "uploaded": 
        return <FileCheck className="h-4 w-4 text-dealverse-blue" />;
      case "rejected": 
        return <XCircle className="h-4 w-4 text-dealverse-coral" />;
      default: 
        return <FileText className="h-4 w-4 text-dealverse-medium-gray" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "analyzed":
      case "approved": 
        return "text-dealverse-green";
      case "processing": 
        return "text-dealverse-amber";
      case "uploaded": 
        return "text-dealverse-blue";
      case "rejected": 
        return "text-dealverse-coral";
      default: 
        return "text-dealverse-medium-gray";
    }
  };

  const getRiskLevel = () => {
    if (!document.risk_score) return { level: "Unknown", color: "text-dealverse-medium-gray", score: 0 };
    
    const score = parseInt(document.risk_score);
    if (score >= 70) return { level: "High", color: "text-dealverse-coral", score };
    if (score >= 40) return { level: "Medium", color: "text-dealverse-amber", score };
    return { level: "Low", color: "text-dealverse-green", score };
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const risk = getRiskLevel();

  return (
    <Card className="border-0 shadow-lg h-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold text-dealverse-navy mb-2">
              {document.title}
            </CardTitle>
            <CardDescription className="text-dealverse-medium-gray">
              {document.filename} • {formatFileSize(document.file_size)}
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusIcon(document.status)}
            <span className={`text-sm font-medium ${getStatusColor(document.status)}`}>
              {document.status.charAt(0).toUpperCase() + document.status.slice(1)}
            </span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Document Metadata */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4 text-dealverse-medium-gray" />
            <span className="text-dealverse-medium-gray">Uploaded:</span>
            <span className="font-medium">{formatDate(document.created_at)}</span>
          </div>
          <div className="flex items-center space-x-2">
            <User className="h-4 w-4 text-dealverse-medium-gray" />
            <span className="text-dealverse-medium-gray">Type:</span>
            <span className="font-medium">{document.document_type}</span>
          </div>
        </div>

        <Separator />

        {/* Risk Assessment */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold text-dealverse-navy">Risk Assessment</h4>
            <Badge 
              variant="outline" 
              className={`${risk.color} border-current`}
            >
              {risk.level} Risk
            </Badge>
          </div>
          
          {document.risk_score ? (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-dealverse-medium-gray">Risk Score</span>
                <span className="font-medium">{risk.score}/100</span>
              </div>
              <Progress value={risk.score} className="h-2" />
            </div>
          ) : (
            <div className="text-center py-4">
              <Shield className="h-8 w-8 text-dealverse-medium-gray mx-auto mb-2" />
              <p className="text-sm text-dealverse-medium-gray mb-3">
                Document not analyzed yet
              </p>
              {onAnalyze && (
                <Button 
                  size="sm" 
                  onClick={() => onAnalyze(document.id)}
                  disabled={isAnalyzing}
                  className="bg-dealverse-blue hover:bg-dealverse-blue/90"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Shield className="h-4 w-4 mr-2" />
                      Analyze Document
                    </>
                  )}
                </Button>
              )}
            </div>
          )}
        </div>

        {/* Key Findings */}
        {document.key_findings && document.key_findings.length > 0 && (
          <>
            <Separator />
            <div className="space-y-3">
              <h4 className="font-semibold text-dealverse-navy">Key Findings</h4>
              <div className="space-y-2">
                {document.key_findings.map((finding, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <AlertCircle className="h-4 w-4 text-dealverse-coral mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-dealverse-medium-gray">{finding}</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* AI Analysis */}
        {document.ai_analysis && Object.keys(document.ai_analysis).length > 0 && (
          <>
            <Separator />
            <div className="space-y-3">
              <h4 className="font-semibold text-dealverse-navy">AI Analysis</h4>
              <div className="bg-dealverse-light-gray/30 rounded-lg p-3">
                <div className="space-y-2 text-sm">
                  {document.ai_analysis.summary && (
                    <div>
                      <span className="font-medium text-dealverse-navy">Summary: </span>
                      <span className="text-dealverse-medium-gray">{document.ai_analysis.summary}</span>
                    </div>
                  )}
                  {document.ai_analysis.confidence && (
                    <div className="flex items-center space-x-2">
                      <Star className="h-4 w-4 text-dealverse-amber" />
                      <span className="font-medium text-dealverse-navy">Confidence: </span>
                      <span className="text-dealverse-medium-gray">
                        {Math.round(document.ai_analysis.confidence * 100)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}

        {/* Actions */}
        <Separator />
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" className="flex-1">
            <Eye className="h-4 w-4 mr-2" />
            View
          </Button>
          <Button variant="outline" size="sm" className="flex-1">
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          {onAnalyze && document.status !== 'analyzed' && (
            <Button 
              variant="outline" 
              size="sm" 
              className="flex-1"
              onClick={() => onAnalyze(document.id)}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Shield className="h-4 w-4 mr-2" />
              )}
              Analyze
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
