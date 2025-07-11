# CRUD operations package
from .crud_user import crud_user
from .crud_organization import crud_organization
from .crud_deal import crud_deal
from .crud_client import crud_client
from .crud_task import crud_task
from .crud_document import crud_document
from .crud_financial_model import crud_financial_model
from .crud_presentation import (
    crud_presentation,
    crud_presentation_slide,
    crud_presentation_template,
    crud_presentation_comment,
    crud_presentation_collaboration
)
from .crud_prospect import (
    crud_prospect,
    crud_prospect_analysis,
    crud_market_intelligence
)
from .crud_document_analysis import (
    crud_document_analysis,
    crud_risk_assessment,
    crud_document_category,
    crud_document_review,
    crud_document_comparison
)
