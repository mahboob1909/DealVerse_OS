#!/usr/bin/env python3
"""
Create subscription and payment tracking tables for FastSpring integration
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_V70ClUBEgqiZ@ep-royal-shadow-a1gedm82-pooler.ap-southeast-1.aws.neon.tech/dealverse_db?sslmode=require&channel_binding=require"

def create_subscription_tables():
    """Create tables for FastSpring subscription management"""
    
    engine = create_engine(DATABASE_URL)
    
    # SQL to create subscription-related tables
    sql_commands = [
        # Subscription plans table
        """
        CREATE TABLE IF NOT EXISTS subscription_plans (
            id SERIAL PRIMARY KEY,
            plan_name VARCHAR(100) NOT NULL UNIQUE,
            fastspring_product_path VARCHAR(200) NOT NULL UNIQUE,
            price_monthly DECIMAL(10,2) NOT NULL,
            billing_cycle VARCHAR(20) NOT NULL CHECK (billing_cycle IN ('monthly', 'annual')),
            features JSONB DEFAULT '{}',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # User subscriptions table
        """
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id SERIAL PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            plan_id INTEGER NOT NULL REFERENCES subscription_plans(id),
            fastspring_subscription_id VARCHAR(200) UNIQUE,
            fastspring_account_id VARCHAR(200),
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            current_period_start TIMESTAMP,
            current_period_end TIMESTAMP,
            trial_start TIMESTAMP,
            trial_end TIMESTAMP,
            canceled_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, fastspring_subscription_id)
        );
        """,
        
        # Payment transactions table
        """
        CREATE TABLE IF NOT EXISTS payment_transactions (
            id SERIAL PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subscription_id INTEGER REFERENCES user_subscriptions(id),
            fastspring_order_id VARCHAR(200) UNIQUE,
            fastspring_transaction_id VARCHAR(200),
            amount DECIMAL(10,2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'USD',
            status VARCHAR(50) NOT NULL,
            payment_method VARCHAR(100),
            processed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # FastSpring webhook events log
        """
        CREATE TABLE IF NOT EXISTS fastspring_webhook_events (
            id SERIAL PRIMARY KEY,
            event_id VARCHAR(200) UNIQUE NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            processed BOOLEAN DEFAULT false,
            payload JSONB NOT NULL,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        );
        """,
        
        # Insert default subscription plans
        """
        INSERT INTO subscription_plans (plan_name, fastspring_product_path, price_monthly, billing_cycle, features)
        VALUES 
            ('Professional Monthly', 'dealverse-professional-monthly', 25.00, 'monthly', 
             '{"modules": ["prospect-ai", "diligence-navigator", "valuation-hub", "compliance-guardian", "pitchcraft-suite"], "support": "standard", "users": 1}'),
            ('Professional Annual', 'dealverse-professional-annual', 20.00, 'annual', 
             '{"modules": ["prospect-ai", "diligence-navigator", "valuation-hub", "compliance-guardian", "pitchcraft-suite"], "support": "priority", "users": 1, "savings": "20%"}'),
            ('Enterprise', 'dealverse-enterprise', 0.00, 'annual', 
             '{"modules": ["all"], "support": "dedicated", "users": "unlimited", "custom_integrations": true, "on_premise": true}')
        ON CONFLICT (plan_name) DO NOTHING;
        """,
        
        # Create indexes for performance
        """
        CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status);
        CREATE INDEX IF NOT EXISTS idx_user_subscriptions_fastspring_id ON user_subscriptions(fastspring_subscription_id);
        CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_id ON payment_transactions(user_id);
        CREATE INDEX IF NOT EXISTS idx_payment_transactions_order_id ON payment_transactions(fastspring_order_id);
        CREATE INDEX IF NOT EXISTS idx_webhook_events_type ON fastspring_webhook_events(event_type);
        CREATE INDEX IF NOT EXISTS idx_webhook_events_processed ON fastspring_webhook_events(processed);
        """,
        
        # Add subscription status to users table if not exists
        """
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'free',
        ADD COLUMN IF NOT EXISTS subscription_plan_id INTEGER REFERENCES subscription_plans(id),
        ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP;
        """
    ]
    
    try:
        with engine.connect() as connection:
            for sql in sql_commands:
                print(f"Executing: {sql[:100]}...")
                connection.execute(text(sql))
                connection.commit()
        
        print("✅ Successfully created all subscription tables and indexes!")
        print("✅ Inserted default subscription plans!")
        
    except SQLAlchemyError as e:
        print(f"❌ Error creating subscription tables: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Creating FastSpring subscription tables...")
    create_subscription_tables()
