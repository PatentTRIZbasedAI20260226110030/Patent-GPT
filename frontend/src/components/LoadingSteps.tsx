"use client";

const STEPS = [
  { id: 1, label: "TRIZ 원리 분류 중..." },
  { id: 2, label: "선행특허 검색 및 평가 중..." },
  { id: 3, label: "아이디어 생성 및 신규성 평가 중..." },
  { id: 4, label: "특허 초안 생성 중..." },
];

type StepStatus = "done" | "active" | "pending";

interface LoadingStepsProps {
  currentStep: number;
}

function StepIcon({ status }: { status: StepStatus }) {
  if (status === "done") {
    return (
      <div className="w-6 h-6 rounded-full bg-success flex items-center justify-center">
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
      <div className="w-6 h-6 rounded-full border-2 border-primary border-t-transparent animate-spin" />
    );
  }
  return (
    <div className="w-6 h-6 rounded-full border-2 border-border bg-transparent" />
  );
}

export function LoadingSteps({ currentStep }: LoadingStepsProps) {
  return (
    <div className="max-w-[480px] mx-auto">
      {STEPS.map((step, index) => {
        const status: StepStatus =
          index < currentStep
            ? "done"
            : index === currentStep
              ? "active"
              : "pending";
        const isLast = index === STEPS.length - 1;
        return (
          <div key={step.id} className="flex items-start gap-4">
            <div className="flex flex-col items-center">
              <StepIcon status={status} />
              {!isLast && (
                <div
                  className={`w-0.5 h-6 mt-1 ${
                    status === "done" ? "bg-success" : "bg-border"
                  }`}
                />
              )}
            </div>
            <div className={isLast ? "" : "pb-2"}>
              <p
                className={`text-body-m ${
                  status === "done"
                    ? "text-success"
                    : status === "active"
                      ? "text-text-primary"
                      : "text-text-muted"
                }`}
              >
                {step.label}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
