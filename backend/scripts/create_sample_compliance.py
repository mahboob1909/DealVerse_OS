#!/usr/bin/env python3
"""
Script to create sample compliance data for testing the Compliance Guardian
"""
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import get_db, engine
from app.models.compliance import (
    ComplianceCategory, 
    ComplianceRequirement, 
    ComplianceAssessment, 
    RegulatoryUpdate,
    ComplianceStatus
)
from app.models.user import User
from app.models.organization import Organization

# Sample compliance data
SAMPLE_CATEGORIES = [
    {
        "name": "SEC Compliance",
        "description": "Securities and Exchange Commission regulatory requirements",
        "code": "SEC",
        "priority_level": 1,
        "review_frequency_days": 30,
        "regulatory_body": "Securities and Exchange Commission",
        "regulation_url": "https://www.sec.gov/rules"
    },
    {
        "name": "FINRA Regulations",
        "description": "Financial Industry Regulatory Authority compliance requirements",
        "code": "FINRA",
        "priority_level": 1,
        "review_frequency_days": 30,
        "regulatory_body": "Financial Industry Regulatory Authority",
        "regulation_url": "https://www.finra.org/rules-guidance"
    },
    {
        "name": "Anti-Money Laundering",
        "description": "AML and BSA compliance requirements",
        "code": "AML",
        "priority_level": 1,
        "review_frequency_days": 90,
        "regulatory_body": "FinCEN",
        "regulation_url": "https://www.fincen.gov/resources/statutes-regulations"
    },
    {
        "name": "Data Privacy",
        "description": "GDPR, CCPA and other data privacy regulations",
        "code": "PRIVACY",
        "priority_level": 2,
        "review_frequency_days": 180,
        "regulatory_body": "Various",
        "regulation_url": "https://gdpr.eu/"
    }
]

SAMPLE_REQUIREMENTS = [
    # SEC Requirements
    {
        "category_code": "SEC",
        "title": "Form ADV Annual Update",
        "description": "Annual update of Form ADV registration",
        "requirement_code": "SEC-ADV-001",
        "is_mandatory": True,
        "risk_level": "high",
        "required_documents": ["Form ADV Part 1", "Form ADV Part 2", "Financial statements"],
        "evidence_requirements": "Filed Form ADV with SEC within 90 days of fiscal year end",
        "review_frequency_days": 365,
        "status": ComplianceStatus.COMPLIANT,
        "completion_percentage": 100.0
    },
    {
        "category_code": "SEC",
        "title": "Investment Adviser Brochure Delivery",
        "description": "Deliver brochure to clients annually and upon material changes",
        "requirement_code": "SEC-ADV-002",
        "is_mandatory": True,
        "risk_level": "medium",
        "required_documents": ["Form ADV Part 2A", "Delivery receipts"],
        "evidence_requirements": "Documentation of brochure delivery to all clients",
        "review_frequency_days": 365,
        "status": ComplianceStatus.COMPLIANT,
        "completion_percentage": 95.0
    },
    # FINRA Requirements
    {
        "category_code": "FINRA",
        "title": "Books and Records Maintenance",
        "description": "Maintain required books and records per FINRA Rule 4511",
        "requirement_code": "FINRA-4511-001",
        "is_mandatory": True,
        "risk_level": "high",
        "required_documents": ["Trading records", "Customer records", "Financial records"],
        "evidence_requirements": "Complete and accurate books and records maintained",
        "review_frequency_days": 90,
        "status": ComplianceStatus.WARNING,
        "completion_percentage": 85.0
    },
    {
        "category_code": "FINRA",
        "title": "Annual Compliance Meeting",
        "description": "Conduct annual compliance meeting per FINRA Rule 3110",
        "requirement_code": "FINRA-3110-001",
        "is_mandatory": True,
        "risk_level": "medium",
        "required_documents": ["Meeting agenda", "Attendance records", "Meeting minutes"],
        "evidence_requirements": "Documentation of annual compliance meeting",
        "review_frequency_days": 365,
        "status": ComplianceStatus.PENDING,
        "completion_percentage": 60.0
    },
    # AML Requirements
    {
        "category_code": "AML",
        "title": "Customer Identification Program",
        "description": "Maintain and update Customer Identification Program",
        "requirement_code": "AML-CIP-001",
        "is_mandatory": True,
        "risk_level": "high",
        "required_documents": ["CIP procedures", "Customer verification records"],
        "evidence_requirements": "Current CIP procedures and verification documentation",
        "review_frequency_days": 180,
        "status": ComplianceStatus.COMPLIANT,
        "completion_percentage": 100.0
    },
    {
        "category_code": "AML",
        "title": "Suspicious Activity Monitoring",
        "description": "Monitor and report suspicious activities",
        "requirement_code": "AML-SAR-001",
        "is_mandatory": True,
        "risk_level": "high",
        "required_documents": ["SAR filings", "Monitoring procedures"],
        "evidence_requirements": "Documentation of monitoring activities and SAR filings",
        "review_frequency_days": 90,
        "status": ComplianceStatus.COMPLIANT,
        "completion_percentage": 98.0
    },
    # Privacy Requirements
    {
        "category_code": "PRIVACY",
        "title": "Privacy Policy Updates",
        "description": "Maintain current privacy policy and notify clients of changes",
        "requirement_code": "PRIVACY-001",
        "is_mandatory": True,
        "risk_level": "medium",
        "required_documents": ["Privacy policy", "Client notifications"],
        "evidence_requirements": "Current privacy policy and notification records",
        "review_frequency_days": 365,
        "status": ComplianceStatus.WARNING,
        "completion_percentage": 75.0
    }
]

SAMPLE_REGULATORY_UPDATES = [
    {
        "title": "SEC Adopts New Marketing Rule for Investment Advisers",
        "description": "The SEC adopted new Rule 206(4)-1 under the Investment Advisers Act, replacing the current advertising and cash solicitation rules.",
        "update_type": "new_regulation",
        "source": "SEC",
        "publication_date": datetime(2024, 1, 15),
        "effective_date": datetime(2024, 5, 1),
        "impact_level": "high",
        "affected_categories": ["SEC"],
        "content": "The new marketing rule modernizes the regulatory framework for investment adviser marketing...",
        "source_url": "https://www.sec.gov/rules/final/2020/ia-5653.pdf",
        "is_reviewed": True
    },
    {
        "title": "FINRA Updates Guidance on Digital Assets",
        "description": "FINRA provides updated guidance on digital asset activities and compliance considerations.",
        "update_type": "guidance",
        "source": "FINRA",
        "publication_date": datetime(2024, 2, 10),
        "effective_date": datetime(2024, 3, 1),
        "impact_level": "medium",
        "affected_categories": ["FINRA"],
        "content": "FINRA reminds firms of their obligations when engaging in digital asset activities...",
        "source_url": "https://www.finra.org/rules-guidance/notices/21-16",
        "is_reviewed": False
    },
    {
        "title": "FinCEN Issues Final Rule on Beneficial Ownership",
        "description": "FinCEN issues final rule requiring reporting of beneficial ownership information.",
        "update_type": "amendment",
        "source": "FinCEN",
        "publication_date": datetime(2024, 1, 20),
        "effective_date": datetime(2024, 6, 1),
        "impact_level": "high",
        "affected_categories": ["AML"],
        "content": "The final rule requires certain entities to report beneficial ownership information...",
        "source_url": "https://www.fincen.gov/news/news-releases",
        "is_reviewed": False
    }
]

def create_sample_compliance_data():
    """Create sample compliance data in the database"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get the first organization and user for testing
        organization = db.query(Organization).first()
        user = db.query(User).first()
        
        if not organization or not user:
            print("❌ No organization or user found. Please run the database initialization script first.")
            return False
        
        print(f"🛡️ Creating sample compliance data for organization: {organization.name}")
        print(f"👤 Using user: {user.email}")
        
        # Create compliance categories
        categories = {}
        for cat_data in SAMPLE_CATEGORIES:
            # Check if category already exists
            existing_category = db.query(ComplianceCategory).filter(
                ComplianceCategory.code == cat_data["code"],
                ComplianceCategory.organization_id == organization.id
            ).first()
            
            if existing_category:
                print(f"⏭️  Category already exists: {cat_data['name']}")
                categories[cat_data["code"]] = existing_category
                continue
            
            # Create category
            category = ComplianceCategory(
                name=cat_data["name"],
                description=cat_data["description"],
                code=cat_data["code"],
                priority_level=cat_data["priority_level"],
                review_frequency_days=cat_data["review_frequency_days"],
                regulatory_body=cat_data["regulatory_body"],
                regulation_url=cat_data["regulation_url"],
                organization_id=organization.id
            )
            
            db.add(category)
            db.flush()  # Get the ID
            categories[cat_data["code"]] = category
            print(f"✅ Created category: {cat_data['name']}")
        
        # Create compliance requirements
        for req_data in SAMPLE_REQUIREMENTS:
            category = categories.get(req_data["category_code"])
            if not category:
                continue
            
            # Check if requirement already exists
            existing_req = db.query(ComplianceRequirement).filter(
                ComplianceRequirement.requirement_code == req_data["requirement_code"],
                ComplianceRequirement.organization_id == organization.id
            ).first()
            
            if existing_req:
                print(f"⏭️  Requirement already exists: {req_data['title']}")
                continue
            
            # Calculate dates
            due_date = datetime.utcnow() + timedelta(days=30)
            next_review = datetime.utcnow() + timedelta(days=req_data["review_frequency_days"])
            
            requirement = ComplianceRequirement(
                title=req_data["title"],
                description=req_data["description"],
                requirement_code=req_data["requirement_code"],
                is_mandatory=req_data["is_mandatory"],
                risk_level=req_data["risk_level"],
                required_documents=req_data["required_documents"],
                evidence_requirements=req_data["evidence_requirements"],
                review_frequency_days=req_data["review_frequency_days"],
                due_date=due_date,
                next_review_date=next_review,
                status=req_data["status"],
                completion_percentage=req_data["completion_percentage"],
                category_id=category.id,
                organization_id=organization.id
            )
            
            db.add(requirement)
            print(f"✅ Created requirement: {req_data['title']}")
        
        # Create regulatory updates
        for update_data in SAMPLE_REGULATORY_UPDATES:
            # Check if update already exists
            existing_update = db.query(RegulatoryUpdate).filter(
                RegulatoryUpdate.title == update_data["title"],
                RegulatoryUpdate.organization_id == organization.id
            ).first()
            
            if existing_update:
                print(f"⏭️  Update already exists: {update_data['title']}")
                continue
            
            update = RegulatoryUpdate(
                title=update_data["title"],
                description=update_data["description"],
                update_type=update_data["update_type"],
                source=update_data["source"],
                publication_date=update_data["publication_date"],
                effective_date=update_data["effective_date"],
                impact_level=update_data["impact_level"],
                affected_categories=update_data["affected_categories"],
                content=update_data["content"],
                source_url=update_data["source_url"],
                is_reviewed=update_data["is_reviewed"],
                organization_id=organization.id
            )
            
            if update_data["is_reviewed"]:
                update.reviewed_by_id = user.id
                update.reviewed_at = datetime.utcnow()
            
            db.add(update)
            print(f"✅ Created regulatory update: {update_data['title']}")
        
        db.commit()
        print(f"\n🎉 Successfully created sample compliance data!")
        
        # Show summary
        categories_count = db.query(ComplianceCategory).filter(ComplianceCategory.organization_id == organization.id).count()
        requirements_count = db.query(ComplianceRequirement).filter(ComplianceRequirement.organization_id == organization.id).count()
        updates_count = db.query(RegulatoryUpdate).filter(RegulatoryUpdate.organization_id == organization.id).count()
        
        print(f"📊 Summary:")
        print(f"   Categories: {categories_count}")
        print(f"   Requirements: {requirements_count}")
        print(f"   Regulatory Updates: {updates_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample compliance data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 DealVerse OS - Sample Compliance Data Creator")
    print("=" * 50)
    
    success = create_sample_compliance_data()
    if not success:
        print("\n❌ Failed to create sample compliance data")
        sys.exit(1)
