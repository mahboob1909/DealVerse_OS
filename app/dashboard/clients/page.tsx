"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  Search, 
  Plus, 
  Building,
  MapPin,
  DollarSign,
  Calendar,
  Phone,
  Mail,
  Globe,
  Users,
  TrendingUp,
  Eye,
  Edit,
  MoreHorizontal,
  Star,
  Briefcase
} from "lucide-react";
import { useState } from "react";

// Mock data for clients
const clients = [
  {
    id: "1",
    name: "TechFlow Industries",
    industry: "Technology",
    type: "Corporate",
    location: "San Francisco, CA",
    revenue: "$180M",
    employees: "450-500",
    relationship: "Active",
    dealCount: 3,
    totalValue: "$125M",
    lastContact: "2 days ago",
    contactPerson: "John Smith",
    email: "john.smith@techflow.com",
    phone: "+1 (555) 123-4567",
    website: "www.techflow.com",
    avatar: "/avatars/techflow.png",
    initials: "TF",
    priority: "high",
    description: "Leading SaaS platform for enterprise workflow automation"
  },
  {
    id: "2",
    name: "GreenEnergy Solutions",
    industry: "Energy",
    type: "Corporate", 
    location: "Austin, TX",
    revenue: "$320M",
    employees: "800-1000",
    relationship: "Active",
    dealCount: 2,
    totalValue: "$95M",
    lastContact: "1 week ago",
    contactPerson: "Sarah Johnson",
    email: "sarah.j@greenenergy.com",
    phone: "+1 (555) 987-6543",
    website: "www.greenenergy.com",
    avatar: "/avatars/greenenergy.png",
    initials: "GE",
    priority: "high",
    description: "Renewable energy infrastructure development company"
  },
  {
    id: "3",
    name: "HealthTech Innovations",
    industry: "Healthcare",
    type: "Startup",
    location: "Boston, MA",
    revenue: "$85M",
    employees: "200-250", 
    relationship: "Prospect",
    dealCount: 1,
    totalValue: "$32M",
    lastContact: "3 days ago",
    contactPerson: "Dr. Michael Chen",
    email: "m.chen@healthtech.com",
    phone: "+1 (555) 456-7890",
    website: "www.healthtech.com",
    avatar: "/avatars/healthtech.png",
    initials: "HT",
    priority: "medium",
    description: "AI-powered diagnostic medical devices manufacturer"
  },
  {
    id: "4",
    name: "RetailCorp",
    industry: "Retail",
    type: "Corporate",
    location: "New York, NY", 
    revenue: "$2.1B",
    employees: "5000+",
    relationship: "Active",
    dealCount: 4,
    totalValue: "$180M",
    lastContact: "1 day ago",
    contactPerson: "Lisa Wang",
    email: "lisa.wang@retailcorp.com",
    phone: "+1 (555) 234-5678",
    website: "www.retailcorp.com",
    avatar: "/avatars/retailcorp.png",
    initials: "RC",
    priority: "high",
    description: "Multi-channel retail and e-commerce platform"
  },
  {
    id: "5",
    name: "StartupXYZ",
    industry: "Fintech",
    type: "Startup",
    location: "Seattle, WA",
    revenue: "$15M",
    employees: "50-100",
    relationship: "Former",
    dealCount: 1,
    totalValue: "$5M",
    lastContact: "2 months ago",
    contactPerson: "Alex Rodriguez",
    email: "alex@startupxyz.com", 
    phone: "+1 (555) 345-6789",
    website: "www.startupxyz.com",
    avatar: "/avatars/startupxyz.png",
    initials: "SX",
    priority: "low",
    description: "Digital payment solutions for small businesses"
  }
];

const clientMetrics = [
  { label: "Total Clients", value: "127", change: "+8", icon: Building },
  { label: "Active Relationships", value: "89", change: "+5", icon: Users },
  { label: "Total AUM", value: "$2.4B", change: "+12%", icon: DollarSign },
  { label: "Avg Deal Size", value: "$18.9M", change: "+3%", icon: TrendingUp }
];

export default function ClientsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [industryFilter, setIndustryFilter] = useState("all");
  const [relationshipFilter, setRelationshipFilter] = useState("all");
  const [selectedClient, setSelectedClient] = useState(clients[0]);

  const getRelationshipColor = (relationship: string) => {
    switch (relationship) {
      case "Active": return "bg-dealverse-green/10 text-dealverse-green border-dealverse-green/20";
      case "Prospect": return "bg-dealverse-blue/10 text-dealverse-blue border-dealverse-blue/20";
      case "Former": return "bg-dealverse-medium-gray/10 text-dealverse-medium-gray border-dealverse-medium-gray/20";
      default: return "bg-gray-100 text-gray-600";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "text-dealverse-coral";
      case "medium": return "text-dealverse-amber";
      case "low": return "text-dealverse-green";
      default: return "text-dealverse-medium-gray";
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "Corporate": return "bg-dealverse-navy/10 text-dealverse-navy border-dealverse-navy/20";
      case "Startup": return "bg-dealverse-blue/10 text-dealverse-blue border-dealverse-blue/20";
      case "PE/VC": return "bg-dealverse-green/10 text-dealverse-green border-dealverse-green/20";
      default: return "bg-gray-100 text-gray-600";
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-dealverse-navy to-dealverse-blue bg-clip-text text-transparent">
          Client Management
        </h1>
        <p className="text-dealverse-medium-gray dark:text-dealverse-light-gray">
          Manage client relationships and track engagement across all deals
        </p>
      </div>

      {/* Client Metrics */}
      <div className="grid gap-6 md:grid-cols-4">
        {clientMetrics.map((metric, index) => (
          <Card key={index} className="border-0 bg-gradient-to-br from-dealverse-blue/10 to-dealverse-blue/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-dealverse-navy">{metric.label}</CardTitle>
              <metric.icon className="h-4 w-4 text-dealverse-blue" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-dealverse-navy">{metric.value}</div>
              <p className="text-xs text-dealverse-green">
                <TrendingUp className="h-3 w-3 inline mr-1" />
                {metric.change} from last month
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Clients List */}
        <div className="lg:col-span-2">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl font-semibold text-dealverse-navy">Client Portfolio</CardTitle>
                  <CardDescription className="text-dealverse-medium-gray">
                    Manage and track all client relationships
                  </CardDescription>
                </div>
                <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Client
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-dealverse-medium-gray" />
                  <Input
                    placeholder="Search clients..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={industryFilter} onValueChange={setIndustryFilter}>
                  <SelectTrigger className="w-full sm:w-48">
                    <SelectValue placeholder="Industry" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Industries</SelectItem>
                    <SelectItem value="technology">Technology</SelectItem>
                    <SelectItem value="healthcare">Healthcare</SelectItem>
                    <SelectItem value="energy">Energy</SelectItem>
                    <SelectItem value="retail">Retail</SelectItem>
                    <SelectItem value="fintech">Fintech</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={relationshipFilter} onValueChange={setRelationshipFilter}>
                  <SelectTrigger className="w-full sm:w-48">
                    <SelectValue placeholder="Relationship" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Relationships</SelectItem>
                    <SelectItem value="Active">Active</SelectItem>
                    <SelectItem value="Prospect">Prospect</SelectItem>
                    <SelectItem value="Former">Former</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Client Cards */}
              <div className="space-y-4">
                {clients.map((client) => (
                  <Card 
                    key={client.id}
                    className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                      selectedClient.id === client.id 
                        ? 'ring-2 ring-dealverse-blue bg-dealverse-blue/5' 
                        : 'hover:bg-dealverse-light-gray/50'
                    }`}
                    onClick={() => setSelectedClient(client)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start space-x-4">
                        <Avatar className="h-12 w-12">
                          <AvatarImage src={client.avatar} alt={client.name} />
                          <AvatarFallback className="bg-gradient-to-br from-dealverse-blue to-dealverse-green text-white font-semibold">
                            {client.initials}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="font-semibold text-dealverse-navy">{client.name}</h3>
                            <Badge className={`text-xs ${getTypeColor(client.type)}`}>
                              {client.type}
                            </Badge>
                            <Badge className={`text-xs ${getRelationshipColor(client.relationship)}`}>
                              {client.relationship}
                            </Badge>
                            <Star className={`h-4 w-4 ${getPriorityColor(client.priority)}`} />
                          </div>
                          <p className="text-sm text-dealverse-medium-gray mb-2">{client.description}</p>
                          <div className="flex items-center space-x-4 text-xs text-dealverse-medium-gray">
                            <span className="flex items-center">
                              <Briefcase className="h-3 w-3 mr-1" />
                              {client.industry}
                            </span>
                            <span className="flex items-center">
                              <MapPin className="h-3 w-3 mr-1" />
                              {client.location}
                            </span>
                            <span className="flex items-center">
                              <DollarSign className="h-3 w-3 mr-1" />
                              {client.revenue} revenue
                            </span>
                            <span className="flex items-center">
                              <Users className="h-3 w-3 mr-1" />
                              {client.employees}
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-dealverse-navy">
                            {client.totalValue}
                          </div>
                          <div className="text-xs text-dealverse-medium-gray">
                            {client.dealCount} deals
                          </div>
                          <div className="text-xs text-dealverse-medium-gray">
                            Last contact: {client.lastContact}
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
                          <Mail className="h-3 w-3" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Phone className="h-3 w-3" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="h-3 w-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Client Details Sidebar */}
        <div>
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-dealverse-navy">Client Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-3">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={selectedClient.avatar} alt={selectedClient.name} />
                  <AvatarFallback className="bg-gradient-to-br from-dealverse-blue to-dealverse-green text-white font-semibold">
                    {selectedClient.initials}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h4 className="font-semibold text-dealverse-navy">{selectedClient.name}</h4>
                  <p className="text-sm text-dealverse-medium-gray">{selectedClient.industry}</p>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-dealverse-medium-gray">Type:</span>
                  <Badge className={`text-xs ${getTypeColor(selectedClient.type)}`}>
                    {selectedClient.type}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-dealverse-medium-gray">Relationship:</span>
                  <Badge className={`text-xs ${getRelationshipColor(selectedClient.relationship)}`}>
                    {selectedClient.relationship}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-dealverse-medium-gray">Revenue:</span>
                  <span className="font-medium">{selectedClient.revenue}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dealverse-medium-gray">Employees:</span>
                  <span className="font-medium">{selectedClient.employees}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dealverse-medium-gray">Location:</span>
                  <span className="font-medium">{selectedClient.location}</span>
                </div>
              </div>

              <div className="border-t pt-4">
                <h5 className="font-medium text-dealverse-navy mb-2">Contact Information</h5>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center space-x-2">
                    <Users className="h-3 w-3 text-dealverse-medium-gray" />
                    <span>{selectedClient.contactPerson}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Mail className="h-3 w-3 text-dealverse-medium-gray" />
                    <span className="text-dealverse-blue">{selectedClient.email}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Phone className="h-3 w-3 text-dealverse-medium-gray" />
                    <span>{selectedClient.phone}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Globe className="h-3 w-3 text-dealverse-medium-gray" />
                    <span className="text-dealverse-blue">{selectedClient.website}</span>
                  </div>
                </div>
              </div>

              <div className="border-t pt-4">
                <h5 className="font-medium text-dealverse-navy mb-2">Deal Summary</h5>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-dealverse-medium-gray">Total Deals:</span>
                    <span className="font-medium">{selectedClient.dealCount}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dealverse-medium-gray">Total Value:</span>
                    <span className="font-medium text-dealverse-green">{selectedClient.totalValue}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dealverse-medium-gray">Last Contact:</span>
                    <span className="font-medium">{selectedClient.lastContact}</span>
                  </div>
                </div>
              </div>

              <div className="border-t pt-4">
                <h5 className="font-medium text-dealverse-navy mb-2">Quick Actions</h5>
                <div className="space-y-2">
                  <Button className="w-full bg-dealverse-blue hover:bg-dealverse-blue/90" size="sm">
                    <Mail className="h-3 w-3 mr-2" />
                    Send Email
                  </Button>
                  <Button variant="outline" className="w-full" size="sm">
                    <Phone className="h-3 w-3 mr-2" />
                    Schedule Call
                  </Button>
                  <Button variant="outline" className="w-full" size="sm">
                    <Calendar className="h-3 w-3 mr-2" />
                    Book Meeting
                  </Button>
                  <Button variant="outline" className="w-full" size="sm">
                    <Edit className="h-3 w-3 mr-2" />
                    Edit Profile
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
