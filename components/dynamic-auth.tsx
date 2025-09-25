'use client'

import { ReactNode, useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import { Button } from '@/components/ui/button'

// Dynamically import Clerk components to avoid SSR issues
const SignInButton = dynamic(
  () => import('@clerk/nextjs').then(mod => mod.SignInButton),
  { 
    ssr: false,
    loading: () => <Button variant="outline">Loading...</Button>
  }
)

const SignUpButton = dynamic(
  () => import('@clerk/nextjs').then(mod => mod.SignUpButton),
  { 
    ssr: false,
    loading: () => <Button>Loading...</Button>
  }
)

const SignedIn = dynamic(
  () => import('@clerk/nextjs').then(mod => mod.SignedIn),
  { ssr: false }
)

const SignedOut = dynamic(
  () => import('@clerk/nextjs').then(mod => mod.SignedOut),
  { ssr: false }
)

const UserButton = dynamic(
  () => import('@clerk/nextjs').then(mod => mod.UserButton),
  { 
    ssr: false,
    loading: () => <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse" />
  }
)

interface DynamicAuthProps {
  children?: ReactNode
  fallback?: ReactNode
}

export function DynamicSignInButton({ children, fallback }: DynamicAuthProps) {
  const [isClient, setIsClient] = useState(false)
  const [authEnabled, setAuthEnabled] = useState(false)

  useEffect(() => {
    setIsClient(true)
    const isStaticExport = process.env.NEXT_PUBLIC_STATIC_EXPORT === 'true'
    const hasClerkKeys = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
    setAuthEnabled(!isStaticExport && hasClerkKeys)
  }, [])

  if (!isClient) {
    return fallback || <Button variant="outline">Sign In</Button>
  }

  if (authEnabled) {
    return <SignInButton>{children}</SignInButton>
  }

  return fallback || (
    <Button 
      variant="outline" 
      onClick={() => alert('Authentication is currently disabled in static export mode')}
    >
      Sign In
    </Button>
  )
}

export function DynamicSignUpButton({ children, fallback }: DynamicAuthProps) {
  const [isClient, setIsClient] = useState(false)
  const [authEnabled, setAuthEnabled] = useState(false)

  useEffect(() => {
    setIsClient(true)
    const isStaticExport = process.env.NEXT_PUBLIC_STATIC_EXPORT === 'true'
    const hasClerkKeys = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
    setAuthEnabled(!isStaticExport && hasClerkKeys)
  }, [])

  if (!isClient) {
    return fallback || <Button>Get Started</Button>
  }

  if (authEnabled) {
    return <SignUpButton>{children}</SignUpButton>
  }

  return fallback || (
    <Button 
      onClick={() => alert('Authentication is currently disabled in static export mode')}
    >
      Get Started
    </Button>
  )
}

export function DynamicSignedIn({ children, fallback }: DynamicAuthProps) {
  const [isClient, setIsClient] = useState(false)
  const [authEnabled, setAuthEnabled] = useState(false)

  useEffect(() => {
    setIsClient(true)
    const isStaticExport = process.env.NEXT_PUBLIC_STATIC_EXPORT === 'true'
    const hasClerkKeys = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
    setAuthEnabled(!isStaticExport && hasClerkKeys)
  }, [])

  if (!isClient) {
    return null
  }

  if (authEnabled) {
    return <SignedIn>{children}</SignedIn>
  }

  return fallback || null
}

export function DynamicSignedOut({ children, fallback }: DynamicAuthProps) {
  const [isClient, setIsClient] = useState(false)
  const [authEnabled, setAuthEnabled] = useState(false)

  useEffect(() => {
    setIsClient(true)
    const isStaticExport = process.env.NEXT_PUBLIC_STATIC_EXPORT === 'true'
    const hasClerkKeys = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
    setAuthEnabled(!isStaticExport && hasClerkKeys)
  }, [])

  if (!isClient) {
    return <>{children}</>
  }

  if (authEnabled) {
    return <SignedOut>{children}</SignedOut>
  }

  return <>{children}</>
}

export function DynamicUserButton({ fallback }: { fallback?: ReactNode }) {
  const [isClient, setIsClient] = useState(false)
  const [authEnabled, setAuthEnabled] = useState(false)

  useEffect(() => {
    setIsClient(true)
    const isStaticExport = process.env.NEXT_PUBLIC_STATIC_EXPORT === 'true'
    const hasClerkKeys = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
    setAuthEnabled(!isStaticExport && hasClerkKeys)
  }, [])

  if (!isClient) {
    return fallback || <div className="w-8 h-8 bg-gray-200 rounded-full" />
  }

  if (authEnabled) {
    return <UserButton />
  }

  return fallback || (
    <Button 
      variant="ghost" 
      size="sm"
      onClick={() => alert('User menu is currently disabled in static export mode')}
    >
      User
    </Button>
  )
}
