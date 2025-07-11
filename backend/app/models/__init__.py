# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .organization import Organization
from .deal import Deal
from .client import Client
from .task import Task
from .document import Document
from .financial_model import FinancialModel
from .compliance import (
    ComplianceCategory,
    ComplianceRequirement,
    ComplianceAssessment,
    ComplianceAuditLog,
    RegulatoryUpdate
)
from .presentation import (
    Presentation,
    PresentationSlide,
    PresentationTemplate,
    PresentationComment,
    PresentationCollaboration
)
from .prospect import (
    Prospect,
    ProspectAnalysis,
    MarketIntelligence
)
from .document_analysis import (
    DocumentAnalysis,
    RiskAssessment,
    DocumentCategory,
    DocumentReview,
    DocumentComparison
)

__all__ = [
    "User",
    "Organization",
    "Deal",
    "Client",
    "Task",
    "Document",
    "FinancialModel",
    "ComplianceCategory",
    "ComplianceRequirement",
    "ComplianceAssessment",
    "ComplianceAuditLog",
    "RegulatoryUpdate",
    "Presentation",
    "PresentationSlide",
    "PresentationTemplate",
    "PresentationComment",
    "PresentationCollaboration",
    "Prospect",
    "ProspectAnalysis",
    "MarketIntelligence",
    "DocumentAnalysis",
    "RiskAssessment",
    "DocumentCategory",
    "DocumentReview",
    "DocumentComparison"
]
