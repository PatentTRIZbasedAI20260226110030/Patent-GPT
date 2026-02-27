"use client";

import type { TrizPrinciple } from "@/types/patent";
import { cn } from "@/lib/utils";

interface TrizCardProps {
  principle: TrizPrinciple;
  className?: string;
}

export function TrizCard({ principle, className }: TrizCardProps) {
  return (
    <div
      className={cn(
        "rounded-card border border-border bg-bg-surface p-5 pl-6 border-l-4 border-l-primary",
        className
      )}
    >
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold text-body-m shrink-0">
          {principle.number}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-h3 text-text-primary mb-2">
            {principle.name_ko}
          </h3>
          <p className="text-body-m text-text-secondary line-clamp-3">
            {principle.description}
          </p>
        </div>
      </div>
    </div>
  );
}
