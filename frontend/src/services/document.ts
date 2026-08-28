import api from './api';
import { Document, CreateDocumentRequest, UpdateDocumentRequest } from '../types/document';

export interface UploadProgress {
  phase: 'upload' | 'processing' | 'done';
  percent: number;
  message: string;
  estimateSeconds?: number | null;
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
  ): Promise<void> => {
    const formData = new FormData();
    formData.append('knowledge_base_id', kbId);
    formData.append('file', file);

    onProgress?.({ phase: 'upload', percent: 0, message: '准备上传...', estimateSeconds: null });

    // 1) 上传文件：后端只保存文件并创建后台任务，立即返回任务号
    let res: any;
    try {
      res = await api.post<ApiResponse<{ task_id?: string; filename?: string }>>('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 0, // 上传请求不做硬超时限制
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadPercent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress?.({
              phase: 'upload',
              percent: Math.min(uploadPercent, 40),
              message: `上传文件中... ${uploadPercent}%`,
              estimateSeconds: null,
            });
          }
        },
      });
    } catch (error) {
      throw new Error(`上传失败: ${(error as Error)?.message ?? error}`);
    }

    const taskId = res?.data?.task_id;
    if (!taskId) throw new Error('未获取到处理任务，上传失败');

    // 2) 轮询后台处理进度，用真实进度替换旧的模拟进度
    // eslint-disable-next-line no-constant-condition
    while (true) {
      await new Promise((resolve) => setTimeout(resolve, 1000));

      let poll: any;
      try {
        poll = await api.get(`/documents/upload-progress/${taskId}`);
      } catch (error) {
        throw new Error('查询处理进度失败');
      }

      const state = poll?.data ?? {};
      if (state.status === 'done') {
        onProgress?.({ phase: 'done', percent: 100, message: '处理完成', estimateSeconds: 0 });
        return;
      }
      if (state.status === 'error') {
        throw new Error(state.error || state.message || '文档处理失败');
      }
      onProgress?.({
        phase: 'processing',
        percent: state.percent ?? 0,
        message: state.message ?? '处理中...',
        estimateSeconds: state.estimate_seconds ?? null,
      });
    }
  },
};
