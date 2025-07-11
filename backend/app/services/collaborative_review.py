"""
Collaborative Review System for DealVerse OS
Manages document reviews, approvals, and collaborative workflows
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy.orm import Session
from app.services.realtime_notifications import realtime_notifications
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


class ReviewStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    COMPLETED = "completed"


class ReviewPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class CollaborativeReviewService:
    """Service for managing collaborative document reviews"""
    
    def __init__(self):
        self.active_reviews: Dict[str, Dict[str, Any]] = {}
        self.review_workflows: Dict[str, List[Dict[str, Any]]] = {}
        self.review_templates: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default review templates
        self._initialize_review_templates()
    
    def _initialize_review_templates(self):
        """Initialize default review templates"""
        self.review_templates = {
            "financial_review": {
                "name": "Financial Document Review",
                "description": "Standard review for financial documents",
                "required_roles": ["financial_analyst", "manager"],
                "review_criteria": [
                    "Accuracy of financial data",
                    "Compliance with accounting standards",
                    "Risk assessment completeness",
                    "Supporting documentation"
                ],
                "approval_threshold": 2,
                "auto_escalation_hours": 24
            },
            "legal_review": {
                "name": "Legal Document Review",
                "description": "Standard review for legal documents",
                "required_roles": ["legal_counsel", "compliance_officer"],
                "review_criteria": [
                    "Legal compliance",
                    "Contract terms accuracy",
                    "Risk mitigation clauses",
                    "Regulatory requirements"
                ],
                "approval_threshold": 1,
                "auto_escalation_hours": 48
            },
            "due_diligence_review": {
                "name": "Due Diligence Review",
                "description": "Comprehensive review for due diligence documents",
                "required_roles": ["analyst", "manager", "vp"],
                "review_criteria": [
                    "Data completeness",
                    "Risk identification",
                    "Compliance verification",
                    "Strategic implications"
                ],
                "approval_threshold": 3,
                "auto_escalation_hours": 12
            }
        }
    
    async def create_review_workflow(
        self,
        document_id: str,
        review_type: str,
        requested_by: str,
        reviewers: List[str],
        priority: ReviewPriority = ReviewPriority.MEDIUM,
        deadline: datetime = None,
        custom_criteria: List[str] = None
    ) -> str:
        """Create a new review workflow for a document"""
        
        review_id = str(uuid4())
        
        # Get review template
        template = self.review_templates.get(review_type, {})
        
        # Set deadline if not provided
        if not deadline:
            hours_to_add = template.get("auto_escalation_hours", 24)
            deadline = datetime.utcnow() + timedelta(hours=hours_to_add)
        
        # Create review workflow
        workflow = {
            "review_id": review_id,
            "document_id": document_id,
            "review_type": review_type,
            "template": template,
            "requested_by": requested_by,
            "reviewers": reviewers,
            "priority": priority.value,
            "deadline": deadline,
            "status": ReviewStatus.PENDING.value,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "review_criteria": custom_criteria or template.get("review_criteria", []),
            "approval_threshold": template.get("approval_threshold", len(reviewers)),
            "reviews": {},
            "comments": [],
            "approvals": 0,
            "rejections": 0
        }
        
        self.review_workflows[review_id] = workflow
        
        # Notify reviewers
        await self._notify_reviewers_assigned(review_id, reviewers)
        
        # Send real-time notification
        await realtime_notifications.send_custom_notification(
            "review_workflow_created",
            {
                "review_id": review_id,
                "document_id": document_id,
                "review_type": review_type,
                "priority": priority.value,
                "deadline": deadline.isoformat(),
                "reviewers": reviewers
            },
            "document",
            document_id
        )
        
        logger.info(f"Created review workflow {review_id} for document {document_id}")
        return review_id
    
    async def submit_review(
        self,
        review_id: str,
        reviewer_id: str,
        decision: str,  # approve, reject, request_changes
        comments: str = None,
        criteria_scores: Dict[str, int] = None,
        attachments: List[str] = None
    ) -> Dict[str, Any]:
        """Submit a review for a document"""
        
        if review_id not in self.review_workflows:
            raise ValueError(f"Review workflow {review_id} not found")
        
        workflow = self.review_workflows[review_id]
        
        # Check if reviewer is authorized
        if reviewer_id not in workflow["reviewers"]:
            raise ValueError(f"User {reviewer_id} is not authorized to review this document")
        
        # Check if already reviewed
        if reviewer_id in workflow["reviews"]:
            raise ValueError(f"User {reviewer_id} has already submitted a review")
        
        # Create review entry
        review_entry = {
            "reviewer_id": reviewer_id,
            "decision": decision,
            "comments": comments,
            "criteria_scores": criteria_scores or {},
            "attachments": attachments or [],
            "submitted_at": datetime.utcnow()
        }
        
        workflow["reviews"][reviewer_id] = review_entry
        workflow["updated_at"] = datetime.utcnow()
        
        # Update counters
        if decision == "approve":
            workflow["approvals"] += 1
        elif decision == "reject":
            workflow["rejections"] += 1
        
        # Add comment to workflow
        if comments:
            workflow["comments"].append({
                "comment_id": str(uuid4()),
                "reviewer_id": reviewer_id,
                "comment": comments,
                "timestamp": datetime.utcnow()
            })
        
        # Check if workflow is complete
        await self._check_workflow_completion(review_id)
        
        # Send real-time notifications
        await self._notify_review_submitted(review_id, reviewer_id, decision)
        
        return {
            "review_id": review_id,
            "status": workflow["status"],
            "approvals": workflow["approvals"],
            "rejections": workflow["rejections"],
            "remaining_reviewers": len(workflow["reviewers"]) - len(workflow["reviews"])
        }
    
    async def _check_workflow_completion(self, review_id: str):
        """Check if review workflow is complete and update status"""
        workflow = self.review_workflows[review_id]
        
        total_reviews = len(workflow["reviews"])
        total_reviewers = len(workflow["reviewers"])
        approval_threshold = workflow["approval_threshold"]
        
        # Check for completion conditions
        if workflow["rejections"] > 0:
            # Any rejection fails the review
            workflow["status"] = ReviewStatus.REJECTED.value
            await self._notify_workflow_completed(review_id, "rejected")
        
        elif workflow["approvals"] >= approval_threshold:
            # Sufficient approvals
            workflow["status"] = ReviewStatus.APPROVED.value
            await self._notify_workflow_completed(review_id, "approved")
        
        elif total_reviews == total_reviewers:
            # All reviewers have responded but not enough approvals
            workflow["status"] = ReviewStatus.CHANGES_REQUESTED.value
            await self._notify_workflow_completed(review_id, "changes_requested")
        
        elif total_reviews > 0:
            # Some reviews submitted, workflow in progress
            workflow["status"] = ReviewStatus.IN_PROGRESS.value
    
    async def _notify_reviewers_assigned(self, review_id: str, reviewers: List[str]):
        """Notify reviewers about new assignment"""
        workflow = self.review_workflows[review_id]
        
        for reviewer_id in reviewers:
            await realtime_notifications.send_custom_notification(
                "review_assigned",
                {
                    "review_id": review_id,
                    "document_id": workflow["document_id"],
                    "review_type": workflow["review_type"],
                    "priority": workflow["priority"],
                    "deadline": workflow["deadline"].isoformat(),
                    "review_criteria": workflow["review_criteria"]
                },
                "user",
                reviewer_id
            )
    
    async def _notify_review_submitted(self, review_id: str, reviewer_id: str, decision: str):
        """Notify about submitted review"""
        workflow = self.review_workflows[review_id]
        
        await realtime_notifications.send_custom_notification(
            "review_submitted",
            {
                "review_id": review_id,
                "document_id": workflow["document_id"],
                "reviewer_id": reviewer_id,
                "decision": decision,
                "approvals": workflow["approvals"],
                "rejections": workflow["rejections"],
                "status": workflow["status"]
            },
            "document",
            workflow["document_id"]
        )
    
    async def _notify_workflow_completed(self, review_id: str, final_status: str):
        """Notify about completed workflow"""
        workflow = self.review_workflows[review_id]
        
        await realtime_notifications.send_custom_notification(
            "review_workflow_completed",
            {
                "review_id": review_id,
                "document_id": workflow["document_id"],
                "final_status": final_status,
                "approvals": workflow["approvals"],
                "rejections": workflow["rejections"],
                "completion_time": datetime.utcnow().isoformat()
            },
            "document",
            workflow["document_id"]
        )
    
    def get_review_workflow(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get review workflow details"""
        return self.review_workflows.get(review_id)
    
    def get_document_reviews(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all review workflows for a document"""
        return [
            workflow for workflow in self.review_workflows.values()
            if workflow["document_id"] == document_id
        ]
    
    def get_user_pending_reviews(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending reviews for a user"""
        pending_reviews = []
        
        for workflow in self.review_workflows.values():
            if (user_id in workflow["reviewers"] and 
                user_id not in workflow["reviews"] and
                workflow["status"] in [ReviewStatus.PENDING.value, ReviewStatus.IN_PROGRESS.value]):
                
                pending_reviews.append({
                    "review_id": workflow["review_id"],
                    "document_id": workflow["document_id"],
                    "review_type": workflow["review_type"],
                    "priority": workflow["priority"],
                    "deadline": workflow["deadline"],
                    "created_at": workflow["created_at"]
                })
        
        return pending_reviews
    
    async def escalate_overdue_reviews(self):
        """Escalate overdue reviews"""
        current_time = datetime.utcnow()
        
        for review_id, workflow in self.review_workflows.items():
            if (workflow["status"] in [ReviewStatus.PENDING.value, ReviewStatus.IN_PROGRESS.value] and
                workflow["deadline"] < current_time):
                
                # Mark as overdue and notify
                workflow["status"] = "overdue"
                
                await realtime_notifications.send_custom_notification(
                    "review_overdue",
                    {
                        "review_id": review_id,
                        "document_id": workflow["document_id"],
                        "overdue_hours": (current_time - workflow["deadline"]).total_seconds() / 3600,
                        "pending_reviewers": [
                            r for r in workflow["reviewers"] 
                            if r not in workflow["reviews"]
                        ]
                    },
                    "document",
                    workflow["document_id"]
                )


# Global collaborative review service instance
collaborative_review = CollaborativeReviewService()
