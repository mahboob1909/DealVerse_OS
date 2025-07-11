"""
API v1 router configuration
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth,
    users,
    organizations,
    deals,
    clients,
    tasks,
    documents,
    financial_models,
    compliance,
    analytics,
    presentations,
    prospects,
    ai_status,
    websocket,
    reports,
    performance,
    fastspring
)

# Create API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(deals.router, prefix="/deals", tags=["deals"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(financial_models.router, prefix="/financial-models", tags=["financial-models"])
api_router.include_router(prospects.router, prefix="/prospects", tags=["prospects"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(presentations.router, prefix="/presentations", tags=["presentations"])
api_router.include_router(ai_status.router, prefix="/ai", tags=["ai-service"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(performance.router, prefix="/performance", tags=["performance"])
api_router.include_router(fastspring.router, prefix="/fastspring", tags=["payments"])
