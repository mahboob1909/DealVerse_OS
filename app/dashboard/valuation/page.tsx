"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Calculator,
  TrendingUp,
  BarChart3,
  Users,
  GitBranch,
  Download,
  Share,
  History,
  Target,
  DollarSign,
  Percent,
  Calendar,
  FileSpreadsheet,
  Eye,
  Edit,
  Copy,
  Loader2,
  RefreshCw,
  Plus,
  Activity,
  Clock,
  CheckCircle,
  AlertTriangle,
  LineChart,
  PieChart,
  BarChart,
  Settings,
  Save,
  Upload,
  Filter,
  Search,
  UserPlus,
  MessageSquare,
  Bell
} from "lucide-react";
import React, { useState, useEffect } from "react";
import { useFinancialModels, type FinancialModel } from "@/hooks/use-financial-models";
import { useAuth } from "@/lib/auth-context";
import { useWebSocket } from "@/hooks/use-websocket";
import { useFinancialModelCollaboration } from "@/hooks/use-financial-model-collaboration";
import { ExportButton, exportConfigs } from "@/components/ui/export-button";
import { ResponsiveContainer, LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart as RechartsBarChart, Bar } from 'recharts';

// Interfaces for enhanced functionality
interface ScenarioAnalysis {
  id: string;
  name: string;
  description?: string;
  parameters: {
    revenue_growth: number;
    margin_improvement: number;
    capex_ratio: number;
    discount_rate: number;
  };
  results: {
    revenue2024: string;
    revenue2025: string;
    revenue2026: string;
    ebitdaMargin: string;
    valuation: string;
    irr: string;
    multiple: string;
  };
  probability: number;
  created_at: string;
  created_by: string;
}

interface TeamMember {
  id: string;
  name: string;
  role: string;
  status: 'online' | 'away' | 'offline';
  lastActive: string;
  avatar?: string;
  currentModel?: string;
}

interface ModelVersion {
  id: string;
  version: string;
  date: string;
  author: string;
  changes: string;
  model_data: any;
  is_current: boolean;
}

interface CollaborationEvent {
  id: string;
  type: 'cell_update' | 'scenario_add' | 'user_join' | 'user_leave' | 'comment_add';
  user_id: string;
  user_name: string;
  timestamp: string;
  data: any;
}

// Chart data for scenario visualization
const generateScenarioChartData = (scenarios: ScenarioAnalysis[]) => {
  const years = ['2024', '2025', '2026'];
  return years.map(year => {
    const dataPoint: any = { year };
    scenarios.forEach(scenario => {
      const revenueKey = `revenue${year}` as keyof typeof scenario.results;
      const revenue = scenario.results[revenueKey];
      dataPoint[scenario.name] = parseFloat(revenue.replace(/[$M]/g, ''));
    });
    return dataPoint;
  });
};

export default function ValuationPage() {
  const { user } = useAuth();
  const [selectedModel, setSelectedModel] = useState<FinancialModel | null>(null);
  const [activeTab, setActiveTab] = useState("models");

  // Enhanced state for new features
  const [scenarios, setScenarios] = useState<ScenarioAnalysis[]>([]);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [modelVersions, setModelVersions] = useState<ModelVersion[]>([]);
  const [collaborationEvents, setCollaborationEvents] = useState<CollaborationEvent[]>([]);
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [versionsLoading, setVersionsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  // Use the financial models hook to fetch real data
  const {
    models,
    statistics,
    loading,
    error,
    fetchModels,
    createModel,
    updateModel,
    deleteModel,
    createVersion,
    getModelVersions,
    getModelsByType,
    getModelsByStatus,
    getRecentModels,
    calculatePortfolioValue,
    formatCurrency,
  } = useFinancialModels({ autoFetch: true });

  // Real-time collaboration for financial models
  const {
    activeUsers,
    isConnected: collaborationConnected,
    connectionError: collaborationError,
    sendModelUpdate,
    sendScenarioUpdate,
    joinModel,
    leaveModel,
    updateCursorPosition,
    getModelVersion,
    isUserActive
  } = useFinancialModelCollaboration({
    modelId: selectedModel?.id || '',
    onModelUpdate: (update, user) => {
      console.log('Model update received:', update, 'from user:', user);
      // Handle real-time model updates
      if (update.type === 'cell_update') {
        // Update the model data in real-time
        setSelectedModel(prev => {
          if (!prev) return prev;
          return {
            ...prev,
            model_data: {
              ...prev.model_data,
              [update.cellId || '']: update.value
            }
          };
        });
      }
    },
    onUserJoined: (user) => {
      console.log('User joined model collaboration:', user);
    },
    onUserLeft: (user) => {
      console.log('User left model collaboration:', user);
    },
    onScenarioUpdate: (scenario, user) => {
      console.log('Scenario update received:', scenario, 'from user:', user);
      // Handle real-time scenario updates
      setScenarios(prev => {
        const updated = prev.filter(s => s.name !== scenario.name);
        return [...updated, scenario];
      });
    },
    onConnectionError: (error) => {
      console.error('Collaboration error:', error);
    }
  });

  // Set the first model as selected when models are loaded
  useEffect(() => {
    if (models.length > 0 && !selectedModel) {
      setSelectedModel(models[0]);
    }
  }, [models, selectedModel]);

  // Fetch scenarios when model is selected
  useEffect(() => {
    if (selectedModel) {
      fetchScenarios(selectedModel.id);
      fetchModelVersions(selectedModel.id);
      fetchTeamMembers();
    }
  }, [selectedModel]);

  // Helper functions
  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-dealverse-green/10 text-dealverse-green border-dealverse-green/20";
      case "review": return "bg-dealverse-amber/10 text-dealverse-amber border-dealverse-amber/20";
      case "draft": return "bg-dealverse-blue/10 text-dealverse-blue border-dealverse-blue/20";
      default: return "bg-gray-100 text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "online": return "bg-dealverse-green";
      case "away": return "bg-dealverse-amber";
      case "offline": return "bg-dealverse-medium-gray";
      default: return "bg-dealverse-medium-gray";
    }
  };

  // API functions for new features
  const fetchScenarios = async (modelId: string) => {
    setScenarioLoading(true);
    try {
      // Mock scenarios for now - will be replaced with real API
      const mockScenarios: ScenarioAnalysis[] = [
        {
          id: "1",
          name: "Base Case",
          description: "Conservative growth assumptions",
          parameters: {
            revenue_growth: 0.20,
            margin_improvement: 0.02,
            capex_ratio: 0.15,
            discount_rate: 0.10
          },
          results: {
            revenue2024: "$180M",
            revenue2025: "$216M",
            revenue2026: "$259M",
            ebitdaMargin: "22%",
            valuation: "$2.1B",
            irr: "18.5%",
            multiple: "11.7x"
          },
          probability: 0.6,
          created_at: new Date().toISOString(),
          created_by: "Sarah Chen"
        },
        {
          id: "2",
          name: "Upside Case",
          description: "Aggressive growth with market expansion",
          parameters: {
            revenue_growth: 0.30,
            margin_improvement: 0.05,
            capex_ratio: 0.12,
            discount_rate: 0.09
          },
          results: {
            revenue2024: "$180M",
            revenue2025: "$234M",
            revenue2026: "$304M",
            ebitdaMargin: "25%",
            valuation: "$2.8B",
            irr: "24.2%",
            multiple: "15.6x"
          },
          probability: 0.25,
          created_at: new Date().toISOString(),
          created_by: "Michael Rodriguez"
        },
        {
          id: "3",
          name: "Downside Case",
          description: "Conservative assumptions with market headwinds",
          parameters: {
            revenue_growth: 0.10,
            margin_improvement: -0.02,
            capex_ratio: 0.18,
            discount_rate: 0.12
          },
          results: {
            revenue2024: "$180M",
            revenue2025: "$198M",
            revenue2026: "$218M",
            ebitdaMargin: "18%",
            valuation: "$1.5B",
            irr: "12.8%",
            multiple: "8.3x"
          },
          probability: 0.15,
          created_at: new Date().toISOString(),
          created_by: "Emily Watson"
        }
      ];
      setScenarios(mockScenarios);
    } catch (error) {
      console.error('Failed to fetch scenarios:', error);
    } finally {
      setScenarioLoading(false);
    }
  };

  const fetchModelVersions = async (modelId: string) => {
    setVersionsLoading(true);
    try {
      const versions = await getModelVersions(modelId);
      if (versions) {
        const formattedVersions: ModelVersion[] = versions.map((v: any) => ({
          id: v.id,
          version: `v${v.version}`,
          date: new Date(v.created_at).toLocaleString(),
          author: v.created_by?.first_name + ' ' + v.created_by?.last_name || 'Unknown',
          changes: v.description || 'Model update',
          model_data: v.model_data,
          is_current: v.is_current
        }));
        setModelVersions(formattedVersions);
      }
    } catch (error) {
      console.error('Failed to fetch model versions:', error);
      // Fallback to mock data
      const mockVersions: ModelVersion[] = [
        {
          id: "1",
          version: "v2.3",
          date: "Today, 2:30 PM",
          author: "Sarah Chen",
          changes: "Updated revenue projections",
          model_data: {},
          is_current: true
        },
        {
          id: "2",
          version: "v2.2",
          date: "Today, 11:15 AM",
          author: "Michael Rodriguez",
          changes: "Added sensitivity analysis",
          model_data: {},
          is_current: false
        },
        {
          id: "3",
          version: "v2.1",
          date: "Yesterday, 4:45 PM",
          author: "Sarah Chen",
          changes: "Revised EBITDA assumptions",
          model_data: {},
          is_current: false
        },
        {
          id: "4",
          version: "v2.0",
          date: "2 days ago",
          author: "Emily Watson",
          changes: "Major model restructure",
          model_data: {},
          is_current: false
        }
      ];
      setModelVersions(mockVersions);
    } finally {
      setVersionsLoading(false);
    }
  };

  const fetchTeamMembers = async () => {
    try {
      // Mock team members for now - will be replaced with real API
      const mockTeamMembers: TeamMember[] = [
        {
          id: "1",
          name: "Sarah Chen",
          role: "Lead Analyst",
          status: "online",
          lastActive: "now",
          currentModel: selectedModel?.name
        },
        {
          id: "2",
          name: "Michael Rodriguez",
          role: "Associate",
          status: "online",
          lastActive: "5 min ago",
          currentModel: selectedModel?.name
        },
        {
          id: "3",
          name: "Emily Watson",
          role: "VP",
          status: "away",
          lastActive: "1 hour ago"
        },
        {
          id: "4",
          name: "David Kim",
          role: "Analyst",
          status: "offline",
          lastActive: "2 hours ago"
        }
      ];
      setTeamMembers(mockTeamMembers);
    } catch (error) {
      console.error('Failed to fetch team members:', error);
    }
  };

  const handleWebSocketMessage = (message: any) => {
    try {
      const event: CollaborationEvent = {
        id: Date.now().toString(),
        type: message.type,
        user_id: message.user_id,
        user_name: message.user_name,
        timestamp: new Date().toISOString(),
        data: message.data
      };

      setCollaborationEvents(prev => [event, ...prev.slice(0, 49)]); // Keep last 50 events

      // Handle different event types
      switch (message.type) {
        case 'user_join':
          setTeamMembers(prev => prev.map(member =>
            member.id === message.user_id
              ? { ...member, status: 'online', lastActive: 'now' }
              : member
          ));
          break;
        case 'user_leave':
          setTeamMembers(prev => prev.map(member =>
            member.id === message.user_id
              ? { ...member, status: 'offline', lastActive: 'just now' }
              : member
          ));
          break;
        case 'cell_update':
          // Handle real-time model updates
          if (selectedModel && message.data.model_id === selectedModel.id) {
            // Update model data in real-time
            console.log('Model cell updated:', message.data);
          }
          break;
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error);
    }
  };

  // Filter functions
  const filteredModels = models.filter(model => {
    const matchesSearch = model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         model.model_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === "all" || model.model_type === filterType;
    const matchesStatus = filterStatus === "all" || model.status === filterStatus;

    return matchesSearch && matchesType && matchesStatus;
  });

  // Generate chart data for scenarios
  const scenarioChartData = generateScenarioChartData(scenarios);

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-dealverse-navy to-dealverse-blue bg-clip-text text-transparent">
              Valuation & Modeling Hub
            </h1>
            <p className="text-dealverse-medium-gray dark:text-dealverse-light-gray">
              Collaborative financial modeling with version control and scenario analysis
            </p>
          </div>
          <div className="flex items-center space-x-2">
            {isConnected && (
              <Badge className="bg-dealverse-green/10 text-dealverse-green border-dealverse-green/20">
                <Activity className="h-3 w-3 mr-1" />
                Live
              </Badge>
            )}
            {selectedModel && (
              <ExportButton
                options={exportConfigs.financialModel(selectedModel.id)}
                variant="outline"
                size="default"
              />
            )}
            <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90">
              <Plus className="h-4 w-4 mr-2" />
              New Model
            </Button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex items-center space-x-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-dealverse-medium-gray" />
            <Input
              placeholder="Search models..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-dealverse-medium-gray" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-dealverse-light-gray rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-dealverse-blue"
            >
              <option value="all">All Types</option>
              <option value="DCF">DCF</option>
              <option value="Comps">Comps</option>
              <option value="LBO">LBO</option>
              <option value="Sum_of_Parts">Sum of Parts</option>
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-dealverse-light-gray rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-dealverse-blue"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="review">Review</option>
              <option value="draft">Draft</option>
            </select>
          </div>
        </div>
      </div>

      {/* Modeling Dashboard */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 bg-gradient-to-br from-dealverse-blue/10 to-dealverse-blue/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Total Models</CardTitle>
            <FileSpreadsheet className="h-4 w-4 text-dealverse-blue" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : statistics?.total_models || models.length}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Financial models</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-green/10 to-dealverse-green/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Total Valuation</CardTitle>
            <DollarSign className="h-4 w-4 text-dealverse-green" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : formatCurrency(calculatePortfolioValue())}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Portfolio value</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-amber/10 to-dealverse-amber/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Active Models</CardTitle>
            <Percent className="h-4 w-4 text-dealverse-amber" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : statistics?.active_models || getModelsByStatus('approved').length}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Approved models</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-navy/10 to-dealverse-navy/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">In Review</CardTitle>
            <Users className="h-4 w-4 text-dealverse-navy" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">
              {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : statistics?.models_in_review || getModelsByStatus('review').length}
            </div>
            <p className="text-xs text-dealverse-medium-gray">Pending review</p>
          </CardContent>
        </Card>
      </div>

      {/* Real-time Collaboration Status */}
      {selectedModel && (
        <Card className="border-0 bg-gradient-to-r from-dealverse-blue/5 to-dealverse-green/5">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Activity className={`h-4 w-4 ${collaborationConnected ? 'text-dealverse-green' : 'text-dealverse-medium-gray'}`} />
                <CardTitle className="text-sm font-medium text-dealverse-navy">
                  Real-time Collaboration
                </CardTitle>
                <Badge variant={collaborationConnected ? "default" : "secondary"} className="text-xs">
                  {collaborationConnected ? 'Connected' : 'Disconnected'}
                </Badge>
              </div>
              <div className="flex items-center space-x-2">
                <Users className="h-4 w-4 text-dealverse-blue" />
                <span className="text-sm font-medium text-dealverse-navy">
                  {activeUsers.length} active user{activeUsers.length !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex items-center space-x-4">
              <div className="flex -space-x-2">
                {activeUsers.slice(0, 5).map((user, index) => (
                  <div
                    key={user.user_id}
                    className={`w-8 h-8 rounded-full bg-gradient-to-br from-dealverse-blue to-dealverse-green flex items-center justify-center text-white text-xs font-medium border-2 border-white ${
                      isUserActive(user.user_id) ? 'ring-2 ring-dealverse-green' : ''
                    }`}
                    title={`${user.user_name} ${isUserActive(user.user_id) ? '(active)' : '(idle)'}`}
                  >
                    {user.user_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                  </div>
                ))}
                {activeUsers.length > 5 && (
                  <div className="w-8 h-8 rounded-full bg-dealverse-medium-gray flex items-center justify-center text-white text-xs font-medium border-2 border-white">
                    +{activeUsers.length - 5}
                  </div>
                )}
              </div>
              {collaborationError && (
                <Alert className="flex-1">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription className="text-xs">
                    {collaborationError}
                  </AlertDescription>
                </Alert>
              )}
              {selectedModel && (
                <div className="text-xs text-dealverse-medium-gray">
                  Model: {selectedModel.name} (v{getModelVersion()})
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="models">Financial Models</TabsTrigger>
          <TabsTrigger value="scenarios">Scenario Analysis</TabsTrigger>
          <TabsTrigger value="collaboration">Collaboration</TabsTrigger>
          <TabsTrigger value="versions">Version Control</TabsTrigger>
        </TabsList>

        <TabsContent value="models" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Models List */}
            <div className="lg:col-span-2">
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl font-semibold text-dealverse-navy">Financial Models</CardTitle>
                      <CardDescription className="text-dealverse-medium-gray">
                        Active valuation models and analysis
                      </CardDescription>
                    </div>
                    <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90">
                      <Calculator className="h-4 w-4 mr-2" />
                      New Model
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {loading && models.length === 0 ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-dealverse-blue" />
                      <span className="ml-2 text-dealverse-medium-gray">Loading financial models...</span>
                    </div>
                  ) : error ? (
                    <div className="text-center py-8">
                      <p className="text-dealverse-coral mb-4">{error}</p>
                      <Button
                        variant="outline"
                        onClick={fetchModels}
                        disabled={loading}
                      >
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Retry
                      </Button>
                    </div>
                  ) : filteredModels.length === 0 ? (
                    <div className="text-center py-8">
                      <Calculator className="h-12 w-12 text-dealverse-medium-gray mx-auto mb-4" />
                      <p className="text-dealverse-medium-gray mb-4">
                        {models.length === 0 ? "No financial models found." : "No models match your search criteria."}
                      </p>
                      {models.length === 0 ? (
                        <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90">
                          <Plus className="h-4 w-4 mr-2" />
                          Create First Model
                        </Button>
                      ) : (
                        <Button
                          variant="outline"
                          onClick={() => {
                            setSearchTerm("");
                            setFilterType("all");
                            setFilterStatus("all");
                          }}
                        >
                          Clear Filters
                        </Button>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {filteredModels.map((model) => (
                        <Card
                          key={model.id}
                          className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                            selectedModel?.id === model.id
                              ? 'ring-2 ring-dealverse-blue bg-dealverse-blue/5'
                              : 'hover:bg-dealverse-light-gray/50'
                          }`}
                          onClick={() => setSelectedModel(model)}
                        >
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <h3 className="font-semibold text-dealverse-navy">{model.name}</h3>
                                <Badge variant="outline" className="text-xs">
                                  {model.model_type}
                                </Badge>
                                <Badge className={`text-xs ${getStatusColor(model.status)}`}>
                                  {model.status}
                                </Badge>
                              </div>
                              <div className="flex items-center space-x-4 text-xs text-dealverse-medium-gray">
                                <span className="flex items-center">
                                  <Calendar className="h-3 w-3 mr-1" />
                                  {new Date(model.updated_at).toLocaleDateString()}
                                </span>
                                <span className="flex items-center">
                                  <Users className="h-3 w-3 mr-1" />
                                  {model.created_by?.first_name || 'Unknown'}
                                </span>
                                <span className="flex items-center">
                                  <GitBranch className="h-3 w-3 mr-1" />
                                  v{model.version}
                                </span>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-bold text-dealverse-navy">
                                {model.enterprise_value || 'N/A'}
                              </div>
                              <div className="text-xs text-dealverse-medium-gray">
                                {model.model_type} Model
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center justify-end space-x-2 mt-3">
                            <Button variant="ghost" size="sm">
                              <Eye className="h-3 w-3" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Edit className="h-3 w-3" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Copy className="h-3 w-3" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Share className="h-3 w-3" />
                            </Button>
                          </div>
                        </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Model Details */}
            <div>
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-dealverse-navy">Model Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {selectedModel ? (
                    <div>
                      <h4 className="font-semibold text-dealverse-navy mb-2">{selectedModel.name}</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-dealverse-medium-gray">Type:</span>
                          <span className="font-medium">{selectedModel.model_type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-dealverse-medium-gray">Version:</span>
                          <span className="font-medium">v{selectedModel.version}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-dealverse-medium-gray">Status:</span>
                          <Badge className={`text-xs ${getStatusColor(selectedModel.status)}`}>
                            {selectedModel.status}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-dealverse-medium-gray">Last Modified:</span>
                          <span className="font-medium">{new Date(selectedModel.updated_at).toLocaleDateString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-dealverse-medium-gray">Created By:</span>
                          <span className="font-medium">{selectedModel.created_by?.first_name || 'Unknown'} {selectedModel.created_by?.last_name || ''}</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-4">
                      <p className="text-dealverse-medium-gray">Select a model to view details</p>
                    </div>
                  )}

                  {selectedModel && (
                    <div className="border-t pt-4">
                      <h5 className="font-medium text-dealverse-navy mb-2">Current Valuation</h5>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-dealverse-green">
                          {selectedModel.enterprise_value || 'N/A'}
                        </div>
                        <p className="text-xs text-dealverse-medium-gray">Enterprise Value</p>
                        {selectedModel.equity_value && (
                          <div className="mt-2">
                            <div className="text-lg font-semibold text-dealverse-blue">
                              {selectedModel.equity_value}
                            </div>
                            <p className="text-xs text-dealverse-medium-gray">Equity Value</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="border-t pt-4">
                    <h5 className="font-medium text-dealverse-navy mb-2">Key Metrics</h5>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-dealverse-medium-gray">Revenue Multiple:</span>
                        <span className="font-medium">11.7x</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-dealverse-medium-gray">EBITDA Multiple:</span>
                        <span className="font-medium">18.2x</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-dealverse-medium-gray">IRR:</span>
                        <span className="font-medium text-dealverse-green">18.5%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-dealverse-medium-gray">MOIC:</span>
                        <span className="font-medium">2.8x</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex space-x-2 pt-4">
                    <Button className="flex-1 bg-dealverse-blue hover:bg-dealverse-blue/90" size="sm">
                      Open Model
                    </Button>
                    <Button variant="outline" size="sm">
                      <Download className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="scenarios" className="space-y-6">
          {/* Scenario Analysis Header */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-dealverse-navy">Scenario Analysis</h2>
              <p className="text-dealverse-medium-gray">Compare different scenarios and sensitivity analysis</p>
            </div>
            <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90">
              <Plus className="h-4 w-4 mr-2" />
              Add Scenario
            </Button>
          </div>

          {/* Scenario Visualization */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Revenue Projection Chart */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-dealverse-navy">Revenue Projections</CardTitle>
                <CardDescription>Scenario comparison over time</CardDescription>
              </CardHeader>
              <CardContent>
                {scenarioLoading ? (
                  <div className="flex items-center justify-center h-64">
                    <Loader2 className="h-8 w-8 animate-spin text-dealverse-blue" />
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={scenarioChartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="year" stroke="#6b7280" />
                      <YAxis stroke="#6b7280" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px'
                        }}
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="Base Case"
                        stroke="#0066ff"
                        strokeWidth={3}
                        dot={{ fill: '#0066ff', strokeWidth: 2, r: 4 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="Upside Case"
                        stroke="#00c896"
                        strokeWidth={3}
                        dot={{ fill: '#00c896', strokeWidth: 2, r: 4 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="Downside Case"
                        stroke="#ff6b6b"
                        strokeWidth={3}
                        dot={{ fill: '#ff6b6b', strokeWidth: 2, r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            {/* Scenario Probability Distribution */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-dealverse-navy">Probability Distribution</CardTitle>
                <CardDescription>Scenario likelihood and impact</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {scenarios.map((scenario) => (
                    <div key={scenario.id} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-dealverse-navy">{scenario.name}</span>
                        <span className="text-sm text-dealverse-medium-gray">{(scenario.probability * 100).toFixed(0)}%</span>
                      </div>
                      <Progress
                        value={scenario.probability * 100}
                        className="h-2"
                      />
                      <div className="flex items-center justify-between text-xs text-dealverse-medium-gray">
                        <span>Valuation: {scenario.results.valuation}</span>
                        <span>IRR: {scenario.results.irr}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Scenario Table */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-dealverse-navy">Detailed Analysis</CardTitle>
              <CardDescription>Complete scenario breakdown and metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-dealverse-light-gray">
                      <th className="text-left py-3 px-4 font-medium text-dealverse-navy">Scenario</th>
                      <th className="text-right py-3 px-4 font-medium text-dealverse-navy">2024 Revenue</th>
                      <th className="text-right py-3 px-4 font-medium text-dealverse-navy">2025 Revenue</th>
                      <th className="text-right py-3 px-4 font-medium text-dealverse-navy">2026 Revenue</th>
                      <th className="text-right py-3 px-4 font-medium text-dealverse-navy">EBITDA Margin</th>
                      <th className="text-right py-3 px-4 font-medium text-dealverse-navy">Valuation</th>
                      <th className="text-right py-3 px-4 font-medium text-dealverse-navy">IRR</th>
                      <th className="text-right py-3 px-4 font-medium text-dealverse-navy">Multiple</th>
                      <th className="text-center py-3 px-4 font-medium text-dealverse-navy">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scenarios.map((scenario) => (
                      <tr key={scenario.id} className="border-b border-dealverse-light-gray/50">
                        <td className="py-3 px-4">
                          <div className="flex items-center space-x-2">
                            <Badge
                              className={`${
                                scenario.name === 'Base Case' ? 'bg-dealverse-blue/10 text-dealverse-blue' :
                                scenario.name === 'Upside Case' ? 'bg-dealverse-green/10 text-dealverse-green' :
                                'bg-dealverse-coral/10 text-dealverse-coral'
                              }`}
                            >
                              {scenario.name}
                            </Badge>
                            <span className="text-xs text-dealverse-medium-gray">
                              {(scenario.probability * 100).toFixed(0)}%
                            </span>
                          </div>
                          {scenario.description && (
                            <p className="text-xs text-dealverse-medium-gray mt-1">{scenario.description}</p>
                          )}
                        </td>
                        <td className="text-right py-3 px-4 text-dealverse-navy">{scenario.results.revenue2024}</td>
                        <td className="text-right py-3 px-4 text-dealverse-navy">{scenario.results.revenue2025}</td>
                        <td className="text-right py-3 px-4 text-dealverse-navy">{scenario.results.revenue2026}</td>
                        <td className="text-right py-3 px-4 text-dealverse-navy">{scenario.results.ebitdaMargin}</td>
                        <td className="text-right py-3 px-4 font-semibold text-dealverse-navy">{scenario.results.valuation}</td>
                        <td className="text-right py-3 px-4 text-dealverse-green">{scenario.results.irr}</td>
                        <td className="text-right py-3 px-4 text-dealverse-navy">{scenario.results.multiple}</td>
                        <td className="text-center py-3 px-4">
                          <div className="flex items-center justify-center space-x-1">
                            <Button variant="ghost" size="sm">
                              <Edit className="h-3 w-3" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Copy className="h-3 w-3" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Download className="h-3 w-3" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="collaboration" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Team Members */}
            <div className="lg:col-span-2">
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl font-semibold text-dealverse-navy">Team Collaboration</CardTitle>
                      <CardDescription className="text-dealverse-medium-gray">
                        Real-time collaboration and team member activity
                      </CardDescription>
                    </div>
                    <Button variant="outline" size="sm">
                      <UserPlus className="h-4 w-4 mr-2" />
                      Invite
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {teamMembers.map((member) => (
                      <div key={member.id} className="flex items-center justify-between p-3 rounded-lg bg-dealverse-light-gray/30">
                        <div className="flex items-center space-x-3">
                          <div className="relative">
                            <div className="w-10 h-10 bg-dealverse-blue/20 rounded-full flex items-center justify-center">
                              <span className="text-sm font-medium text-dealverse-blue">
                                {member.name.split(' ').map(n => n[0]).join('')}
                              </span>
                            </div>
                            <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${getStatusIcon(member.status)}`}></div>
                          </div>
                          <div>
                            <div className="font-medium text-dealverse-navy">{member.name}</div>
                            <div className="text-sm text-dealverse-medium-gray">{member.role}</div>
                            {member.currentModel && (
                              <div className="text-xs text-dealverse-blue">Working on: {member.currentModel}</div>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-dealverse-medium-gray">Last active</div>
                          <div className="text-sm font-medium text-dealverse-navy">{member.lastActive}</div>
                          <div className="flex items-center space-x-1 mt-1">
                            <Button variant="ghost" size="sm">
                              <MessageSquare className="h-3 w-3" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Bell className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Real-time Activity Feed */}
            <div>
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-dealverse-navy">Live Activity</CardTitle>
                  <CardDescription>Real-time collaboration events</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {collaborationEvents.length === 0 ? (
                      <div className="text-center py-8">
                        <Activity className="h-8 w-8 text-dealverse-medium-gray mx-auto mb-2" />
                        <p className="text-sm text-dealverse-medium-gray">No recent activity</p>
                      </div>
                    ) : (
                      collaborationEvents.map((event) => (
                        <div key={event.id} className="flex items-start space-x-2 p-2 rounded-lg hover:bg-dealverse-light-gray/20">
                          <div className="w-2 h-2 bg-dealverse-blue rounded-full mt-2 flex-shrink-0"></div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-dealverse-navy">
                              <span className="font-medium">{event.user_name}</span>
                              {event.type === 'cell_update' && ' updated a cell'}
                              {event.type === 'scenario_add' && ' added a scenario'}
                              {event.type === 'user_join' && ' joined the model'}
                              {event.type === 'user_leave' && ' left the model'}
                              {event.type === 'comment_add' && ' added a comment'}
                            </p>
                            <p className="text-xs text-dealverse-medium-gray">
                              {new Date(event.timestamp).toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Collaborative Modeling Interface */}
          {selectedModel && (
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-dealverse-navy">
                  Collaborative Modeling - {selectedModel.name}
                </CardTitle>
                <CardDescription>
                  Real-time collaborative financial modeling interface
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  {/* Key Metrics Cards */}
                  <Card className="p-4">
                    <div className="flex items-center space-x-2">
                      <DollarSign className="h-4 w-4 text-dealverse-green" />
                      <span className="text-sm font-medium text-dealverse-navy">Revenue Growth</span>
                    </div>
                    <div className="mt-2">
                      <div className="text-2xl font-bold text-dealverse-navy">20%</div>
                      <p className="text-xs text-dealverse-medium-gray">Annual growth rate</p>
                    </div>
                  </Card>

                  <Card className="p-4">
                    <div className="flex items-center space-x-2">
                      <Percent className="h-4 w-4 text-dealverse-blue" />
                      <span className="text-sm font-medium text-dealverse-navy">EBITDA Margin</span>
                    </div>
                    <div className="mt-2">
                      <div className="text-2xl font-bold text-dealverse-navy">22%</div>
                      <p className="text-xs text-dealverse-medium-gray">Current margin</p>
                    </div>
                  </Card>

                  <Card className="p-4">
                    <div className="flex items-center space-x-2">
                      <Target className="h-4 w-4 text-dealverse-coral" />
                      <span className="text-sm font-medium text-dealverse-navy">IRR</span>
                    </div>
                    <div className="mt-2">
                      <div className="text-2xl font-bold text-dealverse-navy">18.5%</div>
                      <p className="text-xs text-dealverse-medium-gray">Internal rate of return</p>
                    </div>
                  </Card>

                  <Card className="p-4">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4 text-dealverse-green" />
                      <span className="text-sm font-medium text-dealverse-navy">Multiple</span>
                    </div>
                    <div className="mt-2">
                      <div className="text-2xl font-bold text-dealverse-navy">11.7x</div>
                      <p className="text-xs text-dealverse-medium-gray">Revenue multiple</p>
                    </div>
                  </Card>
                </div>

                <div className="mt-6 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Badge className="bg-dealverse-green/10 text-dealverse-green border-dealverse-green/20">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Auto-saved
                    </Badge>
                    <span className="text-xs text-dealverse-medium-gray">Last saved 2 minutes ago</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm">
                      <Save className="h-4 w-4 mr-2" />
                      Save Version
                    </Button>
                    <Button variant="outline" size="sm">
                      <Upload className="h-4 w-4 mr-2" />
                      Export
                    </Button>
                    <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90" size="sm">
                      <Share className="h-4 w-4 mr-2" />
                      Share Model
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="versions" className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-dealverse-navy">Version History</h2>
              <p className="text-dealverse-medium-gray">Track changes and model evolution over time</p>
            </div>
            <Button
              className="bg-dealverse-blue hover:bg-dealverse-blue/90"
              onClick={() => selectedModel && createVersion(selectedModel.id)}
              disabled={!selectedModel || versionsLoading}
            >
              <GitBranch className="h-4 w-4 mr-2" />
              Create Version
            </Button>
          </div>

          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-dealverse-navy">
                {selectedModel ? `${selectedModel.name} - Version History` : 'Select a model to view versions'}
              </CardTitle>
              <CardDescription className="text-dealverse-medium-gray">
                Complete version control with change tracking and rollback capabilities
              </CardDescription>
            </CardHeader>
            <CardContent>
              {versionsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-dealverse-blue" />
                  <span className="ml-2 text-dealverse-medium-gray">Loading version history...</span>
                </div>
              ) : !selectedModel ? (
                <div className="text-center py-8">
                  <GitBranch className="h-12 w-12 text-dealverse-medium-gray mx-auto mb-4" />
                  <p className="text-dealverse-medium-gray">Select a financial model to view its version history</p>
                </div>
              ) : modelVersions.length === 0 ? (
                <div className="text-center py-8">
                  <History className="h-12 w-12 text-dealverse-medium-gray mx-auto mb-4" />
                  <p className="text-dealverse-medium-gray mb-4">No version history available</p>
                  <Button
                    className="bg-dealverse-blue hover:bg-dealverse-blue/90"
                    onClick={() => createVersion(selectedModel.id)}
                  >
                    <GitBranch className="h-4 w-4 mr-2" />
                    Create First Version
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {modelVersions.map((version) => (
                    <div
                      key={version.id}
                      className={`flex items-center justify-between p-4 rounded-lg border transition-all duration-200 hover:shadow-md ${
                        version.is_current
                          ? 'border-dealverse-blue bg-dealverse-blue/5'
                          : 'border-dealverse-light-gray hover:border-dealverse-blue/50'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          version.is_current
                            ? 'bg-dealverse-blue/20'
                            : 'bg-dealverse-green/20'
                        }`}>
                          {version.is_current ? (
                            <CheckCircle className="h-5 w-5 text-dealverse-blue" />
                          ) : (
                            <History className="h-5 w-5 text-dealverse-green" />
                          )}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-semibold text-dealverse-navy">{version.version}</span>
                            {version.is_current && (
                              <Badge className="bg-dealverse-blue/10 text-dealverse-blue border-dealverse-blue/20">
                                Current
                              </Badge>
                            )}
                          </div>
                          <div className="text-sm text-dealverse-medium-gray mt-1">{version.changes}</div>
                          <div className="text-xs text-dealverse-medium-gray mt-1">
                            {version.date} by {version.author}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm" title="View Version">
                          <Eye className="h-3 w-3" />
                        </Button>
                        <Button variant="outline" size="sm" title="Download Version">
                          <Download className="h-3 w-3" />
                        </Button>
                        <Button variant="outline" size="sm" title="Compare Versions">
                          <GitBranch className="h-3 w-3" />
                        </Button>
                        {!version.is_current && (
                          <Button variant="outline" size="sm" title="Restore Version">
                            <RefreshCw className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Version Comparison */}
          {selectedModel && modelVersions.length > 1 && (
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-dealverse-navy">Version Comparison</CardTitle>
                <CardDescription>Compare changes between different versions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="text-sm font-medium text-dealverse-navy">Compare from:</label>
                    <select className="w-full mt-1 px-3 py-2 border border-dealverse-light-gray rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-dealverse-blue">
                      {modelVersions.map((version) => (
                        <option key={version.id} value={version.id}>
                          {version.version} - {version.changes}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-dealverse-navy">Compare to:</label>
                    <select className="w-full mt-1 px-3 py-2 border border-dealverse-light-gray rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-dealverse-blue">
                      {modelVersions.map((version) => (
                        <option key={version.id} value={version.id}>
                          {version.version} - {version.changes}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="mt-4 flex justify-end">
                  <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Compare Versions
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
