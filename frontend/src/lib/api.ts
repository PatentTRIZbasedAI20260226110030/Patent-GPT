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
