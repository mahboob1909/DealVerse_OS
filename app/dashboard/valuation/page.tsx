"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Calculator,
  TrendingUp,
  FileSpreadsheet,
  Users,
  RefreshCw,
  Plus,
  Search,
  Download,
  Share
} from "lucide-react";
import { useState } from "react";
import { useToast } from '@/hooks/use-toast';

export default function ValuationPage() {
  const [activeTab, setActiveTab] = useState("models");
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  
  const { toast } = useToast();

  // Mock data for financial models
  const models = [
    {
      id: 1,
      name: "TechCorp DCF Model",
      model_type: "DCF",
      status: "Active",
      last_updated: "2 hours ago",
      created_by: "John Smith",
      valuation: "$125M",
      description: "Comprehensive DCF analysis for TechCorp acquisition"
    },
    {
      id: 2,
      name: "HealthTech Comparable Analysis",
      model_type: "Comparable",
      status: "Draft",
      last_updated: "1 day ago",
      created_by: "Sarah Johnson",
      valuation: "$87M",
      description: "Market multiple analysis for healthcare sector"
    }
  ];

  const statistics = {
    total_models: 12,
    active_models: 8,
    avg_valuation: "$154M",
    models_this_month: 5
  };

  const filteredModels = models.filter(model => {
    const matchesSearch = model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         model.model_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === "all" || model.model_type === filterType;
    const matchesStatus = filterStatus === "all" || model.status === filterStatus;

    return matchesSearch && matchesType && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Active": return "bg-green-100 text-green-800";
      case "Draft": return "bg-yellow-100 text-yellow-800";
      case "Archived": return "bg-gray-100 text-gray-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-900 to-blue-600 bg-clip-text text-transparent">
              Valuation & Modeling Hub
            </h1>
            <p className="text-gray-600">
              Advanced financial modeling and valuation tools
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-2" />
              New Model
            </Button>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 bg-gradient-to-br from-blue-50 to-blue-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-900">Total Models</CardTitle>
            <FileSpreadsheet className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900">{statistics.total_models}</div>
            <p className="text-xs text-gray-600">Financial models</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-green-50 to-green-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-900">Active Models</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900">{statistics.active_models}</div>
            <p className="text-xs text-gray-600">Currently in use</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-purple-50 to-purple-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-900">Avg Valuation</CardTitle>
            <Calculator className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900">{statistics.avg_valuation}</div>
            <p className="text-xs text-gray-600">Average model value</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-orange-50 to-orange-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-900">This Month</CardTitle>
            <Users className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-900">{statistics.models_this_month}</div>
            <p className="text-xs text-gray-600">New models created</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabbed Interface */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="models">Financial Models</TabsTrigger>
          <TabsTrigger value="scenarios">Scenario Analysis</TabsTrigger>
          <TabsTrigger value="collaboration">Collaboration</TabsTrigger>
          <TabsTrigger value="versions">Version Control</TabsTrigger>
        </TabsList>

        {/* Financial Models Tab */}
        <TabsContent value="models" className="space-y-6">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-gray-900">Financial Models</CardTitle>
              <CardDescription className="text-gray-600">
                {filteredModels.length} models available
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredModels.map((model) => (
                  <Card
                    key={model.id}
                    className="cursor-pointer transition-all duration-200 hover:shadow-md hover:bg-gray-50"
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="font-semibold text-gray-900">{model.name}</h3>
                            <Badge className={getStatusColor(model.status)}>
                              {model.status}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {model.model_type}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{model.description}</p>
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>Created by {model.created_by}</span>
                            <span>Updated {model.last_updated}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-blue-600">
                            {model.valuation}
                          </div>
                          <div className="text-xs text-gray-500">Valuation</div>
                          <div className="mt-2 flex space-x-2">
                            <Button size="sm" variant="outline">
                              <Download className="h-3 w-3 mr-1" />
                              Export
                            </Button>
                            <Button size="sm" variant="outline">
                              <Share className="h-3 w-3 mr-1" />
                              Share
                            </Button>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Other tabs with placeholder content */}
        <TabsContent value="scenarios">
          <Card>
            <CardHeader>
              <CardTitle>Scenario Analysis</CardTitle>
              <CardDescription>Coming soon - Advanced scenario modeling capabilities</CardDescription>
            </CardHeader>
          </Card>
        </TabsContent>

        <TabsContent value="collaboration">
          <Card>
            <CardHeader>
              <CardTitle>Real-time Collaboration</CardTitle>
              <CardDescription>Coming soon - Team collaboration features</CardDescription>
            </CardHeader>
          </Card>
        </TabsContent>

        <TabsContent value="versions">
          <Card>
            <CardHeader>
              <CardTitle>Version Control</CardTitle>
              <CardDescription>Coming soon - Model version management</CardDescription>
            </CardHeader>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
