"""
CRUD operations for Document model
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate


class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    """CRUD operations for Document model"""
    
    def get_by_organization(
        self,
        db: Session,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        document_type: Optional[str] = None,
        deal_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[Document]:
        """Get documents by organization with optional filters"""
        query = (
            db.query(self.model)
            .filter(Document.organization_id == organization_id)
            .filter(Document.is_archived == False)
        )

        # Apply optional filters
        if document_type:
            query = query.filter(Document.document_type == document_type)

        if deal_id:
            query = query.filter(Document.deal_id == deal_id)

        if status:
            query = query.filter(Document.status == status)

        return query.offset(skip).limit(limit).all()
    
    def get_by_deal(
        self, 
        db: Session, 
        deal_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """Get documents by deal"""
        return (
            db.query(self.model)
            .filter(Document.deal_id == deal_id)
            .filter(Document.is_archived == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_type(
        self, 
        db: Session, 
        document_type: str,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """Get documents by type"""
        query = (
            db.query(self.model)
            .filter(Document.document_type == document_type)
            .filter(Document.is_archived == False)
        )
        
        if organization_id:
            query = query.filter(Document.organization_id == organization_id)
            
        return query.offset(skip).limit(limit).all()
    
    def get_by_category(
        self, 
        db: Session, 
        category: str,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """Get documents by category"""
        query = (
            db.query(self.model)
            .filter(Document.category == category)
            .filter(Document.is_archived == False)
        )
        
        if organization_id:
            query = query.filter(Document.organization_id == organization_id)
            
        return query.offset(skip).limit(limit).all()
    
    def get_by_status(
        self, 
        db: Session, 
        status: str,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """Get documents by status"""
        query = (
            db.query(self.model)
            .filter(Document.status == status)
            .filter(Document.is_archived == False)
        )
        
        if organization_id:
            query = query.filter(Document.organization_id == organization_id)
            
        return query.offset(skip).limit(limit).all()
    
    def get_confidential(
        self, 
        db: Session,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """Get confidential documents"""
        return (
            db.query(self.model)
            .filter(Document.organization_id == organization_id)
            .filter(Document.is_confidential == True)
            .filter(Document.is_archived == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_documents(
        self, 
        db: Session,
        query: str,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """Search documents by title, filename, or description"""
        search_query = (
            db.query(self.model)
            .filter(
                (Document.title.ilike(f"%{query}%")) |
                (Document.filename.ilike(f"%{query}%")) |
                (Document.description.ilike(f"%{query}%"))
            )
            .filter(Document.is_archived == False)
        )
        
        if organization_id:
            search_query = search_query.filter(Document.organization_id == organization_id)
            
        return search_query.offset(skip).limit(limit).all()
    
    def increment_download_count(
        self, 
        db: Session, 
        document_id: UUID
    ) -> Optional[Document]:
        """Increment download count and update last accessed"""
        document = self.get(db, id=document_id)
        if document:
            document.download_count += 1
            document.last_accessed = datetime.utcnow()
            db.commit()
            db.refresh(document)
        return document
    
    def archive_document(
        self, 
        db: Session, 
        document_id: UUID
    ) -> Optional[Document]:
        """Archive a document"""
        document = self.get(db, id=document_id)
        if document:
            document.is_archived = True
            db.commit()
            db.refresh(document)
        return document


crud_document = CRUDDocument(Document)
