"use client"

import { useCallback, useMemo, useRef, useEffect, useState } from 'react'

// Debounce hook for performance optimization
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

// Throttle hook for performance optimization
export function useThrottle<T>(value: T, limit: number): T {
  const [throttledValue, setThrottledValue] = useState<T>(value)
  const lastRan = useRef<number>(Date.now())

  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value)
        lastRan.current = Date.now()
      }
    }, limit - (Date.now() - lastRan.current))

    return () => {
      clearTimeout(handler)
    }
  }, [value, limit])

  return throttledValue
}

// Memoized callback with dependencies optimization
export function useOptimizedCallback<T extends (...args: any[]) => any>(
  callback: T,
  deps: React.DependencyList
): T {
  return useCallback(callback, deps)
}

// Memoized value with deep comparison
export function useDeepMemo<T>(factory: () => T, deps: React.DependencyList): T {
  const ref = useRef<{ deps: React.DependencyList; value: T }>()

  if (!ref.current || !deepEqual(ref.current.deps, deps)) {
    ref.current = { deps, value: factory() }
  }

  return ref.current.value
}

// Deep equality check
function deepEqual(a: any, b: any): boolean {
  if (a === b) return true
  
  if (a == null || b == null) return false
  
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false
    for (let i = 0; i < a.length; i++) {
      if (!deepEqual(a[i], b[i])) return false
    }
    return true
  }
  
  if (typeof a === 'object' && typeof b === 'object') {
    const keysA = Object.keys(a)
    const keysB = Object.keys(b)
    
    if (keysA.length !== keysB.length) return false
    
    for (const key of keysA) {
      if (!keysB.includes(key) || !deepEqual(a[key], b[key])) {
        return false
      }
    }
    return true
  }
  
  return false
}

// Performance monitoring hook
export function usePerformanceMonitor(componentName: string) {
  const renderCount = useRef(0)
  const startTime = useRef<number>(Date.now())

  useEffect(() => {
    renderCount.current += 1
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`${componentName} rendered ${renderCount.current} times`)
      
      // Log slow renders
      const renderTime = Date.now() - startTime.current
      if (renderTime > 16) { // More than one frame (60fps)
        console.warn(`Slow render detected in ${componentName}: ${renderTime}ms`)
      }
    }
    
    startTime.current = Date.now()
  })

  return {
    renderCount: renderCount.current,
    logRender: (message?: string) => {
      if (process.env.NODE_ENV === 'development') {
        console.log(`${componentName}: ${message || 'rendered'}`)
      }
    }
  }
}

// Intersection observer hook for lazy loading
export function useIntersectionObserver(
  options: IntersectionObserverInit = {}
) {
  const [isIntersecting, setIsIntersecting] = useState(false)
  const [entry, setEntry] = useState<IntersectionObserverEntry | null>(null)
  const elementRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    const element = elementRef.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting)
        setEntry(entry)
      },
      options
    )

    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [options])

  return {
    ref: elementRef,
    isIntersecting,
    entry
  }
}

// Optimized list rendering hook
export function useVirtualizedList<T>({
  items,
  itemHeight,
  containerHeight,
  overscan = 5
}: {
  items: T[]
  itemHeight: number
  containerHeight: number
  overscan?: number
}) {
  const [scrollTop, setScrollTop] = useState(0)

  const visibleRange = useMemo(() => {
    const start = Math.floor(scrollTop / itemHeight)
    const end = Math.min(
      start + Math.ceil(containerHeight / itemHeight),
      items.length
    )

    return {
      start: Math.max(0, start - overscan),
      end: Math.min(items.length, end + overscan)
    }
  }, [scrollTop, itemHeight, containerHeight, items.length, overscan])

  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.start, visibleRange.end)
  }, [items, visibleRange])

  const totalHeight = items.length * itemHeight
  const offsetY = visibleRange.start * itemHeight

  return {
    visibleItems,
    totalHeight,
    offsetY,
    setScrollTop,
    visibleRange
  }
}

// Memory usage monitoring hook
export function useMemoryMonitor() {
  const [memoryInfo, setMemoryInfo] = useState<any>(null)

  useEffect(() => {
    if ('memory' in performance) {
      const updateMemoryInfo = () => {
        setMemoryInfo({
          usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
          totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
          jsHeapSizeLimit: (performance as any).memory.jsHeapSizeLimit
        })
      }

      updateMemoryInfo()
      const interval = setInterval(updateMemoryInfo, 5000) // Update every 5 seconds

      return () => clearInterval(interval)
    }
  }, [])

  return memoryInfo
}

// Optimized state updates hook
export function useBatchedUpdates() {
  const [updates, setUpdates] = useState<Array<() => void>>([])
  const timeoutRef = useRef<NodeJS.Timeout>()

  const batchUpdate = useCallback((updateFn: () => void) => {
    setUpdates(prev => [...prev, updateFn])

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    timeoutRef.current = setTimeout(() => {
      setUpdates(currentUpdates => {
        currentUpdates.forEach(update => update())
        return []
      })
    }, 0)
  }, [])

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return batchUpdate
}

// Component size monitoring hook
export function useElementSize() {
  const [size, setSize] = useState({ width: 0, height: 0 })
  const elementRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    const element = elementRef.current
    if (!element) return

    const resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect
        setSize({ width, height })
      }
    })

    resizeObserver.observe(element)

    return () => {
      resizeObserver.disconnect()
    }
  }, [])

  return {
    ref: elementRef,
    size
  }
}

// Optimized search hook with debouncing
export function useOptimizedSearch<T>(
  items: T[],
  searchFn: (item: T, query: string) => boolean,
  delay: number = 300
) {
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounce(query, delay)

  const filteredItems = useMemo(() => {
    if (!debouncedQuery.trim()) return items
    return items.filter(item => searchFn(item, debouncedQuery))
  }, [items, debouncedQuery, searchFn])

  return {
    query,
    setQuery,
    filteredItems,
    isSearching: query !== debouncedQuery
  }
}

// Performance timing hook
export function usePerformanceTiming(name: string) {
  const startTime = useRef<number>()

  const start = useCallback(() => {
    startTime.current = performance.now()
    if (process.env.NODE_ENV === 'development') {
      console.time(name)
    }
  }, [name])

  const end = useCallback(() => {
    if (startTime.current) {
      const duration = performance.now() - startTime.current
      if (process.env.NODE_ENV === 'development') {
        console.timeEnd(name)
        if (duration > 100) {
          console.warn(`Performance warning: ${name} took ${duration.toFixed(2)}ms`)
        }
      }
      return duration
    }
    return 0
  }, [name])

  return { start, end }
}
