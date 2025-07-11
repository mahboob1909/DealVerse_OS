"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Search,
  Filter,
  TrendingUp,
  Target,
  Brain,
  Globe,
  DollarSign,
  Building,
  Calendar,
  Star,
  AlertCircle,
  RefreshCw,
  MapPin,
  Users,
  AlertTriangle,
  Lightbulb,
  BarChart3,
  PieChart,
  Activity,
  Zap,
  Award,
  Clock,
  ArrowUp,
  ArrowDown,
  Minus
} from "lucide-react";
import { useState, useEffect, useMemo } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell, LineChart, Line, BarChart, Bar } from "recharts";
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { useProspects } from '@/hooks/use-prospects';
import { useWebSocket } from '@/hooks/use-websocket';

// Enhanced interfaces for Prospect AI
interface ProspectAnalysisData {
  company_name: string;
  industry: string;
  location?: string;
  market_cap?: number;
  revenue?: number;
  employees?: number;
  financial_data?: Record<string, any>;
  business_model?: string;
  target_market?: string;
  competitive_landscape?: string;
}

interface MarketIntelligenceData {
  market_overview: {
    total_market_size: string;
    growth_rate: string;
    key_trends: string[];
    market_sentiment: string;
  };
  industry_trends: Array<{
    trend: string;
    impact: string;
    confidence: number;
  }>;
  recent_transactions: Array<{
    company: string;
    deal_size: string;
    deal_type: string;
    date: string;
    multiple: string;
  }>;
  market_alerts: Array<{
    type: string;
    message: string;
    severity: string;
    date: string;
  }>;
}

interface ScoreBreakdown {
  financial_health: number;
  market_position: number;
  growth_potential: number;
  strategic_fit: number;
}

// Chart data generation functions
const generateScoreDistributionData = (prospects: any[]) => {
  const scoreRanges = [
    { range: '90-100', count: 0, color: '#00c896' },
    { range: '80-89', count: 0, color: '#0066ff' },
    { range: '70-79', count: 0, color: '#ffa500' },
    { range: '60-69', count: 0, color: '#ff6b6b' },
    { range: '0-59', count: 0, color: '#6c757d' }
  ];

  prospects.forEach(prospect => {
    const score = prospect.ai_score;
    if (score >= 90) scoreRanges[0].count++;
    else if (score >= 80) scoreRanges[1].count++;
    else if (score >= 70) scoreRanges[2].count++;
    else if (score >= 60) scoreRanges[3].count++;
    else scoreRanges[4].count++;
  });

  return scoreRanges;
};

const generateIndustryTrendsData = (marketIntelligence: MarketIntelligenceData | null) => {
  if (!marketIntelligence?.industry_trends) {
    return [
      { industry: 'Technology', growth: 15.2, deals: 45 },
      { industry: 'Healthcare', growth: 12.8, deals: 32 },
      { industry: 'Energy', growth: 18.5, deals: 28 },
      { industry: 'Finance', growth: 8.9, deals: 38 },
      { industry: 'Manufacturing', growth: 6.7, deals: 22 }
    ];
  }

  return marketIntelligence.industry_trends.map(trend => ({
    industry: trend.trend,
    growth: trend.confidence,
    deals: Math.floor(Math.random() * 50) + 10
  }));
};

// Pipeline stages for drag-and-drop
const pipelineStages = {
  "prospect": {
    id: "prospect",
    title: "Prospects",
    color: "#6c757d",
    items: ["1"]
  },
  "initial-contact": {
    id: "initial-contact",
    title: "Initial Contact",
    color: "#0066ff",
    items: []
  },
  "due-diligence": {
    id: "due-diligence",
    title: "Due Diligence",
    color: "#ff9500",
    items: ["2"]
  },
  "negotiation": {
    id: "negotiation",
    title: "Negotiation",
    color: "#ff9500",
    items: []
  },
  "closing": {
    id: "closing",
    title: "Closing",
    color: "#00c896",
    items: ["3"]
  }
};

// Market trend data for charts
const marketTrendData = [
  { month: "Jan", deals: 45, value: 2.1 },
  { month: "Feb", deals: 52, value: 2.8 },
  { month: "Mar", deals: 48, value: 2.4 },
  { month: "Apr", deals: 61, value: 3.2 },
  { month: "May", deals: 55, value: 2.9 },
  { month: "Jun", deals: 67, value: 3.8 },
];

const industryDistribution = [
  { name: "Technology", value: 35, color: "#0066ff" },
  { name: "Healthcare", value: 25, color: "#00c896" },
  { name: "Energy", value: 20, color: "#ff9500" },
  { name: "Finance", value: 15, color: "#1a2332" },
  { name: "Other", value: 5, color: "#6c757d" },
];

const marketIntelligence = [
  {
    title: "Tech M&A Activity Surges 15%",
    category: "Market Trend",
    time: "2 hours ago",
    impact: "High",
    summary: "Technology sector M&A activity increased significantly in Q4..."
  },
  {
    title: "Energy Sector Consolidation",
    category: "Industry News",
    time: "4 hours ago",
    impact: "Medium",
    summary: "Major energy companies announcing strategic partnerships..."
  },
  {
    title: "Healthcare Valuations Rise",
    category: "Valuation Alert",
    time: "1 day ago",
    impact: "High",
    summary: "Healthcare technology valuations up 22% year-over-year..."
  }
];

export default function ProspectAIPage() {
  // Enhanced state management
  const [searchTerm, setSearchTerm] = useState("");
  const [industryFilter, setIndustryFilter] = useState("all");
  const [dealSizeFilter, setDealSizeFilter] = useState("all");
  const [stageFilter, setStageFilter] = useState("all");
  const [scoreFilter, setScoreFilter] = useState("all");
  const [selectedProspect, setSelectedProspect] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("prospects");
  const [marketIntelligenceData, setMarketIntelligenceData] = useState<MarketIntelligenceData | null>(null);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [analysisForm, setAnalysisForm] = useState<ProspectAnalysisData>({
    company_name: '',
    industry: '',
    location: '',
    market_cap: 0,
    revenue: 0,
    employees: 0,
    financial_data: {},
    business_model: '',
    target_market: '',
    competitive_landscape: ''
  });

  // Hooks
  const { toast } = useToast();
  const {
    prospects,
    statistics,
    loading,
    error,
    fetchProspects,
    fetchStatistics,
    analyzeProspect,
    getMarketIntelligence,
    getProspectsByScore,
    getProspectsByStage,
    getProspectsByIndustry,
    refreshData
  } = useProspects({
    autoFetch: true,
    filters: {
      query: searchTerm,
      industry: industryFilter !== 'all' ? industryFilter : undefined,
      stage: stageFilter !== 'all' ? stageFilter : undefined,
      min_ai_score: scoreFilter !== 'all' ? parseInt(scoreFilter) : undefined,
      sort_by: 'ai_score',
      sort_order: 'desc'
    },
    limit: 50
  });

  // WebSocket for real-time updates
  const { isConnected, sendMessage } = useWebSocket({
    onMessage: (message) => {
      if (message.type === 'prospect_updated') {
        refreshData();
        toast({
          title: "Prospect Updated",
          description: `${message.data.company_name} has been updated`,
        });
      }
    }
  });

  // Helper functions
  const fetchMarketIntelligence = async () => {
    try {
      const data = await getMarketIntelligence({
        industry: industryFilter !== 'all' ? industryFilter : undefined,
        time_period: '3M'
      });
      setMarketIntelligenceData(data);
    } catch (error) {
      console.error('Failed to fetch market intelligence:', error);
    }
  };

  const handleAnalyzeProspect = async () => {
    if (!analysisForm.company_name || !analysisForm.industry) {
      toast({
        title: "Missing Information",
        description: "Please provide at least company name and industry",
        variant: "destructive"
      });
      return;
    }

    setIsAnalyzing(true);
    try {
      const result = await analyzeProspect(analysisForm);
      setAnalysisData(result);
      toast({
        title: "Analysis Complete",
        description: `AI score: ${result.ai_score}% with ${result.confidence_level} confidence`,
      });
    } catch (error) {
      toast({
        title: "Analysis Failed",
        description: error instanceof Error ? error.message : "Failed to analyze prospect",
        variant: "destructive"
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRefreshData = async () => {
    try {
      await Promise.all([refreshData(), fetchMarketIntelligence()]);
      toast({
        title: "Data Refreshed",
        description: "All prospect data has been updated",
      });
    } catch (error) {
      toast({
        title: "Refresh Failed",
        description: "Failed to refresh data",
        variant: "destructive"
      });
    }
  };

  // Effects
  useEffect(() => {
    fetchMarketIntelligence();
  }, [industryFilter]);

  useEffect(() => {
    if (prospects.length > 0 && !selectedProspect) {
      setSelectedProspect(prospects[0]);
    }
  }, [prospects, selectedProspect]);

  // Computed values
  const filteredProspects = useMemo(() => {
    let filtered = prospects;

    if (dealSizeFilter !== 'all') {
      filtered = filtered.filter(prospect => {
        const dealSize = parseFloat(prospect.deal_size?.replace(/[$M]/g, '') || '0');
        switch (dealSizeFilter) {
          case 'small': return dealSize < 10;
          case 'medium': return dealSize >= 10 && dealSize < 50;
          case 'large': return dealSize >= 50;
          default: return true;
        }
      });
    }

    return filtered;
  }, [prospects, dealSizeFilter]);

  const scoreDistributionData = useMemo(() =>
    generateScoreDistributionData(prospects), [prospects]);

  const industryTrendsData = useMemo(() =>
    generateIndustryTrendsData(marketIntelligenceData), [marketIntelligenceData]);

  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-dealverse-green";
    if (score >= 70) return "text-dealverse-amber";
    return "text-dealverse-coral";
  };

  const getScoreBg = (score: number) => {
    if (score >= 85) return "bg-dealverse-green/10 border-dealverse-green/20";
    if (score >= 70) return "bg-dealverse-amber/10 border-dealverse-amber/20";
    return "bg-dealverse-coral/10 border-dealverse-coral/20";
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Enhanced Header */}
      <div className="flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex flex-col space-y-2">
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-dealverse-navy to-dealverse-blue bg-clip-text text-transparent">
              Prospect AI
            </h1>
            <p className="text-dealverse-medium-gray dark:text-dealverse-light-gray">
              AI-powered deal sourcing and opportunity management
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-dealverse-green' : 'bg-dealverse-coral'}`} />
              <span className="text-sm text-dealverse-medium-gray">
                {isConnected ? 'Live' : 'Offline'}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefreshData}
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button
              size="sm"
              onClick={() => setShowAnalysisModal(true)}
            >
              <Zap className="h-4 w-4 mr-2" />
              Analyze New
            </Button>
          </div>
        </div>

        {/* Enhanced Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-dealverse-medium-gray h-4 w-4" />
            <Input
              placeholder="Search prospects by company name, industry, or location..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex gap-2">
            <Select value={industryFilter} onValueChange={setIndustryFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Industry" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Industries</SelectItem>
                <SelectItem value="Technology">Technology</SelectItem>
                <SelectItem value="Healthcare">Healthcare</SelectItem>
                <SelectItem value="Energy">Energy</SelectItem>
                <SelectItem value="Finance">Finance</SelectItem>
                <SelectItem value="Manufacturing">Manufacturing</SelectItem>
              </SelectContent>
            </Select>
            <Select value={stageFilter} onValueChange={setStageFilter}>
              <SelectTrigger className="w-[130px]">
                <SelectValue placeholder="Stage" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Stages</SelectItem>
                <SelectItem value="Initial Contact">Initial Contact</SelectItem>
                <SelectItem value="Due Diligence">Due Diligence</SelectItem>
                <SelectItem value="Proposal">Proposal</SelectItem>
                <SelectItem value="Negotiation">Negotiation</SelectItem>
                <SelectItem value="Closing">Closing</SelectItem>
              </SelectContent>
            </Select>
            <Select value={scoreFilter} onValueChange={setScoreFilter}>
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="Score" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Scores</SelectItem>
                <SelectItem value="90">90+ Score</SelectItem>
                <SelectItem value="80">80+ Score</SelectItem>
                <SelectItem value="70">70+ Score</SelectItem>
                <SelectItem value="60">60+ Score</SelectItem>
              </SelectContent>
            </Select>
            <Select value={dealSizeFilter} onValueChange={setDealSizeFilter}>
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="Deal Size" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sizes</SelectItem>
                <SelectItem value="small">< $10M</SelectItem>
                <SelectItem value="medium">$10M - $50M</SelectItem>
                <SelectItem value="large">$50M+</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* AI Insights Dashboard */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 bg-gradient-to-br from-dealverse-blue/10 to-dealverse-blue/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Active Prospects</CardTitle>
            <Target className="h-4 w-4 text-dealverse-blue" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {loading ? '...' : statistics?.total_prospects || prospects.length}
            </div>
            <p className="text-xs text-dealverse-medium-gray">
              {statistics?.recent_activity_count || 0} recent activities
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-green/10 to-dealverse-green/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">High-Score Deals</CardTitle>
            <Brain className="h-4 w-4 text-dealverse-green" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {loading ? '...' : statistics?.high_score_prospects || getProspectsByScore(85).length}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Score 85+</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-amber/10 to-dealverse-amber/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Average Score</CardTitle>
            <Award className="h-4 w-4 text-dealverse-amber" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {loading ? '...' : (statistics?.average_score ||
                (prospects.reduce((sum, p) => sum + p.ai_score, 0) / prospects.length || 0).toFixed(1))}
            </div>
            <p className="text-xs text-dealverse-medium-gray">AI scoring average</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-navy/10 to-dealverse-navy/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">AI Accuracy</CardTitle>
            <Star className="h-4 w-4 text-dealverse-navy" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {loading ? '...' : `${(statistics?.ai_accuracy || 94.2).toFixed(1)}%`}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Prediction rate</p>
          </CardContent>
        </Card>
      </div>

      {/* Enhanced Tabbed Interface */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="prospects">Prospects</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="market-intelligence">Market Intel</TabsTrigger>
          <TabsTrigger value="scoring">AI Scoring</TabsTrigger>
        </TabsList>

        {/* Prospects Tab */}
        <TabsContent value="prospects" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Prospect List */}
            <div className="lg:col-span-2">
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl font-semibold text-dealverse-navy">AI-Scored Prospects</CardTitle>
                      <CardDescription className="text-dealverse-medium-gray">
                        {filteredProspects.length} opportunities ranked by AI confidence and deal potential
                      </CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      {loading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-dealverse-blue" />}
                      <Button variant="outline" size="sm" onClick={handleRefreshData} disabled={loading}>
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                      </Button>
                    </div>
                  </div>
                </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-dealverse-medium-gray" />
                  <Input
                    placeholder="Search prospects..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={industryFilter} onValueChange={setIndustryFilter}>
                  <SelectTrigger className="w-full sm:w-48">
                    <SelectValue placeholder="Industry" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Industries</SelectItem>
                    <SelectItem value="technology">Technology</SelectItem>
                    <SelectItem value="healthcare">Healthcare</SelectItem>
                    <SelectItem value="energy">Energy</SelectItem>
                    <SelectItem value="finance">Finance</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={dealSizeFilter} onValueChange={setDealSizeFilter}>
                  <SelectTrigger className="w-full sm:w-48">
                    <SelectValue placeholder="Deal Size" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Sizes</SelectItem>
                    <SelectItem value="small">$10M - $50M</SelectItem>
                    <SelectItem value="medium">$50M - $100M</SelectItem>
                    <SelectItem value="large">$100M+</SelectItem>
                  </SelectContent>
                </Select>
              </div>

                  {error && (
                    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-red-600 text-sm">{error}</p>
                    </div>
                  )}

                  {/* Prospect Cards */}
                  <div className="space-y-4">
                    {loading ? (
                      <div className="space-y-4">
                        {[...Array(3)].map((_, i) => (
                          <div key={i} className="animate-pulse">
                            <div className="h-24 bg-gray-200 rounded-lg"></div>
                          </div>
                        ))}
                      </div>
                    ) : filteredProspects.length === 0 ? (
                      <div className="text-center py-8">
                        <Target className="h-12 w-12 text-dealverse-medium-gray mx-auto mb-4" />
                        <p className="text-dealverse-medium-gray">No prospects found matching your criteria</p>
                      </div>
                    ) : (
                      filteredProspects.map((prospect) => (
                        <Card
                          key={prospect.id}
                          className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                            selectedProspect?.id === prospect.id
                              ? 'ring-2 ring-dealverse-blue bg-dealverse-blue/5'
                              : 'hover:bg-dealverse-light-gray/50'
                          }`}
                          onClick={() => setSelectedProspect(prospect)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-3 mb-2">
                                  <h3 className="font-semibold text-dealverse-navy">{prospect.company_name}</h3>
                                  <Badge variant="outline" className="text-xs">
                                    {prospect.industry}
                                  </Badge>
                                  <Badge variant="outline" className="text-xs">
                                    {prospect.stage}
                                  </Badge>
                                </div>
                                <p className="text-sm text-dealverse-medium-gray mb-2">{prospect.description}</p>
                                <div className="flex items-center space-x-4 text-xs text-dealverse-medium-gray">
                                  <div className="flex items-center space-x-1">
                                    <MapPin className="h-3 w-3" />
                                    <span>{prospect.location}</span>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <DollarSign className="h-3 w-3" />
                                    <span>{prospect.deal_size}</span>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <Clock className="h-3 w-3" />
                                    <span>{prospect.last_activity}</span>
                                  </div>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className={`text-2xl font-bold ${getScoreColor(prospect.ai_score)}`}>
                                  {prospect.ai_score}
                                </div>
                                <div className="text-xs text-dealverse-medium-gray">{prospect.confidence_level}</div>
                                <div className={`mt-2 px-2 py-1 rounded-full text-xs border ${getScoreBg(prospect.ai_score)}`}>
                                  AI Score
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Enhanced Prospect Details Sidebar */}
            <div className="space-y-6">
              {selectedProspect ? (
                <Card className="border-0 shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-lg font-semibold text-dealverse-navy">Prospect Details</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-dealverse-navy mb-2">{selectedProspect.company_name}</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-dealverse-medium-gray">Market Cap:</span>
                          <span className="font-medium">{selectedProspect.market_cap || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-dealverse-medium-gray">Revenue:</span>
                          <span className="font-medium">{selectedProspect.revenue || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-dealverse-medium-gray">Employees:</span>
                          <span className="font-medium">{selectedProspect.employees || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-dealverse-medium-gray">Stage:</span>
                          <span className="font-medium">{selectedProspect.stage}</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h5 className="font-medium text-dealverse-navy mb-2">AI Confidence Score</h5>
                      <Progress value={selectedProspect.ai_score} className="h-2" />
                      <p className="text-xs text-dealverse-medium-gray mt-1">
                        {selectedProspect.ai_score}% confidence based on market data and historical patterns
                      </p>
                    </div>

                    {selectedProspect.risk_factors && (
                      <div>
                        <h5 className="font-medium text-dealverse-navy mb-2">Risk Factors</h5>
                        <div className="space-y-1">
                          {selectedProspect.risk_factors.map((risk, index) => (
                            <div key={index} className="flex items-center text-sm">
                              <AlertCircle className="h-3 w-3 text-dealverse-coral mr-2" />
                              <span className="text-dealverse-medium-gray">{risk}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedProspect.opportunities && (
                      <div>
                        <h5 className="font-medium text-dealverse-navy mb-2">Opportunities</h5>
                        <div className="space-y-1">
                          {selectedProspect.opportunities.map((opportunity, index) => (
                            <div key={index} className="flex items-center text-sm">
                              <TrendingUp className="h-3 w-3 text-dealverse-green mr-2" />
                              <span className="text-dealverse-medium-gray">{opportunity}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <Button
                      className="w-full bg-dealverse-blue hover:bg-dealverse-blue/90"
                      onClick={() => {
                        // Handle initiate contact
                        toast({
                          title: "Contact Initiated",
                          description: `Outreach sequence started for ${selectedProspect.company_name}`,
                        });
                      }}
                    >
                      <Mail className="h-4 w-4 mr-2" />
                      Initiate Contact
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <Card className="border-0 shadow-lg">
                  <CardContent className="p-8 text-center">
                    <Target className="h-12 w-12 text-dealverse-medium-gray mx-auto mb-4" />
                    <p className="text-dealverse-medium-gray">Select a prospect to view details</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Score Distribution Chart */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-dealverse-navy">Score Distribution</CardTitle>
                <CardDescription>AI scoring distribution across all prospects</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <BarChart width={400} height={250} data={scoreDistributionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="range" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#0066ff" />
                  </BarChart>
                </div>
              </CardContent>
            </Card>

            {/* Industry Trends Chart */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-dealverse-navy">Industry Trends</CardTitle>
                <CardDescription>Growth rates and deal activity by industry</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <LineChart width={400} height={250} data={industryTrendsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="industry" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="growth" stroke="#00c896" strokeWidth={2} />
                    <Line type="monotone" dataKey="deals" stroke="#0066ff" strokeWidth={2} />
                  </LineChart>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Market Intelligence Tab */}
        <TabsContent value="market-intelligence" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-dealverse-navy">Market Overview</CardTitle>
              </CardHeader>
              <CardContent>
                {marketIntelligenceData ? (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-dealverse-navy mb-2">Market Size</h4>
                      <p className="text-2xl font-bold text-dealverse-blue">
                        {marketIntelligenceData.market_overview.total_market_size}
                      </p>
                      <p className="text-sm text-dealverse-medium-gray">
                        Growth Rate: {marketIntelligenceData.market_overview.growth_rate}
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium text-dealverse-navy mb-2">Key Trends</h4>
                      <div className="space-y-2">
                        {marketIntelligenceData.market_overview.key_trends.map((trend, index) => (
                          <div key={index} className="flex items-center text-sm">
                            <TrendingUp className="h-3 w-3 text-dealverse-green mr-2" />
                            <span>{trend}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Brain className="h-12 w-12 text-dealverse-medium-gray mx-auto mb-4" />
                    <p className="text-dealverse-medium-gray">Loading market intelligence...</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-dealverse-navy">Recent Transactions</CardTitle>
              </CardHeader>
              <CardContent>
                {marketIntelligenceData?.recent_transactions ? (
                  <div className="space-y-3">
                    {marketIntelligenceData.recent_transactions.slice(0, 5).map((transaction, index) => (
                      <div key={index} className="border-l-2 border-dealverse-blue/20 pl-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <h5 className="font-medium text-dealverse-navy">{transaction.company}</h5>
                            <p className="text-sm text-dealverse-medium-gray">{transaction.deal_type}</p>
                          </div>
                          <div className="text-right">
                            <p className="font-medium text-dealverse-blue">{transaction.deal_size}</p>
                            <p className="text-xs text-dealverse-medium-gray">{transaction.date}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <DollarSign className="h-12 w-12 text-dealverse-medium-gray mx-auto mb-4" />
                    <p className="text-dealverse-medium-gray">No recent transactions available</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* AI Scoring Tab */}
        <TabsContent value="scoring" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-dealverse-navy">Analyze New Prospect</CardTitle>
                <CardDescription>Use AI to analyze and score a new prospect</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4">
                  <div>
                    <label className="text-sm font-medium text-dealverse-navy">Company Name</label>
                    <Input
                      value={analysisForm.company_name}
                      onChange={(e) => setAnalysisForm(prev => ({ ...prev, company_name: e.target.value }))}
                      placeholder="Enter company name"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-dealverse-navy">Industry</label>
                    <Select
                      value={analysisForm.industry}
                      onValueChange={(value) => setAnalysisForm(prev => ({ ...prev, industry: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select industry" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Technology">Technology</SelectItem>
                        <SelectItem value="Healthcare">Healthcare</SelectItem>
                        <SelectItem value="Energy">Energy</SelectItem>
                        <SelectItem value="Finance">Finance</SelectItem>
                        <SelectItem value="Manufacturing">Manufacturing</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-dealverse-navy">Location</label>
                    <Input
                      value={analysisForm.location}
                      onChange={(e) => setAnalysisForm(prev => ({ ...prev, location: e.target.value }))}
                      placeholder="City, State/Country"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-dealverse-navy">Revenue ($M)</label>
                      <Input
                        type="number"
                        value={analysisForm.revenue}
                        onChange={(e) => setAnalysisForm(prev => ({ ...prev, revenue: parseFloat(e.target.value) || 0 }))}
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-dealverse-navy">Employees</label>
                      <Input
                        type="number"
                        value={analysisForm.employees}
                        onChange={(e) => setAnalysisForm(prev => ({ ...prev, employees: parseInt(e.target.value) || 0 }))}
                        placeholder="0"
                      />
                    </div>
                  </div>
                </div>
                <Button
                  onClick={handleAnalyzeProspect}
                  disabled={isAnalyzing}
                  className="w-full"
                >
                  {isAnalyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Zap className="h-4 w-4 mr-2" />
                      Analyze Prospect
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Analysis Results */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-dealverse-navy">Analysis Results</CardTitle>
              </CardHeader>
              <CardContent>
                {analysisData ? (
                  <div className="space-y-4">
                    <div className="text-center">
                      <div className={`text-4xl font-bold ${getScoreColor(analysisData.ai_score)}`}>
                        {analysisData.ai_score}
                      </div>
                      <p className="text-sm text-dealverse-medium-gray">AI Score</p>
                      <Badge className={`mt-2 ${getScoreBg(analysisData.ai_score)}`}>
                        {analysisData.confidence_level} Confidence
                      </Badge>
                    </div>

                    {analysisData.score_breakdown && (
                      <div className="space-y-3">
                        <h4 className="font-medium text-dealverse-navy">Score Breakdown</h4>
                        {Object.entries(analysisData.score_breakdown).map(([key, value]) => (
                          <div key={key} className="space-y-1">
                            <div className="flex justify-between text-sm">
                              <span className="capitalize">{key.replace('_', ' ')}</span>
                              <span>{value}/100</span>
                            </div>
                            <Progress value={value} className="h-2" />
                          </div>
                        ))}
                      </div>
                    )}

                    {analysisData.recommendations && (
                      <div>
                        <h4 className="font-medium text-dealverse-navy mb-2">Recommendations</h4>
                        <div className="space-y-2">
                          {analysisData.recommendations.map((rec, index) => (
                            <div key={index} className="flex items-start text-sm">
                              <CheckCircle className="h-3 w-3 text-dealverse-green mr-2 mt-0.5" />
                              <span>{rec}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Brain className="h-12 w-12 text-dealverse-medium-gray mx-auto mb-4" />
                    <p className="text-dealverse-medium-gray">Run analysis to see AI scoring results</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Analysis Modal */}
      <Dialog open={showAnalysisModal} onOpenChange={setShowAnalysisModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Analyze New Prospect</DialogTitle>
            <DialogDescription>
              Provide company information for AI-powered analysis and scoring
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Company Name</label>
                <Input
                  value={analysisForm.company_name}
                  onChange={(e) => setAnalysisForm(prev => ({ ...prev, company_name: e.target.value }))}
                  placeholder="Enter company name"
                />
              </div>
              <div>
                <label className="text-sm font-medium">Industry</label>
                <Select
                  value={analysisForm.industry}
                  onValueChange={(value) => setAnalysisForm(prev => ({ ...prev, industry: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select industry" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Technology">Technology</SelectItem>
                    <SelectItem value="Healthcare">Healthcare</SelectItem>
                    <SelectItem value="Energy">Energy</SelectItem>
                    <SelectItem value="Finance">Finance</SelectItem>
                    <SelectItem value="Manufacturing">Manufacturing</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium">Business Model</label>
              <Input
                value={analysisForm.business_model}
                onChange={(e) => setAnalysisForm(prev => ({ ...prev, business_model: e.target.value }))}
                placeholder="Describe the business model"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Target Market</label>
              <Input
                value={analysisForm.target_market}
                onChange={(e) => setAnalysisForm(prev => ({ ...prev, target_market: e.target.value }))}
                placeholder="Describe the target market"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAnalysisModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleAnalyzeProspect} disabled={isAnalyzing}>
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
