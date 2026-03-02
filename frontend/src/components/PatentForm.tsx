"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";

const TECHNICAL_FIELDS = [
  { value: "", label: "선택하세요" },
  { value: "전자기기", label: "전자기기" },
  { value: "소재", label: "소재" },
  { value: "기계", label: "기계" },
  { value: "화학", label: "화학" },
  { value: "바이오", label: "바이오" },
  { value: "기타", label: "기타" },
];

interface PatentFormProps {
  onSubmit: (data: {
    problem_description: string;
    technical_field?: string;
    max_evasion_attempts?: number;
  }) => void;
  isLoading?: boolean;
  initialValues?: {
    problem_description?: string;
    technical_field?: string;
    max_evasion_attempts?: number;
  } | null;
}

export function PatentForm({ onSubmit, isLoading, initialValues }: PatentFormProps) {
  const [problemDescription, setProblemDescription] = useState(initialValues?.problem_description ?? "");
  const [technicalField, setTechnicalField] = useState(initialValues?.technical_field ?? "");
  const [maxEvasionAttempts, setMaxEvasionAttempts] = useState(initialValues?.max_evasion_attempts ?? 3);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const trimmed = problemDescription.trim();
    if (!trimmed) {
      setError("문제 설명을 입력해 주세요.");
      return;
    }

    onSubmit({
      problem_description: trimmed,
      technical_field: technicalField || undefined,
      max_evasion_attempts: maxEvasionAttempts,
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

      {/* Max Evasion Attempts */}
      <div>
        <label
          htmlFor="max_evasion_attempts"
          className="block text-label text-text-secondary mb-2"
        >
          최대 회피설계 횟수
        </label>
        <Select
          id="max_evasion_attempts"
          value={String(maxEvasionAttempts)}
          onChange={(e) => setMaxEvasionAttempts(Number(e.target.value))}
          disabled={isLoading}
        >
          {[1, 2, 3, 4, 5].map((attempt) => (
            <option key={attempt} value={attempt}>
              {attempt}회
            </option>
          ))}
        </Select>
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
