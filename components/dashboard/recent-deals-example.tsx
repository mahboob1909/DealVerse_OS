"use client";

import React, { useState } from "react";
import { RecentDeals } from "./recent-deals";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Deal } from "@/hooks/use-deals";
import { useDealStats } from "@/hooks/use-recent-deals";

export function RecentDealsExample() {
  const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null);
  const [useHookData, setUseHookData] = useState(false);
  const { stats, isLoading: statsLoading } = useDealStats();

  const handleDealClick = (deal: Deal) => {
    setSelectedDeal(deal);
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Deals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? "..." : stats.total}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats.active} active deals
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? "..." : `${stats.winRate.toFixed(1)}%`}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats.won} won, {stats.lost} lost
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? "..." : `$${stats.totalValue.toLocaleString()}`}
            </div>
            <p className="text-xs text-muted-foreground">
              Avg: ${stats.averageValue.toLocaleString()}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Source</CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              variant={useHookData ? "default" : "outline"}
              size="sm"
              onClick={() => setUseHookData(!useHookData)}
            >
              {useHookData ? "Live Data" : "Static Data"}
            </Button>
            <p className="text-xs text-muted-foreground mt-1">
              {useHookData ? "Using API hook" : "Using props"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Deals Component */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recent Deals</CardTitle>
            <CardDescription>
              Your most recent deals with advanced filtering and pagination
            </CardDescription>
          </CardHeader>
          <CardContent>
            <RecentDeals
              useHook={useHookData}
              autoRefresh={useHookData}
              refreshInterval={10000} // 10 seconds
              showFilters={true}
              showPagination={true}
              itemsPerPage={5}
              onDealClick={handleDealClick}
            />
          </CardContent>
        </Card>

        {/* Deal Details Panel */}
        <Card>
          <CardHeader>
            <CardTitle>Deal Details</CardTitle>
            <CardDescription>
              {selectedDeal ? "Selected deal information" : "Click a deal to view details"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedDeal ? (
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold">{selectedDeal.clientName}</h3>
                  <p className="text-sm text-muted-foreground">
                    {selectedDeal.projectTitle}
                  </p>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Status:</span>
                    <Badge variant="outline">
                      {selectedDeal.status}
                    </Badge>
                  </div>
                  
                  {selectedDeal.value && (
                    <div className="flex justify-between">
                      <span className="text-sm">Value:</span>
                      <span className="text-sm font-medium">
                        ${selectedDeal.value.toLocaleString()}
                      </span>
                    </div>
                  )}
                  
                  {selectedDeal.createdAt && (
                    <div className="flex justify-between">
                      <span className="text-sm">Created:</span>
                      <span className="text-sm">
                        {selectedDeal.createdAt.toLocaleDateString()}
                      </span>
                    </div>
                  )}
                  
                  {selectedDeal.description && (
                    <div>
                      <span className="text-sm font-medium">Description:</span>
                      <p className="text-sm text-muted-foreground mt-1">
                        {selectedDeal.description}
                      </p>
                    </div>
                  )}
                </div>

                <div className="pt-4 space-y-2">
                  <Button size="sm" className="w-full">
                    Edit Deal
                  </Button>
                  <Button size="sm" variant="outline" className="w-full">
                    View Full Details
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-sm text-muted-foreground">
                  Select a deal from the list to view its details here.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Feature Showcase */}
      <Card>
        <CardHeader>
          <CardTitle>Features Implemented</CardTitle>
          <CardDescription>
            All the improvements made to the RecentDeals component
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-2">
              <h4 className="font-medium">✅ Loading States</h4>
              <p className="text-sm text-muted-foreground">
                Skeleton loaders for better UX
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">✅ Pagination</h4>
              <p className="text-sm text-muted-foreground">
                Handle large datasets efficiently
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">✅ Filtering</h4>
              <p className="text-sm text-muted-foreground">
                Search and status filtering
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">✅ Performance</h4>
              <p className="text-sm text-muted-foreground">
                React.memo and useMemo optimizations
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">✅ Data Integration</h4>
              <p className="text-sm text-muted-foreground">
                Custom hooks for API integration
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">✅ Unit Tests</h4>
              <p className="text-sm text-muted-foreground">
                Comprehensive test coverage
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
