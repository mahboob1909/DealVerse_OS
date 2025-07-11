#!/usr/bin/env python3
"""
Script to create sample documents for testing the Diligence Navigator
"""
import sys
import os
import json
from datetime import datetime, timedelta
from uuid import uuid4

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import get_db, engine
from app.models.document import Document
from app.models.user import User
from app.models.organization import Organization
from app.models.deal import Deal

# Sample document data
SAMPLE_DOCUMENTS = [
    {
        "title": "Audited Financial Statements 2023",
        "filename": "financial_statements_2023.pdf",
        "document_type": "financial",
        "category": "financial_statements",
        "file_size": 2457600,  # 2.4 MB
        "file_type": "application/pdf",
        "file_extension": "pdf",
        "status": "analyzed",
        "risk_score": "25",
        "ai_analysis": {
            "summary": "Clean financial statements with strong revenue growth and healthy margins",
            "key_points": ["Revenue increased 23% YoY", "EBITDA margin improved to 18%", "Strong cash position"],
            "sentiment": "positive",
            "confidence": 0.92
        },
        "key_findings": ["Strong revenue growth", "Healthy cash flow", "Conservative debt levels"],
        "compliance_status": "compliant",
        "review_status": "approved"
    },
    {
        "title": "Management Accounts Q3 2024",
        "filename": "mgmt_accounts_q3_2024.xlsx",
        "document_type": "financial",
        "category": "management_accounts",
        "file_size": 1887436,  # 1.8 MB
        "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "file_extension": "xlsx",
        "status": "analyzed",
        "risk_score": "35",
        "ai_analysis": {
            "summary": "Q3 performance shows slight margin compression but overall positive trends",
            "key_points": ["Revenue on track", "Margin pressure from increased costs", "Working capital optimization needed"],
            "sentiment": "neutral",
            "confidence": 0.87
        },
        "key_findings": ["Margin compression noted", "Cost inflation impact", "Working capital increase"],
        "compliance_status": "compliant",
        "review_status": "approved"
    },
    {
        "title": "Cash Flow Projections",
        "filename": "cash_flow_projections.xlsx",
        "document_type": "financial",
        "category": "projections",
        "file_size": 876544,  # 856 KB
        "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "file_extension": "xlsx",
        "status": "review",
        "risk_score": "55",
        "ai_analysis": {
            "summary": "Aggressive growth assumptions require validation",
            "key_points": ["High growth rates assumed", "Capex requirements significant", "Seasonal patterns not fully reflected"],
            "sentiment": "cautious",
            "confidence": 0.78
        },
        "key_findings": ["Aggressive assumptions", "High capex requirements", "Seasonal adjustments needed"],
        "compliance_status": "review_required",
        "review_status": "pending"
    },
    {
        "title": "Material Contracts Summary",
        "filename": "material_contracts.pdf",
        "document_type": "legal",
        "category": "contracts",
        "file_size": 4934656,  # 4.7 MB
        "file_type": "application/pdf",
        "file_extension": "pdf",
        "status": "flagged",
        "risk_score": "75",
        "ai_analysis": {
            "summary": "Several contracts contain concerning clauses and renewal risks",
            "key_points": ["Key customer contract expires in 6 months", "Unfavorable termination clauses", "Price escalation limitations"],
            "sentiment": "negative",
            "confidence": 0.89
        },
        "key_findings": ["Contract renewal risk", "Unfavorable terms", "Customer concentration risk"],
        "compliance_status": "non_compliant",
        "review_status": "needs_revision"
    },
    {
        "title": "Litigation Summary Report",
        "filename": "litigation_summary.pdf",
        "document_type": "legal",
        "category": "litigation",
        "file_size": 1363148,  # 1.3 MB
        "file_type": "application/pdf",
        "file_extension": "pdf",
        "status": "flagged",
        "risk_score": "85",
        "ai_analysis": {
            "summary": "Active litigation with material financial exposure",
            "key_points": ["Patent dispute with $50M exposure", "Employment lawsuit pending", "Regulatory investigation ongoing"],
            "sentiment": "negative",
            "confidence": 0.94
        },
        "key_findings": ["High financial exposure", "Multiple active cases", "Regulatory scrutiny"],
        "compliance_status": "review_required",
        "review_status": "pending"
    },
    {
        "title": "IP Portfolio Analysis",
        "filename": "ip_portfolio.pdf",
        "document_type": "legal",
        "category": "intellectual_property",
        "file_size": 2202009,  # 2.1 MB
        "file_type": "application/pdf",
        "file_extension": "pdf",
        "status": "analyzed",
        "risk_score": "20",
        "ai_analysis": {
            "summary": "Strong IP portfolio with good protection coverage",
            "key_points": ["15 patents granted", "Strong trademark protection", "Trade secrets well documented"],
            "sentiment": "positive",
            "confidence": 0.91
        },
        "key_findings": ["Strong patent portfolio", "Good trademark coverage", "Well-documented trade secrets"],
        "compliance_status": "compliant",
        "review_status": "approved"
    },
    {
        "title": "Customer Contracts Database",
        "filename": "customer_contracts.xlsx",
        "document_type": "commercial",
        "category": "customer_contracts",
        "file_size": 3565158,  # 3.4 MB
        "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "file_extension": "xlsx",
        "status": "analyzed",
        "risk_score": "30",
        "ai_analysis": {
            "summary": "Diverse customer base with reasonable contract terms",
            "key_points": ["Top 10 customers represent 45% of revenue", "Average contract length 2.5 years", "Standard payment terms"],
            "sentiment": "positive",
            "confidence": 0.85
        },
        "key_findings": ["Reasonable customer concentration", "Standard contract terms", "Good payment history"],
        "compliance_status": "compliant",
        "review_status": "approved"
    },
    {
        "title": "Market Analysis Report",
        "filename": "market_analysis.pdf",
        "document_type": "commercial",
        "category": "market_research",
        "file_size": 1677721,  # 1.6 MB
        "file_type": "application/pdf",
        "file_extension": "pdf",
        "status": "analyzed",
        "risk_score": "40",
        "ai_analysis": {
            "summary": "Market showing growth but increasing competition",
            "key_points": ["Market growing at 8% CAGR", "New competitors entering", "Technology disruption risk"],
            "sentiment": "neutral",
            "confidence": 0.82
        },
        "key_findings": ["Market growth opportunities", "Competitive pressure increasing", "Technology disruption risk"],
        "compliance_status": "compliant",
        "review_status": "approved"
    }
]

def create_sample_documents():
    """Create sample documents in the database"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get the first organization and user for testing
        organization = db.query(Organization).first()
        user = db.query(User).first()
        
        if not organization or not user:
            print("❌ No organization or user found. Please run the database initialization script first.")
            return False
        
        print(f"📁 Creating sample documents for organization: {organization.name}")
        print(f"👤 Using user: {user.email}")
        
        # Get or create a sample deal
        deal = db.query(Deal).first()
        if not deal:
            print("📊 Creating sample deal...")
            deal = Deal(
                title="TechFlow Industries Acquisition",
                description="Strategic acquisition of SaaS platform company",
                deal_type="M&A",
                deal_value=45000000,
                currency="USD",
                stage="due_diligence",
                status="active",
                organization_id=organization.id,
                created_by_id=user.id
            )
            db.add(deal)
            db.commit()
            db.refresh(deal)
        
        # Create sample documents
        created_count = 0
        for doc_data in SAMPLE_DOCUMENTS:
            # Check if document already exists
            existing_doc = db.query(Document).filter(
                Document.filename == doc_data["filename"],
                Document.organization_id == organization.id
            ).first()
            
            if existing_doc:
                print(f"⏭️  Document already exists: {doc_data['title']}")
                continue
            
            # Create document
            document = Document(
                title=doc_data["title"],
                filename=doc_data["filename"],
                file_path=f"/uploads/{doc_data['filename']}",  # Placeholder path
                file_size=doc_data["file_size"],
                file_type=doc_data["file_type"],
                file_extension=doc_data["file_extension"],
                document_type=doc_data["document_type"],
                category=doc_data.get("category"),
                status=doc_data["status"],
                is_confidential=doc_data.get("is_confidential", False),
                risk_score=doc_data.get("risk_score"),
                ai_analysis=doc_data.get("ai_analysis", {}),
                key_findings=doc_data.get("key_findings", []),
                compliance_status=doc_data.get("compliance_status", "pending"),
                review_status=doc_data.get("review_status", "pending"),

                tags=doc_data.get("tags", []),
                keywords=doc_data.get("keywords", []),
                organization_id=organization.id,
                deal_id=deal.id,
                uploaded_by_id=user.id
            )
            
            db.add(document)
            created_count += 1
            print(f"✅ Created document: {doc_data['title']}")
        
        db.commit()
        print(f"\n🎉 Successfully created {created_count} sample documents!")
        print(f"📊 Total documents in database: {db.query(Document).count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample documents: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def list_documents():
    """List all documents in the database"""
    db = next(get_db())
    
    try:
        documents = db.query(Document).all()
        print(f"\n📋 Documents in database ({len(documents)} total):")
        print("-" * 80)
        
        for doc in documents:
            risk_level = "High" if doc.risk_score and int(doc.risk_score) > 70 else \
                        "Medium" if doc.risk_score and int(doc.risk_score) > 40 else "Low"
            
            print(f"📄 {doc.title}")
            print(f"   Type: {doc.document_type} | Status: {doc.status} | Risk: {risk_level}")
            print(f"   Size: {doc.file_size:,} bytes | Created: {doc.created_at.strftime('%Y-%m-%d %H:%M')}")
            print()
            
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 DealVerse OS - Sample Documents Creator")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_documents()
    else:
        success = create_sample_documents()
        if success:
            print("\n📋 Listing created documents:")
            list_documents()
        else:
            print("\n❌ Failed to create sample documents")
            sys.exit(1)
