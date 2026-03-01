"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { PatentForm } from "@/components/PatentForm";
import { LoadingSteps } from "@/components/LoadingSteps";
import { ResultPanel } from "@/components/ResultPanel";
import { Button } from "@/components/ui/button";
import { generatePatent } from "@/lib/api";
import type { PatentGenerateResponse } from "@/types/patent";

type ViewState = "input" | "loading" | "result" | "error";

export default function GeneratePage() {
  const [viewState, setViewState] = useState<ViewState>("input");
  const [loadingStep, setLoadingStep] = useState(0);
  const [result, setResult] = useState<PatentGenerateResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (data: {
      problem_description: string;
      technical_field?: string;
      max_evasion_attempts?: number;
    }) => {
      setViewState("loading");
      setLoadingStep(0);
      setErrorMessage(null);

      const interval = setInterval(() => {
        setLoadingStep((prev) => {
          if (prev >= 3) {
            clearInterval(interval);
            return 3;
          }
          return prev + 1;
        });
      }, 1500);

      try {
        const res = await generatePatent(data);
        clearInterval(interval);
        setLoadingStep(4);
        setResult(res);
        setViewState("result");
      } catch (err) {
        clearInterval(interval);
        setErrorMessage(
          err instanceof Error ? err.message : "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
        );
        setViewState("error");
      }
    },
    []
  );

  const handleRegenerate = useCallback(() => {
    setViewState("input");
    setResult(null);
    setErrorMessage(null);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="flex items-center justify-between px-6 py-4 max-w-content mx-auto w-full">
        <Link href="/" className="text-xl font-bold text-text-primary">
          Patent-GPT
        </Link>
        <div className="flex gap-3">
          <Link href="/search">
            <Button variant="ghost">선행특허 검색</Button>
          </Link>
          <Link href="/generate">
            <Button variant="primary">특허 생성하기</Button>
          </Link>
        </div>
      </nav>

      <main className="flex-1 px-6 py-8 max-w-content mx-auto w-full">
        {viewState === "input" && (
          <>
            <div className="max-w-[680px] mx-auto mb-8">
              <h1 className="text-h1 text-text-primary mb-2">
                특허 아이디어 생성
              </h1>
              <p className="text-body-m text-text-secondary">
                해결하고 싶은 문제를 입력하면 TRIZ 기반으로 특허 아이디어를
                생성합니다
              </p>
            </div>
            <div className="max-w-[680px] mx-auto rounded-card border border-border bg-bg-surface p-6 md:p-8">
              <PatentForm onSubmit={handleSubmit} isLoading={false} />
            </div>
          </>
        )}

        {viewState === "loading" && (
          <div className="py-24 text-center">
            <h2 className="text-h2 text-text-primary mb-2">
              AI가 분석 중입니다...
            </h2>
            <p className="text-body-m text-text-muted mb-12">
              4단계 파이프라인을 순차 실행합니다
            </p>
            <LoadingSteps currentStep={loadingStep} />
          </div>
        )}

        {viewState === "result" && result && (
          <div className="max-w-content">
            <ResultPanel data={result} onRegenerate={handleRegenerate} />
          </div>
        )}

        {viewState === "error" && (
          <div className="max-w-[680px] mx-auto rounded-card border border-error/50 bg-error/5 p-6 md:p-8">
            <h2 className="text-h2 text-error mb-2">오류가 발생했습니다</h2>
            <p className="text-body-m text-text-secondary mb-6">
              {errorMessage}
            </p>
            <div className="flex gap-4">
              <Button variant="primary" onClick={handleRegenerate}>
                다시 시도하기
              </Button>
              <Link href="/">
                <Button variant="ghost">홈으로</Button>
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
