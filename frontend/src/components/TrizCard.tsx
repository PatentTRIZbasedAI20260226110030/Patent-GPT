"use client";

import type { TrizPrinciple } from "@/types/patent";
import { cn } from "@/lib/utils";

interface TrizCardProps {
  principle: TrizPrinciple;
  className?: string;
}

export function TrizCard({ principle, className }: TrizCardProps) {
  const matchingPercent =
    typeof principle.matching_score === "number"
      ? Math.round(principle.matching_score * 100)
      : null;

  return (
    <div
      className={cn(
        "rounded-card border border-border bg-bg-surface p-5 shadow-card transition-shadow hover:shadow-md",
        className
      )}
    >
      <div className="flex items-start gap-4">
        <div className="min-w-[44px] h-[44px] rounded-[10px] bg-primary-bg flex items-center justify-center text-primary font-mono font-extrabold text-lg shrink-0">
          {principle.number}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-3 mb-2">
            <h3 className="text-h3 text-text-primary">{principle.name_ko}</h3>
            {matchingPercent !== null && (
              <span className="rounded-full bg-primary/10 text-primary text-caption px-2 py-1 shrink-0">
                {matchingPercent}%
              </span>
            )}
          </div>
          {principle.name_en && (
            <p className="text-caption text-text-muted mb-2">{principle.name_en}</p>
          )}
          <p className="text-body-m text-text-secondary line-clamp-3">
            {principle.description}
          </p>
        </div>
      </div>
    </div>
  );
}
