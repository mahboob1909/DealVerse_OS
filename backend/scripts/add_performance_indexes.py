#!/usr/bin/env python3
"""
Database Performance Optimization Script
Adds missing indexes for improved query performance
"""
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from app.core.config import settings
from app.db.database import engine, SessionLocal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_index_if_not_exists(index_name: str, table_name: str, columns: str):
    """Create index if it doesn't already exist"""
    db = SessionLocal()
    try:
        # Check if index exists
        check_query = text("""
            SELECT 1 FROM pg_indexes
            WHERE indexname = :index_name AND tablename = :table_name
        """)

        result = db.execute(check_query, {"index_name": index_name, "table_name": table_name})

        if result.fetchone():
            logger.info(f"Index {index_name} already exists, skipping...")
            return

        # Create the index (without CONCURRENTLY for development)
        create_query = text(f"CREATE INDEX {index_name} ON {table_name} ({columns})")
        db.execute(create_query)
        db.commit()
        logger.info(f"Created index: {index_name}")

    except ProgrammingError as e:
        db.rollback()
        if "already exists" in str(e):
            logger.info(f"Index {index_name} already exists")
        else:
            logger.error(f"Error creating index {index_name}: {e}")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating index {index_name}: {e}")
    finally:
        db.close()

def add_performance_indexes():
    """Add all performance indexes to the database"""
    logger.info("Starting database performance optimization...")
    
    # Deal indexes
    logger.info("Adding Deal table indexes...")
    deal_indexes = [
        ("idx_deals_organization_id", "deals", "organization_id"),
        ("idx_deals_client_id", "deals", "client_id"),
        ("idx_deals_created_by_id", "deals", "created_by_id"),
        ("idx_deals_stage", "deals", "stage"),
        ("idx_deals_status", "deals", "status"),
        ("idx_deals_deal_type", "deals", "deal_type"),
        ("idx_deals_target_industry", "deals", "target_industry"),
        ("idx_deals_expected_close_date", "deals", "expected_close_date"),
        ("idx_deals_actual_close_date", "deals", "actual_close_date"),
        ("idx_deals_org_stage", "deals", "organization_id, stage"),
        ("idx_deals_org_status", "deals", "organization_id, status"),
        ("idx_deals_org_type", "deals", "organization_id, deal_type"),
        ("idx_deals_org_created", "deals", "organization_id, created_at"),
        ("idx_deals_stage_status", "deals", "stage, status"),
        ("idx_deals_org_stage_status", "deals", "organization_id, stage, status"),
        ("idx_deals_client_stage", "deals", "client_id, stage"),
        ("idx_deals_created_by_stage", "deals", "created_by_id, stage"),
        ("idx_deals_org_close_date", "deals", "organization_id, expected_close_date"),
        ("idx_deals_stage_close_date", "deals", "stage, expected_close_date"),
        ("idx_deals_org_value", "deals", "organization_id, deal_value"),
        ("idx_deals_stage_value", "deals", "stage, deal_value"),
    ]
    
    for index_name, table_name, columns in deal_indexes:
        create_index_if_not_exists(index_name, table_name, columns)
    
    # Client indexes
    logger.info("Adding Client table indexes...")
    client_indexes = [
        ("idx_clients_organization_id", "clients", "organization_id"),
        ("idx_clients_client_type", "clients", "client_type"),
        ("idx_clients_relationship_status", "clients", "relationship_status"),
        ("idx_clients_industry", "clients", "industry"),
        ("idx_clients_company_size", "clients", "company_size"),
        ("idx_clients_email", "clients", "email"),
        ("idx_clients_company", "clients", "company"),
        ("idx_clients_name", "clients", "name"),
        ("idx_clients_org_type", "clients", "organization_id, client_type"),
        ("idx_clients_org_status", "clients", "organization_id, relationship_status"),
        ("idx_clients_org_industry", "clients", "organization_id, industry"),
        ("idx_clients_org_created", "clients", "organization_id, created_at"),
        ("idx_clients_type_status", "clients", "client_type, relationship_status"),
        ("idx_clients_org_type_status", "clients", "organization_id, client_type, relationship_status"),
        ("idx_clients_name_company", "clients", "name, company"),
        ("idx_clients_email_company", "clients", "email, company"),
        ("idx_clients_industry_size", "clients", "industry, company_size"),
        ("idx_clients_org_name", "clients", "organization_id, name"),
    ]
    
    for index_name, table_name, columns in client_indexes:
        create_index_if_not_exists(index_name, table_name, columns)

    # Document indexes
    logger.info("Adding Document table indexes...")
    document_indexes = [
        ("idx_documents_organization_id", "documents", "organization_id"),
        ("idx_documents_deal_id", "documents", "deal_id"),
        ("idx_documents_client_id", "documents", "client_id"),
        ("idx_documents_uploaded_by_id", "documents", "uploaded_by_id"),
        ("idx_documents_document_type", "documents", "document_type"),
        ("idx_documents_category", "documents", "category"),
        ("idx_documents_status", "documents", "status"),
        ("idx_documents_processing_status", "documents", "processing_status"),
        ("idx_documents_compliance_status", "documents", "compliance_status"),
        ("idx_documents_review_status", "documents", "review_status"),
        ("idx_documents_is_confidential", "documents", "is_confidential"),
        ("idx_documents_is_archived", "documents", "is_archived"),
        ("idx_documents_is_latest_version", "documents", "is_latest_version"),
        ("idx_documents_file_type", "documents", "file_type"),
        ("idx_documents_file_extension", "documents", "file_extension"),
        ("idx_documents_org_type", "documents", "organization_id, document_type"),
        ("idx_documents_org_status", "documents", "organization_id, status"),
        ("idx_documents_org_archived", "documents", "organization_id, is_archived"),
        ("idx_documents_org_created", "documents", "organization_id, created_at"),
        ("idx_documents_deal_type", "documents", "deal_id, document_type"),
        ("idx_documents_deal_status", "documents", "deal_id, status"),
        ("idx_documents_client_type", "documents", "client_id, document_type"),
        ("idx_documents_type_status", "documents", "document_type, status"),
        ("idx_documents_org_type_status", "documents", "organization_id, document_type, status"),
        ("idx_documents_title", "documents", "title"),
        ("idx_documents_filename", "documents", "filename"),
        ("idx_documents_org_title", "documents", "organization_id, title"),
        ("idx_documents_category_subcategory", "documents", "category, subcategory"),
        ("idx_documents_compliance_review", "documents", "compliance_status, review_status"),
        ("idx_documents_org_compliance", "documents", "organization_id, compliance_status"),
        ("idx_documents_processing_compliance", "documents", "processing_status, compliance_status"),
        ("idx_documents_parent_version", "documents", "parent_document_id, is_latest_version"),
        ("idx_documents_version_latest", "documents", "version, is_latest_version"),
        ("idx_documents_file_size", "documents", "file_size"),
        ("idx_documents_type_size", "documents", "file_type, file_size"),
    ]
    
    for index_name, table_name, columns in document_indexes:
        create_index_if_not_exists(index_name, table_name, columns)

    # User indexes
    logger.info("Adding User table indexes...")
    user_indexes = [
        ("idx_users_organization_id", "users", "organization_id"),
        ("idx_users_role", "users", "role"),
        ("idx_users_is_active", "users", "is_active"),
        ("idx_users_is_superuser", "users", "is_superuser"),
        ("idx_users_is_verified", "users", "is_verified"),
        ("idx_users_last_login", "users", "last_login"),
        ("idx_users_department", "users", "department"),
        ("idx_users_title", "users", "title"),
        ("idx_users_org_role", "users", "organization_id, role"),
        ("idx_users_org_active", "users", "organization_id, is_active"),
        ("idx_users_org_verified", "users", "organization_id, is_verified"),
        ("idx_users_role_active", "users", "role, is_active"),
        ("idx_users_org_role_active", "users", "organization_id, role, is_active"),
        ("idx_users_org_department", "users", "organization_id, department"),
        ("idx_users_active_verified", "users", "is_active, is_verified"),
        ("idx_users_org_last_login", "users", "organization_id, last_login"),
        ("idx_users_first_last_name", "users", "first_name, last_name"),
        ("idx_users_org_name", "users", "organization_id, first_name, last_name"),
    ]

    for index_name, table_name, columns in user_indexes:
        create_index_if_not_exists(index_name, table_name, columns)

    # Task indexes
    logger.info("Adding Task table indexes...")
    task_indexes = [
        ("idx_tasks_organization_id", "tasks", "organization_id"),
        ("idx_tasks_assignee_id", "tasks", "assignee_id"),
        ("idx_tasks_deal_id", "tasks", "deal_id"),
        ("idx_tasks_status", "tasks", "status"),
        ("idx_tasks_priority", "tasks", "priority"),
        ("idx_tasks_task_type", "tasks", "task_type"),
        ("idx_tasks_category", "tasks", "category"),
        ("idx_tasks_due_date", "tasks", "due_date"),
        ("idx_tasks_start_date", "tasks", "start_date"),
        ("idx_tasks_completed_date", "tasks", "completed_date"),
        ("idx_tasks_org_status", "tasks", "organization_id, status"),
        ("idx_tasks_org_priority", "tasks", "organization_id, priority"),
        ("idx_tasks_org_assignee", "tasks", "organization_id, assignee_id"),
        ("idx_tasks_org_type", "tasks", "organization_id, task_type"),
        ("idx_tasks_assignee_status", "tasks", "assignee_id, status"),
        ("idx_tasks_assignee_priority", "tasks", "assignee_id, priority"),
        ("idx_tasks_deal_status", "tasks", "deal_id, status"),
        ("idx_tasks_status_priority", "tasks", "status, priority"),
        ("idx_tasks_org_status_priority", "tasks", "organization_id, status, priority"),
        ("idx_tasks_org_due_date", "tasks", "organization_id, due_date"),
        ("idx_tasks_assignee_due_date", "tasks", "assignee_id, due_date"),
        ("idx_tasks_status_due_date", "tasks", "status, due_date"),
        ("idx_tasks_priority_due_date", "tasks", "priority, due_date"),
        ("idx_tasks_type_status", "tasks", "task_type, status"),
        ("idx_tasks_org_type_status", "tasks", "organization_id, task_type, status"),
        ("idx_tasks_deal_type_status", "tasks", "deal_id, task_type, status"),
    ]

    for index_name, table_name, columns in task_indexes:
        create_index_if_not_exists(index_name, table_name, columns)

    logger.info("Database performance optimization completed!")

if __name__ == "__main__":
    add_performance_indexes()
