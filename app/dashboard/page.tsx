"use client";

import { useEffect, useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Overview } from "@/components/dashboard/overview";
import { RecentDeals } from "@/components/dashboard/recent-deals";
import { PipelineStatusTable } from "@/components/dashboard/pipeline-status-table";
import { TrendingUp, Users, FileText, Clock, Loader2, DollarSign, Target, Activity } from "lucide-react";
import { useAuth, withAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import { useAnalytics } from "@/hooks/use-analytics";
import { ExportButton, exportConfigs } from "@/components/ui/export-button";

interface DashboardData {
  deals: {
    total_deals: number;
    active_deals: number;
    closed_deals: number;
    total_value: number;
    win_rate: number;
  };
  clients: {
    total_clients: number;
    prospects: number;
    active_clients: number;
  };
  team: {
    total_users: number;
    active_users: number;
  };
  recent_deals: any[];
}

function DashboardPage() {
  const { user } = useAuth();

  // Use analytics hook for real-time dashboard data
  const {
    dashboardAnalytics,
    dealsPerformance,
    clientInsights,
    teamProductivity,
    loading,
    error,
    refreshAll,
    formatCurrency,
    formatPercentage,
    getRevenueGrowth,
    getConversionRate
  } = useAnalytics({
    autoFetch: true,
    refreshInterval: 60000 // Refresh every minute
  });

  // Legacy support for existing dashboard data structure
  const [legacyDashboardData, setLegacyDashboardData] = useState<DashboardData | null>(null);
  const [legacyLoading, setLegacyLoading] = useState(false);
  const [legacyError, setLegacyError] = useState<string | null>(null);

  // Fallback to legacy API if analytics data is not available
  useEffect(() => {
    if (!dashboardAnalytics && !loading) {
      const fetchLegacyData = async () => {
        setLegacyLoading(true);
        try {
          const response = await apiClient.getDashboardAnalytics();
          if (response.data) {
            setLegacyDashboardData(response.data as DashboardData);
          } else {
            setLegacyError(response.error || 'Failed to load dashboard data');
          }
        } catch (err) {
          setLegacyError('Failed to load dashboard data');
          console.error('Dashboard data fetch error:', err);
        } finally {
          setLegacyLoading(false);
        }
      };

      fetchLegacyData();
    }
  }, [dashboardAnalytics, loading]);

  // Determine loading and error states
  const isLoading = loading || legacyLoading;
  const currentError = error || legacyError;
  const currentData = dashboardAnalytics || legacyDashboardData;

  // Calculate dynamic KPI values from real analytics data
  const kpiData = useMemo(() => {
    if (!currentData) return null;

    return {
      totalDeals: dashboardAnalytics?.deals?.total_deals || currentData?.deals?.total_deals || 0,
      activeDeals: dashboardAnalytics?.deals?.active_deals || currentData?.deals?.active_deals || 0,
      totalClients: dashboardAnalytics?.clients?.total_clients || currentData?.clients?.total_clients || 0,
      teamSize: dashboardAnalytics?.team?.total_users || currentData?.team?.total_users || 0,
      totalRevenue: dashboardAnalytics?.deals?.total_value || 0,
      pipelineValue: dashboardAnalytics?.deals?.pipeline_value || 0,
      conversionRate: getConversionRate(),
      revenueGrowth: getRevenueGrowth(),
    };
  }, [currentData, dashboardAnalytics, getConversionRate, getRevenueGrowth]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="text-lg">Loading dashboard...</span>
        </div>
      </div>
    );
  }

  if (currentError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <p className="text-red-600 mb-4">{currentError}</p>
          <button
            onClick={() => refreshAll()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }
  return (
    <div className="flex flex-col space-y-8">
      {/* Dashboard Header */}
      <div className="flex flex-col space-y-unit-2">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-h1 bg-gradient-to-r from-dealverse-navy to-dealverse-blue bg-clip-text text-transparent">
              Welcome back, {user?.first_name}!
            </h1>
            <p className="text-body text-dealverse-medium-gray dark:text-dealverse-light-gray leading-relaxed">
              Here's what's happening with your deals today.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <ExportButton
              options={exportConfigs.analytics()}
              variant="outline"
              size="default"
            />
            <Button
              onClick={refreshAll}
              disabled={isLoading}
              className="dealverse-button-secondary"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Activity className="h-4 w-4" />
              )}
              <span className="ml-2">Refresh</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Enhanced KPI Cards */}
      <div className="grid gap-unit-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Deals Card */}
        <Card className="dealverse-card-interactive relative overflow-hidden border-0 bg-gradient-to-br from-dealverse-blue/10 to-dealverse-blue/20 dark:from-dealverse-blue/20 dark:to-dealverse-blue/30 shadow-lg group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-dealverse-blue/10 rounded-full -translate-y-12 translate-x-12"></div>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-unit-2">
            <CardTitle className="text-caption font-medium text-dealverse-navy dark:text-dealverse-light-gray">
              Total Deals
            </CardTitle>
            <div className="p-unit-2 bg-dealverse-blue/20 rounded-xl group-hover:bg-dealverse-blue/30 transition-colors duration-300">
              <FileText className="h-5 w-5 text-dealverse-blue" />
            </div>
          </CardHeader>
          <CardContent className="space-y-unit-2">
            <div className="text-h1 font-mono text-dealverse-navy dark:text-white">
              {kpiData?.totalDeals || 0}
            </div>
            <div className="flex items-center space-x-unit-1 text-caption">
              <TrendingUp className="h-4 w-4 text-dealverse-green" />
              <span className="text-dealverse-green font-semibold">
                +{kpiData?.activeDeals || 0}
              </span>
              <span className="text-dealverse-medium-gray dark:text-dealverse-light-gray">active deals</span>
            </div>
          </CardContent>
        </Card>

        {/* Active Deals Card */}
        <Card className="dealverse-card-interactive relative overflow-hidden border-0 bg-gradient-to-br from-dealverse-green/10 to-dealverse-green/20 dark:from-dealverse-green/20 dark:to-dealverse-green/30 shadow-lg group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-dealverse-green/10 rounded-full -translate-y-12 translate-x-12"></div>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-unit-2">
            <CardTitle className="text-caption font-medium text-dealverse-navy dark:text-dealverse-light-gray">
              Active Deals
            </CardTitle>
            <div className="p-unit-2 bg-dealverse-green/20 rounded-xl group-hover:bg-dealverse-green/30 transition-colors duration-300">
              <TrendingUp className="h-5 w-5 text-dealverse-green" />
            </div>
          </CardHeader>
          <CardContent className="space-y-unit-2">
            <div className="text-h1 font-mono text-dealverse-navy dark:text-white">
              {kpiData?.activeDeals || 0}
            </div>
            <div className="flex items-center space-x-unit-1 text-caption">
              <TrendingUp className="h-4 w-4 text-dealverse-green" />
              <span className="text-dealverse-green font-semibold">
                {formatPercentage(kpiData?.conversionRate || 0)}
              </span>
              <span className="text-dealverse-medium-gray dark:text-dealverse-light-gray">conversion rate</span>
            </div>
          </CardContent>
        </Card>

        {/* Revenue YTD Card */}
        <Card className="dealverse-card-interactive relative overflow-hidden border-0 bg-gradient-to-br from-dealverse-navy/10 to-dealverse-navy/20 dark:from-dealverse-navy/40 dark:to-dealverse-navy/50 shadow-lg group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-dealverse-navy/10 rounded-full -translate-y-12 translate-x-12"></div>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-unit-2">
            <CardTitle className="text-caption font-medium text-dealverse-navy dark:text-dealverse-light-gray">
              Revenue YTD
            </CardTitle>
            <div className="p-unit-2 bg-dealverse-navy/20 rounded-xl group-hover:bg-dealverse-navy/30 transition-colors duration-300">
              <DollarSign className="h-5 w-5 text-dealverse-navy dark:text-dealverse-light-gray" />
            </div>
          </CardHeader>
          <CardContent className="space-y-unit-2">
            <div className="text-h1 font-mono text-dealverse-navy dark:text-white">
              {formatCurrency(kpiData?.totalRevenue || 0)}
            </div>
            <div className="flex items-center space-x-unit-1 text-caption">
              <TrendingUp className={`h-4 w-4 ${(kpiData?.revenueGrowth ?? 0) >= 0 ? 'text-dealverse-green' : 'text-dealverse-coral'}`} />
              <span className={`font-semibold ${(kpiData?.revenueGrowth ?? 0) >= 0 ? 'text-dealverse-green' : 'text-dealverse-coral'}`}>
                {(kpiData?.revenueGrowth ?? 0) >= 0 ? '+' : ''}{formatPercentage(kpiData?.revenueGrowth || 0)}
              </span>
              <span className="text-dealverse-medium-gray dark:text-dealverse-light-gray">vs last month</span>
            </div>
          </CardContent>
        </Card>

        {/* Pipeline Value Card */}
        <Card className="dealverse-card-interactive relative overflow-hidden border-0 bg-gradient-to-br from-dealverse-amber/10 to-dealverse-amber/20 dark:from-dealverse-amber/20 dark:to-dealverse-amber/30 shadow-lg group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-dealverse-amber/10 rounded-full -translate-y-12 translate-x-12"></div>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-unit-2">
            <CardTitle className="text-caption font-medium text-dealverse-navy dark:text-dealverse-light-gray">
              Pipeline Value
            </CardTitle>
            <div className="p-unit-2 bg-dealverse-amber/20 rounded-xl group-hover:bg-dealverse-amber/30 transition-colors duration-300">
              <Target className="h-5 w-5 text-dealverse-amber" />
            </div>
          </CardHeader>
          <CardContent className="space-y-unit-2">
            <div className="text-h1 font-mono text-dealverse-navy dark:text-white">
              {formatCurrency(kpiData?.pipelineValue || 0)}
            </div>
            <div className="flex items-center space-x-unit-1 text-caption">
              <Activity className="h-4 w-4 text-dealverse-amber" />
              <span className="text-dealverse-amber font-semibold">{kpiData?.teamSize || 0}</span>
              <span className="text-dealverse-medium-gray dark:text-dealverse-light-gray">team members</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Enhanced Charts and Recent Deals Section */}
      <div className="grid gap-4 md:gap-6 lg:gap-8 grid-cols-1 lg:grid-cols-7">
        {/* Overview Chart */}
        <Card className="lg:col-span-4 border-0 shadow-xl bg-white dark:bg-dealverse-navy/50 hover:shadow-2xl transition-shadow duration-300">
          <CardHeader className="pb-6 space-y-2">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <CardTitle className="text-2xl font-semibold text-dealverse-navy dark:text-white">Revenue Overview</CardTitle>
                <CardDescription className="text-dealverse-medium-gray dark:text-dealverse-light-gray">
                  Monthly revenue trends and performance metrics
                </CardDescription>
              </div>
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-4 h-4 bg-dealverse-blue rounded-full"></div>
                  <span className="text-dealverse-medium-gray dark:text-dealverse-light-gray font-medium">Revenue</span>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pl-2">
            <Overview loading={isLoading} />
          </CardContent>
        </Card>

        {/* Recent Deals */}
        <Card className="col-span-3 border-0 shadow-xl bg-white dark:bg-dealverse-navy/50 hover:shadow-2xl transition-shadow duration-300">
          <CardHeader className="pb-6 space-y-2">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <CardTitle className="text-2xl font-semibold text-dealverse-navy dark:text-white">Recent Deals</CardTitle>
                <CardDescription className="text-dealverse-medium-gray dark:text-dealverse-light-gray">
                  Latest deals and their current status
                </CardDescription>
              </div>
              <button className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium">
                View All
              </button>
            </div>
          </CardHeader>
          <CardContent>
            <RecentDeals
              deals={dashboardAnalytics?.recent_deals?.map(deal => ({
                id: deal.id,
                clientName: deal.client_name,
                projectTitle: deal.project_title,
                status: deal.status as "negotiation" | "proposal" | "follow-up" | "won" | "lost",
                fallbackInitials: deal.client_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'UN',
                value: deal.value,
                createdAt: new Date(deal.created_at)
              }))}
              useHook={!dashboardAnalytics?.recent_deals}
              autoRefresh={true}
              refreshInterval={60000}
              showFilters={false}
              showPagination={false}
              itemsPerPage={5}
            />
          </CardContent>
        </Card>
      </div>

      {/* Pipeline Status Table */}
      <Card className="dealverse-card border-0 shadow-xl bg-white dark:bg-dealverse-navy/50">
        <CardHeader className="pb-unit-3 space-y-unit-1">
          <div className="flex items-center justify-between">
            <div className="space-y-unit-1">
              <CardTitle className="text-h2 text-dealverse-navy dark:text-white">
                Deal Pipeline Status
              </CardTitle>
              <CardDescription className="text-body text-dealverse-medium-gray dark:text-dealverse-light-gray">
                Current deal status with clear visual indicators and sortable columns
              </CardDescription>
            </div>
            <Button variant="outline" className="dealverse-button">
              Export Data
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <PipelineStatusTable />
        </CardContent>
      </Card>

      {/* Additional Dashboard Widgets */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Quick Actions */}
        <Card className="border-0 shadow-lg bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-slate-900 dark:text-slate-100">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <button className="w-full p-3 text-left rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
              <div className="font-medium text-slate-900 dark:text-slate-100">Create New Deal</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Start tracking a new opportunity</div>
            </button>
            <button className="w-full p-3 text-left rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
              <div className="font-medium text-slate-900 dark:text-slate-100">Add Client</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Register a new client</div>
            </button>
            <button className="w-full p-3 text-left rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
              <div className="font-medium text-slate-900 dark:text-slate-100">Schedule Follow-up</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Set reminder for client contact</div>
            </button>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="border-0 shadow-lg bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-slate-900 dark:text-slate-100">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <div className="text-sm font-medium text-slate-900 dark:text-slate-100">Deal closed with Acme Corp</div>
                <div className="text-xs text-slate-600 dark:text-slate-400">2 hours ago</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <div className="text-sm font-medium text-slate-900 dark:text-slate-100">New proposal sent to TechTron</div>
                <div className="text-xs text-slate-600 dark:text-slate-400">4 hours ago</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
              <div>
                <div className="text-sm font-medium text-slate-900 dark:text-slate-100">Follow-up scheduled with StartupXYZ</div>
                <div className="text-xs text-slate-600 dark:text-slate-400">6 hours ago</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Performance Summary */}
        <Card className="border-0 shadow-lg bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-slate-900 dark:text-slate-100">This Month</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600 dark:text-slate-400">Win Rate</span>
              <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">67%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600 dark:text-slate-400">Avg. Deal Size</span>
              <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">$15,400</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600 dark:text-slate-400">Sales Cycle</span>
              <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">23 days</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600 dark:text-slate-400">Revenue Goal</span>
              <span className="text-sm font-semibold text-green-600 dark:text-green-400">85% achieved</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default withAuth(DashboardPage);