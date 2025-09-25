# DealVerse OS Backend Deployment Guide

## Overview
This guide provides instructions for deploying the DealVerse OS FastAPI backend to various cloud providers.

## Prerequisites
- ✅ Neon.tech database configured and working
- ✅ Backend code ready with Dockerfile
- ✅ Environment variables configured

## Deployment Options

### Option 1: Render.com (Recommended - Free Tier Available)

1. **Create Render Account**
   - Go to https://render.com
   - Sign up for a free account

2. **Deploy via Web Interface**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository or upload the backend folder
   - Configure settings:
     - **Name**: `dealverse-os-backend`
     - **Runtime**: `Docker`
     - **Plan**: `Free`
     - **Region**: `Oregon (US West)`
     - **Dockerfile Path**: `./Dockerfile`
     - **Health Check Path**: `/health`

3. **Environment Variables**
   Set these in Render dashboard:
   ```
   NEON_DATABASE_URL=postgresql://neondb_owner:npg_V70ClUBEgqiZ@ep-royal-shadow-a1gedm82-pooler.ap-southeast-1.aws.neon.tech/dealverse_db?sslmode=require&channel_binding=require
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=<generate-secure-key>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   API_V1_STR=/api/v1
   OPENROUTER_API_KEY=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
   OPENROUTER_MODEL=deepseek/deepseek-r1-0528:free
   OPENROUTER_MAX_TOKENS=4000
   OPENROUTER_TEMPERATURE=0.1
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_SITE_URL=https://dealverse.com
   OPENROUTER_SITE_NAME=DealVerse OS
   AI_PROVIDER=openrouter
   AI_ENABLE_FALLBACK=true
   AI_REQUEST_TIMEOUT=60
   AI_MAX_RETRIES=3
   LOG_LEVEL=INFO
   RATE_LIMIT_PER_MINUTE=60
   ALLOWED_HOSTS=["*"]
   BACKEND_CORS_ORIGINS=["https://7b2d90ba.dealverse-os.pages.dev", "https://dealverse-os.pages.dev", "http://localhost:3000"]
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note the deployment URL (e.g., `https://dealverse-os-backend.onrender.com`)

### Option 2: Railway.app

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up and upgrade to a paid plan (required for deployments)

2. **Deploy via CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   railway init
   railway up
   ```

3. **Set Environment Variables**
   ```bash
   railway variables --set "NEON_DATABASE_URL=postgresql://..."
   railway variables --set "ENVIRONMENT=production"
   # ... (add all other variables)
   ```

### Option 3: Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Initialize and Deploy**
   ```bash
   fly auth login
   fly launch
   fly deploy
   ```

3. **Set Environment Variables**
   ```bash
   fly secrets set NEON_DATABASE_URL="postgresql://..."
   fly secrets set ENVIRONMENT="production"
   # ... (add all other variables)
   ```

## Post-Deployment Steps

1. **Test Backend Health**
   - Visit `https://your-backend-url.com/health`
   - Should return: `{"status": "healthy", "service": "DealVerse OS", ...}`

2. **Test API Documentation**
   - Visit `https://your-backend-url.com/api/v1/docs`
   - Should show FastAPI Swagger documentation

3. **Update Frontend Environment Variables**
   - Update `NEXT_PUBLIC_API_URL` in Cloudflare Pages environment variables
   - Set to your backend URL: `https://your-backend-url.com/api/v1`

## Files Included for Deployment

- ✅ `Dockerfile` - Docker configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `render.yaml` - Render.com configuration
- ✅ `railway.toml` - Railway configuration
- ✅ Health check endpoint at `/health`
- ✅ CORS configuration for Cloudflare Pages

## Database Connection

- ✅ Neon.tech PostgreSQL database configured
- ✅ Connection string: `postgresql://neondb_owner:npg_V70ClUBEgqiZ@ep-royal-shadow-a1gedm82-pooler.ap-southeast-1.aws.neon.tech/dealverse_db?sslmode=require&channel_binding=require`
- ✅ Database schema initialized with sample data

## Security Notes

- All sensitive environment variables should be set in the deployment platform's dashboard
- CORS is configured to allow requests from Cloudflare Pages
- Rate limiting is enabled (60 requests per minute)
- Security headers are configured via middleware

## Next Steps

1. Deploy backend using one of the options above
2. Update Cloudflare Pages environment variables with backend URL
3. Test full application functionality
4. Configure custom domain (optional)
