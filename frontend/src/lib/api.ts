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
): Promise<void> {
  const url = `${BASE_URL}/api/v1/patent/generate/stream`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

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

  const flushEvent = () => {
    if (currentEvent === "step" && currentData) {
      try {
        const parsed = JSON.parse(currentData) as GenerateStreamEvent;
        onStep(parsed);
      } catch {
        // Ignore malformed SSE chunks
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
