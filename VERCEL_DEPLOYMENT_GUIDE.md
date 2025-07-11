# DealVerse OS - Vercel Deployment Guide

## 🚀 Quick Deployment Steps

### Step 1: Push to GitHub

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: DealVerse OS with FastSpring integration"
   ```

2. **Connect to your GitHub repository**:
   ```bash
   git remote add origin https://github.com/yourusername/DealVerse_OS.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Vercel

1. **Go to [vercel.com](https://vercel.com)** and sign in with GitHub
2. **Click "New Project"**
3. **Import your `DealVerse_OS` repository**
4. **Configure the project**:
   - Framework Preset: **Next.js**
   - Root Directory: **/** (leave as default)
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

### Step 3: Configure Environment Variables

In Vercel dashboard, go to **Settings** → **Environment Variables** and add:

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = pk_test_d2VsbC1tZWVya2F0LTUxLmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_SECRET_KEY = sk_test_VdLSkIvJsrEo1qNHhF8KbaiFD3C1wbLmpbJ2Csq3jx
NEXT_PUBLIC_FASTSPRING_STORE_ID = dealverseos.test.onfastspring.com/popup-dealverseos
FASTSPRING_API_USERNAME = UG3FOKLPT6CJOWY-W-YUFA
FASTSPRING_API_PASSWORD = 8XuW68HDTMW-b_MaaBy38g
```

### Step 4: Deploy

1. **Click "Deploy"**
2. **Wait for deployment** (usually 2-3 minutes)
3. **Get your Vercel URL** (e.g., `https://deal-verse-os.vercel.app`)

## 🔗 Configure FastSpring Webhook

### Update FastSpring Webhook URL

1. **Go to FastSpring Dashboard** → **Developer Tools** → **Webhooks**
2. **Edit your webhook** and update the URL to:
   ```
   https://your-vercel-app.vercel.app/api/v1/fastspring/webhook
   ```
3. **Save the webhook configuration**

### Test the Integration

1. **Visit your Vercel URL**
2. **Test the pricing cards**
3. **Complete a test purchase**
4. **Check webhook delivery in FastSpring dashboard**

## 🛠️ Backend Deployment (Optional)

Since your backend is Python/FastAPI, you have a few options:

### Option 1: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Deploy the `backend` folder
4. Add environment variables for database connection

### Option 2: Render
1. Go to [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option 3: Heroku
1. Create a `Procfile` in backend folder:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
2. Deploy to Heroku

## 🔧 Production Configuration

### Update API URL

Once your backend is deployed, update the environment variable:
```
NEXT_PUBLIC_API_URL = https://your-backend-url.com/api/v1
```

### Update FastSpring to Production Mode

1. **In FastSpring Dashboard**:
   - Switch from Test Mode to Production Mode
   - Update webhook URL to production domain
   - Verify all products are configured correctly

### Security Checklist

- ✅ Environment variables are set in Vercel
- ✅ `.env.local` is in `.gitignore`
- ✅ FastSpring webhook URL uses HTTPS
- ✅ Clerk authentication is configured
- ✅ Database connection is secure

## 🎯 Testing Checklist

After deployment:

1. **Landing Page**:
   - ✅ Page loads correctly
   - ✅ Animations work
   - ✅ Pricing cards display properly

2. **Authentication**:
   - ✅ Sign up works
   - ✅ Sign in works
   - ✅ User button appears when signed in

3. **FastSpring Integration**:
   - ✅ Checkout popup opens
   - ✅ Test payment completes
   - ✅ Webhook receives events
   - ✅ User subscription status updates

## 🚨 Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check for TypeScript errors
   - Ensure all dependencies are in `package.json`
   - Check build logs in Vercel dashboard

2. **Environment Variables Not Working**:
   - Ensure variables are set in Vercel dashboard
   - Redeploy after adding variables
   - Check variable names match exactly

3. **FastSpring Checkout Not Opening**:
   - Verify `NEXT_PUBLIC_FASTSPRING_STORE_ID` is correct
   - Check browser console for errors
   - Ensure FastSpring script loads

4. **Webhook Not Receiving Events**:
   - Verify webhook URL is accessible
   - Check FastSpring webhook logs
   - Ensure URL uses HTTPS

## 📞 Support

- **Vercel**: [vercel.com/docs](https://vercel.com/docs)
- **FastSpring**: [developer.fastspring.com](https://developer.fastspring.com)
- **Clerk**: [clerk.com/docs](https://clerk.com/docs)

## 🎉 Next Steps

Once deployed:
1. Test all functionality thoroughly
2. Set up monitoring and analytics
3. Configure custom domain (optional)
4. Set up CI/CD for automatic deployments
5. Plan for backend deployment and integration
