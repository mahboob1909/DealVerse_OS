"use client";

import React, { useState, useMemo } from 'react';
import { useAuth } from '@/lib/auth-context';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Plus,
  Search,
  Filter,
  FileText,
  Users,
  Clock,
  Star,
  Eye,
  Edit,
  Copy,
  Trash2,
  Share2,
  MessageSquare,
  Activity,
  Layout,
  Presentation as PresentationIcon
} from 'lucide-react';
import { usePresentations, usePresentationTemplates } from '@/hooks/use-presentations';
import { PRESENTATION_STATUS, PRESENTATION_TYPES, ACCESS_LEVELS } from '@/lib/types/presentation';
import { ExportButton, exportConfigs } from '@/components/ui/export-button';
import { PresentationCard } from './presentation-card';
import { TemplateGallery } from './template-gallery-simple';
import { CreatePresentationDialog } from './create-presentation-dialog';

export function PitchCraftSuite() {
  const { user, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState('presentations');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [typeFilter, setTypeFilter] = useState<string | undefined>(undefined);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Memoize filter objects to prevent unnecessary re-renders
  const presentationFilters = useMemo(() => ({
    status: statusFilter,
    presentation_type: typeFilter,
    limit: 50
  }), [statusFilter, typeFilter]);

  const templateFilters = useMemo(() => ({
    public_only: false,
    limit: 20
  }), []);

  // Fetch presentations with filters
  const {
    presentations,
    loading: presentationsLoading,
    error: presentationsError,
    refetch: refetchPresentations,
    createPresentation,
    updatePresentation,
    deletePresentation,
    createVersion
  } = usePresentations(presentationFilters);

  // Fetch templates
  const {
    templates,
    loading: templatesLoading,
    error: templatesError,
    createFromTemplate
  } = usePresentationTemplates(templateFilters);

  // Filter presentations by search query
  const filteredPresentations = presentations.filter(presentation =>
    presentation.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    presentation.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    presentation.client_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Show loading state while authentication is being checked
  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Show error if user is not authenticated
  if (!user) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center">
            <div className="text-red-600 mb-4">
              Authentication required. Please log in to access PitchCraft Suite.
            </div>
            <Button
              variant="outline"
              onClick={() => window.location.href = '/auth/login'}
            >
              Go to Login
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }



  const handleCreatePresentation = async (data: any) => {
    try {
      await createPresentation(data);
      setShowCreateDialog(false);
    } catch (error) {
      console.error('Failed to create presentation:', error);
    }
  };

  const handleCreateFromTemplate = async (templateId: string, data: any) => {
    try {
      await createFromTemplate(templateId, data);
      setActiveTab('presentations');
      refetchPresentations();
    } catch (error) {
      console.error('Failed to create presentation from template:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'active': return 'bg-blue-100 text-blue-800';
      case 'review': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'archived': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'investment_pitch': return <PresentationIcon className="h-4 w-4" />;
      case 'market_research': return <FileText className="h-4 w-4" />;
      case 'financial_analysis': return <Layout className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">PitchCraft Suite</h1>
          <p className="text-muted-foreground">
            Create, manage, and collaborate on professional presentations
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)} className="bg-[#0066ff] hover:bg-[#0052cc]">
          <Plus className="mr-2 h-4 w-4" />
          New Presentation
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Presentations</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{presentations.length}</div>
            <p className="text-xs text-muted-foreground">
              {presentations.filter(p => p.status === 'active').length} active
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Shared</CardTitle>
            <Share2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {presentations.filter(p => p.is_shared).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Collaborative presentations
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Templates</CardTitle>
            <Layout className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{templates.length}</div>
            <p className="text-xs text-muted-foreground">
              {templates.filter(t => t.is_featured).length} featured
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Review</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {presentations.filter(p => p.status === 'review').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Pending approval
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="presentations">My Presentations</TabsTrigger>
          <TabsTrigger value="templates">Template Gallery</TabsTrigger>
          <TabsTrigger value="shared">Shared with Me</TabsTrigger>
          <TabsTrigger value="recent">Recent Activity</TabsTrigger>
        </TabsList>

        {/* Presentations Tab */}
        <TabsContent value="presentations" className="space-y-4">
          {/* Search and Filters */}
          <div className="flex items-center space-x-2">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search presentations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
            <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value === "all" ? undefined : value)}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="review">Review</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="archived">Archived</SelectItem>
              </SelectContent>
            </Select>
            <Select value={typeFilter} onValueChange={(value) => setTypeFilter(value === "all" ? undefined : value)}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="investment_pitch">Investment Pitch</SelectItem>
                <SelectItem value="market_research">Market Research</SelectItem>
                <SelectItem value="financial_analysis">Financial Analysis</SelectItem>
                <SelectItem value="due_diligence">Due Diligence</SelectItem>
                <SelectItem value="compliance_report">Compliance Report</SelectItem>
                <SelectItem value="custom">Custom</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
              <Filter className="mr-2 h-4 w-4" />
              Filters
            </Button>
          </div>

          {/* Presentations Grid */}
          {presentationsLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardHeader>
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </CardHeader>
                  <CardContent>
                    <div className="h-20 bg-gray-200 rounded"></div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : presentationsError ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-red-600 mb-4">
                    Error loading presentations: {presentationsError}
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => refetchPresentations()}
                    className="gap-2"
                  >
                    <Activity className="h-4 w-4" />
                    Retry
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : filteredPresentations.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <FileText className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No presentations</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Get started by creating a new presentation.
                  </p>
                  <div className="mt-6">
                    <Button onClick={() => setShowCreateDialog(true)}>
                      <Plus className="mr-2 h-4 w-4" />
                      New Presentation
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredPresentations.map((presentation) => (
                <PresentationCard
                  key={presentation.id}
                  presentation={presentation}
                  onUpdate={updatePresentation}
                  onDelete={deletePresentation}
                  onCreateVersion={createVersion}
                />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates">
          <TemplateGallery
            templates={templates}
            loading={templatesLoading}
            error={templatesError}
            onCreateFromTemplate={handleCreateFromTemplate}
          />
        </TabsContent>

        {/* Shared Tab */}
        <TabsContent value="shared">
          <Card>
            <CardHeader>
              <CardTitle>Shared Presentations</CardTitle>
              <CardDescription>
                Presentations that have been shared with you by team members
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center text-gray-500">
                Shared presentations feature coming soon...
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Recent Activity Tab */}
        <TabsContent value="recent">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest updates and collaboration activities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center text-gray-500">
                Activity feed coming soon...
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Presentation Dialog */}
      <CreatePresentationDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onSubmit={handleCreatePresentation}
      />
    </div>
  );
}
