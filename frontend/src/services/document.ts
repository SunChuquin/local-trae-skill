import api from './api';
import { Document, CreateDocumentRequest, UpdateDocumentRequest } from '../types/document';

export interface UploadProgress {
  phase: 'upload' | 'processing' | 'done';
  percent: number;
  message: string;
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export const documentApi = {
  list: async (kbId: string): Promise<Document[]> => {
    const response = await api.get<ApiResponse<Document[]>>(`/documents/knowledge-base/${kbId}`);
    return (response as unknown as ApiResponse<Document[]>).data;
  },

  get: async (id: string): Promise<Document> => {
    const response = await api.get<ApiResponse<Document>>(`/documents/${id}`);
    return (response as unknown as ApiResponse<Document>).data;
  },

  create: async (data: CreateDocumentRequest): Promise<Document> => {
    const response = await api.post<ApiResponse<Document>>('/documents', data);
    return (response as unknown as ApiResponse<Document>).data;
  },

  update: async (id: string, data: UpdateDocumentRequest): Promise<Document> => {
    const response = await api.put<ApiResponse<Document>>(`/documents/${id}`, data);
    return (response as unknown as ApiResponse<Document>).data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },

  upload: async (
    kbId: string,
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<Document> => {
    const formData = new FormData();
    formData.append('knowledge_base_id', kbId);
    formData.append('file', file);

    let processingTimer: number | null = null;

    const reportProgress = (phase: UploadProgress['phase'], percent: number, message: string) => {
      onProgress?.({ phase, percent, message });
    };

    reportProgress('upload', 0, '准备上传...');

    try {
      const response = await api.post<ApiResponse<Document>>('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadPercent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            reportProgress('upload', Math.min(uploadPercent, 40), `上传文件中... ${uploadPercent}%`);
          }
        },
      });

      reportProgress('processing', 42, '文件已上传，等待后端处理...');

      await new Promise<void>((resolve) => {
        let simulatedPercent = 42;
        const phases = [
          { at: 48, msg: '解析文档内容...' },
          { at: 58, msg: '文本分块处理中...' },
          { at: 70, msg: '生成向量嵌入...' },
          { at: 82, msg: '写入向量数据库...' },
          { at: 92, msg: '即将完成...' },
        ];
        let phaseIdx = 0;

        processingTimer = setInterval(() => {
          if (simulatedPercent < 92) {
            simulatedPercent += 1;
            if (phaseIdx < phases.length && simulatedPercent >= phases[phaseIdx].at) {
              reportProgress('processing', simulatedPercent, phases[phaseIdx].msg);
              phaseIdx++;
            } else {
              reportProgress('processing', simulatedPercent, '');
            }
          } else {
            clearInterval(processingTimer!);
            processingTimer = null;
            resolve();
          }
        }, 200);
      });

      if (processingTimer) {
        clearInterval(processingTimer!);
        processingTimer = null;
      }

      reportProgress('done', 100, '完成');
      return (response as unknown as ApiResponse<Document>).data;

    } catch (error) {
      if (processingTimer) {
        clearInterval(processingTimer);
        processingTimer = null;
      }
      throw error;
    }
  },
};
