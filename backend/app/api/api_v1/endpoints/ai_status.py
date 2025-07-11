"""
AI Service Status and Configuration Endpoints
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException

from app.api import deps
from app.models.user import User
from app.services.integrated_ai_service import integrated_ai_service
from app.core.ai_config import validate_ai_configuration

router = APIRouter()


@router.get("/status", response_model=Dict[str, Any])
def get_ai_service_status(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get comprehensive AI service status and configuration
    """
    try:
        # Get service status
        service_status = integrated_ai_service.get_service_status()
        
        # Get AI configuration validation
        ai_config_status = validate_ai_configuration()
        
        return {
            "status": "operational" if service_status.get("real_ai_enabled", False) else "fallback_only",
            "service_info": service_status,
            "configuration": ai_config_status,
            "capabilities": {
                "document_analysis": True,
                "risk_assessment": True,
                "entity_extraction": service_status.get("real_ai_enabled", False),
                "compliance_checking": service_status.get("real_ai_enabled", False),
                "financial_analysis": service_status.get("real_ai_enabled", False),
                "document_processing": service_status.get("document_processing_enabled", True)
            },
            "supported_formats": service_status.get("supported_formats", []),
            "recommendations": _get_service_recommendations(service_status, ai_config_status)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get AI service status: {str(e)}"
        )


@router.get("/health", response_model=Dict[str, Any])
def check_ai_service_health(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Quick health check for AI services
    """
    try:
        service_status = integrated_ai_service.get_service_status()
        
        health_status = {
            "healthy": True,
            "services": {
                "integrated_ai": True,
                "real_ai": service_status.get("real_ai_enabled", False),
                "fallback_ai": service_status.get("fallback_available", True),
                "document_processor": service_status.get("document_processing_enabled", True)
            },
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }
        
        # Check if any critical services are down
        if not any(health_status["services"].values()):
            health_status["healthy"] = False
            
        return health_status
        
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "services": {
                "integrated_ai": False,
                "real_ai": False,
                "fallback_ai": False,
                "document_processor": False
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }


@router.get("/configuration", response_model=Dict[str, Any])
def get_ai_configuration(
    current_user: User = Depends(deps.check_permission("admin:view")),
) -> Any:
    """
    Get AI configuration details (admin only)
    """
    try:
        ai_config_status = validate_ai_configuration()
        service_status = integrated_ai_service.get_service_status()
        
        return {
            "ai_providers": {
                "openai": {
                    "configured": ai_config_status.get("openai_configured", False),
                    "model": service_status.get("real_ai_status", {}).get("model_versions", {}).get("openai", "N/A")
                },
                "anthropic": {
                    "configured": ai_config_status.get("anthropic_configured", False),
                    "model": service_status.get("real_ai_status", {}).get("model_versions", {}).get("anthropic", "N/A")
                }
            },
            "preferred_provider": ai_config_status.get("preferred_provider", "openai"),
            "fallback_enabled": ai_config_status.get("fallback_enabled", True),
            "document_processing": {
                "max_file_size": "10MB",
                "supported_formats": len(service_status.get("supported_formats", [])),
                "ocr_enabled": True
            },
            "analysis_features": {
                "entity_extraction": True,
                "risk_assessment": True,
                "compliance_checking": True,
                "financial_analysis": True
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get AI configuration: {str(e)}"
        )


@router.post("/test", response_model=Dict[str, Any])
async def test_ai_service(
    current_user: User = Depends(deps.check_permission("admin:test")),
) -> Any:
    """
    Test AI service with a simple analysis (admin only)
    """
    try:
        from app.schemas.document_analysis import DocumentAnalysisRequest
        
        # Create a test analysis request
        test_request = DocumentAnalysisRequest(
            document_id="test-document-id",
            analysis_type="full",
            priority="low"
        )
        
        test_document_info = {
            "id": "test-document-id",
            "title": "Test Document",
            "filename": "test.txt",
            "document_type": "txt",
            "content": "This is a test document for AI service validation. It contains sample text to verify that the AI analysis pipeline is working correctly."
        }
        
        # Perform test analysis
        result = await integrated_ai_service.analyze_document(test_request, test_document_info)
        
        return {
            "test_status": "success",
            "analysis_completed": True,
            "model_version": result.model_version,
            "processing_time": float(result.processing_time),
            "confidence_score": float(result.confidence_score),
            "risk_score": float(result.overall_risk_score),
            "summary": result.summary[:100] + "..." if len(result.summary) > 100 else result.summary
        }
        
    except Exception as e:
        return {
            "test_status": "failed",
            "error": str(e),
            "analysis_completed": False
        }


def _get_service_recommendations(service_status: Dict[str, Any], ai_config_status: Dict[str, Any]) -> list:
    """Generate recommendations based on service status"""
    recommendations = []
    
    if not service_status.get("real_ai_enabled", False):
        if not ai_config_status.get("openai_configured", False) and not ai_config_status.get("anthropic_configured", False):
            recommendations.append("Configure at least one AI provider (OpenAI or Anthropic) for enhanced analysis capabilities")
        elif "error" in ai_config_status:
            recommendations.append(f"Fix AI configuration: {ai_config_status['error']}")
    
    if not ai_config_status.get("fallback_enabled", True):
        recommendations.append("Consider enabling fallback AI to ensure service availability")
    
    if service_status.get("preferred_provider") == "openai" and not ai_config_status.get("openai_configured", False):
        recommendations.append("OpenAI is set as preferred provider but not configured")
    
    if service_status.get("preferred_provider") == "anthropic" and not ai_config_status.get("anthropic_configured", False):
        recommendations.append("Anthropic is set as preferred provider but not configured")
    
    if not recommendations:
        recommendations.append("AI service is properly configured and operational")
    
    return recommendations
