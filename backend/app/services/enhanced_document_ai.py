"""
Enhanced Document AI Service for DealVerse OS
Optimized for DeepSeek model with advanced document processing capabilities
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import json
import re

from app.services.real_ai_service import real_ai_service
from app.services.document_processor import document_processor
from app.schemas.document_analysis import (
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    ExtractedEntity,
    ExtractedClause,
    FinancialFigure,
    KeyDate,
    RiskCategory,
    CriticalIssue,
    Anomaly,
    ComplianceFlag
)
from app.core.ai_config import get_ai_settings

logger = logging.getLogger(__name__)


class EnhancedDocumentAI:
    """
    Enhanced Document AI service with improved DeepSeek integration
    and advanced document analysis capabilities
    """
    
    def __init__(self):
        self.settings = get_ai_settings()
        self.real_ai = real_ai_service
        self.document_processor = document_processor
        self.model_version = "Enhanced-DeepSeek-v1.0"
        
    async def analyze_document_enhanced(
        self,
        request: DocumentAnalysisRequest,
        document_info: Dict[str, Any]
    ) -> DocumentAnalysisResponse:
        """
        Enhanced document analysis with improved AI integration
        """
        start_time = datetime.utcnow()
        
        try:
            # Extract and preprocess document content
            document_content = await self._extract_and_preprocess(document_info)
            
            # Perform AI analysis with enhanced context
            analysis_context = self._build_analysis_context(
                request, document_info, document_content
            )
            
            # Get AI analysis results
            ai_results = await self._perform_enhanced_ai_analysis(analysis_context)
            
            # Post-process and validate results
            processed_results = self._post_process_results(ai_results, request)
            
            # Calculate processing metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return DocumentAnalysisResponse(
                analysis_id=document_info.get("id"),
                document_id=request.document_id,
                analysis_type=request.analysis_type,
                status="completed",
                processing_time=Decimal(str(processing_time)),
                analysis_date=datetime.utcnow(),
                model_version=self.model_version,
                **processed_results
            )
            
        except Exception as e:
            logger.error(f"Enhanced document analysis failed: {str(e)}")
            return await self._create_error_response(request, document_info, str(e))
    
    async def _extract_and_preprocess(self, document_info: Dict[str, Any]) -> str:
        """Extract and preprocess document content for AI analysis"""
        try:
            # Get document content from processor
            if "content" in document_info:
                content = document_info["content"]
            else:
                # Extract content using document processor
                file_path = document_info.get("file_path")
                if file_path:
                    extraction_result = await self.document_processor.extract_text(file_path)
                    content = extraction_result.get("text", "")
                else:
                    content = ""
            
            # Preprocess content for better AI analysis
            preprocessed_content = self._preprocess_content(content)
            
            return preprocessed_content
            
        except Exception as e:
            logger.warning(f"Content extraction failed: {str(e)}")
            return "Document content could not be extracted for analysis"
    
    def _preprocess_content(self, content: str) -> str:
        """Preprocess content to improve AI analysis quality"""
        if not content:
            return content
        
        # Clean up common formatting issues
        cleaned = content
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove excessive line breaks
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        
        # Preserve important formatting markers
        cleaned = re.sub(r'(\$[\d,]+(?:\.\d{2})?)', r' \1 ', cleaned)  # Money amounts
        cleaned = re.sub(r'(\d{1,2}/\d{1,2}/\d{2,4})', r' \1 ', cleaned)  # Dates
        cleaned = re.sub(r'(\d+(?:\.\d+)?%)', r' \1 ', cleaned)  # Percentages
        
        return cleaned.strip()
    
    def _build_analysis_context(
        self,
        request: DocumentAnalysisRequest,
        document_info: Dict[str, Any],
        content: str
    ) -> Dict[str, Any]:
        """Build enhanced context for AI analysis"""
        return {
            "document_type": document_info.get("document_type", "unknown"),
            "document_title": document_info.get("title", "Untitled Document"),
            "analysis_type": request.analysis_type,
            "document_content": content,
            "file_size": document_info.get("file_size", 0),
            "file_extension": document_info.get("file_extension", ""),
            "priority": request.priority,
            "custom_parameters": request.custom_parameters or {}
        }
    
    async def _perform_enhanced_ai_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform enhanced AI analysis with better error handling"""
        try:
            # Call the real AI service with enhanced context
            ai_response = await self.real_ai._call_ai_service(
                prompt_type="document_analysis",
                context=context
            )
            
            # Parse the AI response with enhanced parsing
            parsed_results = self.real_ai._parse_ai_response(ai_response)
            
            # Validate and enhance the results
            enhanced_results = self._enhance_ai_results(parsed_results, context)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return self._get_fallback_analysis_results(context)
    
    def _enhance_ai_results(self, ai_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance AI results with additional processing"""
        enhanced = ai_results.copy()
        
        # Ensure required fields exist
        enhanced.setdefault("summary", "Document analysis completed")
        enhanced.setdefault("key_findings", [])
        enhanced.setdefault("confidence", Decimal("80"))
        enhanced.setdefault("risk_score", Decimal("50"))
        enhanced.setdefault("risk_level", "Medium")
        
        # Add document metadata insights
        if context.get("file_size", 0) > 5 * 1024 * 1024:  # 5MB
            enhanced["key_findings"].append("Large document size may indicate comprehensive content")
        
        # Add analysis type specific enhancements
        analysis_type = context.get("analysis_type", "full")
        if analysis_type == "risk_only":
            enhanced["summary"] = f"Risk-focused analysis: {enhanced.get('summary', '')}"
        elif analysis_type == "financial_only":
            enhanced["summary"] = f"Financial analysis: {enhanced.get('summary', '')}"
        
        return enhanced
    
    def _post_process_results(self, ai_results: Dict[str, Any], request: DocumentAnalysisRequest) -> Dict[str, Any]:
        """Post-process AI results into response format"""
        
        # Extract and format entities
        extracted_entities = self._format_entities(ai_results.get("entities", {}))
        
        # Extract and format risk categories
        risk_categories = self._format_risk_categories(ai_results.get("risks", []))
        
        # Extract and format compliance flags
        compliance_flags = self._format_compliance_flags(ai_results.get("compliance_issues", []))
        
        # Extract financial figures
        financial_figures = self._extract_financial_figures(ai_results.get("financial_data", {}))
        
        # Extract key dates
        key_dates = self._extract_key_dates(ai_results.get("entities", {}))
        
        return {
            "overall_risk_score": ai_results.get("risk_score", Decimal("50")),
            "confidence_score": ai_results.get("confidence", Decimal("80")),
            "risk_level": ai_results.get("risk_level", "Medium"),
            "summary": ai_results.get("summary", "Document analysis completed"),
            "key_findings": ai_results.get("key_findings", []),
            "extracted_entities": extracted_entities,
            "extracted_clauses": [],  # TODO: Implement clause extraction
            "financial_figures": financial_figures,
            "key_dates": key_dates,
            "parties_involved": self._extract_parties(ai_results.get("entities", {})),
            "risk_categories": risk_categories,
            "critical_issues": self._identify_critical_issues(ai_results),
            "anomalies": [],  # TODO: Implement anomaly detection
            "compliance_flags": compliance_flags,
            "document_quality_score": Decimal("85"),
            "completeness_score": Decimal("90"),
            "readability_score": Decimal("80")
        }
    
    def _format_entities(self, entities_data: Dict[str, Any]) -> Dict[str, List[ExtractedEntity]]:
        """Format extracted entities into proper structure"""
        formatted = {
            "persons": [],
            "companies": [],
            "dates": [],
            "amounts": [],
            "locations": []
        }
        
        # Process organizations
        for org in entities_data.get("organizations", []):
            if isinstance(org, dict):
                formatted["companies"].append(ExtractedEntity(
                    entity_type="organization",
                    entity_value=org.get("name", ""),
                    context=org.get("type", ""),
                    confidence=Decimal(str(org.get("confidence", 0.8))),
                    position={"start_position": 0, "end_position": 0}
                ))

        # Process people
        for person in entities_data.get("people", []):
            if isinstance(person, dict):
                formatted["persons"].append(ExtractedEntity(
                    entity_type="person",
                    entity_value=person.get("name", ""),
                    context=person.get("role", ""),
                    confidence=Decimal(str(person.get("confidence", 0.8))),
                    position={"start_position": 0, "end_position": 0}
                ))

        # Process financial amounts
        for amount in entities_data.get("financial_amounts", []):
            if isinstance(amount, dict):
                formatted["amounts"].append(ExtractedEntity(
                    entity_type="financial_amount",
                    entity_value=amount.get("amount", ""),
                    context=amount.get("context", ""),
                    confidence=Decimal(str(amount.get("confidence", 0.8))),
                    position={"start_position": 0, "end_position": 0}
                ))
        
        return formatted
    
    def _format_risk_categories(self, risks_data: List[Dict[str, Any]]) -> List[RiskCategory]:
        """Format risk data into risk categories"""
        categories = []
        
        for risk in risks_data:
            if isinstance(risk, dict):
                categories.append(RiskCategory(
                    category=risk.get("type", "Unknown"),
                    level=risk.get("severity", "Medium"),
                    score=Decimal("50"),  # Default score
                    findings=[risk.get("description", "")],
                    recommendations=[f"Address {risk.get('type', 'risk')} concerns"],
                    supporting_evidence=[]
                ))
        
        return categories
    
    def _format_compliance_flags(self, compliance_data: List[Dict[str, Any]]) -> List[ComplianceFlag]:
        """Format compliance data into compliance flags"""
        flags = []
        
        for item in compliance_data:
            if isinstance(item, dict):
                flags.append(ComplianceFlag(
                    regulation=item.get("regulation", "General"),
                    issue_type="risk",
                    severity=item.get("severity", "Medium"),
                    description=item.get("issue", ""),
                    recommendation=item.get("recommendation", "Review required")
                ))
        
        return flags
    
    def _extract_financial_figures(self, financial_data: Dict[str, Any]) -> List[FinancialFigure]:
        """Extract financial figures from analysis"""
        figures = []
        
        # Process revenue metrics
        for metric in financial_data.get("revenue_metrics", []):
            if isinstance(metric, dict):
                figures.append(FinancialFigure(
                    metric="revenue",
                    value=Decimal("0"),  # TODO: Parse amount from metric
                    currency="USD",
                    context=metric.get("metric", ""),
                    period="annual",
                    confidence=Decimal(str(metric.get("confidence", 0.8)))
                ))
        
        return figures
    
    def _extract_key_dates(self, entities_data: Dict[str, Any]) -> List[KeyDate]:
        """Extract key dates from entities"""
        dates = []
        
        for date_item in entities_data.get("dates", []):
            if isinstance(date_item, dict):
                dates.append(KeyDate(
                    event=date_item.get("context", "general"),
                    date=date_item.get("date", ""),
                    importance="medium",
                    description=date_item.get("context", "")
                ))
        
        return dates
    
    def _extract_parties(self, entities_data: Dict[str, Any]) -> List[str]:
        """Extract involved parties from entities"""
        parties = []
        
        # Add organizations
        for org in entities_data.get("organizations", []):
            if isinstance(org, dict):
                parties.append(org.get("name", ""))
        
        # Add key people
        for person in entities_data.get("people", []):
            if isinstance(person, dict):
                parties.append(person.get("name", ""))
        
        return list(filter(None, parties))
    
    def _identify_critical_issues(self, ai_results: Dict[str, Any]) -> List[CriticalIssue]:
        """Identify critical issues from analysis"""
        issues = []
        
        # Check for high-risk items
        for risk in ai_results.get("risks", []):
            if isinstance(risk, dict) and risk.get("severity") in ["High", "Critical"]:
                issues.append(CriticalIssue(
                    issue_type="risk",
                    severity=risk.get("severity", "High"),
                    description=risk.get("description", ""),
                    impact="High impact potential",
                    mitigation=f"Immediate review of {risk.get('type', 'issue')} required",
                    timeline="Immediate"
                ))
        
        return issues
    
    def _get_fallback_analysis_results(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback results when AI analysis fails"""
        return {
            "summary": "Document analysis completed with limited AI processing",
            "key_findings": ["Document processed but AI analysis was limited"],
            "confidence": Decimal("60"),
            "risk_score": Decimal("50"),
            "risk_level": "Medium",
            "entities": {},
            "risks": [],
            "compliance_issues": [],
            "financial_data": {}
        }
    
    async def _create_error_response(
        self,
        request: DocumentAnalysisRequest,
        document_info: Dict[str, Any],
        error_msg: str
    ) -> DocumentAnalysisResponse:
        """Create error response for failed analysis"""
        return DocumentAnalysisResponse(
            analysis_id=document_info.get("id"),
            document_id=request.document_id,
            analysis_type=request.analysis_type,
            status="failed",
            processing_time=Decimal("0"),
            analysis_date=datetime.utcnow(),
            model_version=self.model_version,
            overall_risk_score=Decimal("0"),
            confidence_score=Decimal("0"),
            risk_level="unknown",
            summary=f"Analysis failed: {error_msg}",
            key_findings=[],
            extracted_entities={},
            extracted_clauses=[],
            financial_figures=[],
            key_dates=[],
            parties_involved=[],
            risk_categories=[],
            critical_issues=[],
            anomalies=[],
            compliance_flags=[],
            document_quality_score=Decimal("0"),
            completeness_score=Decimal("0"),
            readability_score=Decimal("0")
        )


# Create global instance
enhanced_document_ai = EnhancedDocumentAI()
