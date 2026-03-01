"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { downloadDocx, resolveDraftId } from "@/lib/api";

interface DownloadButtonProps {
  draftId?: string | null;
  docxDownloadUrl: string | null;
  disabled?: boolean;
  className?: string;
}

export function DownloadButton({
  draftId,
  docxDownloadUrl,
  disabled,
  className,
}: DownloadButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resolvedDraftId = resolveDraftId(draftId ?? null, docxDownloadUrl);
  const canDownload = !!resolvedDraftId && !disabled && !isLoading;

  const handleDownload = async () => {
    if (!resolvedDraftId) return;
    setIsLoading(true);
    setError(null);
    try {
      const blob = await downloadDocx(resolvedDraftId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `patent_draft_${resolvedDraftId}.docx`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 100);
    } catch (err) {
      setError(err instanceof Error ? err.message : "다운로드에 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={className}>
      <Button
        variant="primary"
        onClick={handleDownload}
        disabled={!canDownload}
      >
        {isLoading ? "다운로드 중..." : "DOCX 다운로드"}
      </Button>
      {error && (
        <p className="mt-2 text-body-m text-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
