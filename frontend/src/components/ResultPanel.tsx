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

      <div className="flex flex-wrap gap-4 pt-4 border-t border-border">
        <Button variant="ghost" onClick={onRegenerate}>
          다시 생성하기
        </Button>
        <DownloadButton docxDownloadUrl={data.docx_download_url} />
      </div>
    </div>
  );
}
