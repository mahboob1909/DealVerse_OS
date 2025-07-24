"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Star,
  Eye,
  Plus,
  Search,
  Layout,
  FileText,
  Presentation as PresentationIcon,
  TrendingUp,
  Shield,
  Users,
  Image as ImageIcon
} from 'lucide-react';
import type { PresentationTemplate } from '@/lib/types/presentation';

interface TemplateGalleryProps {
  templates: PresentationTemplate[];
  loading: boolean;
  error: string | null;
  onCreateFromTemplate: (templateId: string, data: any) => Promise<any>;
}

export function TemplateGallery({ 
  templates, 
  loading, 
  error, 
  onCreateFromTemplate 
}: TemplateGalleryProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [featuredOnly, setFeaturedOnly] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<PresentationTemplate | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  // Filter templates
  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !categoryFilter || template.category === categoryFilter;
    const matchesFeatured = !featuredOnly || template.is_featured;
    
    return matchesSearch && matchesCategory && matchesFeatured;
  });

  // Get unique categories
  const categories = Array.from(new Set(templates.map(t => t.category).filter(Boolean))) as string[];

  const getCategoryIcon = (category: string) => {
    switch (category?.toLowerCase()) {
      case 'investment': return <TrendingUp className="h-4 w-4" />;
      case 'research': return <FileText className="h-4 w-4" />;
      case 'analysis': return <Layout className="h-4 w-4" />;
      case 'compliance': return <Shield className="h-4 w-4" />;
      case 'pitch': return <PresentationIcon className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  const handlePreview = (template: PresentationTemplate) => {
    setSelectedTemplate(template);
    setShowPreview(true);
  };

  const handleUseTemplate = async (template: PresentationTemplate) => {
    try {
      setIsCreating(true);
      await onCreateFromTemplate(template.id, {
        title: `${template.name} - Copy`,
        description: template.description,
        presentation_type: 'custom'
      });
      setShowPreview(false);
    } catch (error) {
      console.error('Failed to create from template:', error);
    } finally {
      setIsCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {/* Search and Filters Skeleton */}
        <div className="flex items-center space-x-2">
          <div className="h-10 bg-gray-200 rounded flex-1 animate-pulse"></div>
          <div className="h-10 bg-gray-200 rounded w-32 animate-pulse"></div>
          <div className="h-10 bg-gray-200 rounded w-24 animate-pulse"></div>
        </div>
        
        {/* Templates Grid Skeleton */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[...Array(8)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-32 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-red-600">
            Error loading templates: {error}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="flex items-center space-x-2">
        <div className="relative flex-1">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8"
          />
        </div>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Categories</SelectItem>
            {categories.map((category) => (
              <SelectItem key={category} value={category}>
                {category}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          variant={featuredOnly ? "default" : "outline"}
          onClick={() => setFeaturedOnly(!featuredOnly)}
          className="whitespace-nowrap"
        >
          <Star className="mr-2 h-4 w-4" />
          Featured
        </Button>
      </div>

      {/* Templates Grid */}
      {filteredTemplates.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <Layout className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No templates found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your search or filter criteria.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filteredTemplates.map((template) => (
            <Card key={template.id} className="group hover:shadow-md transition-shadow duration-200">
              <CardHeader className="pb-3">
                {/* Template Preview */}
                <div className="relative h-32 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg overflow-hidden">
                  {template.thumbnail_url ? (
                    <img 
                      src={template.thumbnail_url} 
                      alt={template.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      {getCategoryIcon(template.category || '')}
                    </div>
                  )}
                  
                  {/* Overlay with actions */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 space-x-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handlePreview(template)}
                      >
                        <Eye className="h-3 w-3 mr-1" />
                        Preview
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleUseTemplate(template)}
                        className="bg-[#0066ff] hover:bg-[#0052cc]"
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        Use
                      </Button>
                    </div>
                  </div>

                  {/* Featured Badge */}
                  {template.is_featured && (
                    <Badge className="absolute top-2 right-2 bg-yellow-500 text-yellow-900">
                      <Star className="h-3 w-3 mr-1" />
                      Featured
                    </Badge>
                  )}
                </div>

                {/* Template Info */}
                <div>
                  <CardTitle className="text-base leading-tight">
                    {template.name}
                  </CardTitle>
                  <CardDescription className="text-sm mt-1">
                    {template.category && (
                      <span className="inline-flex items-center gap-1">
                        {getCategoryIcon(template.category)}
                        {template.category}
                      </span>
                    )}
                  </CardDescription>
                </div>
              </CardHeader>

              <CardContent className="pt-0">
                {/* Description */}
                {template.description && (
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                    {template.description}
                  </p>
                )}

                {/* Stats */}
                <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
                  <div className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    <span>{template.usage_count} uses</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <FileText className="h-3 w-3" />
                    <span>{template.default_slides.length} slides</span>
                  </div>
                </div>

                {/* Action Button */}
                <Button 
                  className="w-full bg-[#0066ff] hover:bg-[#0052cc]"
                  onClick={() => handleUseTemplate(template)}
                  disabled={isCreating}
                >
                  <Plus className="mr-2 h-3 w-3" />
                  {isCreating ? 'Creating...' : 'Use Template'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Template Preview Dialog */}
      <Dialog open={showPreview} onOpenChange={setShowPreview}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedTemplate && getCategoryIcon(selectedTemplate.category || '')}
              {selectedTemplate?.name}
              {selectedTemplate?.is_featured && (
                <Badge className="bg-yellow-500 text-yellow-900">
                  <Star className="h-3 w-3 mr-1" />
                  Featured
                </Badge>
              )}
            </DialogTitle>
            <DialogDescription>
              {selectedTemplate?.description}
            </DialogDescription>
          </DialogHeader>

          {/* Template Preview Content */}
          <div className="space-y-4">
            {/* Preview Images */}
            {selectedTemplate?.preview_images && selectedTemplate.preview_images.length > 0 ? (
              <div className="grid gap-2 md:grid-cols-2">
                {selectedTemplate.preview_images.slice(0, 4).map((image, index) => (
                  <div key={index} className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                    <img 
                      src={image} 
                      alt={`Preview ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
            ) : (
              <div className="aspect-video bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <ImageIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500">No preview available</p>
                </div>
              </div>
            )}

            {/* Template Stats */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold">{selectedTemplate?.default_slides.length || 0}</div>
                <div className="text-sm text-muted-foreground">Slides</div>
              </div>
              <div>
                <div className="text-2xl font-bold">{selectedTemplate?.usage_count || 0}</div>
                <div className="text-sm text-muted-foreground">Uses</div>
              </div>
              <div>
                <div className="text-2xl font-bold">{selectedTemplate?.category || 'General'}</div>
                <div className="text-sm text-muted-foreground">Category</div>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPreview(false)}>
              Close
            </Button>
            <Button 
              onClick={() => selectedTemplate && handleUseTemplate(selectedTemplate)}
              disabled={isCreating}
              className="bg-[#0066ff] hover:bg-[#0052cc]"
            >
              <Plus className="mr-2 h-4 w-4" />
              {isCreating ? 'Creating...' : 'Use Template'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
