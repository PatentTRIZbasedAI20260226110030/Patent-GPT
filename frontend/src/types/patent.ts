// API 요청/응답 타입 (백엔드 스키마와 동기화)

export interface PatentGenerateRequest {
  problem_description: string;
  technical_field?: string;
  max_evasion_attempts?: number;
}

export interface PatentDraft {
  title: string;
  abstract: string;
  background: string;
  problem_statement: string;
  solution: string;
  claims: string[];
  effects: string;
}

export interface TrizPrinciple {
  number: number;
  name_en?: string;
  name_ko: string;
  description: string;
  matching_score?: number;
}

export interface SimilarPatent {
  title: string;
  abstract?: string;
  application_number?: string;
  similarity_score: number;
}

export interface EvaluationResult {
  faithfulness: number;
  answer_relevancy: number;
  context_recall: number;
  passed: boolean;
}

export interface PatentGenerateResponse {
  patent_draft: PatentDraft;
  triz_principles: TrizPrinciple[];
  similar_patents: SimilarPatent[];
  reasoning_trace: string[];
  draft_id: string | null;
  novelty_score: number | null;
  threshold: number | null;
  docx_download_url: string | null;
  evaluation: EvaluationResult | null;
}

export interface PatentSearchRequest {
  query: string;
  top_k?: number;
}

export interface PatentSearchResponse {
  results: SimilarPatent[];
}
