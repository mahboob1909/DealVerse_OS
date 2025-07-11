"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  LineChart,
  Target,
  Users,
  DollarSign,
  Calendar,
  Award,
  AlertTriangle,
  CheckCircle,
  Loader2,
  RefreshCw,
  Download,
  Filter,
  Zap
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { toast } from 'sonner';

interface AdvancedAnalytics {
  overview: {
    date_range: {
      start: string;
      end: string;
    };
    organization_id: string;
    generated_at: string;
  };
  kpis: {
    revenue_efficiency: any;
    growth_metrics: any;
    operational_efficiency: any;
  };
  deal_analytics: any;
  client_analytics: any;
  team_analytics: any;
  financial_analytics: any;
  trends: any;
  predictions: any;
  benchmarks: any;
}

export function AdvancedAnalyticsDashboard() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState<AdvancedAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('90');
  const [selectedFocus, setSelectedFocus] = useState('all');

  useEffect(() => {
    fetchAdvancedAnalytics();
  }, [selectedPeriod]);

  const fetchAdvancedAnalytics = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/analytics/advanced?days=${selectedPeriod}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch analytics');
      }

      const data = await response.json();
      setAnalytics(data.analytics);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      toast.error('Failed to load advanced analytics');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const getPerformanceColor = (rating: string) => {
    switch (rating) {
      case 'excellent': return 'text-green-600 bg-green-50';
      case 'good': return 'text-blue-600 bg-blue-50';
      case 'average': return 'text-yellow-600 bg-yellow-50';
      case 'poor': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getPerformanceIcon = (rating: string) => {
    switch (rating) {
      case 'excellent': return <Award className="h-4 w-4" />;
      case 'good': return <CheckCircle className="h-4 w-4" />;
      case 'average': return <Target className="h-4 w-4" />;
      case 'poor': return <AlertTriangle className="h-4 w-4" />;
      default: return <BarChart3 className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading advanced analytics...</span>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="h-12 w-12 mx-auto text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Analytics Data</h3>
        <p className="text-gray-500 mb-4">Unable to load analytics data.</p>
        <Button onClick={fetchAdvancedAnalytics}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-dealverse-navy to-dealverse-blue bg-clip-text text-transparent">
            Advanced Analytics
          </h1>
          <p className="text-dealverse-medium-gray dark:text-dealverse-light-gray">
            Business intelligence and predictive insights for data-driven decisions
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="30">30 Days</SelectItem>
              <SelectItem value="60">60 Days</SelectItem>
              <SelectItem value="90">90 Days</SelectItem>
              <SelectItem value="180">6 Months</SelectItem>
              <SelectItem value="365">1 Year</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={fetchAdvancedAnalytics}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Performance Score Overview */}
      <Card className="border-0 bg-gradient-to-br from-dealverse-blue/10 to-dealverse-green/10">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Zap className="h-5 w-5 mr-2 text-dealverse-blue" />
            Overall Performance Score
          </CardTitle>
          <CardDescription>
            Comprehensive performance rating based on key business metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-4xl font-bold text-dealverse-navy">
                {analytics.benchmarks?.overall_score?.score || 0}
              </div>
              <div className="flex flex-col">
                <Badge className={`${getPerformanceColor(analytics.benchmarks?.overall_score?.rating || 'average')} border-0`}>
                  {getPerformanceIcon(analytics.benchmarks?.overall_score?.rating || 'average')}
                  <span className="ml-1 capitalize">{analytics.benchmarks?.overall_score?.rating || 'Average'}</span>
                </Badge>
                <span className="text-sm text-dealverse-medium-gray mt-1">
                  Based on {analytics.benchmarks?.overall_score?.total_metrics || 0} metrics
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-dealverse-medium-gray">Performance Trend</div>
              <div className="flex items-center text-green-600">
                <TrendingUp className="h-4 w-4 mr-1" />
                <span className="font-medium">+5.2%</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Revenue Efficiency</CardTitle>
            <DollarSign className="h-4 w-4 text-dealverse-green" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {formatCurrency(analytics.kpis?.revenue_efficiency?.revenue_per_deal || 0)}
            </div>
            <p className="text-xs text-dealverse-medium-gray">
              Revenue per deal
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
            <Target className="h-4 w-4 text-dealverse-blue" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {formatPercentage(analytics.deal_analytics?.win_rate || 0)}
            </div>
            <p className="text-xs text-dealverse-medium-gray">
              Deal conversion rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Deal Velocity</CardTitle>
            <Calendar className="h-4 w-4 text-dealverse-purple" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {Math.round(analytics.deal_analytics?.average_deal_duration_days || 0)}
            </div>
            <p className="text-xs text-dealverse-medium-gray">
              Days to close
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Productivity</CardTitle>
            <Users className="h-4 w-4 text-dealverse-orange" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {analytics.team_analytics?.team_productivity?.average_deals_per_user?.toFixed(1) || '0.0'}
            </div>
            <p className="text-xs text-dealverse-medium-gray">
              Deals per team member
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Analytics Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="deals">Deals</TabsTrigger>
          <TabsTrigger value="clients">Clients</TabsTrigger>
          <TabsTrigger value="team">Team</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Deal Stage Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <PieChart className="h-5 w-5 mr-2" />
                  Deal Stage Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(analytics.deal_analytics?.stage_distribution || {}).map(([stage, count]) => (
                    <div key={stage} className="flex items-center justify-between">
                      <span className="text-sm capitalize">{stage.replace('_', ' ')}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-dealverse-blue h-2 rounded-full" 
                            style={{ 
                              width: `${(count as number / analytics.deal_analytics?.deals_in_period * 100) || 0}%` 
                            }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium w-8">{count as number}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Performance Benchmarks */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Award className="h-5 w-5 mr-2" />
                  Performance vs Benchmarks
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(analytics.benchmarks?.performance_ratings || {}).map(([metric, data]: [string, any]) => (
                    <div key={metric} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm capitalize">{metric.replace('_', ' ')}</span>
                        <Badge className={`${getPerformanceColor(data.rating)} border-0 text-xs`}>
                          {data.rating}
                        </Badge>
                      </div>
                      <div className="text-xs text-dealverse-medium-gray">
                        Current: {typeof data.current_value === 'number' ? 
                          (metric.includes('size') ? formatCurrency(data.current_value) : 
                           metric.includes('rate') ? formatPercentage(data.current_value) : 
                           data.current_value) : data.current_value}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="deals" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Deal Analytics Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>Total Deals</span>
                    <span className="font-medium">{analytics.deal_analytics?.total_deals || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Active Deals</span>
                    <span className="font-medium">{analytics.deal_analytics?.active_deals || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Pipeline Value</span>
                    <span className="font-medium">{formatCurrency(analytics.deal_analytics?.total_pipeline_value || 0)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average Deal Size</span>
                    <span className="font-medium">{formatCurrency(analytics.deal_analytics?.average_deal_size || 0)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Conversion Funnel</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(analytics.deal_analytics?.conversion_funnel || {}).map(([stage, count]) => (
                    <div key={stage} className="flex items-center justify-between">
                      <span className="text-sm capitalize">{stage.replace('_', ' ')}</span>
                      <span className="font-medium">{count as number}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="clients" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Client Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>Total Clients</span>
                    <span className="font-medium">{analytics.client_analytics?.total_clients || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>New Clients (Period)</span>
                    <span className="font-medium">{analytics.client_analytics?.new_clients_in_period || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average Client Value</span>
                    <span className="font-medium">{formatCurrency(analytics.client_analytics?.average_client_value || 0)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Acquisition Rate</span>
                    <span className="font-medium">{analytics.client_analytics?.client_acquisition_rate?.toFixed(1) || 0}/month</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Industries</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analytics.client_analytics?.top_industries?.slice(0, 5).map(([industry, count]: [string, number]) => (
                    <div key={industry} className="flex items-center justify-between">
                      <span className="text-sm">{industry}</span>
                      <span className="font-medium">{count}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="team" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Team Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-dealverse-navy">
                      {analytics.team_analytics?.total_team_members || 0}
                    </div>
                    <div className="text-sm text-dealverse-medium-gray">Team Members</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-dealverse-navy">
                      {analytics.team_analytics?.team_productivity?.total_deals_in_period || 0}
                    </div>
                    <div className="text-sm text-dealverse-medium-gray">Total Deals</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-dealverse-navy">
                      {analytics.team_analytics?.team_productivity?.average_deals_per_user?.toFixed(1) || '0.0'}
                    </div>
                    <div className="text-sm text-dealverse-medium-gray">Avg Deals/User</div>
                  </div>
                </div>

                {/* Top Performers */}
                <div className="mt-6">
                  <h4 className="font-medium mb-3">Top Performers</h4>
                  <div className="space-y-2">
                    {analytics.team_analytics?.team_productivity?.top_performers?.slice(0, 5).map((performer: any, index: number) => (
                      <div key={performer.user_id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="w-6 h-6 rounded-full p-0 flex items-center justify-center">
                            {index + 1}
                          </Badge>
                          <span className="text-sm font-medium">{performer.name}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium">{formatCurrency(performer.total_value)}</div>
                          <div className="text-xs text-dealverse-medium-gray">{performer.deals_count} deals</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Next Month Projections
                </CardTitle>
              </CardHeader>
              <CardContent>
                {analytics.predictions?.next_month_projection ? (
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>Projected Deals</span>
                      <span className="font-medium">{analytics.predictions.next_month_projection.projected_deals || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Projected Value</span>
                      <span className="font-medium">{formatCurrency(analytics.predictions.next_month_projection.projected_value || 0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Growth Rate (Deals)</span>
                      <span className="font-medium">{formatPercentage(analytics.predictions.next_month_projection.growth_rate_deals || 0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Growth Rate (Value)</span>
                      <span className="font-medium">{formatPercentage(analytics.predictions.next_month_projection.growth_rate_value || 0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Confidence</span>
                      <Badge variant="outline" className="capitalize">
                        {analytics.predictions.next_month_projection.confidence || 'Low'}
                      </Badge>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <AlertTriangle className="h-8 w-8 mx-auto text-yellow-500 mb-2" />
                    <p className="text-sm text-dealverse-medium-gray">
                      Insufficient data for predictions
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                {analytics.predictions?.recommendations?.length > 0 ? (
                  <div className="space-y-3">
                    {analytics.predictions.recommendations.map((recommendation: string, index: number) => (
                      <div key={index} className="flex items-start space-x-2">
                        <CheckCircle className="h-4 w-4 text-dealverse-green mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{recommendation}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <CheckCircle className="h-8 w-8 mx-auto text-green-500 mb-2" />
                    <p className="text-sm text-dealverse-medium-gray">
                      Performance is on track - no specific recommendations at this time
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
