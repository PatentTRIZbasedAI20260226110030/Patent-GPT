"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PatentCard } from "@/components/PatentCard";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { searchPatent } from "@/lib/api";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<
    { title: string; abstract?: string; application_number?: string; similarity_score: number }[] | null
  >(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const res = await searchPatent({ query: trimmed, top_k: topK });
      setResults(res.results);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "검색 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1 px-6 py-8 max-w-content mx-auto w-full">
        <div className="max-w-[680px] mx-auto mb-8">
          <h1 className="text-h1 text-text-primary mb-2">
            선행특허 검색
          </h1>
          <p className="text-body-m text-text-secondary">
            키워드로 선행 특허를 검색합니다
          </p>
        </div>

        <form
          onSubmit={handleSearch}
          className="max-w-[680px] mx-auto flex flex-col gap-3 mb-8"
        >
          <Input
            placeholder="방열 구조, 열관리 등 검색어 입력"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            className="w-full"
          />
          <div className="flex gap-3 items-end">
            <div>
              <label htmlFor="top-k" className="text-caption text-text-muted mb-1 block">건수</label>
              <Input
                id="top-k"
                type="number"
                min={1}
                max={50}
                value={topK}
                onChange={(e) => {
                  const value = Number(e.target.value);
                  if (!Number.isNaN(value)) {
                    setTopK(Math.min(50, Math.max(1, value)));
                  }
                }}
                disabled={isLoading}
                className="w-20"
              />
            </div>
            <Button type="submit" variant="primary" disabled={isLoading} className="flex-1 sm:flex-none">
              {isLoading ? "검색 중..." : "검색"}
            </Button>
          </div>
          <p className="text-caption text-text-muted">결과 개수: 1~50 (기본 5)</p>
        </form>

        {error && (
          <div className="max-w-[680px] mx-auto rounded-card border border-error/50 bg-error/5 p-6 mb-8">
            <p className="text-body-m text-error">{error}</p>
            <Button
              variant="ghost"
              className="mt-4"
              onClick={() => setError(null)}
            >
              닫기
            </Button>
          </div>
        )}

        {isLoading && (
          <div className="max-w-[680px] mx-auto py-12 text-center">
            <div className="w-10 h-10 rounded-full border-2 border-primary border-t-transparent animate-spin mx-auto mb-4" />
            <p className="text-body-m text-text-muted">검색 중...</p>
          </div>
        )}

        {!isLoading && results !== null && results.length === 0 && (
          <div className="max-w-[680px] mx-auto py-16 text-center rounded-card border border-border bg-bg-surface">
            <p className="text-body-m text-text-muted mb-2">
              검색 결과가 없습니다.
            </p>
            <p className="text-caption text-text-muted">
              다른 검색어로 시도해 보세요.
            </p>
          </div>
        )}

        {!isLoading && results === null && !error && (
          <div className="max-w-[680px] mx-auto py-16 text-center">
            <div className="text-4xl mb-4" aria-hidden="true">
              🔍
            </div>
            <p className="text-body-m text-text-muted mb-1">
              검색어를 입력하고 선행특허를 탐색하세요
            </p>
            <p className="text-caption text-text-muted">
              키워드, 기술명, 발명 제목 등으로 검색할 수 있습니다
            </p>
          </div>
        )}

        {!isLoading && results && results.length > 0 && (
          <div className="space-y-4">
            <p className="text-body-m text-text-secondary mb-4">
              {results.length}건의 결과
            </p>
            {results.map((p, i) => (
              <PatentCard key={i} patent={p} />
            ))}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
