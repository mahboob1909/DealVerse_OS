"use client"

import React, { Suspense, lazy, ComponentType, useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

// Loading spinner component
export function LoadingSpinner({ 
  size = 'md', 
  className 
}: { 
  size?: 'sm' | 'md' | 'lg'
  className?: string 
}) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8', 
    lg: 'h-12 w-12'
  }

  return (
    <div className={cn("flex items-center justify-center", className)}>
      <div className={cn(
        "animate-spin rounded-full border-2 border-gray-300 border-t-blue-600",
        sizeClasses[size]
      )} />
    </div>
  )
}

// Loading skeleton for different content types
export function LoadingSkeleton({ 
  type = 'card',
  count = 1,
  className 
}: {
  type?: 'card' | 'table' | 'list' | 'text' | 'chart'
  count?: number
  className?: string
}) {
  const renderSkeleton = () => {
    switch (type) {
      case 'card':
        return (
          <div className="animate-pulse">
            <div className="bg-gray-200 rounded-lg p-6 space-y-4">
              <div className="h-4 bg-gray-300 rounded w-3/4"></div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-300 rounded"></div>
                <div className="h-3 bg-gray-300 rounded w-5/6"></div>
              </div>
              <div className="h-8 bg-gray-300 rounded w-1/4"></div>
            </div>
          </div>
        )
      
      case 'table':
        return (
          <div className="animate-pulse">
            <div className="bg-gray-200 rounded-lg overflow-hidden">
              <div className="bg-gray-300 h-12"></div>
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="border-t border-gray-300 h-16 bg-gray-200"></div>
              ))}
            </div>
          </div>
        )
      
      case 'list':
        return (
          <div className="animate-pulse space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center space-x-4">
                <div className="rounded-full bg-gray-300 h-10 w-10"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-300 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-300 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        )
      
      case 'chart':
        return (
          <div className="animate-pulse">
            <div className="bg-gray-200 rounded-lg p-6">
              <div className="h-4 bg-gray-300 rounded w-1/4 mb-4"></div>
              <div className="h-64 bg-gray-300 rounded"></div>
            </div>
          </div>
        )
      
      case 'text':
        return (
          <div className="animate-pulse space-y-2">
            <div className="h-4 bg-gray-300 rounded"></div>
            <div className="h-4 bg-gray-300 rounded w-5/6"></div>
            <div className="h-4 bg-gray-300 rounded w-4/6"></div>
          </div>
        )
      
      default:
        return <LoadingSpinner />
    }
  }

  return (
    <div className={className}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={count > 1 ? "mb-4" : ""}>
          {renderSkeleton()}
        </div>
      ))}
    </div>
  )
}

// Lazy component wrapper with error boundary
interface LazyWrapperProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  errorFallback?: React.ReactNode
  className?: string
}

export function LazyWrapper({ 
  children, 
  fallback = <LoadingSpinner />, 
  errorFallback,
  className 
}: LazyWrapperProps) {
  return (
    <div className={className}>
      <Suspense fallback={fallback}>
        <ErrorBoundary fallback={errorFallback}>
          {children}
        </ErrorBoundary>
      </Suspense>
    </div>
  )
}

// Error boundary component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode; fallback?: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Lazy loading error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex items-center justify-center p-8 text-center">
          <div className="text-red-600">
            <p className="font-medium">Failed to load component</p>
            <p className="text-sm text-gray-500 mt-1">Please try refreshing the page</p>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook for lazy loading with intersection observer
export function useLazyLoad(threshold = 0.1) {
  const [isVisible, setIsVisible] = useState(false)
  const [ref, setRef] = useState<HTMLElement | null>(null)

  useEffect(() => {
    if (!ref) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      { threshold }
    )

    observer.observe(ref)

    return () => observer.disconnect()
  }, [ref, threshold])

  return { ref: setRef, isVisible }
}

// Lazy image component with intersection observer
interface LazyImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string
  alt: string
  placeholder?: string
  className?: string
  containerClassName?: string
}

export function LazyImage({ 
  src, 
  alt, 
  placeholder, 
  className, 
  containerClassName,
  ...props 
}: LazyImageProps) {
  const { ref, isVisible } = useLazyLoad()
  const [loaded, setLoaded] = useState(false)
  const [error, setError] = useState(false)

  return (
    <div ref={ref} className={cn("relative overflow-hidden", containerClassName)}>
      {!isVisible ? (
        <div className={cn("bg-gray-200 animate-pulse", className)} />
      ) : (
        <>
          {!loaded && !error && (
            <div className={cn("absolute inset-0 bg-gray-200 animate-pulse", className)} />
          )}
          
          {error ? (
            <div className={cn("bg-gray-100 flex items-center justify-center", className)}>
              <span className="text-gray-400 text-sm">Failed to load</span>
            </div>
          ) : (
            <img
              src={src}
              alt={alt}
              className={cn(
                "transition-opacity duration-300",
                loaded ? "opacity-100" : "opacity-0",
                className
              )}
              onLoad={() => setLoaded(true)}
              onError={() => setError(true)}
              {...props}
            />
          )}
        </>
      )}
    </div>
  )
}

// Lazy section component for large pages
interface LazySectionProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  className?: string
  threshold?: number
}

export function LazySection({ 
  children, 
  fallback = <LoadingSkeleton type="card" />, 
  className,
  threshold = 0.1 
}: LazySectionProps) {
  const { ref, isVisible } = useLazyLoad(threshold)

  return (
    <div ref={ref} className={className}>
      {isVisible ? children : fallback}
    </div>
  )
}

// Higher-order component for lazy loading
export function withLazyLoading<P extends object>(
  Component: ComponentType<P>,
  fallback?: React.ReactNode
) {
  const LazyComponent = lazy(() => Promise.resolve({ default: Component }))
  
  return function WrappedComponent(props: P) {
    return (
      <LazyWrapper fallback={fallback}>
        <LazyComponent {...props} />
      </LazyWrapper>
    )
  }
}

// Preloader for critical components
export function preloadComponent(importFn: () => Promise<any>) {
  // Preload on idle or after a delay
  if (typeof window !== 'undefined') {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => importFn())
    } else {
      setTimeout(() => importFn(), 100)
    }
  }
}

// Bundle analyzer helper (development only)
export function logBundleSize(componentName: string) {
  if (process.env.NODE_ENV === 'development') {
    console.log(`Loading component: ${componentName}`)
  }
}
