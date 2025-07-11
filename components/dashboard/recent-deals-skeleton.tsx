import { Skeleton } from "@/components/ui/skeleton";

interface RecentDealsSkeletonProps {
  count?: number;
}

export function RecentDealsSkeleton({ count = 3 }: RecentDealsSkeletonProps) {
  return (
    <div className="space-y-8">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="flex items-center">
          {/* Avatar skeleton */}
          <Skeleton className="h-9 w-9 rounded-full" />
          
          {/* Content skeleton */}
          <div className="ml-4 space-y-1 flex-1">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-3 w-32" />
          </div>
          
          {/* Status badge skeleton */}
          <div className="ml-auto">
            <Skeleton className="h-6 w-20 rounded-md" />
          </div>
        </div>
      ))}
    </div>
  );
}
