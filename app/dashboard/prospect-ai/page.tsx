"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Search,
  Target,
  Brain,
  DollarSign,
  RefreshCw,
  MapPin,
  Clock,
  Zap,
  Award,
  Star
} from "lucide-react";
import { useState } from "react";
import { useToast } from '@/hooks/use-toast';

export default function ProspectAIPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [industryFilter, setIndustryFilter] = useState("all");
  const [dealSizeFilter, setDealSizeFilter] = useState("all");
  const [stageFilter, setStageFilter] = useState("all");
  const [scoreFilter, setScoreFilter] = useState("all");
  
  const { toast } = useToast();

  // Mock data for now
  const prospects = [
    {
      id: 1,
      company_name: "TechCorp Inc",
      industry: "Technology",
      location: "San Francisco, CA",
      deal_size: "$25M",
      ai_score: 92,
      confidence_level: "High",
      stage: "Due Diligence",
      description: "Leading AI software company",
      last_activity: "2 days ago"
    },
    {
      id: 2,
      company_name: "HealthTech Solutions",
      industry: "Healthcare",
      location: "Boston, MA",
      deal_size: "$15M",
      ai_score: 87,
      confidence_level: "High",
      stage: "Initial Contact",
      description: "Medical device manufacturer",
      last_activity: "1 week ago"
    }
  ];

  const statistics = {
    total_prospects: 45,
    high_score_prospects: 12,
    average_score: 78.5,
    ai_accuracy: 94.2
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-green-600";
    if (score >= 70) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBg = (score: number) => {
    if (score >= 85) return "bg-green-50 border-green-200";
    if (score >= 70) return "bg-yellow-50 border-yellow-200";
    return "bg-red-50 border-red-200";
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex flex-col space-y-2">
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-900 to-blue-600 bg-clip-text text-transparent">
              Prospect AI
            </h1>
            <p className="text-gray-600">
              AI-powered deal sourcing and opportunity management
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button size="sm">
              <Zap className="h-4 w-4 mr-2" />
              Analyze New
            </Button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search prospects by company name, industry, or location..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex gap-2">
            <Select value={industryFilter} onValueChange={setIndustryFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Industry" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Industries</SelectItem>
                <SelectItem value="Technology">Technology</SelectItem>
                <SelectItem value="Healthcare">Healthcare</SelectItem>
                <SelectItem value="Energy">Energy</SelectItem>
                <SelectItem value="Finance">Finance</SelectItem>
              </SelectContent>
            </Select>
            <Select value={stageFilter} onValueChange={setStageFilter}>
              <SelectTrigger className="w-[130px]">
                <SelectValue placeholder="Stage" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Stages</SelectItem>
                <SelectItem value="Initial Contact">Initial Contact</SelectItem>
                <SelectItem value="Due Diligence">Due Diligence</SelectItem>
                <SelectItem value="Proposal">Proposal</SelectItem>
                <SelectItem value="Negotiation">Negotiation</SelectItem>
                <SelectItem value="Closing">Closing</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 bg-gradient-to-br from-blue-50 to-blue-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-900">Active Prospects</CardTitle>
            <Target className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900">{statistics.total_prospects}</div>
            <p className="text-xs text-gray-600">Total opportunities</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-green-50 to-green-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-900">High-Score Deals</CardTitle>
            <Brain className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900">{statistics.high_score_prospects}</div>
            <p className="text-xs text-gray-600">Score 85+</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-yellow-50 to-yellow-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-yellow-900">Average Score</CardTitle>
            <Award className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-900">{statistics.average_score}</div>
            <p className="text-xs text-gray-600">AI scoring average</p>
          </CardContent>
        </Card>

        <Card className="border-0 bg-gradient-to-br from-purple-50 to-purple-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-900">AI Accuracy</CardTitle>
            <Star className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900">{statistics.ai_accuracy}%</div>
            <p className="text-xs text-gray-600">Prediction rate</p>
          </CardContent>
        </Card>
      </div>

      {/* Prospects List */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="text-xl font-semibold text-gray-900">AI-Scored Prospects</CardTitle>
          <CardDescription className="text-gray-600">
            {prospects.length} opportunities ranked by AI confidence and deal potential
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {prospects.map((prospect) => (
              <Card
                key={prospect.id}
                className="cursor-pointer transition-all duration-200 hover:shadow-md hover:bg-gray-50"
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="font-semibold text-gray-900">{prospect.company_name}</h3>
                        <Badge variant="outline" className="text-xs">
                          {prospect.industry}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {prospect.stage}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{prospect.description}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <div className="flex items-center space-x-1">
                          <MapPin className="h-3 w-3" />
                          <span>{prospect.location}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <DollarSign className="h-3 w-3" />
                          <span>{prospect.deal_size}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="h-3 w-3" />
                          <span>{prospect.last_activity}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getScoreColor(prospect.ai_score)}`}>
                        {prospect.ai_score}
                      </div>
                      <div className="text-xs text-gray-500">{prospect.confidence_level}</div>
                      <div className={`mt-2 px-2 py-1 rounded-full text-xs border ${getScoreBg(prospect.ai_score)}`}>
                        AI Score
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
