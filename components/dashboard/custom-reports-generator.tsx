"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import {
  FileText,
  Download,
  Eye,
  Settings,
  Calendar,
  BarChart3,
  PieChart,
  TrendingUp,
  Users,
  DollarSign,
  Shield,
  Loader2,
  CheckCircle,
  AlertCircle,
  Plus,
  Filter
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { toast } from 'sonner';

interface ReportTemplate {
  name: string;
  description: string;
  sections: string[];
  default_period: number;
  format_options: string[];
  charts: string[];
}

interface TemplateSection {
  id: string;
  name: string;
  description: string;
}

interface TemplateChart {
  id: string;
  name: string;
  description: string;
  type: string;
}

export function CustomReportsGenerator() {
  const { user } = useAuth();
  const [templates, setTemplates] = useState<Record<string, ReportTemplate>>({});
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [templateSections, setTemplateSections] = useState<TemplateSection[]>([]);
  const [templateCharts, setTemplateCharts] = useState<TemplateChart[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  
  // Form state
  const [reportTitle, setReportTitle] = useState('');
  const [dateRangeDays, setDateRangeDays] = useState<number>(90);
  const [formatType, setFormatType] = useState<string>('pdf');
  const [selectedSections, setSelectedSections] = useState<string[]>([]);
  const [selectedCharts, setSelectedCharts] = useState<string[]>([]);
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');
  const [useCustomDateRange, setUseCustomDateRange] = useState(false);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/reports/templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch templates');
      }

      const data = await response.json();
      setTemplates(data.templates);
    } catch (error) {
      console.error('Error fetching templates:', error);
      toast.error('Failed to load report templates');
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplateDetails = useCallback(async () => {
    try {
      // Fetch sections
      const sectionsResponse = await fetch(`/api/v1/reports/templates/${selectedTemplate}/sections`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (sectionsResponse.ok) {
        const sectionsData = await sectionsResponse.json();
        setTemplateSections(sectionsData.sections);
        setSelectedSections(sectionsData.sections.map((s: TemplateSection) => s.id));
      }

      // Fetch charts
      const chartsResponse = await fetch(`/api/v1/reports/templates/${selectedTemplate}/charts`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (chartsResponse.ok) {
        const chartsData = await chartsResponse.json();
        setTemplateCharts(chartsData.charts);
        setSelectedCharts(chartsData.charts.map((c: TemplateChart) => c.id));
      }

      // Set default values
      const template = templates[selectedTemplate];
      if (template) {
        setDateRangeDays(template.default_period);
        setFormatType(template.format_options[0] || 'pdf');
      }
    } catch (error) {
      console.error('Error fetching template details:', error);
      toast.error('Failed to load template details');
    }
  }, [selectedTemplate, templates]);

  useEffect(() => {
    if (selectedTemplate) {
      fetchTemplateDetails();
    }
  }, [selectedTemplate, fetchTemplateDetails]);

  const handlePreviewReport = async () => {
    if (!selectedTemplate) {
      toast.error('Please select a template');
      return;
    }

    try {
      setPreviewing(true);
      
      const requestBody = {
        template_id: selectedTemplate,
        customizations: {
          sections: selectedSections,
          charts: selectedCharts,
          title: reportTitle || undefined
        },
        date_range_days: useCustomDateRange ? undefined : dateRangeDays,
        start_date: useCustomDateRange ? customStartDate : undefined,
        end_date: useCustomDateRange ? customEndDate : undefined,
        format_type: formatType,
        title: reportTitle || undefined
      };

      const response = await fetch('/api/v1/reports/preview', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error('Failed to generate preview');
      }

      const data = await response.json();
      
      // Show preview in a dialog or modal
      toast.success('Report preview generated successfully');
      console.log('Preview data:', data.preview);
      
    } catch (error) {
      console.error('Error generating preview:', error);
      toast.error('Failed to generate report preview');
    } finally {
      setPreviewing(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!selectedTemplate) {
      toast.error('Please select a template');
      return;
    }

    try {
      setGenerating(true);
      
      const requestBody = {
        template_id: selectedTemplate,
        customizations: {
          sections: selectedSections,
          charts: selectedCharts,
          title: reportTitle || undefined
        },
        date_range_days: useCustomDateRange ? undefined : dateRangeDays,
        start_date: useCustomDateRange ? customStartDate : undefined,
        end_date: useCustomDateRange ? customEndDate : undefined,
        format_type: formatType,
        title: reportTitle || undefined
      };

      const response = await fetch('/api/v1/reports/generate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error('Failed to generate report');
      }

      // Handle file download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const filename = response.headers.get('Content-Disposition')?.split('filename=')[1] || 
                     `${selectedTemplate}_report.${formatType === 'excel' ? 'xlsx' : formatType}`;
      link.download = filename.replace(/"/g, '');
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Report generated and downloaded successfully');
      
    } catch (error) {
      console.error('Error generating report:', error);
      toast.error('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const getTemplateIcon = (templateId: string) => {
    switch (templateId) {
      case 'executive_summary': return <TrendingUp className="h-5 w-5" />;
      case 'sales_performance': return <BarChart3 className="h-5 w-5" />;
      case 'client_analysis': return <Users className="h-5 w-5" />;
      case 'financial_summary': return <DollarSign className="h-5 w-5" />;
      case 'team_productivity': return <Users className="h-5 w-5" />;
      case 'compliance_audit': return <Shield className="h-5 w-5" />;
      default: return <FileText className="h-5 w-5" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading report templates...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-dealverse-navy to-dealverse-blue bg-clip-text text-transparent">
            Custom Reports Generator
          </h1>
          <p className="text-dealverse-medium-gray dark:text-dealverse-light-gray">
            Create customized reports with automated data analysis and professional formatting
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Template Selection */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Report Templates
              </CardTitle>
              <CardDescription>
                Choose from predefined report templates
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(templates).map(([templateId, template]) => (
                <div
                  key={templateId}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedTemplate === templateId
                      ? 'border-dealverse-blue bg-dealverse-blue/5'
                      : 'border-gray-200 hover:border-dealverse-blue/50'
                  }`}
                  onClick={() => setSelectedTemplate(templateId)}
                >
                  <div className="flex items-start space-x-3">
                    <div className="text-dealverse-blue mt-1">
                      {getTemplateIcon(templateId)}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-sm">{template.name}</h4>
                      <p className="text-xs text-dealverse-medium-gray mt-1">
                        {template.description}
                      </p>
                      <div className="flex items-center space-x-2 mt-2">
                        <Badge variant="outline" className="text-xs">
                          {template.default_period} days
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {template.sections.length} sections
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Configuration */}
        <div className="lg:col-span-2">
          {selectedTemplate ? (
            <Tabs defaultValue="basic" className="space-y-4">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="basic">Basic Settings</TabsTrigger>
                <TabsTrigger value="sections">Sections & Charts</TabsTrigger>
                <TabsTrigger value="generate">Generate Report</TabsTrigger>
              </TabsList>

              <TabsContent value="basic" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Basic Configuration</CardTitle>
                    <CardDescription>
                      Configure basic report settings
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="reportTitle">Report Title (Optional)</Label>
                      <Input
                        id="reportTitle"
                        placeholder="Enter custom report title"
                        value={reportTitle}
                        onChange={(e) => setReportTitle(e.target.value)}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Date Range</Label>
                      <div className="space-y-3">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="useCustomRange"
                            checked={useCustomDateRange}
                            onCheckedChange={(checked) => setUseCustomDateRange(checked as boolean)}
                          />
                          <Label htmlFor="useCustomRange">Use custom date range</Label>
                        </div>

                        {useCustomDateRange ? (
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="startDate">Start Date</Label>
                              <Input
                                id="startDate"
                                type="date"
                                value={customStartDate}
                                onChange={(e) => setCustomStartDate(e.target.value)}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="endDate">End Date</Label>
                              <Input
                                id="endDate"
                                type="date"
                                value={customEndDate}
                                onChange={(e) => setCustomEndDate(e.target.value)}
                              />
                            </div>
                          </div>
                        ) : (
                          <Select value={dateRangeDays.toString()} onValueChange={(value) => setDateRangeDays(parseInt(value))}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="7">Last 7 days</SelectItem>
                              <SelectItem value="30">Last 30 days</SelectItem>
                              <SelectItem value="60">Last 60 days</SelectItem>
                              <SelectItem value="90">Last 90 days</SelectItem>
                              <SelectItem value="180">Last 6 months</SelectItem>
                              <SelectItem value="365">Last year</SelectItem>
                            </SelectContent>
                          </Select>
                        )}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Output Format</Label>
                      <Select value={formatType} onValueChange={setFormatType}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {templates[selectedTemplate]?.format_options.map((format) => (
                            <SelectItem key={format} value={format}>
                              {format.toUpperCase()}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="sections" className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  {/* Sections */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Report Sections</CardTitle>
                      <CardDescription>
                        Select which sections to include in your report
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {templateSections.map((section) => (
                        <div key={section.id} className="flex items-start space-x-2">
                          <Checkbox
                            id={section.id}
                            checked={selectedSections.includes(section.id)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setSelectedSections([...selectedSections, section.id]);
                              } else {
                                setSelectedSections(selectedSections.filter(s => s !== section.id));
                              }
                            }}
                          />
                          <div className="flex-1">
                            <Label htmlFor={section.id} className="text-sm font-medium">
                              {section.name}
                            </Label>
                            <p className="text-xs text-dealverse-medium-gray mt-1">
                              {section.description}
                            </p>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>

                  {/* Charts */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Charts & Visualizations</CardTitle>
                      <CardDescription>
                        Select which charts to include in your report
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {templateCharts.map((chart) => (
                        <div key={chart.id} className="flex items-start space-x-2">
                          <Checkbox
                            id={chart.id}
                            checked={selectedCharts.includes(chart.id)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setSelectedCharts([...selectedCharts, chart.id]);
                              } else {
                                setSelectedCharts(selectedCharts.filter(c => c !== chart.id));
                              }
                            }}
                          />
                          <div className="flex-1">
                            <Label htmlFor={chart.id} className="text-sm font-medium">
                              {chart.name}
                            </Label>
                            <p className="text-xs text-dealverse-medium-gray mt-1">
                              {chart.description}
                            </p>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="generate" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Generate Report</CardTitle>
                    <CardDescription>
                      Review your settings and generate the custom report
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Summary */}
                    <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                      <h4 className="font-medium">Report Summary</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-dealverse-medium-gray">Template:</span>
                          <span className="ml-2 font-medium">{templates[selectedTemplate]?.name}</span>
                        </div>
                        <div>
                          <span className="text-dealverse-medium-gray">Format:</span>
                          <span className="ml-2 font-medium">{formatType.toUpperCase()}</span>
                        </div>
                        <div>
                          <span className="text-dealverse-medium-gray">Sections:</span>
                          <span className="ml-2 font-medium">{selectedSections.length}</span>
                        </div>
                        <div>
                          <span className="text-dealverse-medium-gray">Charts:</span>
                          <span className="ml-2 font-medium">{selectedCharts.length}</span>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex space-x-3">
                      <Button
                        variant="outline"
                        onClick={handlePreviewReport}
                        disabled={previewing || generating}
                      >
                        {previewing ? (
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        ) : (
                          <Eye className="h-4 w-4 mr-2" />
                        )}
                        Preview
                      </Button>
                      <Button
                        onClick={handleGenerateReport}
                        disabled={generating || previewing}
                        className="bg-dealverse-blue hover:bg-dealverse-blue/90"
                      >
                        {generating ? (
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        ) : (
                          <Download className="h-4 w-4 mr-2" />
                        )}
                        Generate Report
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center h-96">
                <div className="text-center">
                  <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Template</h3>
                  <p className="text-gray-500">Choose a report template from the left to get started</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
