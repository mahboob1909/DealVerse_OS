"use client"

import React, { useMemo, useCallback, useState } from 'react'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { VirtualTable, useVirtualScroll } from '@/components/ui/virtual-scroll'
// Removed lazy-loader import as it was causing build issues
import { useOptimizedSearch, usePerformanceMonitor, useDebounce } from '@/hooks/use-performance'
import { useRecentDeals } from '@/hooks/use-recent-deals'
import { Deal } from '@/hooks/use-deals'
import { formatCurrency, cn } from '@/lib/utils'
import { Search, Filter, TrendingUp, DollarSign, Calendar, Eye } from 'lucide-react'
import Link from 'next/link'

interface OptimizedDealsListProps {
  maxHeight?: number
  showSearch?: boolean
  showFilters?: boolean
  enableVirtualization?: boolean
  itemsPerPage?: number
  onDealClick?: (deal: Deal) => void
  className?: string
}

export function OptimizedDealsList({
  maxHeight = 600,
  showSearch = true,
  showFilters = true,
  enableVirtualization = true,
  itemsPerPage = 50,
  onDealClick,
  className
}: OptimizedDealsListProps) {
  const { logRender } = usePerformanceMonitor('OptimizedDealsList')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  
  // Fetch deals with virtual scrolling support
  const fetchDeals = useCallback(async (page: number, limit: number) => {
    // This would be replaced with actual API call
    const response = await fetch(`/api/deals?page=${page}&limit=${limit}&status=${statusFilter}`)
    return response.json()
  }, [statusFilter])

  const {
    items: deals,
    loading,
    hasMore,
    loadMore
  } = useVirtualScroll({
    fetchItems: fetchDeals,
    itemsPerPage,
    initialItems: []
  })

  // Optimized search with debouncing
  const searchFn = useCallback((deal: Deal, query: string) => {
    const searchText = query.toLowerCase()
    return (
      deal.clientName?.toLowerCase().includes(searchText) ||
      deal.projectTitle?.toLowerCase().includes(searchText) ||
      deal.status?.toLowerCase().includes(searchText)
    )
  }, [])

  const {
    query: searchQuery,
    setQuery: setSearchQuery,
    filteredItems: searchedDeals,
    isSearching
  } = useOptimizedSearch(deals, searchFn, 300)

  // Memoized filtered deals
  const filteredDeals = useMemo(() => {
    if (statusFilter === 'all') return searchedDeals
    return searchedDeals.filter(deal => deal.status === statusFilter)
  }, [searchedDeals, statusFilter])

  // Memoized table columns
  const columns = useMemo(() => [
    {
      key: 'client',
      header: 'Client',
      width: 250,
      render: (value: any, deal: Deal) => (
        <div className="flex items-center space-x-3">
          <Avatar className="h-8 w-8">
            <AvatarImage src={deal.avatarUrl} alt={deal.clientName} />
            <AvatarFallback>{deal.fallbackInitials}</AvatarFallback>
          </Avatar>
          <div>
            <p className="font-medium text-sm">{deal.clientName}</p>
            <p className="text-xs text-gray-500">{deal.projectTitle}</p>
          </div>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      width: 120,
      render: (value: string) => (
        <Badge 
          variant={
            value === 'closed' ? 'default' :
            value === 'negotiation' ? 'secondary' :
            value === 'proposal' ? 'outline' : 'destructive'
          }
          className="capitalize"
        >
          {value}
        </Badge>
      )
    },
    {
      key: 'value',
      header: 'Value',
      width: 120,
      render: (value: number) => (
        <div className="flex items-center space-x-1">
          <DollarSign className="h-4 w-4 text-green-600" />
          <span className="font-medium">{formatCurrency(value)}</span>
        </div>
      )
    },
    {
      key: 'createdAt',
      header: 'Created',
      width: 120,
      render: (value: Date) => (
        <div className="flex items-center space-x-1">
          <Calendar className="h-4 w-4 text-gray-400" />
          <span className="text-sm">{new Date(value).toLocaleDateString()}</span>
        </div>
      )
    },
    {
      key: 'actions',
      header: 'Actions',
      width: 100,
      render: (value: any, deal: Deal) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDealClick?.(deal)}
          className="h-8 w-8 p-0"
        >
          <Eye className="h-4 w-4" />
        </Button>
      )
    }
  ], [onDealClick])

  // Render search and filters
  const renderFilters = useCallback(() => (
    <div className="flex items-center space-x-4 mb-4">
      {showSearch && (
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search deals..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
          {isSearching && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <div className="animate-spin h-4 w-4 border-2 border-gray-300 border-t-blue-600 rounded-full" />
            </div>
          )}
        </div>
      )}
      
      {showFilters && (
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-1 text-sm"
          >
            <option value="all">All Status</option>
            <option value="proposal">Proposal</option>
            <option value="negotiation">Negotiation</option>
            <option value="closed">Closed</option>
            <option value="follow-up">Follow-up</option>
          </select>
        </div>
      )}
    </div>
  ), [showSearch, showFilters, searchQuery, setSearchQuery, isSearching, statusFilter])

  // Render stats summary
  const renderStats = useCallback(() => {
    const totalValue = filteredDeals.reduce((sum, deal) => sum + (deal.value || 0), 0)
    const statusCounts = filteredDeals.reduce((acc, deal) => {
      acc[deal.status || 'unknown'] = (acc[deal.status || 'unknown'] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <Card className="p-3">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4 text-blue-600" />
            <div>
              <p className="text-xs text-gray-500">Total Deals</p>
              <p className="font-semibold">{filteredDeals.length}</p>
            </div>
          </div>
        </Card>
        
        <Card className="p-3">
          <div className="flex items-center space-x-2">
            <DollarSign className="h-4 w-4 text-green-600" />
            <div>
              <p className="text-xs text-gray-500">Total Value</p>
              <p className="font-semibold">{formatCurrency(totalValue)}</p>
            </div>
          </div>
        </Card>
        
        <Card className="p-3">
          <div>
            <p className="text-xs text-gray-500">Active</p>
            <p className="font-semibold">{statusCounts.negotiation || 0}</p>
          </div>
        </Card>
        
        <Card className="p-3">
          <div>
            <p className="text-xs text-gray-500">Closed</p>
            <p className="font-semibold">{statusCounts.closed || 0}</p>
          </div>
        </Card>
      </div>
    )
  }, [filteredDeals])

  logRender('Rendering optimized deals list')

  if (loading && filteredDeals.length === 0) {
    return <div className={`animate-pulse bg-gray-200 h-64 rounded ${className}`}>Loading...</div>
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div>
        {renderStats()}
      </div>
      
      <div>
        {renderFilters()}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Deals ({filteredDeals.length})</span>
            {hasMore && (
              <Button
                variant="outline"
                size="sm"
                onClick={loadMore}
                disabled={loading}
              >
                {loading ? 'Loading...' : 'Load More'}
              </Button>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {enableVirtualization ? (
            <VirtualTable
              data={filteredDeals}
              columns={columns}
              rowHeight={60}
              containerHeight={maxHeight}
              loading={loading}
              hasMore={hasMore}
              onLoadMore={loadMore}
            />
          ) : (
            <div className="max-h-96 overflow-y-auto">
              {filteredDeals.map((deal, index) => (
                <div
                  key={deal.id}
                  className="flex items-center justify-between p-4 border-b border-gray-200 hover:bg-gray-50 cursor-pointer"
                  onClick={() => onDealClick?.(deal)}
                >
                  <div className="flex items-center space-x-3">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={deal.avatarUrl} alt={deal.clientName} />
                      <AvatarFallback>{deal.fallbackInitials}</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-medium text-sm">{deal.clientName}</p>
                      <p className="text-xs text-gray-500">{deal.projectTitle}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <Badge variant="outline" className="capitalize">
                      {deal.status}
                    </Badge>
                    <span className="font-medium">{formatCurrency(deal.value || 0)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
