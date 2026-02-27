"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { downloadDocx, extractDraftIdFromUrl } from "@/lib/api";

interface DownloadButtonProps {
  docxDownloadUrl: string | null;
  disabled?: boolean;
  className?: string;
}

export function DownloadButton({
  docxDownloadUrl,
  disabled,
  className,
}: DownloadButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const draftId = extractDraftIdFromUrl(docxDownloadUrl);
  const canDownload = !!draftId && !disabled && !isLoading;

  const handleDownload = async () => {
    if (!draftId) return;
    setIsLoading(true);
    setError(null);
    try {
      const blob = await downloadDocx(draftId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `patent_draft_${draftId}.docx`;
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
