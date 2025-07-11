"""
Financial AI Analysis schemas for DealVerse OS
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, validator


class FinancialAIAnalysisRequest(BaseModel):
    """Request schema for financial AI analysis"""
    model_id: Optional[UUID] = None
    model_data: Dict[str, Any]
    analysis_type: str = "comprehensive"  # comprehensive, validation, optimization, scenario
    include_suggestions: bool = True
    include_validation: bool = True
    include_scenarios: bool = True
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        allowed = ["comprehensive", "validation", "optimization", "scenario", "risk_assessment"]
        if v not in allowed:
            raise ValueError(f"Analysis type must be one of: {allowed}")
        return v


class ModelingSuggestion(BaseModel):
    """Individual modeling suggestion"""
    category: str  # structure, assumption, calculation, scenario, validation
    suggestion: str
    priority: str  # high, medium, low
    impact: str  # high, medium, low
    implementation_effort: str  # easy, moderate, complex


class ValidationIssue(BaseModel):
    """Model validation issue"""
    issue_type: str  # missing_field, unreasonable_assumption, calculation_error
    severity: str  # critical, high, medium, low
    description: str
    recommendation: str
    field_path: Optional[str] = None


class ScenarioRecommendation(BaseModel):
    """Scenario analysis recommendation"""
    scenario_name: str
    description: str
    parameters: Dict[str, Any]
    probability: Optional[Decimal] = None
    rationale: str


class ConfidenceMetrics(BaseModel):
    """AI analysis confidence metrics"""
    overall_confidence: Decimal
    confidence_level: str  # high, medium, low
    ai_analysis_confidence: Decimal
    validation_confidence: Decimal
    reliability_score: Decimal
    recommendation_strength: str


class FinancialAIInsights(BaseModel):
    """AI-generated insights about the financial model"""
    model_quality_score: Decimal
    key_insights: List[str]
    risk_factors: List[str]
    optimization_opportunities: List[str]
    assumption_analysis: Dict[str, str]
    valuation_reasonableness: str
    recommended_scenarios: List[str] = []
    calculation_checks: Dict[str, str] = {}


class FinancialAIAnalysisResponse(BaseModel):
    """Response schema for financial AI analysis"""
    analysis_id: Optional[UUID] = None
    model_id: Optional[UUID] = None
    analysis_type: str
    
    # AI Analysis Results
    ai_insights: FinancialAIInsights
    modeling_suggestions: Dict[str, List[ModelingSuggestion]] = {}
    validation_results: Dict[str, Any] = {}
    scenario_recommendations: Dict[str, Any] = {}
    confidence_metrics: ConfidenceMetrics
    
    # Processing metadata
    processing_time: Decimal
    analysis_date: datetime
    model_version: str
    
    # Status
    status: str = "completed"  # processing, completed, failed
    error_message: Optional[str] = None


class ModelOptimizationRequest(BaseModel):
    """Request for model optimization suggestions"""
    model_id: UUID
    optimization_focus: List[str] = ["accuracy", "completeness", "scenarios"]  # accuracy, completeness, scenarios, performance
    current_issues: List[str] = []
    target_confidence_level: str = "high"
    
    @validator('optimization_focus')
    def validate_optimization_focus(cls, v):
        allowed = ["accuracy", "completeness", "scenarios", "performance", "assumptions", "calculations"]
        for focus in v:
            if focus not in allowed:
                raise ValueError(f"Optimization focus must be from: {allowed}")
        return v


class ModelOptimizationResponse(BaseModel):
    """Response for model optimization suggestions"""
    model_id: UUID
    optimization_suggestions: List[ModelingSuggestion]
    priority_actions: List[str]
    estimated_improvement: Dict[str, str]  # confidence_increase, accuracy_improvement, etc.
    implementation_roadmap: List[Dict[str, Any]]
    
    # Metrics
    current_quality_score: Decimal
    potential_quality_score: Decimal
    confidence_improvement: Decimal


class ScenarioAnalysisRequest(BaseModel):
    """Request for AI-powered scenario analysis"""
    model_id: UUID
    scenario_types: List[str] = ["conservative", "base", "optimistic"]  # conservative, base, optimistic, stress_test
    sensitivity_variables: List[str] = []
    custom_scenarios: List[Dict[str, Any]] = []
    monte_carlo_iterations: Optional[int] = None
    
    @validator('scenario_types')
    def validate_scenario_types(cls, v):
        allowed = ["conservative", "base", "optimistic", "stress_test", "recession", "expansion", "custom"]
        for scenario_type in v:
            if scenario_type not in allowed:
                raise ValueError(f"Scenario type must be from: {allowed}")
        return v


class ScenarioResult(BaseModel):
    """Individual scenario analysis result"""
    scenario_name: str
    scenario_type: str
    parameters: Dict[str, Any]
    outputs: Dict[str, Any]  # enterprise_value, equity_value, irr, etc.
    probability: Optional[Decimal] = None
    key_drivers: List[Dict[str, Any]] = []
    risk_factors: List[str] = []


class ScenarioAnalysisResponse(BaseModel):
    """Response for scenario analysis"""
    model_id: UUID
    analysis_type: str
    scenario_results: List[ScenarioResult]
    
    # Comparative analysis
    best_case: Dict[str, Any]
    worst_case: Dict[str, Any]
    most_likely: Dict[str, Any]
    risk_adjusted_value: Optional[Decimal] = None
    
    # Sensitivity analysis
    sensitivity_analysis: List[Dict[str, Any]] = []
    key_value_drivers: List[str] = []
    
    # AI insights
    scenario_insights: List[str] = []
    recommendations: List[str] = []
    
    # Metadata
    analysis_date: datetime
    processing_time: Decimal
    confidence_level: str


class ModelValidationRequest(BaseModel):
    """Request for comprehensive model validation"""
    model_id: UUID
    validation_scope: List[str] = ["structure", "calculations", "assumptions", "completeness"]
    benchmark_models: List[UUID] = []
    industry_standards: Optional[str] = None
    
    @validator('validation_scope')
    def validate_scope(cls, v):
        allowed = ["structure", "calculations", "assumptions", "completeness", "consistency", "reasonableness"]
        for scope in v:
            if scope not in allowed:
                raise ValueError(f"Validation scope must be from: {allowed}")
        return v


class ModelValidationResponse(BaseModel):
    """Response for model validation"""
    model_id: UUID
    validation_scope: List[str]
    
    # Overall validation results
    overall_score: Decimal
    validation_passed: bool
    confidence_level: str
    
    # Detailed results by category
    structure_score: Decimal
    calculation_score: Decimal
    assumption_score: Decimal
    completeness_score: Decimal
    
    # Issues and recommendations
    validation_issues: List[ValidationIssue]
    recommendations: List[str]
    critical_fixes: List[str] = []
    
    # Benchmarking (if applicable)
    benchmark_comparison: Optional[Dict[str, Any]] = None
    industry_alignment: Optional[str] = None
    
    # Metadata
    validation_date: datetime
    processing_time: Decimal
    model_version: str
