"use client";

import React, { useMemo, useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RecentDealsSkeleton } from "./recent-deals-skeleton";
import { useRecentDeals } from "@/hooks/use-recent-deals";
import { Deal } from "@/hooks/use-deals";
import { Search, Filter } from "lucide-react";

interface RecentDealsProps {
  deals?: Deal[];
  isLoading?: boolean;
  showFilters?: boolean;
  showPagination?: boolean;
  itemsPerPage?: number;
  onDealClick?: (deal: Deal) => void;
  useHook?: boolean; // Whether to use the data hook or external data
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const defaultDeals: Deal[] = [
  {
    id: "1",
    clientName: "Acme Corp",
    projectTitle: "Website Redesign",
    status: "negotiation",
    avatarUrl: "/avatars/01.png",
    fallbackInitials: "AC",
    createdAt: new Date("2024-01-15"),
    value: 15000,
  },
  {
    id: "2",
    clientName: "TechTron Inc.",
    projectTitle: "Mobile App Development",
    status: "proposal",
    avatarUrl: "/avatars/02.png",
    fallbackInitials: "TT",
    createdAt: new Date("2024-01-10"),
    value: 25000,
  },
  {
    id: "3",
    clientName: "Global Solutions",
    projectTitle: "Consulting Services",
    status: "follow-up",
    avatarUrl: "/avatars/03.png",
    fallbackInitials: "GS",
    createdAt: new Date("2024-01-08"),
    value: 8000,
  },
  {
    id: "4",
    clientName: "StartupXYZ",
    projectTitle: "Brand Identity",
    status: "won",
    avatarUrl: "/avatars/04.png",
    fallbackInitials: "SX",
    createdAt: new Date("2024-01-05"),
    value: 12000,
  },
  {
    id: "5",
    clientName: "Enterprise Co",
    projectTitle: "System Integration",
    status: "lost",
    avatarUrl: "/avatars/05.png",
    fallbackInitials: "EC",
    createdAt: new Date("2024-01-03"),
    value: 50000,
  },
];

const getStatusStyles = (status: Deal["status"]) => {
  const styles = {
    negotiation: "bg-gradient-to-r from-green-50 to-green-100 dark:from-green-950/50 dark:to-green-900/50 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800",
    proposal: "bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-950/50 dark:to-blue-900/50 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800",
    "follow-up": "bg-gradient-to-r from-yellow-50 to-yellow-100 dark:from-yellow-950/50 dark:to-yellow-900/50 text-yellow-700 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-800",
    won: "bg-gradient-to-r from-emerald-50 to-emerald-100 dark:from-emerald-950/50 dark:to-emerald-900/50 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800",
    lost: "bg-gradient-to-r from-red-50 to-red-100 dark:from-red-950/50 dark:to-red-900/50 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800",
  };
  return styles[status];
};

const getStatusLabel = (status: Deal["status"]) => {
  const labels = {
    negotiation: "Negotiation",
    proposal: "Proposal",
    "follow-up": "Follow-up",
    won: "Won",
    lost: "Lost",
  };
  return labels[status];
};

// Individual deal item component
interface DealItemProps {
  deal: Deal;
  onClick?: (deal: Deal) => void;
}

const DealItem = React.memo(function DealItem({ deal, onClick }: DealItemProps) {
  const handleClick = () => {
    if (onClick) {
      onClick(deal);
    }
  };

  return (
    <div
      className={`group flex items-center p-3 rounded-xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900/50 hover:shadow-md hover:border-slate-200 dark:hover:border-slate-700 transition-all duration-200 ${onClick ? 'cursor-pointer hover:scale-[1.02]' : ''}`}
      onClick={handleClick}
    >
      <div className="relative">
        <Avatar className="h-11 w-11 ring-2 ring-slate-100 dark:ring-slate-800">
          <AvatarImage
            src={deal.avatarUrl}
            alt={`${deal.clientName} avatar`}
          />
          <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
            {deal.fallbackInitials}
          </AvatarFallback>
        </Avatar>
        <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-white dark:bg-slate-900 rounded-full flex items-center justify-center">
          <div className={`w-2 h-2 rounded-full ${
            deal.status === 'won' ? 'bg-green-500' :
            deal.status === 'negotiation' ? 'bg-blue-500' :
            deal.status === 'proposal' ? 'bg-yellow-500' :
            deal.status === 'follow-up' ? 'bg-orange-500' :
            'bg-red-500'
          }`}></div>
        </div>
      </div>

      <div className="ml-4 space-y-1 flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
            {deal.clientName}
          </p>
          {deal.value && (
            <p className="text-sm font-bold text-slate-900 dark:text-slate-100 bg-slate-50 dark:bg-slate-800 px-2 py-1 rounded-md">
              ${deal.value.toLocaleString()}
            </p>
          )}
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-400 truncate">
          {deal.projectTitle}
        </p>
        {deal.createdAt && (
          <p className="text-xs text-slate-500 dark:text-slate-500">
            {deal.createdAt.toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            })}
          </p>
        )}
      </div>

      <div className="ml-4 flex flex-col items-end space-y-2">
        <span
          className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold shadow-sm ${getStatusStyles(deal.status)}`}
        >
          {getStatusLabel(deal.status)}
        </span>
      </div>
    </div>
  );
});

// Memoized component for performance optimization
export const RecentDeals = React.memo(function RecentDeals({
  deals: externalDeals = defaultDeals,
  isLoading: externalIsLoading = false,
  showFilters = true,
  showPagination = true,
  itemsPerPage = 5,
  onDealClick,
  useHook = false,
  autoRefresh = false,
  refreshInterval = 30000
}: RecentDealsProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [currentPage, setCurrentPage] = useState(1);

  // Use hook data if specified, otherwise use external data
  const hookData = useRecentDeals(
    useHook ? {
      limit: itemsPerPage * 3, // Load more data for filtering
      autoRefresh,
      refreshInterval
    } : undefined
  );

  const deals = useHook ? hookData.deals : externalDeals;
  const isLoading = useHook ? hookData.isLoading : externalIsLoading;

  // Memoized filtered and paginated deals
  const { filteredDeals, totalPages, paginatedDeals } = useMemo(() => {
    if (!deals) return { filteredDeals: [], totalPages: 0, paginatedDeals: [] };

    // Filter deals based on search term and status
    const filtered = deals.filter((deal) => {
      const matchesSearch =
        deal.clientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        deal.projectTitle.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus = statusFilter === "all" || deal.status === statusFilter;

      return matchesSearch && matchesStatus;
    });

    // Calculate pagination
    const totalPages = Math.ceil(filtered.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginated = filtered.slice(startIndex, startIndex + itemsPerPage);

    return { filteredDeals: filtered, totalPages, paginatedDeals: paginated };
  }, [deals, searchTerm, statusFilter, currentPage, itemsPerPage]);

  // Reset to first page when filters change
  React.useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, statusFilter]);

  if (isLoading) {
    return <RecentDealsSkeleton count={itemsPerPage} />;
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      {showFilters && (
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search deals..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="negotiation">Negotiation</SelectItem>
              <SelectItem value="proposal">Proposal</SelectItem>
              <SelectItem value="follow-up">Follow-up</SelectItem>
              <SelectItem value="won">Won</SelectItem>
              <SelectItem value="lost">Lost</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Deals List */}
      {paginatedDeals.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-sm text-muted-foreground">
            {filteredDeals.length === 0 && (searchTerm || statusFilter !== "all")
              ? "No deals match your filters."
              : "No recent deals found."}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {paginatedDeals.map((deal) => (
            <DealItem
              key={deal.id}
              deal={deal}
              onClick={onDealClick}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {showPagination && totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {((currentPage - 1) * itemsPerPage) + 1} to{" "}
            {Math.min(currentPage * itemsPerPage, filteredDeals.length)} of{" "}
            {filteredDeals.length} deals
          </p>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <span className="text-sm">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
});