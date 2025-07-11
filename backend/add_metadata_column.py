#!/usr/bin/env python3
"""
Script to add metadata column to documents table
"""
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import get_db, engine

def add_metadata_column():
    """Add metadata column to documents table"""
    
    try:
        with engine.connect() as connection:
            # Check if column already exists
            result = connection.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='documents' AND column_name='document_metadata'
            """))

            if result.fetchone():
                print("✅ Document metadata column already exists")
                return True

            # Drop the old metadata column if it exists
            try:
                connection.execute(text("""
                    ALTER TABLE documents DROP COLUMN IF EXISTS metadata
                """))
            except:
                pass

            # Add the document_metadata column
            connection.execute(text("""
                ALTER TABLE documents
                ADD COLUMN document_metadata JSONB DEFAULT '{}'::jsonb
            """))
            
            connection.commit()
            print("✅ Successfully added document_metadata column to documents table")
            return True
            
    except Exception as e:
        print(f"❌ Error adding metadata column: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Adding document_metadata column to documents table...")
    success = add_metadata_column()
    if not success:
        sys.exit(1)
