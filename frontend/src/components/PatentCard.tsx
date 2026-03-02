"use client";

import type { SimilarPatent } from "@/types/patent";
import { cn } from "@/lib/utils";

interface PatentCardProps {
  patent: SimilarPatent;
  className?: string;
}

function getScoreColor(score: number) {
  if (score >= 0.8) return "bg-error";
  if (score >= 0.6) return "bg-warning";
  return "bg-success";
}

export function PatentCard({ patent, className }: PatentCardProps) {
  const scorePercent = Math.round(patent.similarity_score * 100);
  const isHighSimilarity = patent.similarity_score >= 0.8;

  return (
    <div
      className={cn(
        "rounded-card border bg-bg-surface p-5 shadow-card",
        isHighSimilarity ? "border-warning-border" : "border-border",
        className
      )}
    >
      {isHighSimilarity && (
        <div className="mb-3 inline-flex rounded-full bg-warning/10 text-warning text-caption px-2 py-1">
          유사도 경고
        </div>
      )}
      <h3 className="text-body-l text-text-primary font-medium mb-2 line-clamp-2">
        {patent.title}
      </h3>
      {patent.abstract && (
        <p className="text-body-m text-text-secondary line-clamp-2 mb-4">
          {patent.abstract}
        </p>
      )}
      <div className="space-y-1">
        <div className="flex justify-between text-caption text-text-muted">
          <span>유사도</span>
          <span className="font-mono text-xl font-extrabold">{scorePercent}%</span>
        </div>
        <div className="h-2 w-full rounded-full bg-bg-elevated overflow-hidden">
          <div
            className={cn("h-full rounded-full transition-all", getScoreColor(patent.similarity_score))}
            style={{ width: `${scorePercent}%` }}
          />
        </div>
      </div>
      {patent.application_number && (
        <p className="text-caption text-text-muted mt-2 font-mono">
          {patent.application_number}
        </p>
      )}
    </div>
  );
}
