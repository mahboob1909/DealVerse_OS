"use client"

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { cn } from '@/lib/utils'

interface VirtualScrollProps<T> {
  items: T[]
  itemHeight: number
  containerHeight: number
  renderItem: (item: T, index: number) => React.ReactNode
  className?: string
  overscan?: number
  onScroll?: (scrollTop: number) => void
  loading?: boolean
  hasMore?: boolean
  onLoadMore?: () => void
  loadingComponent?: React.ReactNode
}

export function VirtualScroll<T>({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  className,
  overscan = 5,
  onScroll,
  loading = false,
  hasMore = false,
  onLoadMore,
  loadingComponent
}: VirtualScrollProps<T>) {
  const [scrollTop, setScrollTop] = useState(0)
  const scrollElementRef = useRef<HTMLDivElement>(null)

  // Calculate visible range
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

  // Get visible items
  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.start, visibleRange.end).map((item, index) => ({
      item,
      index: visibleRange.start + index
    }))
  }, [items, visibleRange])

  // Handle scroll
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const scrollTop = e.currentTarget.scrollTop
    setScrollTop(scrollTop)
    onScroll?.(scrollTop)

    // Load more when near bottom
    if (hasMore && onLoadMore && !loading) {
      const { scrollHeight, clientHeight } = e.currentTarget
      const scrolledPercentage = (scrollTop + clientHeight) / scrollHeight
      
      if (scrolledPercentage > 0.8) {
        onLoadMore()
      }
    }
  }, [onScroll, hasMore, onLoadMore, loading])

  // Total height of all items
  const totalHeight = items.length * itemHeight

  // Offset for visible items
  const offsetY = visibleRange.start * itemHeight

  return (
    <div
      ref={scrollElementRef}
      className={cn("overflow-auto", className)}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
          }}
        >
          {visibleItems.map(({ item, index }) => (
            <div
              key={index}
              style={{ height: itemHeight }}
              className="flex items-center"
            >
              {renderItem(item, index)}
            </div>
          ))}
          
          {loading && (
            <div style={{ height: itemHeight }} className="flex items-center justify-center">
              {loadingComponent || (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="text-sm text-gray-500">Loading...</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Hook for virtual scrolling with infinite loading
export function useVirtualScroll<T>({
  fetchItems,
  itemsPerPage = 50,
  initialItems = []
}: {
  fetchItems: (page: number, limit: number) => Promise<T[]>
  itemsPerPage?: number
  initialItems?: T[]
}) {
  const [items, setItems] = useState<T[]>(initialItems)
  const [loading, setLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [page, setPage] = useState(0)

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return

    setLoading(true)
    try {
      const newItems = await fetchItems(page, itemsPerPage)
      
      if (newItems.length === 0) {
        setHasMore(false)
      } else {
        setItems(prev => [...prev, ...newItems])
        setPage(prev => prev + 1)
        
        if (newItems.length < itemsPerPage) {
          setHasMore(false)
        }
      }
    } catch (error) {
      console.error('Error loading more items:', error)
    } finally {
      setLoading(false)
    }
  }, [fetchItems, page, itemsPerPage, loading, hasMore])

  const reset = useCallback(() => {
    setItems(initialItems)
    setPage(0)
    setHasMore(true)
    setLoading(false)
  }, [initialItems])

  return {
    items,
    loading,
    hasMore,
    loadMore,
    reset,
    setItems
  }
}

// Optimized table with virtual scrolling
interface VirtualTableProps<T> {
  data: T[]
  columns: Array<{
    key: string
    header: string
    width?: number
    render?: (value: any, item: T, index: number) => React.ReactNode
  }>
  rowHeight?: number
  containerHeight?: number
  className?: string
  loading?: boolean
  hasMore?: boolean
  onLoadMore?: () => void
}

export function VirtualTable<T extends Record<string, any>>({
  data,
  columns,
  rowHeight = 60,
  containerHeight = 400,
  className,
  loading,
  hasMore,
  onLoadMore
}: VirtualTableProps<T>) {
  const renderRow = useCallback((item: T, index: number) => (
    <div className="flex border-b border-gray-200 hover:bg-gray-50">
      {columns.map((column, colIndex) => (
        <div
          key={column.key}
          className="flex items-center px-4 py-2 text-sm"
          style={{ 
            width: column.width || `${100 / columns.length}%`,
            minWidth: column.width || 'auto'
          }}
        >
          {column.render 
            ? column.render(item[column.key], item, index)
            : item[column.key]
          }
        </div>
      ))}
    </div>
  ), [columns])

  return (
    <div className={cn("border border-gray-200 rounded-lg overflow-hidden", className)}>
      {/* Header */}
      <div className="flex bg-gray-50 border-b border-gray-200">
        {columns.map((column) => (
          <div
            key={column.key}
            className="flex items-center px-4 py-3 text-sm font-medium text-gray-900"
            style={{ 
              width: column.width || `${100 / columns.length}%`,
              minWidth: column.width || 'auto'
            }}
          >
            {column.header}
          </div>
        ))}
      </div>

      {/* Virtual scrolled body */}
      <VirtualScroll
        items={data}
        itemHeight={rowHeight}
        containerHeight={containerHeight}
        renderItem={renderRow}
        loading={loading}
        hasMore={hasMore}
        onLoadMore={onLoadMore}
      />
    </div>
  )
}

// Grid layout with virtual scrolling
interface VirtualGridProps<T> {
  items: T[]
  renderItem: (item: T, index: number) => React.ReactNode
  itemWidth: number
  itemHeight: number
  containerWidth: number
  containerHeight: number
  gap?: number
  className?: string
  loading?: boolean
  hasMore?: boolean
  onLoadMore?: () => void
}

export function VirtualGrid<T>({
  items,
  renderItem,
  itemWidth,
  itemHeight,
  containerWidth,
  containerHeight,
  gap = 16,
  className,
  loading,
  hasMore,
  onLoadMore
}: VirtualGridProps<T>) {
  // Calculate columns that fit in container
  const columnsPerRow = Math.floor((containerWidth + gap) / (itemWidth + gap))
  const totalRows = Math.ceil(items.length / columnsPerRow)
  const rowHeight = itemHeight + gap

  const renderRow = useCallback((rowItems: T[], rowIndex: number) => (
    <div 
      className="flex"
      style={{ 
        height: itemHeight,
        gap: gap,
        marginBottom: gap
      }}
    >
      {rowItems.map((item, colIndex) => (
        <div
          key={rowIndex * columnsPerRow + colIndex}
          style={{ width: itemWidth, height: itemHeight }}
        >
          {renderItem(item, rowIndex * columnsPerRow + colIndex)}
        </div>
      ))}
    </div>
  ), [renderItem, itemWidth, itemHeight, gap, columnsPerRow])

  // Group items into rows
  const rows = useMemo(() => {
    const result: T[][] = []
    for (let i = 0; i < items.length; i += columnsPerRow) {
      result.push(items.slice(i, i + columnsPerRow))
    }
    return result
  }, [items, columnsPerRow])

  return (
    <div className={className} style={{ width: containerWidth }}>
      <VirtualScroll
        items={rows}
        itemHeight={rowHeight}
        containerHeight={containerHeight}
        renderItem={renderRow}
        loading={loading}
        hasMore={hasMore}
        onLoadMore={onLoadMore}
      />
    </div>
  )
}
