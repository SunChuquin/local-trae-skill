export type ChunkMode = 'row_level' | 'topic_semantic';

export interface SheetInfo {
  name: string;
  row_count: number;
  col_count: number;
  merged_cells: number;
}

export interface ExcelDocument {
  id: string;
  name: string;
  knowledge_base_id: string;
  file_path?: string;
  size: number;
  sheet_count: number;
  sheets: SheetInfo[];
  chunk_mode: ChunkMode;
  chunk_count: number;
  vector_count: number;
  created_at: string;
  updated_at: string;
}

export interface ChunkPreview {
  chunk_index: number;
  content: string;
  row_range?: string;
  topic?: string;
}

export interface ParsePreview {
  sheet_name: string;
  headers: string[];
  rows: string[][];
  total_rows: number;
  total_cols: number;
}

export interface ChunkConfig {
  chunk_mode: ChunkMode;
  semantic_threshold: number;
  include_headers: boolean;
  max_chunk_tokens?: number;
}

export interface ChunkPreviewResponse {
  code: number;
  message: string;
  data: ChunkPreview[];
  total: number;
}

export interface ParsePreviewResponse {
  code: number;
  message: string;
  data: ParsePreview[];
}

export interface ExcelDocumentResponse {
  code: number;
  message: string;
  data: ExcelDocument;
}

export interface ExcelDocumentListResponse {
  code: number;
  message: string;
  data: ExcelDocument[];
  total: number;
}
