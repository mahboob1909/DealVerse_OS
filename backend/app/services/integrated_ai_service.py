"""
Integrated AI Service for DealVerse OS
Combines real AI analysis with document processing and fallback capabilities
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import asyncio

from app.services.real_ai_service import real_ai_service
from app.services.document_processor import document_processor
from app.services.document_ai import DocumentAIService  # Fallback service
from app.services.enhanced_document_ai import enhanced_document_ai
from app.schemas.document_analysis import (
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    DocumentCategorizationRequest,
    DocumentCategorizationResponse,
    DocumentComparisonRequest,
    DocumentComparisonResponse
)
from app.core.ai_config import get_ai_settings, validate_ai_configuration

logger = logging.getLogger(__name__)


class IntegratedAIService:
    """
    Integrated AI service that combines:
    - Real AI analysis (OpenAI/Anthropic)
    - Document processing and text extraction
    - Fallback to mock AI when real AI fails
    """
    
    def __init__(self):
        self.settings = get_ai_settings()
        self.real_ai = real_ai_service
        self.enhanced_ai = enhanced_document_ai
        self.fallback_ai = DocumentAIService()  # Mock AI as fallback
        self.document_processor = document_processor

        # Check AI configuration
        self.ai_status = validate_ai_configuration()
        self.use_real_ai = (
            self.ai_status.get("openai_configured", False) or
            self.ai_status.get("anthropic_configured", False) or
            self.ai_status.get("openrouter_configured", False)
        )

        if self.use_real_ai:
            logger.info(f"Integrated AI Service initialized with enhanced real AI ({self.ai_status['preferred_provider']})")
        else:
            logger.warning("Integrated AI Service initialized with fallback AI only - no real AI providers configured")
    
    async def analyze_document_with_file(
        self, 
        request: DocumentAnalysisRequest,
        file_content: bytes,
        filename: str
    ) -> DocumentAnalysisResponse:
        """
        Analyze document from uploaded file
        """
        try:
            # Process the document file
            file_info, extracted_text = await self.document_processor.process_document(
                file_content, filename
            )
            
            # Enhance file info for analysis
            document_info = {
                "id": request.document_id,
                "title": filename,
                "document_type": file_info.get("document_type", "unknown"),
                "file_size": file_info.get("file_size", 0),
                "word_count": file_info.get("word_count", 0),
                "extraction_successful": file_info.get("extraction_successful", False)
            }
            
            # Perform AI analysis with enhanced service
            if self.use_real_ai and file_info.get("extraction_successful", False):
                try:
                    # Use enhanced AI service for better analysis
                    return await self.enhanced_ai.analyze_document_enhanced(
                        request, document_info
                    )
                except Exception as e:
                    logger.warning(f"Enhanced AI analysis failed, trying standard real AI: {str(e)}")
                    try:
                        return await self.real_ai.analyze_document(
                            request, document_info, extracted_text
                        )
                    except Exception as e2:
                        logger.warning(f"Real AI analysis also failed, falling back to mock AI: {str(e2)}")
                        return await self.fallback_ai.analyze_document(request, document_info)
            else:
                # Use fallback AI
                return await self.fallback_ai.analyze_document(request, document_info)
                
        except Exception as e:
            logger.error(f"Error in document analysis with file: {str(e)}")
            # Return error response
            return DocumentAnalysisResponse(
                analysis_id=request.document_id,
                document_id=request.document_id,
                analysis_type=request.analysis_type,
                status="error",
                processing_time=Decimal("1.0"),
                analysis_date=datetime.utcnow(),
                model_version="Error-v1.0",
                overall_risk_score=Decimal("50"),
                confidence_score=Decimal("0"),
                risk_level="unknown",
                summary=f"Analysis failed: {str(e)}",
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
    
    async def analyze_document(
        self, 
        request: DocumentAnalysisRequest,
        document_info: Dict[str, Any]
    ) -> DocumentAnalysisResponse:
        """
        Analyze document with existing document info (no file processing)
        """
        try:
            if self.use_real_ai:
                try:
                    # For real AI, we need document content
                    document_content = document_info.get("content", "")

                    # If no content provided, try to extract from file path
                    if not document_content and document_info.get("file_path"):
                        try:
                            document_content = await self.document_processor.extract_text(
                                document_info.get("file_path", ""),
                                document_info.get("file_type", "")
                            )
                        except Exception as extract_error:
                            logger.warning(f"Failed to extract content from file: {str(extract_error)}")

                    # Provide fallback content if still empty
                    if not document_content or len(document_content.strip()) < 10:
                        document_content = f"""
Document Analysis Request
Title: {document_info.get('title', 'Unknown Document')}
Type: {document_info.get('document_type', 'unknown')}
File Type: {document_info.get('file_type', 'unknown')}
Size: {document_info.get('file_size', 0)} bytes

Note: Document content could not be extracted or is empty.
This analysis is based on metadata only.
"""

                    logger.info(f"Performing real AI analysis for: {document_info.get('title', 'Unknown')}")
                    result = await self.real_ai.analyze_document(
                        request, document_info, document_content
                    )
                    logger.info(f"Real AI analysis completed successfully")
                    return result

                except Exception as e:
                    logger.warning(f"Real AI analysis failed: {str(e)}")
                    if self.settings.enable_fallback:
                        logger.info("Falling back to enhanced AI service")
                        return await self.enhanced_ai.analyze_document_enhanced(request, document_info)
                    else:
                        logger.info("Falling back to mock AI service")
                        return await self.fallback_ai.analyze_document(request, document_info)
            else:
                # Use enhanced AI service when real AI is not available
                logger.info(f"Using enhanced AI service for: {document_info.get('title', 'Unknown')}")
                try:
                    return await self.enhanced_ai.analyze_document_enhanced(request, document_info)
                except Exception as e:
                    logger.warning(f"Enhanced AI analysis failed: {str(e)}")
                    logger.info("Falling back to mock AI service")
                    return await self.fallback_ai.analyze_document(request, document_info)
                
        except Exception as e:
            logger.error(f"Error in document analysis: {str(e)}")
            return await self._create_error_response(request, str(e))
    
    async def assess_risk_with_file(
        self,
        request: RiskAssessmentRequest,
        file_content: bytes,
        filename: str
    ) -> RiskAssessmentResponse:
        """
        Assess risk from uploaded file
        """
        try:
            # Process the document file
            file_info, extracted_text = await self.document_processor.process_document(
                file_content, filename
            )
            
            document_info = {
                "id": request.document_id,
                "title": filename,
                "document_type": file_info.get("document_type", "unknown"),
                "extraction_successful": file_info.get("extraction_successful", False)
            }
            
            # Perform risk assessment
            if self.use_real_ai and file_info.get("extraction_successful", False):
                try:
                    return await self.real_ai.assess_risk(
                        request, document_info, extracted_text
                    )
                except Exception as e:
                    logger.warning(f"Real AI risk assessment failed, falling back to mock AI: {str(e)}")
                    return await self.fallback_ai.assess_risk(request, document_info)
            else:
                # Use fallback AI
                return await self.fallback_ai.assess_risk(request, document_info)
                
        except Exception as e:
            logger.error(f"Error in risk assessment with file: {str(e)}")
            return RiskAssessmentResponse(
                assessment_id=request.document_id,
                document_id=request.document_id,
                overall_risk_score=Decimal("50"),
                risk_level="unknown",
                assessment_date=datetime.utcnow(),
                processing_time=Decimal("1.0"),
                model_version="Error-v1.0",
                risk_categories=[],
                critical_issues=[],
                recommendations=[f"Risk assessment failed: {str(e)}"]
            )
    
    async def assess_risk(
        self,
        request: RiskAssessmentRequest,
        document_info: Dict[str, Any]
    ) -> RiskAssessmentResponse:
        """
        Assess risk with existing document info
        """
        try:
            if self.use_real_ai:
                try:
                    document_content = document_info.get("content", "")
                    if not document_content:
                        document_content = "Document content not available for AI analysis"
                    
                    return await self.real_ai.assess_risk(
                        request, document_info, document_content
                    )
                except Exception as e:
                    logger.warning(f"Real AI risk assessment failed, falling back to mock AI: {str(e)}")
                    return await self.fallback_ai.assess_risk(request, document_info)
            else:
                return await self.fallback_ai.assess_risk(request, document_info)
                
        except Exception as e:
            logger.error(f"Error in risk assessment: {str(e)}")
            return await self._create_risk_error_response(request, str(e))
    
    async def categorize_document(
        self,
        request: DocumentCategorizationRequest,
        document_info: Dict[str, Any]
    ) -> DocumentCategorizationResponse:
        """
        Categorize document (always uses fallback for now)
        """
        return await self.fallback_ai.categorize_document(request, document_info)
    
    async def compare_documents(
        self,
        request: DocumentComparisonRequest,
        document1_info: Dict[str, Any],
        document2_info: Dict[str, Any]
    ) -> DocumentComparisonResponse:
        """
        Compare documents (always uses fallback for now)
        """
        return await self.fallback_ai.compare_documents(request, document1_info, document2_info)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        real_ai_status = self.real_ai.get_service_status() if self.use_real_ai else {}
        
        return {
            "service_name": "Integrated AI Service",
            "version": "1.0.0",
            "real_ai_enabled": self.use_real_ai,
            "ai_configuration": self.ai_status,
            "real_ai_status": real_ai_status,
            "fallback_available": True,
            "document_processing_enabled": True,
            "supported_formats": list(self.document_processor.SUPPORTED_FORMATS.keys())
        }
    
    async def _create_error_response(self, request: DocumentAnalysisRequest, error_msg: str) -> DocumentAnalysisResponse:
        """Create error response for document analysis"""
        return DocumentAnalysisResponse(
            analysis_id=request.document_id,
            document_id=request.document_id,
            analysis_type=request.analysis_type,
            status="error",
            processing_time=Decimal("1.0"),
            analysis_date=datetime.utcnow(),
            model_version="Error-v1.0",
            overall_risk_score=Decimal("50"),
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
    
    async def _create_risk_error_response(self, request: RiskAssessmentRequest, error_msg: str) -> RiskAssessmentResponse:
        """Create error response for risk assessment"""
        return RiskAssessmentResponse(
            assessment_id=request.document_id,
            document_id=request.document_id,
            overall_risk_score=Decimal("50"),
            risk_level="unknown",
            assessment_date=datetime.utcnow(),
            processing_time=Decimal("1.0"),
            model_version="Error-v1.0",
            risk_categories=[],
            critical_issues=[],
            recommendations=[f"Risk assessment failed: {error_msg}"]
        )


# Global instance
integrated_ai_service = IntegratedAIService()
