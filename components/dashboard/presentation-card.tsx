"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  MoreHorizontal,
  Eye,
  Edit,
  Copy,
  Share2,
  Trash2,
  Download,
  Clock,
  Users,
  FileText,
  Presentation as PresentationIcon,
  Layout,
  Calendar,
  DollarSign
} from 'lucide-react';
import type { Presentation, UpdatePresentationData } from '@/lib/types/presentation';
import { formatDistanceToNow } from 'date-fns';
import { ExportButton, exportConfigs } from '@/components/ui/export-button';

interface PresentationCardProps {
  presentation: Presentation;
  onUpdate: (id: string, data: UpdatePresentationData) => Promise<any>;
  onDelete: (id: string) => Promise<any>;
  onCreateVersion: (id: string) => Promise<any>;
}

export function PresentationCard({ 
  presentation, 
  onUpdate, 
  onDelete, 
  onCreateVersion 
}: PresentationCardProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isCreatingVersion, setIsCreatingVersion] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'active': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'review': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'approved': return 'bg-green-100 text-green-800 border-green-200';
      case 'archived': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'investment_pitch': return <PresentationIcon className="h-4 w-4" />;
      case 'market_research': return <FileText className="h-4 w-4" />;
      case 'financial_analysis': return <Layout className="h-4 w-4" />;
      case 'due_diligence': return <Eye className="h-4 w-4" />;
      case 'compliance_report': return <FileText className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'investment_pitch': return 'Investment Pitch';
      case 'market_research': return 'Market Research';
      case 'financial_analysis': return 'Financial Analysis';
      case 'due_diligence': return 'Due Diligence';
      case 'compliance_report': return 'Compliance Report';
      case 'custom': return 'Custom';
      default: return 'Presentation';
    }
  };

  const handleDelete = async () => {
    try {
      setIsDeleting(true);
      await onDelete(presentation.id);
      setShowDeleteDialog(false);
    } catch (error) {
      console.error('Failed to delete presentation:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCreateVersion = async () => {
    try {
      setIsCreatingVersion(true);
      await onCreateVersion(presentation.id);
    } catch (error) {
      console.error('Failed to create version:', error);
    } finally {
      setIsCreatingVersion(false);
    }
  };

  const handleView = () => {
    // Navigate to presentation view
    window.open(`/dashboard/presentations/${presentation.id}`, '_blank');
  };

  const handleEdit = () => {
    // Navigate to presentation editor
    window.open(`/dashboard/presentations/${presentation.id}/edit`, '_blank');
  };

  const handleShare = () => {
    // Open share dialog
    console.log('Share presentation:', presentation.id);
  };

  return (
    <>
      <Card className="group hover:shadow-md transition-shadow duration-200">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                {getTypeIcon(presentation.presentation_type)}
                <Badge variant="outline" className={getStatusColor(presentation.status)}>
                  {presentation.status}
                </Badge>
                {presentation.is_shared && (
                  <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                    <Users className="h-3 w-3 mr-1" />
                    Shared
                  </Badge>
                )}
              </div>
              <CardTitle className="text-lg leading-tight truncate">
                {presentation.title}
              </CardTitle>
              <CardDescription className="text-sm mt-1">
                {getTypeLabel(presentation.presentation_type)}
                {presentation.version > 1 && ` • v${presentation.version}`}
              </CardDescription>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleView}>
                  <Eye className="mr-2 h-4 w-4" />
                  View
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleEdit}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleCreateVersion} disabled={isCreatingVersion}>
                  <Copy className="mr-2 h-4 w-4" />
                  {isCreatingVersion ? 'Creating...' : 'Create Version'}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleShare}>
                  <Share2 className="mr-2 h-4 w-4" />
                  Share
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <div className="px-2 py-1">
                  <ExportButton
                    options={exportConfigs.presentation(presentation.id)}
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start h-8 px-2"
                  />
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={() => setShowDeleteDialog(true)}
                  className="text-red-600 focus:text-red-600"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>

        <CardContent className="pt-0">
          {/* Description */}
          {presentation.description && (
            <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
              {presentation.description}
            </p>
          )}

          {/* Metadata */}
          <div className="space-y-2 text-xs text-muted-foreground">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1">
                <FileText className="h-3 w-3" />
                <span>{presentation.slide_count} slides</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>
                  {formatDistanceToNow(new Date(presentation.updated_at), { addSuffix: true })}
                </span>
              </div>
            </div>

            {/* Business Context */}
            {(presentation.client_name || presentation.deal_value) && (
              <div className="flex items-center justify-between">
                {presentation.client_name && (
                  <div className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    <span className="truncate">{presentation.client_name}</span>
                  </div>
                )}
                {presentation.deal_value && (
                  <div className="flex items-center gap-1">
                    <DollarSign className="h-3 w-3" />
                    <span>{presentation.deal_value}</span>
                  </div>
                )}
              </div>
            )}

            {/* Presentation Date */}
            {presentation.presentation_date && (
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                <span>
                  {new Date(presentation.presentation_date).toLocaleDateString()}
                </span>
              </div>
            )}

            {/* Tags */}
            {presentation.tags && presentation.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {presentation.tags.slice(0, 3).map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs px-1 py-0">
                    {tag}
                  </Badge>
                ))}
                {presentation.tags.length > 3 && (
                  <Badge variant="secondary" className="text-xs px-1 py-0">
                    +{presentation.tags.length - 3}
                  </Badge>
                )}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 mt-4">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleView}
              className="flex-1"
            >
              <Eye className="mr-2 h-3 w-3" />
              View
            </Button>
            <Button 
              size="sm" 
              onClick={handleEdit}
              className="flex-1 bg-[#0066ff] hover:bg-[#0052cc]"
            >
              <Edit className="mr-2 h-3 w-3" />
              Edit
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Presentation</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{presentation.title}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
