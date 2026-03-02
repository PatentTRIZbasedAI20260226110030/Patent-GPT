"use client";

import { useState } from "react";
import type { PatentGenerateResponse } from "@/types/patent";
import { TrizCard } from "./TrizCard";
import { PatentCard } from "./PatentCard";
import { DownloadButton } from "./DownloadButton";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type TabId = "draft" | "triz" | "patents";

interface ResultPanelProps {
  data: PatentGenerateResponse;
  onRegenerate: () => void;
}

export function ResultPanel({ data, onRegenerate }: ResultPanelProps) {
  const [activeTab, setActiveTab] = useState<TabId>("draft");

  const tabs: { id: TabId; label: string }[] = [
    { id: "draft", label: "특허 초안" },
    { id: "triz", label: "TRIZ 원리" },
    { id: "patents", label: "선행특허" },
  ];

  const lastTrace =
    data.reasoning_trace?.length > 0
      ? data.reasoning_trace[data.reasoning_trace.length - 1]
      : null;
  const highSimilarityCount = data.similar_patents.filter(
    (patent) => patent.similarity_score >= (data.threshold ?? 0.8)
  ).length;
  const noveltyPercent =
    typeof data.novelty_score === "number"
      ? Math.round(data.novelty_score * 100)
      : null;
  const thresholdPercent =
    typeof data.threshold === "number" ? Math.round(data.threshold * 100) : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-h1 text-text-primary mb-2">
          {data.patent_draft.title}
        </h1>
        {lastTrace && (
          <p className="text-body-m text-text-muted">{lastTrace}</p>
        )}
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-card border border-border bg-bg-surface p-4 shadow-card">
          <p className="text-caption text-text-muted mb-1">신규성 점수</p>
          <p className="text-h3 text-text-primary font-mono">
            {noveltyPercent !== null ? `${noveltyPercent}%` : "-"}
          </p>
        </div>
        <div className="rounded-card border border-border bg-bg-surface p-4 shadow-card">
          <p className="text-caption text-text-muted mb-1">임계값</p>
          <p className="text-h3 text-text-primary font-mono">
            {thresholdPercent !== null ? `${thresholdPercent}%` : "-"}
          </p>
        </div>
        <div
          className={cn(
            "rounded-card border p-4 shadow-card",
            highSimilarityCount > 0
              ? "border-warning bg-warning/5"
              : "border-success bg-success/5"
          )}
        >
          <p className="text-caption text-text-muted mb-1">유사도 경고 건수</p>
          <p
            className={cn(
              "text-h3",
              highSimilarityCount > 0 ? "text-warning" : "text-success"
            )}
          >
            {highSimilarityCount}건
          </p>
        </div>
      </div>

      {data.evaluation && (
        <div className="rounded-card border border-border bg-bg-surface p-5 shadow-card">
          <h2 className="text-h3 text-text-primary mb-3">품질 평가 (RAGAS)</h2>
          <div className="grid gap-3 sm:grid-cols-3">
            {[
              { label: "충실도", value: data.evaluation.faithfulness },
              { label: "답변 관련성", value: data.evaluation.answer_relevancy },
              { label: "컨텍스트 재현율", value: data.evaluation.context_recall },
            ].map((m) => (
              <div key={m.label} className="text-center">
                <p className="text-caption text-text-muted mb-1">{m.label}</p>
                <p className="text-h3 text-text-primary font-mono">
                  {Math.round(m.value * 100)}%
                </p>
              </div>
            ))}
          </div>
          <p
            className={cn(
              "text-body-s mt-3 text-center font-medium",
              data.evaluation.passed ? "text-success" : "text-warning"
            )}
          >
            {data.evaluation.passed ? "임계값 통과" : "임계값 미달"}
          </p>
        </div>
      )}

      <div className="border-b border-border">
        <nav className="flex gap-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "pb-3 text-body-m font-medium transition-colors border-b-2 -mb-px",
                activeTab === tab.id
                  ? "border-primary text-primary"
                  : "border-transparent text-text-secondary hover:text-text-primary"
              )}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="min-h-[200px]">
        {activeTab === "draft" && (
          <div className="space-y-6">
            <section>
              <h2 className="text-h3 text-text-primary mb-2">요약</h2>
              <p className="text-body-m text-text-secondary leading-relaxed whitespace-pre-line">
                {data.patent_draft.abstract}
              </p>
            </section>
            <section>
              <h2 className="text-h3 text-text-primary mb-2">기술적 배경</h2>
              <p className="text-body-m text-text-secondary leading-relaxed whitespace-pre-line">
                {data.patent_draft.background}
              </p>
            </section>
            <section>
              <h2 className="text-h3 text-text-primary mb-2">해결 과제</h2>
              <p className="text-body-m text-text-secondary leading-relaxed whitespace-pre-line">
                {data.patent_draft.problem_statement}
              </p>
            </section>
            <section>
              <h2 className="text-h3 text-text-primary mb-2">해결 수단</h2>
              <p className="text-body-m text-text-secondary leading-relaxed whitespace-pre-line">
                {data.patent_draft.solution}
              </p>
            </section>
            <section>
              <h2 className="text-h3 text-text-primary mb-2">청구항</h2>
              <ol className="list-decimal list-inside space-y-2 text-body-m text-text-secondary">
                {data.patent_draft.claims.map((claim, i) => (
                  <li key={i} className="leading-relaxed">
                    {claim}
                  </li>
                ))}
              </ol>
            </section>
            <section>
              <h2 className="text-h3 text-text-primary mb-2">발명의 효과</h2>
              <p className="text-body-m text-text-secondary leading-relaxed whitespace-pre-line">
                {data.patent_draft.effects}
              </p>
            </section>
          </div>
        )}

        {activeTab === "triz" && (
          <div className="grid gap-4 sm:grid-cols-2">
            {data.triz_principles.map((p) => (
              <TrizCard key={p.number} principle={p} />
            ))}
          </div>
        )}

        {activeTab === "patents" && (
          <div className="space-y-4">
            {data.similar_patents.map((p, i) => (
              <PatentCard key={i} patent={p} />
            ))}
          </div>
        )}
      </div>

      <section className="rounded-card border border-border bg-bg-surface p-5">
        <h2 className="text-h3 text-text-primary mb-3">추론 과정</h2>
        {data.reasoning_trace.length === 0 ? (
          <p className="text-body-m text-text-muted">표시할 추론 로그가 없습니다.</p>
        ) : (
          <ol className="space-y-2">
            {data.reasoning_trace.map((trace, index) => (
              <li key={`${trace}-${index}`} className="text-body-m text-text-secondary">
                {trace}
              </li>
            ))}
          </ol>
        )}
      </section>

      <div className="flex flex-wrap gap-4 pt-4 border-t border-border">
        <Button variant="ghost" onClick={onRegenerate}>
          다시 생성하기
        </Button>
        <DownloadButton
          draftId={data.draft_id}
          docxDownloadUrl={data.docx_download_url}
        />
      </div>
    </div>
  );
}
