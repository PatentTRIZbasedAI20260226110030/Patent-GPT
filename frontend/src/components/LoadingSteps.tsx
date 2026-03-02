"use client";

const STEPS = [
  { id: 1, label: "TRIZ 원리 분류 중...", sub: "TRIZ 40원리 분석" },
  { id: 2, label: "선행특허 검색 및 평가 중...", sub: "ChromaDB + KIPRISplus" },
  { id: 3, label: "아이디어 생성 및 신규성 평가 중...", sub: "CRAG 기반 생성" },
  { id: 4, label: "특허 초안 생성 중...", sub: "KIPO 형식 출력" },
];

type StepStatus = "done" | "active" | "pending";

interface LoadingStepsProps {
  currentStep: number;
}

function StepIcon({ status, stepNumber }: { status: StepStatus; stepNumber: number }) {
  if (status === "done") {
    return (
      <div className="w-[34px] h-[34px] rounded-lg bg-success flex items-center justify-center">
        <svg
          className="w-4 h-4 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 13l4 4L19 7"
          />
        </svg>
      </div>
    );
  }
  if (status === "active") {
    return (
      <div className="w-[34px] h-[34px] rounded-lg bg-primary flex items-center justify-center">
        <svg
          className="w-4 h-4 text-white animate-spin"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      </div>
    );
  }
  return (
    <div className="w-[34px] h-[34px] rounded-lg bg-bg-elevated flex items-center justify-center text-text-muted text-body-m font-medium">
      {stepNumber}
    </div>
  );
}

export function LoadingSteps({ currentStep }: LoadingStepsProps) {
  return (
    <div className="max-w-[480px] mx-auto space-y-2">
      {STEPS.map((step, index) => {
        const status: StepStatus =
          index < currentStep
            ? "done"
            : index === currentStep
              ? "active"
              : "pending";
        return (
          <div
            key={step.id}
            className={`flex items-center gap-3 p-3.5 rounded-[10px] border transition-colors ${
              status === "done"
                ? "border-accent-border bg-accent-bg"
                : status === "active"
                  ? "border-primary-border bg-primary-bg"
                  : "border-border-light bg-transparent"
            }`}
          >
            <StepIcon status={status} stepNumber={step.id} />
            <div className="flex-1 min-w-0">
              <p
                className={`text-body-m ${
                  status === "done"
                    ? "text-success"
                    : status === "active"
                      ? "text-text-primary font-medium"
                      : "text-text-muted"
                }`}
              >
                {step.label}
              </p>
              <p className="text-[11px] text-text-muted">{step.sub}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
