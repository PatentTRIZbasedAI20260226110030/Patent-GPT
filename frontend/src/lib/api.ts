import type {
  PatentGenerateRequest,
  PatentGenerateResponse,
  PatentSearchRequest,
  PatentSearchResponse,
} from "@/types/patent";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let body: unknown;
    try {
      body = await res.json();
    } catch {
      body = await res.text();
    }
    throw new ApiError(
      `API Error: ${res.status} ${res.statusText}`,
      res.status,
      body
    );
  }

  return res.json();
}

export async function healthCheck(): Promise<{ status: string }> {
  return fetchApi<{ status: string }>("/api/v1/health");
}

export async function generatePatent(
  req: PatentGenerateRequest
): Promise<PatentGenerateResponse> {
  return fetchApi<PatentGenerateResponse>("/api/v1/patent/generate", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export interface GenerateStreamEvent {
  step: string;
  state: Record<string, unknown>;
}

export async function generatePatentStream(
  req: PatentGenerateRequest,
  onStep: (event: GenerateStreamEvent) => void
): Promise<PatentGenerateResponse> {
  const url = `${BASE_URL}/api/v1/patent/generate/stream`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 120_000);

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!res.ok || !res.body) {
      throw new ApiError(
        `Stream API Error: ${res.status} ${res.statusText}`,
        res.status
      );
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let currentEvent = "";
    let currentData = "";
    let finalResponse: PatentGenerateResponse | null = null;
    let streamError: ApiError | null = null;

    const flushEvent = () => {
      if (currentEvent === "step" && currentData) {
        try {
          const parsed = JSON.parse(currentData) as GenerateStreamEvent;
          onStep(parsed);
        } catch {
          // Ignore malformed SSE chunks
        }
      } else if (currentEvent === "done" && currentData) {
        try {
          finalResponse = JSON.parse(currentData) as PatentGenerateResponse;
        } catch {
          // Ignore malformed done event
        }
      } else if (currentEvent === "error" && currentData) {
        try {
          const errPayload = JSON.parse(currentData) as { message: string; step: string };
          streamError = new ApiError(
            `파이프라인 오류 (${errPayload.step}): ${errPayload.message}`,
            0,
            errPayload
          );
        } catch {
          streamError = new ApiError("스트림 오류가 발생했습니다.", 0);
        }
      }
      currentEvent = "";
      currentData = "";
    };

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const rawLine of lines) {
        const line = rawLine.trimEnd();
        if (!line) {
          flushEvent();
          continue;
        }
        if (line.startsWith("event:")) {
          currentEvent = line.replace("event:", "").trim();
        } else if (line.startsWith("data:")) {
          const dataLine = line.replace("data:", "").trim();
          currentData = currentData ? `${currentData}\n${dataLine}` : dataLine;
        }
      }
    }

    flushEvent();

    if (streamError) throw streamError;

    if (!finalResponse) {
      throw new ApiError("Stream ended without a final response", 0);
    }
    return finalResponse;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err instanceof Error && err.name === "AbortError") {
      throw new ApiError("연결 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.", 0);
    }
    throw err;
  }
}

export async function searchPatent(
  req: PatentSearchRequest
): Promise<PatentSearchResponse> {
  return fetchApi<PatentSearchResponse>("/api/v1/patent/search", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/** docx_download_url (예: "data/drafts/patent_draft_xxx.docx")에서 draft_id 추출 */
export function extractDraftIdFromUrl(url: string | null): string | null {
  if (!url) return null;
  const match = url.match(/\/([^/]+)\.docx$/);
  return match ? match[1] : null;
}

export function resolveDraftId(
  draftId: string | null,
  docxDownloadUrl: string | null
): string | null {
  if (draftId) return draftId;
  return extractDraftIdFromUrl(docxDownloadUrl);
}

export async function downloadDocx(draftId: string): Promise<Blob> {
  const url = `${BASE_URL}/api/v1/patent/${draftId}/docx`;
  const res = await fetch(url);

  if (!res.ok) {
    throw new ApiError(
      `Download failed: ${res.status} ${res.statusText}`,
      res.status
    );
  }

  return res.blob();
}

export { ApiError };
