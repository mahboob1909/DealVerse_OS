"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { Download, FileText, FileSpreadsheet, Presentation, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export interface ExportOption {
  label: string;
  format: 'pdf' | 'excel' | 'pptx';
  icon: React.ReactNode;
  endpoint: string;
  filename?: string;
}

interface ExportButtonProps {
  options: ExportOption[];
  resourceId?: string;
  className?: string;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm' | 'lg';
  disabled?: boolean;
}

const formatIcons = {
  pdf: <FileText className="h-4 w-4" />,
  excel: <FileSpreadsheet className="h-4 w-4" />,
  pptx: <Presentation className="h-4 w-4" />,
};

const mimeTypes = {
  pdf: 'application/pdf',
  excel: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
};

export function ExportButton({
  options,
  resourceId,
  className,
  variant = 'outline',
  size = 'default',
  disabled = false,
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState<string | null>(null);

  const handleExport = async (option: ExportOption) => {
    if (disabled) return;

    setIsExporting(option.format);
    
    try {
      // Construct the endpoint URL
      let url = option.endpoint;
      if (resourceId) {
        url = url.replace('{id}', resourceId);
      }

      // Make the API request
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }

      // Get the blob data
      const blob = await response.blob();
      
      // Create download link
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      
      // Set filename
      const filename = option.filename || `export_${Date.now()}.${option.format === 'excel' ? 'xlsx' : option.format}`;
      link.download = filename;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up
      window.URL.revokeObjectURL(downloadUrl);
      
      toast.success(`${option.label} exported successfully`);
      
    } catch (error) {
      console.error('Export error:', error);
      toast.error(`Failed to export ${option.label.toLowerCase()}`);
    } finally {
      setIsExporting(null);
    }
  };

  if (options.length === 1) {
    // Single export option - render as a simple button
    const option = options[0];
    return (
      <Button
        variant={variant}
        size={size}
        className={className}
        onClick={() => handleExport(option)}
        disabled={disabled || isExporting !== null}
      >
        {isExporting === option.format ? (
          <Loader2 className="h-4 w-4 animate-spin mr-2" />
        ) : (
          <>{option.icon || formatIcons[option.format]}</>
        )}
        <span className="ml-2">{option.label}</span>
      </Button>
    );
  }

  // Multiple export options - render as dropdown
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant={variant}
          size={size}
          className={className}
          disabled={disabled || isExporting !== null}
        >
          {isExporting ? (
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
          ) : (
            <Download className="h-4 w-4 mr-2" />
          )}
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {options.map((option, index) => (
          <React.Fragment key={option.format}>
            <DropdownMenuItem
              onClick={() => handleExport(option)}
              disabled={isExporting !== null}
              className="cursor-pointer"
            >
              <div className="flex items-center w-full">
                {isExporting === option.format ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <>{option.icon || formatIcons[option.format]}</>
                )}
                <span className="ml-2">{option.label}</span>
              </div>
            </DropdownMenuItem>
            {index < options.length - 1 && <DropdownMenuSeparator />}
          </React.Fragment>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

// Predefined export configurations for common use cases
export const exportConfigs = {
  financialModel: (modelId: string): ExportOption[] => [
    {
      label: 'Export as PDF',
      format: 'pdf' as const,
      icon: <FileText className="h-4 w-4" />,
      endpoint: `/api/v1/financial-models/${modelId}/export/pdf`,
      filename: `financial_model_${modelId}.pdf`,
    },
    {
      label: 'Export as Excel',
      format: 'excel' as const,
      icon: <FileSpreadsheet className="h-4 w-4" />,
      endpoint: `/api/v1/financial-models/${modelId}/export/excel`,
      filename: `financial_model_${modelId}.xlsx`,
    },
  ],
  
  presentation: (presentationId: string): ExportOption[] => [
    {
      label: 'Export as PowerPoint',
      format: 'pptx' as const,
      icon: <Presentation className="h-4 w-4" />,
      endpoint: `/api/v1/presentations/${presentationId}/export/pptx`,
      filename: `presentation_${presentationId}.pptx`,
    },
    {
      label: 'Export as PDF',
      format: 'pdf' as const,
      icon: <FileText className="h-4 w-4" />,
      endpoint: `/api/v1/presentations/${presentationId}/export/pdf`,
      filename: `presentation_${presentationId}.pdf`,
    },
  ],
  
  complianceReport: (): ExportOption[] => [
    {
      label: 'Export Compliance Report',
      format: 'pdf' as const,
      icon: <FileText className="h-4 w-4" />,
      endpoint: '/api/v1/compliance/reports/export/pdf',
      filename: `compliance_report_${new Date().toISOString().split('T')[0]}.pdf`,
    },
  ],
  
  analytics: (): ExportOption[] => [
    {
      label: 'Export Analytics Data',
      format: 'excel' as const,
      icon: <FileSpreadsheet className="h-4 w-4" />,
      endpoint: '/api/v1/analytics/export/excel',
      filename: `analytics_dashboard_${new Date().toISOString().split('T')[0]}.xlsx`,
    },
  ],
};

// Usage examples:
// <ExportButton options={exportConfigs.financialModel('123')} />
// <ExportButton options={exportConfigs.presentation('456')} />
// <ExportButton options={exportConfigs.complianceReport()} />
// <ExportButton options={exportConfigs.analytics()} />
