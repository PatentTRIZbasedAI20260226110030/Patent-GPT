"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import type { PatentGenerateRequest } from "@/types/patent";

const TECHNICAL_FIELDS = [
  { value: "", label: "선택하세요" },
  { value: "전자기기", label: "전자기기" },
  { value: "소재", label: "소재" },
  { value: "기계", label: "기계" },
  { value: "화학", label: "화학" },
  { value: "바이오", label: "바이오" },
  { value: "기타", label: "기타" },
];

const MAX_EVASION_MIN = 1;
const MAX_EVASION_MAX = 10;
const MAX_EVASION_DEFAULT = 3;

interface PatentFormProps {
  onSubmit: (data: PatentGenerateRequest) => void;
  isLoading?: boolean;
}

export function PatentForm({ onSubmit, isLoading }: PatentFormProps) {
  const [problemDescription, setProblemDescription] = useState("");
  const [technicalField, setTechnicalField] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [maxEvasionAttempts, setMaxEvasionAttempts] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [evasionError, setEvasionError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setEvasionError(null);

    const trimmed = problemDescription.trim();
    if (!trimmed) {
      setError("문제 설명을 입력해 주세요.");
      return;
    }

    let parsedEvasion: number | undefined = undefined;
    if (showAdvanced && maxEvasionAttempts !== "") {
      const n = parseInt(maxEvasionAttempts, 10);
      if (isNaN(n) || n < MAX_EVASION_MIN || n > MAX_EVASION_MAX) {
        setEvasionError(
          `${MAX_EVASION_MIN}에서 ${MAX_EVASION_MAX} 사이의 정수를 입력해 주세요.`
        );
        return;
      }
      parsedEvasion = n;
    }

    onSubmit({
      problem_description: trimmed,
      technical_field: technicalField || undefined,
      max_evasion_attempts: parsedEvasion,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Problem Description */}
      <div>
        <label
          htmlFor="problem"
          className="block text-label text-text-secondary mb-2"
        >
          문제 설명 <span className="text-error">*</span>
        </label>
        <Textarea
          id="problem"
          placeholder="해결하고 싶은 문제를 설명해주세요. 예: 발열은 줄이고 싶지만 두께는 얇아야 한다"
          value={problemDescription}
          onChange={(e) => setProblemDescription(e.target.value)}
          aria-invalid={!!error}
          disabled={isLoading}
          minLength={1}
        />
        {error && (
          <p className="mt-2 text-body-m text-error" role="alert">
            {error}
          </p>
        )}
      </div>

      {/* Technical Field */}
      <div>
        <label
          htmlFor="technical_field"
          className="block text-label text-text-secondary mb-2"
        >
          기술 분야
        </label>
        <Select
          id="technical_field"
          value={technicalField}
          onChange={(e) => setTechnicalField(e.target.value)}
          disabled={isLoading}
        >
          {TECHNICAL_FIELDS.map((opt) => (
            <option key={opt.value || "empty"} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </Select>
      </div>

      {/* Advanced Settings Toggle */}
      <div className="rounded-card border border-border bg-bg-elevated overflow-hidden">
        <button
          type="button"
          onClick={() => setShowAdvanced((v) => !v)}
          disabled={isLoading}
          className="w-full flex items-center justify-between px-4 py-3 text-label text-text-secondary hover:text-text-primary transition-colors disabled:opacity-50"
          aria-expanded={showAdvanced}
          aria-controls="advanced-settings"
        >
          <span>고급 설정</span>
          <svg
            className={`w-4 h-4 transition-transform duration-200 ${
              showAdvanced ? "rotate-180" : ""
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        {showAdvanced && (
          <div
            id="advanced-settings"
            className="px-4 pb-4 pt-2 border-t border-border space-y-4"
          >
            <div>
              <label
                htmlFor="max_evasion_attempts"
                className="block text-label text-text-secondary mb-1"
              >
                최대 회피 시도 횟수
                <span className="ml-2 text-caption text-text-muted">
                  ({MAX_EVASION_MIN}–{MAX_EVASION_MAX}, 기본값{" "}
                  {MAX_EVASION_DEFAULT})
                </span>
              </label>
              <p className="text-caption text-text-muted mb-2">
                특허 회피 설계를 몇 번까지 반복할지 설정합니다. 값이 클수록
                결과가 정교해지지만 처리 시간이 늘어납니다.
              </p>
              <Input
                id="max_evasion_attempts"
                type="number"
                min={MAX_EVASION_MIN}
                max={MAX_EVASION_MAX}
                step={1}
                placeholder={String(MAX_EVASION_DEFAULT)}
                value={maxEvasionAttempts}
                onChange={(e) => {
                  setMaxEvasionAttempts(e.target.value);
                  setEvasionError(null);
                }}
                aria-invalid={!!evasionError}
                aria-describedby={
                  evasionError ? "evasion-error" : undefined
                }
                disabled={isLoading}
                className="max-w-[140px]"
              />
              {evasionError && (
                <p
                  id="evasion-error"
                  className="mt-2 text-body-m text-error"
                  role="alert"
                >
                  {evasionError}
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      <Button
        type="submit"
        variant="primary"
        className="w-full"
        disabled={isLoading}
      >
        {isLoading ? "생성 중..." : "특허 아이디어 생성하기"}
      </Button>
    </form>
  );
}
