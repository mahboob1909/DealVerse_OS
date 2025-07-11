"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  Bell,
  TrendingUp,
  Calendar,
  Users,
  AlertCircle,
  Eye,
  Download,
  RefreshCw,
  Settings,
  BookOpen,
  Scale,
  Loader2,
  ExternalLink,
  Filter,
  Search,
  Plus
} from "lucide-react";
import { useState, useEffect, useMemo } from "react";
import { ExportButton, exportConfigs } from "@/components/ui/export-button";
import { useCompliance } from "@/hooks/use-compliance";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";

export default function CompliancePage() {
  // Compliance hook for real API data
  const {
    dashboard,
    categories,
    requirements,
    assessments,
    regulatoryUpdates,
    loading,
    dashboardLoading,
    categoriesLoading,
    requirementsLoading,
    assessmentsLoading,
    updatesLoading,
    error,
    refreshAll,
    fetchDashboard,
    markUpdateAsReviewed,
    runComplianceCheck,
    generateAuditTrail
  } = useCompliance({ autoFetch: true });

  // Local state for UI interactions
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterRiskLevel, setFilterRiskLevel] = useState<string>("all");
  const [activeTab, setActiveTab] = useState("overview");
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [isRunningCheck, setIsRunningCheck] = useState(false);

  // Computed values from real data
  const complianceMetrics = useMemo(() => {
    if (!dashboard?.compliance_categories) return [];

    return dashboard.compliance_categories.map(cat => ({
      category: cat.category,
      status: cat.status,
      score: cat.score,
      lastReview: cat.last_review,
      nextReview: cat.next_review,
      requirements: requirements.filter(req => req.category_id === cat.category).length,
      completed: requirements.filter(req => req.category_id === cat.category && req.status === 'completed').length
    }));
  }, [dashboard, requirements]);

  const filteredRequirements = useMemo(() => {
    return requirements.filter(req => {
      const matchesSearch = req.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           req.description?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = filterStatus === "all" || req.status === filterStatus;
      const matchesRisk = filterRiskLevel === "all" || req.risk_level === filterRiskLevel;
      const matchesCategory = !selectedCategory || req.category_id === selectedCategory;

      return matchesSearch && matchesStatus && matchesRisk && matchesCategory;
    });
  }, [requirements, searchTerm, filterStatus, filterRiskLevel, selectedCategory]);

  const filteredUpdates = useMemo(() => {
    return regulatoryUpdates.filter(update =>
      update.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      update.description?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [regulatoryUpdates, searchTerm]);

  // Utility functions
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
      case "compliant": return "text-dealverse-green";
      case "in_progress":
      case "warning": return "text-dealverse-amber";
      case "pending":
      case "action_required": return "text-dealverse-coral";
      default: return "text-dealverse-medium-gray";
    }
  };

  const getStatusBg = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
      case "compliant": return "bg-dealverse-green/10 border-dealverse-green/20";
      case "in_progress":
      case "warning": return "bg-dealverse-amber/10 border-dealverse-amber/20";
      case "pending":
      case "action_required": return "bg-dealverse-coral/10 border-dealverse-coral/20";
      default: return "bg-gray-100 border-gray-200";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
      case "compliant": return <CheckCircle className="h-4 w-4 text-dealverse-green" />;
      case "in_progress":
      case "warning": return <AlertTriangle className="h-4 w-4 text-dealverse-amber" />;
      case "pending":
      case "action_required": return <AlertCircle className="h-4 w-4 text-dealverse-coral" />;
      default: return <Clock className="h-4 w-4 text-dealverse-medium-gray" />;
    }
  };

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "high": return "text-dealverse-coral";
      case "medium": return "text-dealverse-amber";
      case "low": return "text-dealverse-green";
      default: return "text-dealverse-medium-gray";
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case "high": return "border-dealverse-coral text-dealverse-coral";
      case "medium": return "border-dealverse-amber text-dealverse-amber";
      case "low": return "border-dealverse-green text-dealverse-green";
      default: return "border-gray-300 text-gray-600";
    }
  };

  // Action handlers
  const handleRefresh = async () => {
    try {
      await refreshAll();
      toast.success("Compliance data refreshed successfully");
    } catch (error) {
      toast.error("Failed to refresh compliance data");
    }
  };

  const handleRunComplianceCheck = async () => {
    try {
      setIsRunningCheck(true);
      await runComplianceCheck(selectedCategory || undefined);
      await fetchDashboard(); // Refresh dashboard after check
      toast.success("Compliance check completed successfully");
    } catch (error) {
      toast.error("Failed to run compliance check");
    } finally {
      setIsRunningCheck(false);
    }
  };

  const handleGenerateReport = async () => {
    try {
      setIsGeneratingReport(true);
      const auditParams = {
        audit_scope: {
          start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), // Last 30 days
          end_date: new Date().toISOString(),
          compliance_areas: selectedCategory ? [selectedCategory] : undefined
        },
        report_format: "detailed",
        export_format: "pdf"
      };

      const report = await generateAuditTrail(auditParams);
      toast.success("Compliance report generated successfully");

      // Handle report download/display logic here
      console.log("Generated report:", report);
    } catch (error) {
      toast.error("Failed to generate compliance report");
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const handleMarkUpdateAsReviewed = async (updateId: string) => {
    try {
      await markUpdateAsReviewed(updateId, "Reviewed and acknowledged");
      toast.success("Regulatory update marked as reviewed");
    } catch (error) {
      toast.error("Failed to mark update as reviewed");
    }
  };

  // Loading state
  if (loading && !dashboard) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-dealverse-blue" />
          <p className="text-dealverse-medium-gray">Loading compliance data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertCircle className="h-8 w-8 mx-auto mb-4 text-dealverse-coral" />
          <p className="text-dealverse-coral mb-4">Failed to load compliance data</p>
          <Button onClick={handleRefresh} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-dealverse-navy to-dealverse-blue bg-clip-text text-transparent">
          Compliance Guardian
        </h1>
        <p className="text-dealverse-medium-gray dark:text-dealverse-light-gray">
          Regulatory compliance monitoring and audit trail management
        </p>
      </div>

      {/* Compliance Dashboard */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 bg-gradient-to-br from-dealverse-green/10 to-dealverse-green/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Compliance Score</CardTitle>
            <Shield className="h-4 w-4 text-dealverse-green" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {dashboardLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                `${dashboard?.overall_score || 0}%`
              )}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Overall rating</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-coral/10 to-dealverse-coral/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Action Items</CardTitle>
            <AlertTriangle className="h-4 w-4 text-dealverse-coral" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {dashboardLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                dashboard?.pending_requirements || 0
              )}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Require attention</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-blue/10 to-dealverse-blue/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Total Requirements</CardTitle>
            <FileText className="h-4 w-4 text-dealverse-blue" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {dashboardLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                dashboard?.total_requirements || 0
              )}
            </div>
            <p className="text-xs text-dealverse-medium-gray">
              {dashboard?.completed_requirements || 0} completed
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-amber/10 to-dealverse-amber/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Overdue Items</CardTitle>
            <Calendar className="h-4 w-4 text-dealverse-amber" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {dashboardLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                dashboard?.overdue_requirements || 0
              )}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Need immediate attention</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content with Tabs */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl font-semibold text-dealverse-navy">Compliance Management</CardTitle>
                  <CardDescription className="text-dealverse-medium-gray">
                    Comprehensive compliance monitoring and management
                  </CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRunComplianceCheck}
                    disabled={isRunningCheck}
                  >
                    {isRunningCheck ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Shield className="h-4 w-4 mr-2" />
                    )}
                    Run Check
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRefresh}
                    disabled={loading}
                  >
                    {loading ? (
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
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="requirements">Requirements</TabsTrigger>
                  <TabsTrigger value="assessments">Assessments</TabsTrigger>
                  <TabsTrigger value="audit">Audit Trail</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4 mt-6">
                  {/* Compliance Categories Overview */}
                  <div className="space-y-4">
                    {complianceMetrics.length > 0 ? (
                      complianceMetrics.map((metric, index) => (
                        <Card
                          key={index}
                          className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                            selectedCategory === metric.category
                              ? 'ring-2 ring-dealverse-blue bg-dealverse-blue/5'
                              : 'hover:bg-dealverse-light-gray/50'
                          }`}
                          onClick={() => setSelectedCategory(selectedCategory === metric.category ? null : metric.category)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                {getStatusIcon(metric.status)}
                                <div>
                                  <h3 className="font-semibold text-dealverse-navy">{metric.category}</h3>
                                  <p className="text-sm text-dealverse-medium-gray">
                                    {metric.completed}/{metric.requirements} requirements met
                                  </p>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className={`text-2xl font-bold ${getStatusColor(metric.status)}`}>
                                  {metric.score}%
                                </div>
                                <Badge className={`text-xs ${getStatusBg(metric.status)}`}>
                                  {metric.status.replace('_', ' ')}
                                </Badge>
                              </div>
                            </div>
                            <div className="mt-3">
                              <Progress value={metric.score} className="h-2" />
                              <div className="flex justify-between text-xs text-dealverse-medium-gray mt-1">
                                <span>Last review: {metric.lastReview}</span>
                                <span>Next review: {metric.nextReview}</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <Shield className="h-12 w-12 mx-auto mb-4 text-dealverse-medium-gray" />
                        <p className="text-dealverse-medium-gray">No compliance categories found</p>
                      </div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="requirements" className="space-y-4 mt-6">
                  {/* Filters */}
                  <div className="flex flex-col sm:flex-row gap-4">
                    <div className="flex-1">
                      <Input
                        placeholder="Search requirements..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full"
                      />
                    </div>
                    <Select value={filterStatus} onValueChange={setFilterStatus}>
                      <SelectTrigger className="w-full sm:w-[180px]">
                        <SelectValue placeholder="Filter by status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                        <SelectItem value="in_progress">In Progress</SelectItem>
                        <SelectItem value="pending">Pending</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={filterRiskLevel} onValueChange={setFilterRiskLevel}>
                      <SelectTrigger className="w-full sm:w-[180px]">
                        <SelectValue placeholder="Filter by risk" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Risk Levels</SelectItem>
                        <SelectItem value="high">High Risk</SelectItem>
                        <SelectItem value="medium">Medium Risk</SelectItem>
                        <SelectItem value="low">Low Risk</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Requirements List */}
                  <div className="space-y-3">
                    {requirementsLoading ? (
                      <div className="text-center py-8">
                        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-dealverse-blue" />
                        <p className="text-dealverse-medium-gray">Loading requirements...</p>
                      </div>
                    ) : filteredRequirements.length > 0 ? (
                      filteredRequirements.map((requirement) => (
                        <Card key={requirement.id} className="border border-dealverse-light-gray">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-2">
                                  {getStatusIcon(requirement.status)}
                                  <h4 className="font-medium text-dealverse-navy">{requirement.title}</h4>
                                  <Badge className={`text-xs ${getRiskColor(requirement.risk_level)}`}>
                                    {requirement.risk_level} risk
                                  </Badge>
                                </div>
                                {requirement.description && (
                                  <p className="text-sm text-dealverse-medium-gray mb-2">
                                    {requirement.description}
                                  </p>
                                )}
                                <div className="flex items-center space-x-4 text-xs text-dealverse-medium-gray">
                                  <span>Progress: {requirement.completion_percentage}%</span>
                                  {requirement.due_date && (
                                    <span>Due: {new Date(requirement.due_date).toLocaleDateString()}</span>
                                  )}
                                  {requirement.next_review_date && (
                                    <span>Next review: {new Date(requirement.next_review_date).toLocaleDateString()}</span>
                                  )}
                                </div>
                              </div>
                              <div className="ml-4">
                                <Progress value={requirement.completion_percentage} className="w-20 h-2" />
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <FileText className="h-12 w-12 mx-auto mb-4 text-dealverse-medium-gray" />
                        <p className="text-dealverse-medium-gray">No requirements found</p>
                      </div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="assessments" className="space-y-4 mt-6">
                  {/* Assessments List */}
                  <div className="space-y-3">
                    {assessmentsLoading ? (
                      <div className="text-center py-8">
                        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-dealverse-blue" />
                        <p className="text-dealverse-medium-gray">Loading assessments...</p>
                      </div>
                    ) : assessments.length > 0 ? (
                      assessments.map((assessment) => (
                        <Card key={assessment.id} className="border border-dealverse-light-gray">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-2">
                                  {getStatusIcon(assessment.status)}
                                  <h4 className="font-medium text-dealverse-navy">
                                    {assessment.assessment_type.replace('_', ' ').toUpperCase()} Assessment
                                  </h4>
                                  <Badge className={`text-xs ${getRiskColor(assessment.risk_level)}`}>
                                    {assessment.risk_level} risk
                                  </Badge>
                                </div>
                                {assessment.findings && (
                                  <p className="text-sm text-dealverse-medium-gray mb-2">
                                    <strong>Findings:</strong> {assessment.findings}
                                  </p>
                                )}
                                {assessment.recommendations && (
                                  <p className="text-sm text-dealverse-medium-gray mb-2">
                                    <strong>Recommendations:</strong> {assessment.recommendations}
                                  </p>
                                )}
                                <div className="flex items-center space-x-4 text-xs text-dealverse-medium-gray">
                                  {assessment.score && <span>Score: {assessment.score}%</span>}
                                  <span>Status: {assessment.status}</span>
                                  <span>Date: {new Date(assessment.created_at).toLocaleDateString()}</span>
                                </div>
                              </div>
                              {assessment.score && (
                                <div className="ml-4 text-right">
                                  <div className={`text-2xl font-bold ${getStatusColor(assessment.status)}`}>
                                    {assessment.score}%
                                  </div>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <Scale className="h-12 w-12 mx-auto mb-4 text-dealverse-medium-gray" />
                        <p className="text-dealverse-medium-gray">No assessments found</p>
                      </div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="audit" className="space-y-4 mt-6">
                  {/* Audit Trail */}
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-dealverse-navy">Audit Trail</h3>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleGenerateReport}
                      disabled={isGeneratingReport}
                    >
                      {isGeneratingReport ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Download className="h-4 w-4 mr-2" />
                      )}
                      Generate Report
                    </Button>
                  </div>

                  <div className="space-y-3">
                    {dashboard?.recent_assessments && dashboard.recent_assessments.length > 0 ? (
                      dashboard.recent_assessments.map((event, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 rounded-lg border border-dealverse-light-gray">
                          <div className={`w-2 h-2 rounded-full mt-2 ${
                            event.status === 'completed' ? 'bg-dealverse-green' :
                            event.status === 'in_progress' ? 'bg-dealverse-amber' :
                            'bg-dealverse-coral'
                          }`}></div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <h4 className="font-medium text-dealverse-navy">
                                {event.assessment_type.replace('_', ' ').toUpperCase()} Assessment
                              </h4>
                              <Badge className={`text-xs ${getStatusBg(event.status)}`}>
                                {event.status}
                              </Badge>
                            </div>
                            <div className="flex items-center space-x-4 text-xs text-dealverse-medium-gray mt-2">
                              <span className="flex items-center">
                                <TrendingUp className="h-3 w-3 mr-1" />
                                Score: {event.score}%
                              </span>
                              <span className="flex items-center">
                                <Clock className="h-3 w-3 mr-1" />
                                {new Date(event.date).toLocaleString()}
                              </span>
                              <span className="flex items-center">
                                <BookOpen className="h-3 w-3 mr-1" />
                                {event.status}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <FileText className="h-12 w-12 mx-auto mb-4 text-dealverse-medium-gray" />
                        <p className="text-dealverse-medium-gray">No audit trail events found</p>
                      </div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Regulatory Updates */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg font-semibold text-dealverse-navy">Regulatory Updates</CardTitle>
                  <CardDescription className="text-dealverse-medium-gray">
                    Latest regulatory changes and notifications
                  </CardDescription>
                </div>
                <Button variant="ghost" size="sm">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {updatesLoading ? (
                  <div className="text-center py-4">
                    <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2 text-dealverse-blue" />
                    <p className="text-xs text-dealverse-medium-gray">Loading updates...</p>
                  </div>
                ) : filteredUpdates.length > 0 ? (
                  filteredUpdates.map((update) => (
                    <div key={update.id} className="border-l-2 border-dealverse-blue/20 pl-4">
                      <div className="flex items-start justify-between mb-1">
                        <h5 className="font-medium text-sm text-dealverse-navy leading-tight">
                          {update.title}
                        </h5>
                        <div className="flex flex-col items-end space-y-1 ml-2">
                          <Badge
                            variant="outline"
                            className={`text-xs ${getImpactColor(update.impact_level)}`}
                          >
                            {update.impact_level}
                          </Badge>
                          {!update.is_reviewed && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 px-2 text-xs"
                              onClick={() => handleMarkUpdateAsReviewed(update.id)}
                            >
                              <Eye className="h-3 w-3 mr-1" />
                              Review
                            </Button>
                          )}
                        </div>
                      </div>
                      {update.description && (
                        <p className="text-xs text-dealverse-medium-gray mb-2 line-clamp-2">
                          {update.description}
                        </p>
                      )}
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-dealverse-blue">{update.regulation_type}</span>
                        <span className="text-dealverse-medium-gray">
                          {new Date(update.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      {update.source_url && (
                        <div className="mt-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 px-2 text-xs"
                            onClick={() => window.open(update.source_url, '_blank')}
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            View Source
                          </Button>
                        </div>
                      )}
                      {update.is_reviewed && (
                        <div className="mt-2 flex items-center text-xs text-dealverse-green">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Reviewed
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-center py-4">
                    <Bell className="h-8 w-8 mx-auto mb-2 text-dealverse-medium-gray" />
                    <p className="text-xs text-dealverse-medium-gray">No regulatory updates</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Upcoming Deadlines */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-dealverse-navy">Upcoming Deadlines</CardTitle>
              <CardDescription className="text-dealverse-medium-gray">
                Critical compliance deadlines and tasks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {dashboard?.upcoming_deadlines && dashboard.upcoming_deadlines.length > 0 ? (
                  dashboard.upcoming_deadlines.map((deadline, index) => (
                    <div key={index} className="flex items-center justify-between p-2 rounded-lg bg-dealverse-light-gray/30">
                      <div className="flex items-center space-x-2">
                        {deadline.status === 'completed' ? (
                          <CheckCircle className="h-4 w-4 text-dealverse-green" />
                        ) : deadline.status === 'in_progress' ? (
                          <Clock className="h-4 w-4 text-dealverse-amber" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-dealverse-coral" />
                        )}
                        <div>
                          <div className="text-sm font-medium text-dealverse-navy">{deadline.requirement}</div>
                          <div className="text-xs text-dealverse-medium-gray">
                            Due: {new Date(deadline.deadline).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <Badge className={`text-xs ${
                        deadline.priority === 'high' ? 'bg-dealverse-coral/10 text-dealverse-coral border-dealverse-coral/20' :
                        deadline.priority === 'medium' ? 'bg-dealverse-amber/10 text-dealverse-amber border-dealverse-amber/20' :
                        'bg-dealverse-green/10 text-dealverse-green border-dealverse-green/20'
                      }`}>
                        {deadline.priority}
                      </Badge>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-4">
                    <Calendar className="h-8 w-8 mx-auto mb-2 text-dealverse-medium-gray" />
                    <p className="text-xs text-dealverse-medium-gray">No upcoming deadlines</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-dealverse-navy">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                className="w-full bg-dealverse-blue hover:bg-dealverse-blue/90"
                size="sm"
                onClick={handleGenerateReport}
                disabled={isGeneratingReport}
              >
                {isGeneratingReport ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <FileText className="h-4 w-4 mr-2" />
                )}
                Generate Report
              </Button>
              <ExportButton
                options={exportConfigs.complianceReport()}
                variant="outline"
                size="sm"
                className="w-full"
                disabled={isGeneratingReport}
              />
              <Button
                variant="outline"
                className="w-full"
                size="sm"
                onClick={handleRunComplianceCheck}
                disabled={isRunningCheck}
              >
                {isRunningCheck ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Shield className="h-4 w-4 mr-2" />
                )}
                Run Compliance Check
              </Button>
              <Button variant="outline" className="w-full" size="sm">
                <Bell className="h-4 w-4 mr-2" />
                Set Reminder
              </Button>
              <Button variant="outline" className="w-full" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Configure Alerts
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
