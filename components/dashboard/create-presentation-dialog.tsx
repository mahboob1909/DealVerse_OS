"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import {
  CalendarIcon,
  X,
  Plus,
  FileText,
  Presentation as PresentationIcon,
  Layout,
  TrendingUp,
  Shield
} from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import type { CreatePresentationData } from '@/lib/types/presentation';
import { PRESENTATION_TYPES, ACCESS_LEVELS } from '@/lib/types/presentation';

interface CreatePresentationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: CreatePresentationData) => Promise<void>;
}

export function CreatePresentationDialog({ 
  open, 
  onOpenChange, 
  onSubmit 
}: CreatePresentationDialogProps) {
  const [formData, setFormData] = useState<Partial<CreatePresentationData>>({
    title: '',
    description: '',
    presentation_type: 'custom',
    access_level: 'team',
    is_shared: false,
    tags: [],
    collaborators: []
  });
  const [presentationDate, setPresentationDate] = useState<Date>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [newTag, setNewTag] = useState('');
  const [newCollaborator, setNewCollaborator] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title?.trim()) {
      return;
    }

    try {
      setIsSubmitting(true);
      
      // For now, we'll use a placeholder organization ID
      // In a real app, this would come from the authenticated user context
      const organizationId = '00000000-0000-0000-0000-000000000001';
      
      const submitData: CreatePresentationData = {
        ...formData,
        title: formData.title.trim(),
        presentation_date: presentationDate?.toISOString(),
        organization_id: organizationId,
      } as CreatePresentationData;

      await onSubmit(submitData);
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        presentation_type: 'custom',
        access_level: 'team',
        is_shared: false,
        tags: [],
        collaborators: []
      });
      setPresentationDate(undefined);
      setNewTag('');
      setNewCollaborator('');
      
    } catch (error) {
      console.error('Failed to create presentation:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const addTag = () => {
    if (newTag.trim() && !formData.tags?.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...(prev.tags || []), newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags?.filter(tag => tag !== tagToRemove) || []
    }));
  };

  const addCollaborator = () => {
    if (newCollaborator.trim() && !formData.collaborators?.includes(newCollaborator.trim())) {
      setFormData(prev => ({
        ...prev,
        collaborators: [...(prev.collaborators || []), newCollaborator.trim()]
      }));
      setNewCollaborator('');
    }
  };

  const removeCollaborator = (collaboratorToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      collaborators: prev.collaborators?.filter(c => c !== collaboratorToRemove) || []
    }));
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'investment_pitch': return <PresentationIcon className="h-4 w-4" />;
      case 'market_research': return <FileText className="h-4 w-4" />;
      case 'financial_analysis': return <Layout className="h-4 w-4" />;
      case 'due_diligence': return <TrendingUp className="h-4 w-4" />;
      case 'compliance_report': return <Shield className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Presentation</DialogTitle>
          <DialogDescription>
            Create a new presentation for your investment banking needs
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={formData.title || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Enter presentation title"
                required
              />
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Brief description of the presentation"
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="type">Presentation Type</Label>
              <Select 
                value={formData.presentation_type || 'custom'} 
                onValueChange={(value) => setFormData(prev => ({ ...prev, presentation_type: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="investment_pitch">
                    <div className="flex items-center gap-2">
                      <PresentationIcon className="h-4 w-4" />
                      Investment Pitch
                    </div>
                  </SelectItem>
                  <SelectItem value="market_research">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Market Research
                    </div>
                  </SelectItem>
                  <SelectItem value="financial_analysis">
                    <div className="flex items-center gap-2">
                      <Layout className="h-4 w-4" />
                      Financial Analysis
                    </div>
                  </SelectItem>
                  <SelectItem value="due_diligence">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4" />
                      Due Diligence
                    </div>
                  </SelectItem>
                  <SelectItem value="compliance_report">
                    <div className="flex items-center gap-2">
                      <Shield className="h-4 w-4" />
                      Compliance Report
                    </div>
                  </SelectItem>
                  <SelectItem value="custom">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Custom
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Business Context */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Business Context</h4>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="client_name">Client Name</Label>
                <Input
                  id="client_name"
                  value={formData.client_name || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, client_name: e.target.value }))}
                  placeholder="Client or company name"
                />
              </div>

              <div>
                <Label htmlFor="deal_value">Deal Value</Label>
                <Input
                  id="deal_value"
                  value={formData.deal_value || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, deal_value: e.target.value }))}
                  placeholder="e.g., $45M"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="target_audience">Target Audience</Label>
              <Input
                id="target_audience"
                value={formData.target_audience || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, target_audience: e.target.value }))}
                placeholder="Who will view this presentation?"
              />
            </div>

            <div>
              <Label>Presentation Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !presentationDate && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {presentationDate ? format(presentationDate, "PPP") : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={presentationDate}
                    onSelect={setPresentationDate}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          {/* Collaboration Settings */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Collaboration</h4>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="is_shared">Enable Sharing</Label>
                <p className="text-sm text-muted-foreground">Allow others to view and collaborate</p>
              </div>
              <Switch
                id="is_shared"
                checked={formData.is_shared || false}
                onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_shared: checked }))}
              />
            </div>

            {formData.is_shared && (
              <div>
                <Label htmlFor="access_level">Access Level</Label>
                <Select 
                  value={formData.access_level || 'team'} 
                  onValueChange={(value) => setFormData(prev => ({ ...prev, access_level: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select access level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="private">Private</SelectItem>
                    <SelectItem value="team">Team</SelectItem>
                    <SelectItem value="organization">Organization</SelectItem>
                    <SelectItem value="public">Public</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>

          {/* Tags */}
          <div className="space-y-2">
            <Label>Tags</Label>
            <div className="flex gap-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Add a tag"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
              />
              <Button type="button" variant="outline" onClick={addTag}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {formData.tags && formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {formData.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="ml-1 hover:text-red-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isSubmitting || !formData.title?.trim()}
              className="bg-[#0066ff] hover:bg-[#0052cc]"
            >
              {isSubmitting ? 'Creating...' : 'Create Presentation'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
