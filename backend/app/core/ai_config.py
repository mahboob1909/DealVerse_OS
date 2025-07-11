"""
AI Configuration for DealVerse OS
"""
import os
from typing import Dict, Any, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    """AI service configuration settings"""

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.1, env="OPENAI_TEMPERATURE")

    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(default=4000, env="ANTHROPIC_MAX_TOKENS")
    anthropic_temperature: float = Field(default=0.1, env="ANTHROPIC_TEMPERATURE")

    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="deepseek/deepseek-chat", env="OPENROUTER_MODEL")
    openrouter_max_tokens: int = Field(default=4000, env="OPENROUTER_MAX_TOKENS")
    openrouter_temperature: float = Field(default=0.1, env="OPENROUTER_TEMPERATURE")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")
    openrouter_site_url: Optional[str] = Field(default="https://dealverse.com", env="OPENROUTER_SITE_URL")
    openrouter_site_name: Optional[str] = Field(default="DealVerse OS", env="OPENROUTER_SITE_NAME")

    # AI Service Configuration
    preferred_ai_provider: str = Field(default="openrouter", env="AI_PROVIDER")  # "openai", "anthropic", or "openrouter"
    enable_fallback: bool = Field(default=True, env="AI_ENABLE_FALLBACK")
    request_timeout: int = Field(default=60, env="AI_REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, env="AI_MAX_RETRIES")
    
    # Document Processing Configuration
    max_document_size: int = Field(default=10 * 1024 * 1024, env="MAX_DOCUMENT_SIZE")  # 10MB
    chunk_size: int = Field(default=4000, env="DOCUMENT_CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="DOCUMENT_CHUNK_OVERLAP")
    
    # Analysis Configuration
    enable_entity_extraction: bool = Field(default=True, env="ENABLE_ENTITY_EXTRACTION")
    enable_risk_assessment: bool = Field(default=True, env="ENABLE_RISK_ASSESSMENT")
    enable_compliance_check: bool = Field(default=True, env="ENABLE_COMPLIANCE_CHECK")
    enable_financial_analysis: bool = Field(default=True, env="ENABLE_FINANCIAL_ANALYSIS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# AI Prompts Configuration
AI_PROMPTS = {
    "document_analysis": {
        "system": """You are an expert investment banking analyst specializing in document analysis for M&A transactions, due diligence, and financial analysis. Your role is to provide comprehensive, accurate, and actionable insights from business documents.

Key responsibilities:
1. Extract and analyze key financial metrics, ratios, and trends
2. Identify potential risks, red flags, and areas of concern
3. Extract important entities (companies, people, dates, amounts)
4. Assess compliance with regulatory requirements
5. Provide clear, structured analysis with confidence scores

Always provide specific, quantifiable insights and flag any uncertainties or missing information.""",
        
        "user_template": """Analyze the following document content and provide a comprehensive analysis:

Document Type: {document_type}
Document Title: {document_title}
Analysis Type: {analysis_type}

Content:
{document_content}

IMPORTANT: Respond with valid JSON in this exact structure:
{{
  "executive_summary": {{
    "summary": "2-3 sentence overview",
    "key_findings": ["finding1", "finding2", "finding3"],
    "confidence_score": 0.95
  }},
  "financial_analysis": {{
    "revenue_metrics": [{{"metric": "name", "value": "amount", "confidence": 0.9}}],
    "cost_analysis": "analysis text",
    "profitability": "analysis text",
    "key_ratios": [{{"ratio": "name", "value": "number", "confidence": 0.85}}]
  }},
  "risk_assessment": {{
    "overall_risk_level": "Low|Medium|High|Critical",
    "risk_score": 0.75,
    "identified_risks": [{{"type": "Financial|Operational|Legal|Strategic", "description": "details", "severity": "Low|Medium|High|Critical", "confidence": 0.8}}]
  }},
  "extracted_entities": {{
    "organizations": [{{"name": "Company Name", "type": "corporation|partnership|llc", "confidence": 0.9}}],
    "people": [{{"name": "John Doe", "role": "CEO|CFO|Director", "confidence": 0.95}}],
    "financial_amounts": [{{"amount": "$1,000,000", "context": "revenue|cost|investment", "confidence": 0.85}}],
    "dates": [{{"date": "2024-01-01", "context": "contract|deadline|milestone", "confidence": 0.9}}]
  }},
  "compliance_flags": [{{"issue": "description", "severity": "Low|Medium|High|Critical", "regulation": "SEC|SOX|GDPR|Other", "recommendation": "action needed", "confidence": 0.8}}],
  "recommendations": {{
    "immediate_actions": ["action1", "action2"],
    "further_investigation": ["area1", "area2"],
    "strategic_considerations": ["consideration1", "consideration2"]
  }}
}}

Ensure all confidence scores are between 0.0 and 1.0. Be precise and analytical."""
    },
    
    "entity_extraction": {
        "system": """You are an expert at extracting structured entities from business documents. Extract all relevant entities with high precision and provide confidence scores.""",
        
        "user_template": """Extract entities from this document content:

{document_content}

Extract the following entity types:
- Companies/Organizations
- People/Individuals  
- Financial Amounts
- Dates
- Locations
- Legal Terms/Clauses
- Key Metrics/KPIs

Return as structured JSON with entity type, value, context, and confidence score (0-1)."""
    },
    
    "risk_assessment": {
        "system": """You are a senior risk analyst specializing in investment banking and M&A transactions. Assess documents for potential risks, red flags, and areas requiring further investigation.""",
        
        "user_template": """Perform a comprehensive risk assessment of this document:

Document Type: {document_type}
Content: {document_content}

Analyze for:
1. Financial Risks (liquidity, solvency, profitability)
2. Operational Risks (business model, market position)
3. Legal/Regulatory Risks (compliance, litigation)
4. Strategic Risks (competitive threats, market changes)
5. Data Quality Issues (missing information, inconsistencies)

Provide risk level (Low/Medium/High/Critical) and detailed explanations."""
    },
    
    "compliance_check": {
        "system": """You are a compliance expert specializing in financial regulations, securities law, and investment banking compliance requirements.""",

        "user_template": """Review this document for compliance considerations:

Document Type: {document_type}
Content: {document_content}

Check for:
1. SEC disclosure requirements
2. Anti-money laundering (AML) considerations
3. Know Your Customer (KYC) requirements
4. GDPR/Privacy compliance
5. Industry-specific regulations
6. Missing required disclosures

Flag any compliance issues with severity levels and recommendations."""
    },

    "prospect_analysis": {
        "system": """You are an expert investment banking analyst specializing in prospect evaluation and M&A target assessment.
        Analyze companies for acquisition potential, strategic fit, and deal viability.

        Focus on:
        - Financial health and performance metrics
        - Market position and competitive advantages
        - Growth potential and scalability
        - Strategic fit for potential acquirers
        - Risk factors and mitigation strategies
        - Deal probability and valuation insights

        Provide data-driven analysis with confidence scores and actionable recommendations.""",

        "user_template": """Analyze the following company prospect for M&A potential:

{company_profile}

Analysis Type: {analysis_type}

Provide comprehensive prospect analysis in this JSON format:
{{
  "ai_score": 85,
  "confidence": 0.92,
  "financial_health": 88,
  "market_position": 82,
  "growth_potential": 90,
  "strategic_fit": 85,
  "deal_probability": 78,
  "deal_size_multiplier": 1.2,
  "risk_factors": [
    "Market volatility in target industry",
    "Integration complexity due to technology stack",
    "Regulatory approval requirements"
  ],
  "opportunities": [
    "Strong market position with growth runway",
    "Synergies with existing portfolio companies",
    "Expansion into new geographic markets"
  ],
  "key_metrics": {{
    "revenue_growth_rate": "25%",
    "profit_margins": "18%",
    "market_share": "12%",
    "customer_retention": "94%"
  }},
  "strategic_recommendations": [
    "Immediate engagement recommended",
    "Focus on technology integration planning",
    "Conduct thorough regulatory review"
  ],
  "valuation_insights": {{
    "estimated_multiple": "8.5x EBITDA",
    "comparable_deals": ["Deal A: 7.2x", "Deal B: 9.1x"],
    "premium_justification": "Market leadership and growth trajectory"
  }}
}}"""
    },

    "financial_modeling": {
        "system": """You are an expert financial modeling analyst and valuation specialist with deep expertise in DCF, LBO, comparable company analysis, and precedent transactions.

        Analyze financial models for accuracy, reasonableness, and optimization opportunities.

        Focus on:
        1. Model structure and calculation accuracy
        2. Assumption reasonableness and market alignment
        3. Scenario analysis and sensitivity testing
        4. Valuation methodology appropriateness
        5. Risk assessment and optimization opportunities

        Provide detailed, actionable insights for model improvement and validation.""",

        "user_template": """Analyze the following financial model for accuracy and optimization opportunities:

{model_data}

Analysis Type: {analysis_type}

Provide comprehensive financial model analysis in this JSON format:
{{
  "model_quality_score": 85,
  "key_insights": [
    "Revenue growth assumptions appear reasonable for the industry",
    "EBITDA margin expansion is achievable based on operational improvements",
    "Discount rate is appropriate for the risk profile"
  ],
  "risk_factors": [
    "High sensitivity to revenue growth assumptions",
    "Terminal value represents significant portion of total value",
    "Market multiple compression risk in downturn"
  ],
  "optimization_opportunities": [
    "Add working capital detail to improve accuracy",
    "Include management case scenario",
    "Enhance sensitivity analysis for key variables"
  ],
  "assumption_analysis": {{
    "revenue_growth": "reasonable",
    "margin_assumptions": "optimistic",
    "discount_rate": "market_appropriate",
    "terminal_growth": "conservative"
  }},
  "valuation_reasonableness": "reasonable",
  "recommended_scenarios": [
    "Conservative case with 20% lower growth",
    "Stress test with recession assumptions",
    "Upside case with market expansion"
  ],
  "calculation_checks": {{
    "dcf_methodology": "correct",
    "terminal_value": "reasonable",
    "working_capital": "needs_detail",
    "tax_assumptions": "appropriate"
  }},
  "confidence_level": "high"
}}

Ensure all assessments are specific and actionable for model improvement."""
    },

    "compliance_monitoring": {
        "system": """You are an expert compliance analyst and regulatory specialist with deep expertise in financial services regulations, investment banking compliance, and risk management. Your role is to provide comprehensive compliance monitoring, regulatory change detection, and risk assessment.

Key responsibilities:
1. Monitor and analyze regulatory requirements and changes
2. Identify compliance violations and potential risks
3. Assess impact of regulatory updates on business operations
4. Provide actionable compliance recommendations and remediation plans
5. Track compliance patterns and trends for proactive risk management

Always provide specific, actionable insights with confidence scores and prioritized recommendations.""",

        "user_template": """Analyze the following compliance data and provide comprehensive monitoring insights:

Compliance Context: {compliance_context}
Analysis Type: {analysis_type}
Regulatory Focus: {regulatory_focus}
Data: {compliance_data}

Provide comprehensive compliance analysis in this JSON format:
{{"compliance_score": 85, "risk_level": "medium", "violations_detected": [...], "regulatory_changes": [...], "risk_patterns": [...], "compliance_trends": {{}}, "recommendations": [...], "remediation_plan": {{}}, "monitoring_alerts": [...], "confidence_level": "high"}}"""
    }
}

# Risk scoring configuration
RISK_SCORING_CONFIG = {
    "weights": {
        "financial_risk": 0.3,
        "operational_risk": 0.25,
        "legal_risk": 0.25,
        "strategic_risk": 0.2
    },
    "thresholds": {
        "low": 30,
        "medium": 60,
        "high": 80,
        "critical": 100
    }
}

# Entity extraction configuration
ENTITY_EXTRACTION_CONFIG = {
    "confidence_threshold": 0.7,
    "max_entities_per_type": 50,
    "entity_types": [
        "PERSON",
        "ORG", 
        "MONEY",
        "DATE",
        "GPE",  # Geopolitical entity
        "PERCENT",
        "CARDINAL",  # Numbers
        "LAW",
        "PRODUCT"
    ]
}


def get_ai_settings() -> AISettings:
    """Get AI configuration settings"""
    return AISettings()


def get_ai_prompt(prompt_type: str, analysis_type: str = "system") -> str:
    """Get AI prompt template"""
    return AI_PROMPTS.get(prompt_type, {}).get(analysis_type, "")


def validate_ai_configuration() -> Dict[str, Any]:
    """Validate AI configuration and return status"""
    settings = get_ai_settings()
    status = {
        "openai_configured": bool(settings.openai_api_key),
        "anthropic_configured": bool(settings.anthropic_api_key),
        "openrouter_configured": bool(settings.openrouter_api_key),
        "preferred_provider": settings.preferred_ai_provider,
        "fallback_enabled": settings.enable_fallback
    }

    # Check if at least one provider is configured
    if not (status["openai_configured"] or status["anthropic_configured"] or status["openrouter_configured"]):
        status["error"] = "No AI provider configured. Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or OPENROUTER_API_KEY"

    return status
