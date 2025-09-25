'use client'

import { ReactNode, useEffect, useState } from 'react'
import dynamic from 'next/dynamic'

interface AuthWrapperProps {
  children: ReactNode
}

// Dynamically import Clerk components to avoid SSR issues
const ClerkProvider = dynamic(
  () => import('@clerk/nextjs').then(mod => mod.ClerkProvider),
  { ssr: false }
)

export function AuthWrapper({ children }: AuthWrapperProps) {
  const [isClient, setIsClient] = useState(false)
  const [enableAuth, setEnableAuth] = useState(false)

  useEffect(() => {
    setIsClient(true)
    // Check if we're in static export mode
    const isStaticExport = process.env.NEXT_PUBLIC_STATIC_EXPORT === 'true'
    // Check if Clerk keys are available
    const hasClerkKeys = !!(
      process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
      process.env.CLERK_SECRET_KEY
    )

    // Enable auth only if not in static export mode and keys are available
    setEnableAuth(!isStaticExport && hasClerkKeys)
  }, [])

  // Don't render anything on server side to avoid hydration issues
  if (!isClient) {
    return <>{children}</>
  }

  // If authentication is enabled and we have the required keys
  if (enableAuth && process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
    return (
      <ClerkProvider publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}>
        {children}
      </ClerkProvider>
    )
  }

  // Fallback: render children without authentication
  return <>{children}</>
}
