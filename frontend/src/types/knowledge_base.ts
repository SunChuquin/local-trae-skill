export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  document_count: number;
  vector_count: number;
  summary?: string;
  summary_updated_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateKnowledgeBaseRequest {
  name: string;
  description?: string;
}

export interface UpdateKnowledgeBaseRequest {
  name?: string;
  description?: string;
}

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}
