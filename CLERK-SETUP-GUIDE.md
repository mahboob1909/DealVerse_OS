# Clerk Authentication Setup Guide

## When You're Ready to Enable Authentication

### Step 1: Get Clerk API Keys
1. Go to [https://dashboard.clerk.com](https://dashboard.clerk.com)
2. Create a new application
3. Choose your authentication methods (email, social, etc.)
4. Copy your API keys from the dashboard

### Step 2: Update Environment Variables
Replace the placeholder values in `.env.local`:

```env
# Replace with your actual Clerk keys
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key
CLERK_SECRET_KEY=sk_test_your_actual_secret_key

# These URLs are already configured correctly
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

### Step 3: Re-enable ClerkProvider
In `app/layout.tsx`, uncomment the ClerkProvider:

```tsx
import { ClerkProvider } from '@clerk/nextjs' // Uncomment this

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider> {/* Add this back */}
      <html lang="en">
        <body className={inter.className}>{children}</body>
      </html>
    </ClerkProvider> {/* Add this back */}
  )
}
```

### Step 4: Re-enable Middleware
In `middleware.ts`, uncomment the auth middleware:

```tsx
import { authMiddleware } from "@clerk/nextjs"; // Uncomment

export default authMiddleware({ // Uncomment
  publicRoutes: [
    "/",
    "/api/webhook",
    "/sign-in",
    "/sign-up",
    "/pricing",
    "/about",
    "/contact"
  ]
}); // Uncomment

export const config = { // Uncomment
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
}; // Uncomment
```

### Step 5: Test Authentication
1. Restart your development server: `npm run dev`
2. Visit `http://localhost:3000`
3. You should be redirected to sign-in
4. Create an account and test the flow

### Authentication Flow
- **Public routes**: `/`, `/sign-in`, `/sign-up` (accessible without auth)
- **Protected routes**: `/dashboard` (requires authentication)
- **After sign-in**: Users are redirected to `/dashboard`

### Troubleshooting
- Make sure your Clerk keys are correct
- Check that your domain is configured in Clerk dashboard
- Verify environment variables are loaded (restart dev server)
- Check browser console for any errors

## Current Status (Authentication Disabled)
- ✅ Application runs without authentication
- ✅ All features accessible at `/dashboard`
- ✅ No sign-in required for development
- ✅ Can focus on building features first
