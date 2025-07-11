'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
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
  Image as ImageIcon,
  RefreshCw
} from 'lucide-react';
import type { PresentationTemplate } from '@/lib/types/presentation';

interface TemplateGalleryProps {
  templates: PresentationTemplate[];
  loading: boolean;
  error: string | null;
  onCreateFromTemplate: (templateId: string, data: any) => Promise<void>;
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
    const matchesFeatured = !featuredOnly || template.featured;
    
    return matchesSearch && matchesCategory && matchesFeatured;
  });

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
        name: `${template.name} - Copy`,
        description: template.description
      });
    } catch (error) {
      console.error('Failed to create from template:', error);
    } finally {
      setIsCreating(false);
    }
  };

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center">
            <div className="text-red-600 mb-4">
              Error loading templates: {error}
            </div>
            <Button 
              variant="outline" 
              onClick={() => window.location.reload()}
              className="gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8"
          />
        </div>
        <Button
          variant={featuredOnly ? "default" : "outline"}
          onClick={() => setFeaturedOnly(!featuredOnly)}
          className="gap-2"
        >
          <Star className="h-4 w-4" />
          Featured
        </Button>
      </div>

      {/* Templates Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-32 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredTemplates.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-muted-foreground">
              {searchQuery || categoryFilter || featuredOnly 
                ? 'No templates match your filters' 
                : 'No templates available'}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => (
            <Card key={template.id} className="group hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    {getCategoryIcon(template.category || '')}
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                  </div>
                  {template.featured && (
                    <Badge variant="secondary" className="gap-1">
                      <Star className="h-3 w-3" />
                      Featured
                    </Badge>
                  )}
                </div>
                <CardDescription>{template.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="relative aspect-video bg-gray-100 rounded-lg mb-4 overflow-hidden">
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
                        disabled={isCreating}
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        Use Template
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>{template.category}</span>
                  <div className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    <span>{template.usage_count || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
