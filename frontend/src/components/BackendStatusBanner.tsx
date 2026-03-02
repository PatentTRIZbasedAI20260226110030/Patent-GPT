"use client";

import { useEffect, useState } from "react";
import { healthCheck } from "@/lib/api";

type Status = "checking" | "ok" | "error";

export default function BackendStatusBanner() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    healthCheck()
      .then(() => setStatus("ok"))
      .catch(() => setStatus("error"));
  }, []);

  if (status === "checking" || status === "ok") {
    return null;
  }

  return (
    <div
      role="alert"
      className="border-b border-error/50 bg-error/5 px-4 py-3 text-center text-body-m text-error"
    >
      백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요
      (localhost:8000).
    </div>
  );
}
