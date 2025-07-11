"use client"

import * as React from "react"
import { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown, MoreHorizontal, Eye, Edit, Trash2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { DataTable } from "@/components/ui/data-table"

export type Deal = {
  id: string
  dealName: string
  client: string
  dealType: string
  dealSize: string
  stage: "prospect" | "initial-contact" | "due-diligence" | "negotiation" | "closing" | "closed" | "cancelled"
  probability: number
  expectedClose: string
  leadBanker: string
  lastActivity: string
  status: "active" | "pending" | "closed" | "cancelled"
}

const getStatusBadge = (status: Deal["status"]) => {
  switch (status) {
    case "active":
      return <Badge variant="deal-active">Active</Badge>
    case "pending":
      return <Badge variant="deal-pending">Pending</Badge>
    case "closed":
      return <Badge variant="deal-closed">Closed</Badge>
    case "cancelled":
      return <Badge variant="deal-cancelled">Cancelled</Badge>
    default:
      return <Badge variant="outline">{status}</Badge>
  }
}

const getStageBadge = (stage: Deal["stage"]) => {
  const stageConfig = {
    "prospect": { label: "Prospect", variant: "outline" as const },
    "initial-contact": { label: "Initial Contact", variant: "info" as const },
    "due-diligence": { label: "Due Diligence", variant: "warning" as const },
    "negotiation": { label: "Negotiation", variant: "warning" as const },
    "closing": { label: "Closing", variant: "success" as const },
    "closed": { label: "Closed", variant: "success" as const },
    "cancelled": { label: "Cancelled", variant: "error" as const },
  }
  
  const config = stageConfig[stage]
  return <Badge variant={config.variant}>{config.label}</Badge>
}

const getProbabilityColor = (probability: number) => {
  if (probability >= 80) return "text-dealverse-green"
  if (probability >= 60) return "text-dealverse-amber"
  if (probability >= 40) return "text-dealverse-blue"
  return "text-dealverse-coral"
}

export const columns: ColumnDef<Deal>[] = [
  {
    accessorKey: "dealName",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="hover:bg-dealverse-blue/10"
        >
          Deal Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => (
      <div className="font-medium text-dealverse-navy dark:text-white">
        {row.getValue("dealName")}
      </div>
    ),
  },
  {
    accessorKey: "client",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="hover:bg-dealverse-blue/10"
        >
          Client
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => (
      <div className="text-dealverse-medium-gray dark:text-dealverse-light-gray">
        {row.getValue("client")}
      </div>
    ),
  },
  {
    accessorKey: "dealType",
    header: "Deal Type",
    cell: ({ row }) => (
      <div className="text-caption text-dealverse-medium-gray">
        {row.getValue("dealType")}
      </div>
    ),
  },
  {
    accessorKey: "dealSize",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="hover:bg-dealverse-blue/10"
        >
          Deal Size
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => (
      <div className="font-mono font-semibold text-dealverse-navy dark:text-white">
        {row.getValue("dealSize")}
      </div>
    ),
  },
  {
    accessorKey: "stage",
    header: "Stage",
    cell: ({ row }) => getStageBadge(row.getValue("stage")),
  },
  {
    accessorKey: "probability",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="hover:bg-dealverse-blue/10"
        >
          Probability
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => {
      const probability = row.getValue("probability") as number
      return (
        <div className={`font-mono font-semibold ${getProbabilityColor(probability)}`}>
          {probability}%
        </div>
      )
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => getStatusBadge(row.getValue("status")),
  },
  {
    accessorKey: "expectedClose",
    header: "Expected Close",
    cell: ({ row }) => (
      <div className="text-caption text-dealverse-medium-gray">
        {row.getValue("expectedClose")}
      </div>
    ),
  },
  {
    accessorKey: "leadBanker",
    header: "Lead Banker",
    cell: ({ row }) => (
      <div className="text-caption text-dealverse-medium-gray">
        {row.getValue("leadBanker")}
      </div>
    ),
  },
  {
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      const deal = row.original

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0 hover:bg-dealverse-blue/10">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuItem className="hover:bg-dealverse-blue/10">
              <Eye className="mr-2 h-4 w-4" />
              View Details
            </DropdownMenuItem>
            <DropdownMenuItem className="hover:bg-dealverse-blue/10">
              <Edit className="mr-2 h-4 w-4" />
              Edit Deal
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="hover:bg-dealverse-coral/10 text-dealverse-coral">
              <Trash2 className="mr-2 h-4 w-4" />
              Delete Deal
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]

// Mock data for the pipeline
const mockDeals: Deal[] = [
  {
    id: "1",
    dealName: "TechFlow Acquisition",
    client: "TechFlow Industries",
    dealType: "M&A",
    dealSize: "$45M",
    stage: "due-diligence",
    probability: 75,
    expectedClose: "Q1 2024",
    leadBanker: "Sarah Chen",
    lastActivity: "2 hours ago",
    status: "active",
  },
  {
    id: "2",
    dealName: "GreenEnergy IPO",
    client: "GreenEnergy Solutions",
    dealType: "IPO",
    dealSize: "$120M",
    stage: "negotiation",
    probability: 85,
    expectedClose: "Q2 2024",
    leadBanker: "Michael Rodriguez",
    lastActivity: "1 day ago",
    status: "active",
  },
  {
    id: "3",
    dealName: "HealthTech Series C",
    client: "HealthTech Innovations",
    dealType: "Private Equity",
    dealSize: "$32M",
    stage: "closing",
    probability: 90,
    expectedClose: "Dec 2023",
    leadBanker: "Emily Watson",
    lastActivity: "3 hours ago",
    status: "active",
  },
  {
    id: "4",
    dealName: "RetailCorp Merger",
    client: "RetailCorp",
    dealType: "M&A",
    dealSize: "$78M",
    stage: "initial-contact",
    probability: 45,
    expectedClose: "Q3 2024",
    leadBanker: "David Kim",
    lastActivity: "1 week ago",
    status: "pending",
  },
  {
    id: "5",
    dealName: "FinTech Acquisition",
    client: "FinTech Solutions",
    dealType: "M&A",
    dealSize: "$95M",
    stage: "closed",
    probability: 100,
    expectedClose: "Nov 2023",
    leadBanker: "Lisa Thompson",
    lastActivity: "2 weeks ago",
    status: "closed",
  },
]

export function PipelineStatusTable() {
  return (
    <div className="space-y-unit-2">
      <DataTable 
        columns={columns} 
        data={mockDeals} 
        searchKey="dealName"
        searchPlaceholder="Search deals..."
      />
    </div>
  )
}
