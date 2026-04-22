export type DocumentType = 'md' | 'txt' | 'pdf' | 'docx';

export interface Document {
  id: string;
  name: string;
  content?: string;
  document_type: DocumentType;
  knowledge_base_id: string;
  file_path?: string;
  size: number;
  chunk_count: number;
  vector_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateDocumentRequest {
  knowledge_base_id: string;
  name: string;
  content: string;
  document_type: DocumentType;
}

export interface UpdateDocumentRequest {
  name?: string;
  content?: string;
}

export interface DocumentListResponse {
  code: number;
  message: string;
  data: Document[];
  total: number;
}
