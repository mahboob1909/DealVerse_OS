# FastSpring Integration Setup Guide for DealVerse OS

## 🎯 Overview

This guide will walk you through completing the FastSpring integration for DealVerse OS. The technical implementation is already complete - you just need to configure your FastSpring account and update the environment variables.

## ✅ What's Already Implemented

### Backend (Complete)
- ✅ Database schema with subscription tables
- ✅ FastSpring webhook endpoint (`/api/v1/fastspring/webhook`)
- ✅ Subscription management logic
- ✅ Payment transaction tracking

### Frontend (Complete)
- ✅ FastSpring Store Builder Library integration
- ✅ Interactive pricing cards with checkout
- ✅ Clerk authentication integration
- ✅ Responsive pricing section

## 🔧 What You Need to Do

### Step 1: Complete FastSpring Account Setup

1. **Login to FastSpring**: Go to [app.fastspring.com](https://app.fastspring.com)

2. **Store Configuration**:
   - Navigate to **Settings** → **Store Settings**
   - Set **Store Name**: "DealVerse OS"
   - Choose your **Store URL** (e.g., `dealverse.fspring.com`)
   - Set **Currency**: USD
   - Configure **Tax Settings** based on your location

3. **Create Products**:
   Navigate to **Products** → **Add Product** and create these three products:

   **Product 1: Professional Monthly**
   ```
   Product Name: DealVerse OS Professional
   Product Type: Subscription
   Pricing: $25.00 USD
   Billing Cycle: Monthly
   Product Path: dealverse-professional-monthly
   Description: AI-powered investment banking platform - Professional plan
   ```

   **Product 2: Professional Annual**
   ```
   Product Name: DealVerse OS Professional Annual
   Product Type: Subscription
   Pricing: $240.00 USD ($20/month × 12)
   Billing Cycle: Annual
   Product Path: dealverse-professional-annual
   Description: AI-powered investment banking platform - Annual plan (Save 20%)
   ```

   **Product 3: Enterprise**
   ```
   Product Name: DealVerse OS Enterprise
   Product Type: Subscription
   Pricing: $1000.00 USD (placeholder)
   Billing Cycle: Annual
   Product Path: dealverse-enterprise
   Description: Enterprise-grade investment banking platform
   ```

4. **Generate API Credentials**:
   - Go to **Developer Tools** → **APIs** → **API Credentials**
   - Click **"Create"** to generate new credentials
   - **IMPORTANT**: Copy both the username and password immediately!
   - Store them securely - you won't see the password again

5. **Configure Webhooks**:
   - Go to **Developer Tools** → **Webhooks**
   - Click **"Add Webhook"**
   - **Webhook URL**: `https://yourdomain.com/api/v1/fastspring/webhook`
   - **Events**: Select these events:
     - `order.completed`
     - `subscription.activated`
     - `subscription.deactivated`
     - `subscription.canceled`
     - `subscription.payment.failed`
     - `subscription.payment.succeeded`

### Step 2: Update Environment Variables

Update your `.env.local` file with the FastSpring credentials:

```env
# FastSpring Configuration
NEXT_PUBLIC_FASTSPRING_STORE_ID=your_actual_store_id.fspring.com
FASTSPRING_API_USERNAME=your_actual_api_username
FASTSPRING_API_PASSWORD=your_actual_api_password
FASTSPRING_WEBHOOK_SECRET=your_webhook_secret_if_configured
```

### Step 3: Test the Integration

1. **Start the Application**:
   ```bash
   npm run dev
   ```

2. **Test Checkout Flow**:
   - Visit the landing page
   - Click on any pricing plan
   - Verify FastSpring checkout opens
   - Complete a test transaction (use FastSpring test mode)

3. **Verify Webhook Processing**:
   - Check the `fastspring_webhook_events` table for logged events
   - Verify subscription status updates in `user_subscriptions` table

## 🚀 Production Deployment Checklist

### Before Going Live:

1. **Switch to Production Mode**:
   - In FastSpring: Disable **Test Mode**
   - Update webhook URL to production domain
   - Verify SSL certificate on webhook endpoint

2. **Security**:
   - Enable webhook signature verification
   - Set up proper CORS policies
   - Configure rate limiting

3. **Monitoring**:
   - Set up webhook event monitoring
   - Configure payment failure alerts
   - Monitor subscription metrics

## 🔍 Testing Scenarios

### Test Cases to Verify:

1. **New Subscription**:
   - User signs up → selects plan → completes payment
   - Verify: User subscription status updated, webhook processed

2. **Subscription Renewal**:
   - Wait for renewal or trigger manually
   - Verify: Payment recorded, subscription period extended

3. **Subscription Cancellation**:
   - Cancel subscription in FastSpring
   - Verify: User status updated to 'canceled'

4. **Payment Failure**:
   - Simulate failed payment
   - Verify: User notified, retry logic triggered

## 📊 Database Schema

The following tables are already created:

- `subscription_plans`: Available subscription plans
- `user_subscriptions`: User subscription records
- `payment_transactions`: Payment history
- `fastspring_webhook_events`: Webhook event log

## 🛠️ Troubleshooting

### Common Issues:

1. **Webhook Not Receiving Events**:
   - Check webhook URL is accessible
   - Verify SSL certificate
   - Check FastSpring webhook configuration

2. **Checkout Not Opening**:
   - Verify FastSpring Store ID is correct
   - Check browser console for JavaScript errors
   - Ensure FastSpring script is loading

3. **User Not Found in Webhook**:
   - Ensure user email matches between Clerk and FastSpring
   - Check user exists in database before webhook processing

## 📞 Support

If you encounter issues:

1. **FastSpring Support**: [FastSpring Help Center](https://community.fastspring.com)
2. **Technical Issues**: Check the webhook event logs in the database
3. **Integration Questions**: Review the FastSpring developer documentation

## 🎉 Next Steps

Once FastSpring is fully configured:

1. Test all payment flows thoroughly
2. Set up monitoring and alerts
3. Configure customer support workflows
4. Plan for subscription management features in the dashboard
5. Consider implementing usage-based billing for enterprise customers

The technical implementation is complete and ready for production use once you complete the FastSpring account configuration!
