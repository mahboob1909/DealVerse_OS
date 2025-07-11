"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { 
  Search, 
  Filter, 
  Plus, 
  MoreHorizontal,
  TrendingUp,
  DollarSign,
  Calendar,
  Users,
  Building,
  Eye,
  Edit,
  Trash2,
  FileText,
  Clock
} from "lucide-react";
import { useState } from "react";

// Mock data for deals
const deals = [
  {
    id: "1",
    title: "TechFlow Industries Acquisition",
    client: "TechFlow Industries",
    type: "M&A",
    status: "negotiation",
    value: "$45M",
    probability: 85,
    stage: "Due Diligence",
    owner: "Sarah Chen",
    created: "2024-01-15",
    lastActivity: "2 hours ago",
    description: "Strategic acquisition of SaaS platform for enterprise workflow automation"
  },
  {
    id: "2",
    title: "GreenEnergy Solutions IPO",
    client: "GreenEnergy Solutions", 
    type: "IPO",
    status: "active",
    value: "$78M",
    probability: 92,
    stage: "Roadshow",
    owner: "Michael Rodriguez",
    created: "2024-01-10",
    lastActivity: "1 day ago",
    description: "Initial public offering for renewable energy infrastructure company"
  },
  {
    id: "3",
    title: "HealthTech Innovations Funding",
    client: "HealthTech Innovations",
    type: "Equity Raise",
    status: "proposal",
    value: "$32M",
    probability: 75,
    stage: "Proposal",
    owner: "Emily Watson",
    created: "2024-01-08",
    lastActivity: "3 days ago",
    description: "Series B funding round for AI-powered diagnostic medical devices"
  },
  {
    id: "4",
    title: "RetailCorp Debt Financing",
    client: "RetailCorp",
    type: "Debt",
    status: "won",
    value: "$25M",
    probability: 100,
    stage: "Closed",
    owner: "David Kim",
    created: "2024-01-05",
    lastActivity: "1 week ago",
    description: "Senior debt facility for retail expansion"
  },
  {
    id: "5",
    title: "StartupXYZ Valuation",
    client: "StartupXYZ",
    type: "Advisory",
    status: "lost",
    value: "$5M",
    probability: 0,
    stage: "Lost",
    owner: "Sarah Chen",
    created: "2024-01-03",
    lastActivity: "2 weeks ago",
    description: "Business valuation for potential sale"
  }
];

const dealStages = [
  { name: "Lead", count: 12, color: "bg-dealverse-medium-gray" },
  { name: "Proposal", count: 8, color: "bg-dealverse-blue" },
  { name: "Due Diligence", count: 5, color: "bg-dealverse-amber" },
  { name: "Negotiation", count: 3, color: "bg-dealverse-green" },
  { name: "Closed", count: 15, color: "bg-dealverse-navy" }
];

export default function DealsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [selectedDeal, setSelectedDeal] = useState(deals[0]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-dealverse-green/10 text-dealverse-green border-dealverse-green/20";
      case "negotiation": return "bg-dealverse-blue/10 text-dealverse-blue border-dealverse-blue/20";
      case "proposal": return "bg-dealverse-amber/10 text-dealverse-amber border-dealverse-amber/20";
      case "won": return "bg-dealverse-green/10 text-dealverse-green border-dealverse-green/20";
      case "lost": return "bg-dealverse-coral/10 text-dealverse-coral border-dealverse-coral/20";
      default: return "bg-gray-100 text-gray-600";
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "M&A": return "bg-dealverse-navy/10 text-dealverse-navy border-dealverse-navy/20";
      case "IPO": return "bg-dealverse-blue/10 text-dealverse-blue border-dealverse-blue/20";
      case "Equity Raise": return "bg-dealverse-green/10 text-dealverse-green border-dealverse-green/20";
      case "Debt": return "bg-dealverse-amber/10 text-dealverse-amber border-dealverse-amber/20";
      case "Advisory": return "bg-dealverse-coral/10 text-dealverse-coral border-dealverse-coral/20";
      default: return "bg-gray-100 text-gray-600";
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-dealverse-navy to-dealverse-blue bg-clip-text text-transparent">
          Deal Management
        </h1>
        <p className="text-dealverse-medium-gray dark:text-dealverse-light-gray">
          Manage your investment banking deal pipeline and track progress
        </p>
      </div>

      {/* Deal Pipeline Overview */}
      <div className="grid gap-6 md:grid-cols-5">
        {dealStages.map((stage, index) => (
          <Card key={index} className="border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-dealverse-navy">{stage.name}</CardTitle>
              <div className={`w-3 h-3 rounded-full ${stage.color}`}></div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-dealverse-navy">{stage.count}</div>
              <p className="text-xs text-dealverse-medium-gray">deals</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Key Metrics */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 bg-gradient-to-br from-dealverse-green/10 to-dealverse-green/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Total Pipeline</CardTitle>
            <DollarSign className="h-4 w-4 text-dealverse-green" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">$185M</div>
            <p className="text-xs text-dealverse-medium-gray">+12% from last month</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-blue/10 to-dealverse-blue/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Active Deals</CardTitle>
            <TrendingUp className="h-4 w-4 text-dealverse-blue" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">28</div>
            <p className="text-xs text-dealverse-medium-gray">5 closing this month</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-amber/10 to-dealverse-amber/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Win Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-dealverse-amber" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">73%</div>
            <p className="text-xs text-dealverse-medium-gray">Above target (70%)</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-dealverse-navy/10 to-dealverse-navy/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-dealverse-navy">Avg Deal Size</CardTitle>
            <DollarSign className="h-4 w-4 text-dealverse-navy" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-dealverse-navy">$37M</div>
            <p className="text-xs text-dealverse-medium-gray">+8% YoY growth</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Deals List */}
        <div className="lg:col-span-2">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl font-semibold text-dealverse-navy">Deal Pipeline</CardTitle>
                  <CardDescription className="text-dealverse-medium-gray">
                    Track and manage all investment banking deals
                  </CardDescription>
                </div>
                <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90">
                  <Plus className="h-4 w-4 mr-2" />
                  New Deal
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-dealverse-medium-gray" />
                  <Input
                    placeholder="Search deals..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-full sm:w-48">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="negotiation">Negotiation</SelectItem>
                    <SelectItem value="proposal">Proposal</SelectItem>
                    <SelectItem value="won">Won</SelectItem>
                    <SelectItem value="lost">Lost</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={typeFilter} onValueChange={setTypeFilter}>
                  <SelectTrigger className="w-full sm:w-48">
                    <SelectValue placeholder="Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="M&A">M&A</SelectItem>
                    <SelectItem value="IPO">IPO</SelectItem>
                    <SelectItem value="Equity Raise">Equity Raise</SelectItem>
                    <SelectItem value="Debt">Debt</SelectItem>
                    <SelectItem value="Advisory">Advisory</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Deal Cards */}
              <div className="space-y-4">
                {deals.map((deal) => (
                  <Card 
                    key={deal.id}
                    className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                      selectedDeal.id === deal.id 
                        ? 'ring-2 ring-dealverse-blue bg-dealverse-blue/5' 
                        : 'hover:bg-dealverse-light-gray/50'
                    }`}
                    onClick={() => setSelectedDeal(deal)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="font-semibold text-dealverse-navy">{deal.title}</h3>
                            <Badge className={`text-xs ${getTypeColor(deal.type)}`}>
                              {deal.type}
                            </Badge>
                            <Badge className={`text-xs ${getStatusColor(deal.status)}`}>
                              {deal.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-dealverse-medium-gray mb-2">{deal.description}</p>
                          <div className="flex items-center space-x-4 text-xs text-dealverse-medium-gray">
                            <span className="flex items-center">
                              <Building className="h-3 w-3 mr-1" />
                              {deal.client}
                            </span>
                            <span className="flex items-center">
                              <Users className="h-3 w-3 mr-1" />
                              {deal.owner}
                            </span>
                            <span className="flex items-center">
                              <Calendar className="h-3 w-3 mr-1" />
                              {deal.lastActivity}
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-dealverse-navy">
                            {deal.value}
                          </div>
                          <div className="text-xs text-dealverse-medium-gray mb-2">
                            {deal.probability}% probability
                          </div>
                          <Progress value={deal.probability} className="h-1 w-20" />
                        </div>
                      </div>
                      <div className="flex items-center justify-between mt-3">
                        <Badge variant="outline" className="text-xs">
                          {deal.stage}
                        </Badge>
                        <div className="flex space-x-2">
                          <Button variant="ghost" size="sm">
                            <Eye className="h-3 w-3" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <FileText className="h-3 w-3" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Deal Details Sidebar */}
        <div>
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-dealverse-navy">Deal Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold text-dealverse-navy mb-2">{selectedDeal.title}</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-dealverse-medium-gray">Client:</span>
                    <span className="font-medium">{selectedDeal.client}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dealverse-medium-gray">Type:</span>
                    <Badge className={`text-xs ${getTypeColor(selectedDeal.type)}`}>
                      {selectedDeal.type}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dealverse-medium-gray">Status:</span>
                    <Badge className={`text-xs ${getStatusColor(selectedDeal.status)}`}>
                      {selectedDeal.status}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dealverse-medium-gray">Value:</span>
                    <span className="font-medium">{selectedDeal.value}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dealverse-medium-gray">Stage:</span>
                    <span className="font-medium">{selectedDeal.stage}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dealverse-medium-gray">Owner:</span>
                    <span className="font-medium">{selectedDeal.owner}</span>
                  </div>
                </div>
              </div>

              <div className="border-t pt-4">
                <h5 className="font-medium text-dealverse-navy mb-2">Probability</h5>
                <Progress value={selectedDeal.probability} className="h-2" />
                <p className="text-xs text-dealverse-medium-gray mt-1">
                  {selectedDeal.probability}% chance of closing
                </p>
              </div>

              <div className="border-t pt-4">
                <h5 className="font-medium text-dealverse-navy mb-2">Quick Actions</h5>
                <div className="space-y-2">
                  <Button className="w-full bg-dealverse-blue hover:bg-dealverse-blue/90" size="sm">
                    <Edit className="h-3 w-3 mr-2" />
                    Edit Deal
                  </Button>
                  <Button variant="outline" className="w-full" size="sm">
                    <FileText className="h-3 w-3 mr-2" />
                    View Documents
                  </Button>
                  <Button variant="outline" className="w-full" size="sm">
                    <Users className="h-3 w-3 mr-2" />
                    Manage Team
                  </Button>
                  <Button variant="outline" className="w-full" size="sm">
                    <Clock className="h-3 w-3 mr-2" />
                    Schedule Meeting
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
