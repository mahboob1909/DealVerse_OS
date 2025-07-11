#!/usr/bin/env python3
"""
Script to create compliance tables in the database
"""
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import get_db, engine
from app.models import *  # Import all models to register them

def create_compliance_tables():
    """Create compliance tables in the database"""
    
    try:
        with engine.connect() as connection:
            # Create compliance_categories table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS compliance_categories (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    code VARCHAR(50) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    priority_level INTEGER DEFAULT 1,
                    review_frequency_days INTEGER DEFAULT 30,
                    regulatory_body VARCHAR(255),
                    regulation_url VARCHAR(500),
                    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    organization_id UUID NOT NULL REFERENCES organizations(id),
                    UNIQUE(code, organization_id)
                )
            """))
            
            # Create compliance_requirements table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS compliance_requirements (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    requirement_code VARCHAR(100),
                    is_mandatory BOOLEAN DEFAULT TRUE,
                    risk_level VARCHAR(20) DEFAULT 'medium',
                    required_documents JSONB DEFAULT '[]'::jsonb,
                    evidence_requirements TEXT,
                    due_date TIMESTAMP WITH TIME ZONE,
                    review_frequency_days INTEGER DEFAULT 90,
                    last_review_date TIMESTAMP WITH TIME ZONE,
                    next_review_date TIMESTAMP WITH TIME ZONE,
                    status VARCHAR(20) DEFAULT 'pending',
                    completion_percentage FLOAT DEFAULT 0.0,
                    category_id UUID NOT NULL REFERENCES compliance_categories(id),
                    organization_id UUID NOT NULL REFERENCES organizations(id)
                )
            """))
            
            # Create compliance_assessments table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS compliance_assessments (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    assessment_type VARCHAR(50) DEFAULT 'regular',
                    status VARCHAR(20) NOT NULL,
                    score FLOAT,
                    findings TEXT,
                    recommendations TEXT,
                    risk_level VARCHAR(20) DEFAULT 'low',
                    impact_assessment TEXT,
                    evidence_provided JSONB DEFAULT '[]'::jsonb,
                    supporting_documents JSONB DEFAULT '[]'::jsonb,
                    action_items JSONB DEFAULT '[]'::jsonb,
                    remediation_plan TEXT,
                    target_completion_date TIMESTAMP WITH TIME ZONE,
                    category_id UUID REFERENCES compliance_categories(id),
                    requirement_id UUID REFERENCES compliance_requirements(id),
                    assessed_by_id UUID REFERENCES users(id),
                    organization_id UUID NOT NULL REFERENCES organizations(id)
                )
            """))
            
            # Create compliance_audit_logs table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS compliance_audit_logs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    event_type VARCHAR(100) NOT NULL,
                    event_description TEXT,
                    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    old_values JSONB DEFAULT '{}'::jsonb,
                    new_values JSONB DEFAULT '{}'::jsonb,
                    event_metadata JSONB DEFAULT '{}'::jsonb,
                    user_id UUID REFERENCES users(id),
                    ip_address VARCHAR(45),
                    user_agent VARCHAR(500),
                    requirement_id UUID REFERENCES compliance_requirements(id),
                    assessment_id UUID REFERENCES compliance_assessments(id),
                    organization_id UUID NOT NULL REFERENCES organizations(id)
                )
            """))
            
            # Create regulatory_updates table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS regulatory_updates (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    update_type VARCHAR(50) DEFAULT 'regulation_change',
                    source VARCHAR(255),
                    publication_date TIMESTAMP WITH TIME ZONE,
                    effective_date TIMESTAMP WITH TIME ZONE,
                    impact_level VARCHAR(20) DEFAULT 'medium',
                    affected_categories JSONB DEFAULT '[]'::jsonb,
                    content TEXT,
                    source_url VARCHAR(500),
                    document_references JSONB DEFAULT '[]'::jsonb,
                    is_reviewed BOOLEAN DEFAULT FALSE,
                    review_notes TEXT,
                    reviewed_by_id UUID REFERENCES users(id),
                    reviewed_at TIMESTAMP WITH TIME ZONE,
                    organization_id UUID NOT NULL REFERENCES organizations(id)
                )
            """))
            
            connection.commit()
            print("✅ Successfully created all compliance tables!")
            return True
            
    except Exception as e:
        print(f"❌ Error creating compliance tables: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Creating compliance tables...")
    success = create_compliance_tables()
    if not success:
        sys.exit(1)
