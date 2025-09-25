# Cloudflare Pages Environment Variables Setup

## Overview
This guide explains how to configure environment variables for the DealVerse OS frontend deployed on Cloudflare Pages.

## Current Deployment
- ✅ **Live URL**: https://7b2d90ba.dealverse-os.pages.dev
- ✅ **Project Name**: dealverse-os
- ✅ **Static Build**: Successfully generated and deployed

## Required Environment Variables

### 1. API Configuration
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com/api/v1
```
**Status**: ⚠️ Pending backend deployment
**Action**: Update after backend is deployed

### 2. Clerk Authentication (Optional - for re-enabling auth)
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_d2VsbC1tZWVya2F0LTUxLmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_SECRET_KEY=sk_test_VdLSkIvJsrEo1qNHhF8KbaiFD3C1wbLmpbJ2Csq3jx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```
**Status**: ✅ Available (currently disabled for static export)
**Action**: Set when re-enabling authentication

### 3. Application Configuration
```
NEXT_PUBLIC_APP_NAME=DealVerse OS
NEXT_PUBLIC_APP_VERSION=0.1.0
NODE_ENV=production
```

### 4. Feature Flags (Optional)
```
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true
NEXT_PUBLIC_ENABLE_REAL_TIME=false
```

## How to Set Environment Variables in Cloudflare Pages

### Method 1: Cloudflare Dashboard (Recommended)

1. **Access Cloudflare Pages Dashboard**
   - Go to https://dash.cloudflare.com
   - Navigate to Pages → dealverse-os

2. **Configure Environment Variables**
   - Click on "Settings" tab
   - Scroll to "Environment variables" section
   - Click "Add variable"

3. **Add Variables for Production**
   - Set "Environment" to "Production"
   - Add each variable name and value
   - Click "Save"

4. **Add Variables for Preview (Optional)**
   - Set "Environment" to "Preview"
   - Add same variables (can use different values for testing)
   - Click "Save"

### Method 2: Wrangler CLI

```bash
# Set production environment variables
wrangler pages secret put NEXT_PUBLIC_API_URL --env production
wrangler pages secret put NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY --env production
wrangler pages secret put CLERK_SECRET_KEY --env production

# Set preview environment variables
wrangler pages secret put NEXT_PUBLIC_API_URL --env preview
```

## Current Status

### ✅ Completed
- Static build configuration
- Cloudflare Pages deployment
- Basic environment structure
- Wrangler configuration

### ⚠️ Pending
- Backend deployment and URL
- Environment variables configuration
- Authentication re-enablement

### 🔄 Next Steps
1. Deploy backend to cloud provider (Render/Railway/Fly.io)
2. Get backend URL
3. Set `NEXT_PUBLIC_API_URL` in Cloudflare Pages
4. Test API connectivity
5. Re-enable authentication system

## Testing Environment Variables

After setting environment variables:

1. **Trigger New Deployment**
   - Make a small change to trigger rebuild
   - Or use "Retry deployment" in Cloudflare dashboard

2. **Verify Variables**
   - Check browser console for `process.env.NEXT_PUBLIC_*` variables
   - Test API calls to backend

3. **Test Functionality**
   - Verify API connectivity
   - Test authentication flow (when re-enabled)
   - Check all features work correctly

## Security Notes

- Only `NEXT_PUBLIC_*` variables are exposed to the browser
- Secret keys (like `CLERK_SECRET_KEY`) are server-side only
- Use different values for preview/production environments
- Rotate keys regularly for security

## Troubleshooting

### Environment Variables Not Working
1. Check variable names (case-sensitive)
2. Ensure `NEXT_PUBLIC_` prefix for client-side variables
3. Trigger new deployment after changes
4. Check Cloudflare Pages build logs

### API Connection Issues
1. Verify `NEXT_PUBLIC_API_URL` is correct
2. Check CORS configuration in backend
3. Ensure backend is deployed and healthy
4. Test backend `/health` endpoint directly

## Integration with Backend

Once backend is deployed:

1. **Update API URL**
   ```
   NEXT_PUBLIC_API_URL=https://dealverse-os-backend.onrender.com/api/v1
   ```

2. **Update Backend CORS**
   - Add Cloudflare Pages URL to backend CORS origins
   - Include both the generated URL and custom domain

3. **Test Integration**
   - Verify API calls work
   - Check authentication flow
   - Test all application features
