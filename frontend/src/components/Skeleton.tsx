import React from "react";

export function Skeleton({
  className = "",
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`atelier-skeleton rounded-xl bg-[var(--skeleton-bg)] ${className}`}
      {...props}
    />
  );
}

export function ResultCardSkeleton() {
  return (
    <div className="atelier-card p-5 sm:p-6 flex flex-col sm:flex-row gap-5 items-start">
      <Skeleton className="w-full sm:w-36 h-48 sm:h-36 rounded-2xl flex-shrink-0" />
      <div className="flex-1 w-full space-y-3">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <Skeleton className="w-8 h-8 rounded-full" />
            <Skeleton className="w-40 h-5 rounded-md" />
          </div>
          <Skeleton className="w-20 h-7 rounded-xl" />
        </div>
        <Skeleton className="w-28 h-3.5 rounded" />
        <Skeleton className="w-36 h-6 rounded-full" />
        <div className="space-y-1.5 pt-2">
          <div className="flex justify-between">
            <Skeleton className="w-24 h-3 rounded" />
            <Skeleton className="w-12 h-3 rounded" />
          </div>
          <Skeleton className="w-full h-2 rounded-full" />
        </div>
      </div>
    </div>
  );
}
