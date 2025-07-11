"""
FastSpring webhook and subscription management endpoints
"""

import json
import hmac
import hashlib
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api import deps
from app.core.config import settings

router = APIRouter()

def verify_fastspring_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify FastSpring webhook signature
    FastSpring uses HMAC-SHA256 for webhook signatures
    """
    if not signature or not secret:
        return False
    
    try:
        # FastSpring sends signature as "sha256=<hash>"
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        # Calculate expected signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures securely
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False

@router.post("/webhook")
async def fastspring_webhook(
    request: Request,
    db: Session = Depends(deps.get_db)
):
    """
    Handle FastSpring webhook events
    """
    try:
        # Get raw payload for signature verification
        payload = await request.body()
        
        # Get signature from headers
        signature = request.headers.get('X-FS-Signature', '')
        
        # TODO: Add signature verification when webhook secret is configured
        # webhook_secret = settings.FASTSPRING_WEBHOOK_SECRET
        # if webhook_secret and not verify_fastspring_signature(payload, signature, webhook_secret):
        #     raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse JSON payload
        try:
            event_data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Extract event information
        event_id = event_data.get('id')
        event_type = event_data.get('type')
        
        if not event_id or not event_type:
            raise HTTPException(status_code=400, detail="Missing event ID or type")
        
        # Log the webhook event
        log_query = text("""
            INSERT INTO fastspring_webhook_events (event_id, event_type, payload, created_at)
            VALUES (:event_id, :event_type, :payload, :created_at)
            ON CONFLICT (event_id) DO NOTHING
        """)
        
        db.execute(log_query, {
            'event_id': event_id,
            'event_type': event_type,
            'payload': json.dumps(event_data),
            'created_at': datetime.utcnow()
        })
        
        # Process the event based on type
        await process_webhook_event(db, event_type, event_data)
        
        # Mark event as processed
        update_query = text("""
            UPDATE fastspring_webhook_events 
            SET processed = true, processed_at = :processed_at
            WHERE event_id = :event_id
        """)
        
        db.execute(update_query, {
            'event_id': event_id,
            'processed_at': datetime.utcnow()
        })
        
        db.commit()
        
        return {"status": "success", "event_id": event_id, "event_type": event_type}
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        if 'event_id' in locals():
            error_query = text("""
                UPDATE fastspring_webhook_events 
                SET error_message = :error_message
                WHERE event_id = :event_id
            """)
            db.execute(error_query, {
                'event_id': event_id,
                'error_message': str(e)
            })
            db.commit()
        
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

async def process_webhook_event(db: Session, event_type: str, event_data: Dict[str, Any]):
    """
    Process different types of FastSpring webhook events
    """
    
    if event_type == "order.completed":
        await handle_order_completed(db, event_data)
    elif event_type == "subscription.activated":
        await handle_subscription_activated(db, event_data)
    elif event_type == "subscription.deactivated":
        await handle_subscription_deactivated(db, event_data)
    elif event_type == "subscription.canceled":
        await handle_subscription_canceled(db, event_data)
    elif event_type == "subscription.payment.succeeded":
        await handle_payment_succeeded(db, event_data)
    elif event_type == "subscription.payment.failed":
        await handle_payment_failed(db, event_data)
    else:
        # Log unhandled event types for future implementation
        print(f"Unhandled webhook event type: {event_type}")

async def handle_order_completed(db: Session, event_data: Dict[str, Any]):
    """Handle completed order events"""
    order_data = event_data.get('data', {})
    order_id = order_data.get('id')
    customer_email = order_data.get('customer', {}).get('email')
    
    if not order_id or not customer_email:
        return
    
    # Find user by email
    user_query = text("SELECT id FROM users WHERE email = :email")
    user_result = db.execute(user_query, {'email': customer_email}).fetchone()
    
    if not user_result:
        print(f"User not found for email: {customer_email}")
        return
    
    user_id = user_result[0]
    
    # Record the transaction
    transaction_query = text("""
        INSERT INTO payment_transactions 
        (user_id, fastspring_order_id, amount, currency, status, processed_at, created_at)
        VALUES (:user_id, :order_id, :amount, :currency, 'completed', :processed_at, :created_at)
        ON CONFLICT (fastspring_order_id) DO NOTHING
    """)
    
    total_amount = order_data.get('total', 0)
    currency = order_data.get('currency', 'USD')
    
    db.execute(transaction_query, {
        'user_id': user_id,
        'order_id': order_id,
        'amount': total_amount,
        'currency': currency,
        'processed_at': datetime.utcnow(),
        'created_at': datetime.utcnow()
    })

async def handle_subscription_activated(db: Session, event_data: Dict[str, Any]):
    """Handle subscription activation events"""
    subscription_data = event_data.get('data', {})
    subscription_id = subscription_data.get('id')
    customer_email = subscription_data.get('customer', {}).get('email')
    product_path = subscription_data.get('product', {}).get('path')
    
    if not subscription_id or not customer_email or not product_path:
        return
    
    # Find user and plan
    user_query = text("SELECT id FROM users WHERE email = :email")
    user_result = db.execute(user_query, {'email': customer_email}).fetchone()
    
    plan_query = text("SELECT id FROM subscription_plans WHERE fastspring_product_path = :path")
    plan_result = db.execute(plan_query, {'path': product_path}).fetchone()
    
    if not user_result or not plan_result:
        print(f"User or plan not found for subscription: {subscription_id}")
        return
    
    user_id = user_result[0]
    plan_id = plan_result[0]
    
    # Create or update subscription
    subscription_query = text("""
        INSERT INTO user_subscriptions 
        (user_id, plan_id, fastspring_subscription_id, status, current_period_start, current_period_end, created_at, updated_at)
        VALUES (:user_id, :plan_id, :subscription_id, 'active', :period_start, :period_end, :created_at, :updated_at)
        ON CONFLICT (fastspring_subscription_id) 
        DO UPDATE SET 
            status = 'active',
            current_period_start = :period_start,
            current_period_end = :period_end,
            updated_at = :updated_at
    """)
    
    period_start = datetime.utcnow()
    period_end = subscription_data.get('nextChargeDate')
    if period_end:
        period_end = datetime.fromisoformat(period_end.replace('Z', '+00:00'))
    
    db.execute(subscription_query, {
        'user_id': user_id,
        'plan_id': plan_id,
        'subscription_id': subscription_id,
        'period_start': period_start,
        'period_end': period_end,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    })
    
    # Update user subscription status
    user_update_query = text("""
        UPDATE users 
        SET subscription_status = 'active', 
            subscription_plan_id = :plan_id,
            subscription_expires_at = :expires_at
        WHERE id = :user_id
    """)
    
    db.execute(user_update_query, {
        'plan_id': plan_id,
        'expires_at': period_end,
        'user_id': user_id
    })

async def handle_subscription_deactivated(db: Session, event_data: Dict[str, Any]):
    """Handle subscription deactivation events"""
    await update_subscription_status(db, event_data, 'inactive')

async def handle_subscription_canceled(db: Session, event_data: Dict[str, Any]):
    """Handle subscription cancellation events"""
    await update_subscription_status(db, event_data, 'canceled')

async def update_subscription_status(db: Session, event_data: Dict[str, Any], status: str):
    """Update subscription status"""
    subscription_data = event_data.get('data', {})
    subscription_id = subscription_data.get('id')
    
    if not subscription_id:
        return
    
    # Update subscription status
    subscription_query = text("""
        UPDATE user_subscriptions 
        SET status = :status, updated_at = :updated_at
        WHERE fastspring_subscription_id = :subscription_id
    """)
    
    db.execute(subscription_query, {
        'status': status,
        'subscription_id': subscription_id,
        'updated_at': datetime.utcnow()
    })
    
    # Update user status if subscription is canceled/inactive
    if status in ['canceled', 'inactive']:
        user_update_query = text("""
            UPDATE users 
            SET subscription_status = 'free'
            WHERE id IN (
                SELECT user_id FROM user_subscriptions 
                WHERE fastspring_subscription_id = :subscription_id
            )
        """)
        
        db.execute(user_update_query, {'subscription_id': subscription_id})

async def handle_payment_succeeded(db: Session, event_data: Dict[str, Any]):
    """Handle successful payment events"""
    # Implementation for payment success handling
    pass

async def handle_payment_failed(db: Session, event_data: Dict[str, Any]):
    """Handle failed payment events"""
    # Implementation for payment failure handling
    pass
