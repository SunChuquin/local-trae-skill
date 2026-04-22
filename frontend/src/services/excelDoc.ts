import api from './api';
import {
  ExcelDocument,
  ChunkMode,
  ChunkPreview,
  ParsePreview,
} from '../types/excel_document';

export interface ExcelUploadProgress {
  phase: 'upload' | 'processing' | 'done';
  percent: number;
  message: string;
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export const excelDocApi = {
  upload: async (
    kbId: string,
    file: File,
    onProgress?: (progress: ExcelUploadProgress) => void
  ): Promise<ExcelDocument> => {
    const formData = new FormData();
    formData.append('knowledge_base_id', kbId);
    formData.append('file', file);

    const reportProgress = (phase: ExcelUploadProgress['phase'], percent: number, message: string) => {
      onProgress?.({ phase, percent, message });
    };

    reportProgress('upload', 0, '准备上传...');

    try {
      const response = await api.post<ApiResponse<ExcelDocument>>('/excel-doc/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadPercent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            reportProgress('upload', Math.min(uploadPercent, 50), `上传文件中... ${uploadPercent}%`);
          }
        },
      });

      reportProgress('processing', 60, '解析 Excel 文件...');
      await new Promise<void>((resolve) => setTimeout(resolve, 500));

      reportProgress('processing', 80, '读取 Sheet 信息...');
      await new Promise<void>((resolve) => setTimeout(resolve, 300));

      reportProgress('done', 100, '完成');
      return (response as unknown as ApiResponse<ExcelDocument>).data;
    } catch (error) {
      throw error;
    }
  },

  parsePreview: async (filePath: string, sheetName?: string): Promise<ParsePreview[]> => {
    const formData = new FormData();
    formData.append('file_path', filePath);
    if (sheetName) formData.append('sheet_name', sheetName);

    const response = await api.post<ApiResponse<ParsePreview[]>>('/excel-doc/parse-preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return (response as unknown as ApiResponse<ParsePreview[]>).data;
  },

  chunkPreview: async (
    filePath: string,
    chunkMode: ChunkMode = 'row_level',
    sheetName?: string,
    semanticThreshold: number = 0.7,
    includeHeaders: boolean = true
  ): Promise<ChunkPreview[]> => {
    const formData = new FormData();
    formData.append('file_path', filePath);
    formData.append('chunk_mode', chunkMode);
    if (sheetName) formData.append('sheet_name', sheetName);
    formData.append('semantic_threshold', String(semanticThreshold));
    formData.append('include_headers', String(includeHeaders));

    const response = await api.post<ApiResponse<ChunkPreview[]>>('/excel-doc/chunk-preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return (response as unknown as ApiResponse<ChunkPreview[]>).data;
  },

  chunkAndStore: async (
    docId: string,
    chunkMode: ChunkMode = 'row_level',
    sheetName?: string,
    semanticThreshold: number = 0.7,
    includeHeaders: boolean = true,
    onProgress?: (progress: ExcelUploadProgress) => void
  ): Promise<ExcelDocument> => {
    const reportProgress = (phase: ExcelUploadProgress['phase'], percent: number, message: string) => {
      onProgress?.({ phase, percent, message });
    };

    reportProgress('processing', 10, '准备分块参数...');

    const formData = new FormData();
    formData.append('doc_id', docId);
    formData.append('chunk_mode', chunkMode);
    if (sheetName) formData.append('sheet_name', sheetName);
    formData.append('semantic_threshold', String(semanticThreshold));
    formData.append('include_headers', String(includeHeaders));

    reportProgress('processing', 20, '开始分块处理...');

    const response = await api.post<ApiResponse<ExcelDocument>>('/excel-doc/chunk-and-store', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    reportProgress('processing', 40, '生成向量嵌入...');
    await new Promise<void>((resolve) => setTimeout(resolve, 300));

    reportProgress('processing', 70, '写入向量数据库...');
    await new Promise<void>((resolve) => setTimeout(resolve, 300));

    reportProgress('done', 100, '完成');
    return (response as unknown as ApiResponse<ExcelDocument>).data;
  },

  list: async (kbId: string): Promise<ExcelDocument[]> => {
    const response = await api.get<ApiResponse<ExcelDocument[]>>('/excel-doc/knowledge-base/' + kbId);
    return (response as unknown as ApiResponse<ExcelDocument[]>).data;
  },

  get: async (docId: string): Promise<ExcelDocument> => {
    const response = await api.get<ApiResponse<ExcelDocument>>('/excel-doc/' + docId);
    return (response as unknown as ApiResponse<ExcelDocument>).data;
  },

  delete: async (docId: string): Promise<void> => {
    await api.delete('/excel-doc/' + docId);
  },

  reChunk: async (
    docId: string,
    chunkMode: ChunkMode = 'row_level',
    sheetName?: string,
    semanticThreshold: number = 0.7,
    includeHeaders: boolean = true,
    onProgress?: (progress: ExcelUploadProgress) => void
  ): Promise<ExcelDocument> => {
    const reportProgress = (phase: ExcelUploadProgress['phase'], percent: number, message: string) => {
      onProgress?.({ phase, percent, message });
    };

    reportProgress('processing', 10, '删除旧向量...');
    await new Promise<void>((resolve) => setTimeout(resolve, 200));

    reportProgress('processing', 30, '重新分块...');

    const response = await api.post<ApiResponse<ExcelDocument>>(
      '/excel-doc/re-chunk/' + docId,
      null,
      {
        params: {
          chunk_mode: chunkMode,
          sheet_name: sheetName,
          semantic_threshold: semanticThreshold,
          include_headers: includeHeaders,
        },
      }
    );

    reportProgress('processing', 60, '生成新向量...');
    await new Promise<void>((resolve) => setTimeout(resolve, 300));

    reportProgress('processing', 80, '写入数据库...');
    await new Promise<void>((resolve) => setTimeout(resolve, 200));

    reportProgress('done', 100, '完成');
    return (response as unknown as ApiResponse<ExcelDocument>).data;
  },
};
