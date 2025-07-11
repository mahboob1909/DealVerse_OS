"use client";

import { useMemo } from "react";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid, Line, LineChart, Area, AreaChart } from "recharts";
import { useAnalytics } from "@/hooks/use-analytics";

// Fallback data for when analytics are loading
const fallbackRevenueData = [
  {
    name: "Jan",
    revenue: 2400000,
    deals: 8,
    pipeline: 15600000,
    target: 2800000,
  },
  {
    name: "Feb",
    revenue: 1398000,
    deals: 5,
    pipeline: 12400000,
    target: 2800000,
  },
  {
    name: "Mar",
    revenue: 9800000,
    deals: 12,
    pipeline: 18900000,
    target: 2800000,
  },
  {
    name: "Apr",
    revenue: 3908000,
    deals: 9,
    pipeline: 16200000,
    target: 2800000,
  },
  {
    name: "May",
    revenue: 4800000,
    deals: 11,
    pipeline: 19800000,
    target: 2800000,
  },
  {
    name: "Jun",
    revenue: 3800000,
    deals: 7,
    pipeline: 14500000,
    target: 2800000,
  },
  {
    name: "Jul",
    revenue: 4300000,
    deals: 10,
    pipeline: 17200000,
    target: 2800000,
  },
  {
    name: "Aug",
    revenue: 5200000,
    deals: 13,
    pipeline: 21300000,
    target: 2800000,
  },
  {
    name: "Sep",
    revenue: 4100000,
    deals: 9,
    pipeline: 16800000,
    target: 2800000,
  },
  {
    name: "Oct",
    revenue: 6200000,
    deals: 15,
    pipeline: 24100000,
    target: 2800000,
  },
  {
    name: "Nov",
    revenue: 5800000,
    deals: 12,
    pipeline: 22400000,
    target: 2800000,
  },
  {
    name: "Dec",
    revenue: 7100000,
    deals: 16,
    pipeline: 26800000,
    target: 2800000,
  },
];

// Enhanced custom tooltip component for DealVerse OS with real-time data
const CustomTooltip = ({ active, payload, label, formatCurrency }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white dark:bg-dealverse-navy p-unit-2 rounded-lg shadow-xl border border-dealverse-blue/20 backdrop-blur-sm">
        <p className="text-caption font-semibold text-dealverse-navy dark:text-white mb-unit-1">
          {`${label} 2024`}
        </p>
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-caption text-dealverse-medium-gray">Revenue:</span>
            <span className="text-caption font-mono font-semibold text-dealverse-blue">
              {formatCurrency ? formatCurrency(data.revenue) : `$${(data.revenue / 1000000).toFixed(1)}M`}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-caption text-dealverse-medium-gray">Deals:</span>
            <span className="text-caption font-mono font-semibold text-dealverse-green">
              {data.deals}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-caption text-dealverse-medium-gray">Pipeline:</span>
            <span className="text-caption font-mono font-semibold text-dealverse-amber">
              {formatCurrency ? formatCurrency(data.pipeline) : `$${(data.pipeline / 1000000).toFixed(1)}M`}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-caption text-dealverse-medium-gray">vs Target:</span>
            <span className={`text-caption font-mono font-semibold ${
              data.revenue >= data.target ? 'text-dealverse-green' : 'text-dealverse-coral'
            }`}>
              {data.target > 0 ? ((data.revenue / data.target - 1) * 100).toFixed(0) : '0'}%
            </span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

interface OverviewProps {
  data?: any[];
  loading?: boolean;
}

export function Overview({ data: externalData, loading: externalLoading }: OverviewProps = {}) {
  // Use analytics hook for real-time data
  const { dashboardAnalytics, loading: analyticsLoading, formatCurrency } = useAnalytics({
    autoFetch: !externalData,
    refreshInterval: 30000 // Refresh every 30 seconds
  });

  // Transform analytics data to chart format
  const chartData = useMemo(() => {
    if (externalData) return externalData;

    if (!dashboardAnalytics?.deals?.deals_by_month) {
      return fallbackRevenueData;
    }

    return dashboardAnalytics.deals.deals_by_month.map(monthData => ({
      name: monthData.month,
      revenue: monthData.value,
      deals: monthData.count,
      pipeline: monthData.pipeline,
      target: dashboardAnalytics.deals.average_deal_size * 10, // Dynamic target based on average deal size
    }));
  }, [dashboardAnalytics, externalData]);

  const isLoading = externalLoading || analyticsLoading;

  return (
    <ResponsiveContainer width="100%" height={400}>
      <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <defs>
          <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0066ff" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#0066ff" stopOpacity={0.05} />
          </linearGradient>
          <linearGradient id="pipelineGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#00c896" stopOpacity={0.2} />
            <stop offset="100%" stopColor="#00c896" stopOpacity={0.05} />
          </linearGradient>
          <linearGradient id="targetGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ff9500" stopOpacity={0.1} />
            <stop offset="100%" stopColor="#ff9500" stopOpacity={0.05} />
          </linearGradient>
        </defs>

        <CartesianGrid
          strokeDasharray="3 3"
          stroke="#1a2332"
          opacity={0.1}
          vertical={false}
        />

        <XAxis
          dataKey="name"
          stroke="#6c757d"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          className="font-mono"
        />

        <YAxis
          stroke="#6c757d"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`}
          className="font-mono"
        />

        <Tooltip content={<CustomTooltip formatCurrency={formatCurrency} />} />

        {/* Loading overlay */}
        {isLoading && (
          <foreignObject x="0" y="0" width="100%" height="100%">
            <div className="flex items-center justify-center h-full bg-white/50 dark:bg-dealverse-navy/50">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-dealverse-blue"></div>
            </div>
          </foreignObject>
        )}

        {/* Pipeline Area */}
        <Area
          type="monotone"
          dataKey="pipeline"
          stroke="#00c896"
          strokeWidth={2}
          fill="url(#pipelineGradient)"
          fillOpacity={1}
        />

        {/* Revenue Area */}
        <Area
          type="monotone"
          dataKey="revenue"
          stroke="#0066ff"
          strokeWidth={3}
          fill="url(#revenueGradient)"
          fillOpacity={1}
        />

        {/* Target Line */}
        <Line
          type="monotone"
          dataKey="target"
          stroke="#ff9500"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}