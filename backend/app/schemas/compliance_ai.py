"""
Compliance AI Schemas for DealVerse OS
Comprehensive schemas for AI-powered compliance monitoring, regulatory change detection, and risk assessment
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, validator


class ComplianceRiskLevel(str, Enum):
    """Compliance risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RegulatoryDomain(str, Enum):
    """Regulatory domains for compliance monitoring"""
    SEC = "sec"
    FINRA = "finra"
    AML = "aml"
    SOX = "sox"
    GDPR = "gdpr"
    BASEL = "basel"
    DODD_FRANK = "dodd_frank"
    MiFID = "mifid"
    GENERAL = "general"


class ComplianceViolation(BaseModel):
    """Individual compliance violation detected by AI"""
    violation_type: str = Field(..., description="Type of compliance violation")
    regulation: RegulatoryDomain = Field(..., description="Regulatory domain affected")
    severity: ComplianceRiskLevel = Field(..., description="Severity level of violation")
    description: str = Field(..., description="Detailed description of the violation")
    evidence: List[str] = Field(default=[], description="Evidence supporting the violation")
    potential_impact: str = Field(..., description="Potential business impact")
    confidence: Decimal = Field(..., ge=0, le=1, description="AI confidence in violation detection")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class RegulatoryChange(BaseModel):
    """Regulatory change detected by AI monitoring"""
    change_id: str = Field(..., description="Unique identifier for the regulatory change")
    regulation: RegulatoryDomain = Field(..., description="Regulatory domain")
    title: str = Field(..., description="Title of the regulatory change")
    description: str = Field(..., description="Description of the change")
    effective_date: Optional[datetime] = Field(None, description="When the change becomes effective")
    impact_level: ComplianceRiskLevel = Field(..., description="Impact level on business")
    affected_areas: List[str] = Field(default=[], description="Business areas affected")
    action_required: bool = Field(..., description="Whether immediate action is required")
    deadline: Optional[datetime] = Field(None, description="Compliance deadline")
    confidence: Decimal = Field(..., ge=0, le=1, description="AI confidence in change detection")


class CompliancePattern(BaseModel):
    """Compliance risk pattern identified by AI"""
    pattern_type: str = Field(..., description="Type of compliance pattern")
    frequency: int = Field(..., description="How often this pattern occurs")
    risk_score: Decimal = Field(..., ge=0, le=100, description="Risk score for this pattern")
    trend: str = Field(..., description="Trend direction (increasing, decreasing, stable)")
    affected_processes: List[str] = Field(default=[], description="Processes affected by this pattern")
    recommendation: str = Field(..., description="Recommendation to address the pattern")


class ComplianceTrend(BaseModel):
    """Compliance trend analysis"""
    metric: str = Field(..., description="Compliance metric being tracked")
    current_value: Decimal = Field(..., description="Current value of the metric")
    previous_value: Decimal = Field(..., description="Previous value for comparison")
    change_percentage: Decimal = Field(..., description="Percentage change")
    trend_direction: str = Field(..., description="Trend direction")
    significance: str = Field(..., description="Statistical significance of the trend")


class ComplianceRecommendation(BaseModel):
    """AI-generated compliance recommendation"""
    priority: str = Field(..., description="Priority level (high, medium, low)")
    category: str = Field(..., description="Category of recommendation")
    recommendation: str = Field(..., description="Detailed recommendation")
    rationale: str = Field(..., description="Rationale behind the recommendation")
    estimated_effort: str = Field(..., description="Estimated effort to implement")
    expected_impact: str = Field(..., description="Expected impact of implementation")
    timeline: str = Field(..., description="Recommended timeline for implementation")


class RemediationStep(BaseModel):
    """Individual step in remediation plan"""
    step_number: int = Field(..., description="Step number in sequence")
    action: str = Field(..., description="Action to be taken")
    responsible_party: str = Field(..., description="Who is responsible for this step")
    timeline: str = Field(..., description="Timeline for completion")
    dependencies: List[str] = Field(default=[], description="Dependencies for this step")
    success_criteria: str = Field(..., description="How to measure success")


class RemediationPlan(BaseModel):
    """Comprehensive remediation plan for compliance issues"""
    plan_id: str = Field(..., description="Unique identifier for the plan")
    title: str = Field(..., description="Title of the remediation plan")
    description: str = Field(..., description="Description of what the plan addresses")
    priority: str = Field(..., description="Priority level of the plan")
    estimated_duration: str = Field(..., description="Estimated time to complete")
    estimated_cost: Optional[str] = Field(None, description="Estimated cost if applicable")
    steps: List[RemediationStep] = Field(..., description="Detailed steps in the plan")
    success_metrics: List[str] = Field(default=[], description="Metrics to measure success")


class MonitoringAlert(BaseModel):
    """Real-time monitoring alert"""
    alert_id: str = Field(..., description="Unique identifier for the alert")
    alert_type: str = Field(..., description="Type of alert")
    severity: ComplianceRiskLevel = Field(..., description="Severity of the alert")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Detailed alert description")
    triggered_at: datetime = Field(..., description="When the alert was triggered")
    source: str = Field(..., description="Source that triggered the alert")
    requires_immediate_action: bool = Field(..., description="Whether immediate action is required")
    escalation_level: int = Field(..., description="Escalation level (1-5)")


class ComplianceAIInsights(BaseModel):
    """Core AI insights for compliance analysis"""
    compliance_score: Decimal = Field(..., ge=0, le=100, description="Overall compliance score")
    risk_level: ComplianceRiskLevel = Field(..., description="Overall risk level")
    violations_detected: List[ComplianceViolation] = Field(default=[], description="Detected violations")
    regulatory_changes: List[RegulatoryChange] = Field(default=[], description="Relevant regulatory changes")
    risk_patterns: List[CompliancePattern] = Field(default=[], description="Identified risk patterns")
    compliance_trends: Dict[str, ComplianceTrend] = Field(default={}, description="Compliance trends analysis")
    recommendations: List[ComplianceRecommendation] = Field(default=[], description="AI recommendations")
    monitoring_alerts: List[MonitoringAlert] = Field(default=[], description="Active monitoring alerts")
    confidence_level: str = Field(..., description="Overall confidence in analysis")


class ComplianceAIAnalysisRequest(BaseModel):
    """Request for AI compliance analysis"""
    compliance_context: str = Field(..., description="Context for compliance analysis")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis to perform")
    regulatory_focus: List[RegulatoryDomain] = Field(default=[], description="Specific regulatory domains to focus on")
    compliance_data: Dict[str, Any] = Field(..., description="Compliance data to analyze")
    include_patterns: bool = Field(default=True, description="Include pattern analysis")
    include_trends: bool = Field(default=True, description="Include trend analysis")
    include_predictions: bool = Field(default=True, description="Include predictive insights")
    time_range_days: int = Field(default=30, description="Time range for analysis in days")


class ConfidenceMetrics(BaseModel):
    """Confidence metrics for compliance analysis"""
    overall_confidence: Decimal = Field(..., ge=0, le=1, description="Overall analysis confidence")
    violation_detection_confidence: Decimal = Field(..., ge=0, le=1, description="Confidence in violation detection")
    pattern_analysis_confidence: Decimal = Field(..., ge=0, le=1, description="Confidence in pattern analysis")
    trend_analysis_confidence: Decimal = Field(..., ge=0, le=1, description="Confidence in trend analysis")
    recommendation_confidence: Decimal = Field(..., ge=0, le=1, description="Confidence in recommendations")
    confidence_level: str = Field(..., description="Qualitative confidence level")


class ComplianceAIAnalysisResponse(BaseModel):
    """Response from AI compliance analysis"""
    ai_insights: ComplianceAIInsights = Field(..., description="Core AI insights")
    remediation_plan: Optional[RemediationPlan] = Field(None, description="Generated remediation plan")
    confidence_metrics: ConfidenceMetrics = Field(..., description="Confidence metrics")
    processing_time: Decimal = Field(..., description="Time taken for analysis")
    analysis_date: datetime = Field(..., description="When analysis was performed")
    model_version: str = Field(..., description="AI model version used")
    status: str = Field(default="completed", description="Analysis status")


class ComplianceMonitoringRequest(BaseModel):
    """Request for ongoing compliance monitoring"""
    organization_id: UUID = Field(..., description="Organization to monitor")
    monitoring_scope: List[RegulatoryDomain] = Field(..., description="Regulatory domains to monitor")
    alert_thresholds: Dict[str, Any] = Field(default={}, description="Custom alert thresholds")
    monitoring_frequency: str = Field(default="daily", description="Monitoring frequency")
    include_predictive: bool = Field(default=True, description="Include predictive monitoring")


class ComplianceMonitoringResponse(BaseModel):
    """Response from compliance monitoring setup"""
    monitoring_id: str = Field(..., description="Unique monitoring session ID")
    status: str = Field(..., description="Monitoring status")
    active_alerts: List[MonitoringAlert] = Field(default=[], description="Currently active alerts")
    next_check: datetime = Field(..., description="Next scheduled monitoring check")
    configuration: Dict[str, Any] = Field(..., description="Monitoring configuration")


class RegulatoryUpdateAnalysisRequest(BaseModel):
    """Request for regulatory update analysis"""
    update_content: str = Field(..., description="Content of the regulatory update")
    regulation_type: RegulatoryDomain = Field(..., description="Type of regulation")
    organization_context: Dict[str, Any] = Field(default={}, description="Organization context for impact analysis")
    current_compliance_status: Dict[str, Any] = Field(default={}, description="Current compliance status")


class RegulatoryUpdateAnalysisResponse(BaseModel):
    """Response from regulatory update analysis"""
    impact_assessment: Dict[str, Any] = Field(..., description="Impact assessment results")
    required_actions: List[str] = Field(default=[], description="Required actions")
    timeline: Dict[str, Any] = Field(..., description="Implementation timeline")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment")
    compliance_gap_analysis: Dict[str, Any] = Field(..., description="Gap analysis results")
    confidence_score: Decimal = Field(..., ge=0, le=1, description="Confidence in analysis")
