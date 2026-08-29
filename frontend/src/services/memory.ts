import api from './api';

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface MemoryRecord {
  id: string;
  question: string;
  answer: string;
  created_at?: string;
  source_note?: string;
}

export const memoryApi = {
  /** 保存一条问答记忆 */
  save: async (question: string, answer: string, source_note?: string): Promise<boolean> => {
    const response = await api.post<ApiResponse<{ saved: boolean }>>('/memory/save', {
      question,
      answer,
      source_note,
    });
    return ((response as unknown as ApiResponse<{ saved: boolean }>).data)?.saved ?? false;
  },

  /** 列出已存记忆（按创建时间倒序） */
  list: async (limit = 200, offset = 0): Promise<MemoryRecord[]> => {
    const response = await api.get<ApiResponse<MemoryRecord[]>>('/memory/list', {
      params: { limit, offset },
    });
    return (response as unknown as ApiResponse<MemoryRecord[]>).data ?? [];
  },

  /** 删除一条记忆 */
  remove: async (id: string): Promise<boolean> => {
    const response = await api.delete<ApiResponse<{ deleted: boolean }>>(
      `/memory/${encodeURIComponent(id)}`
    );
    return ((response as unknown as ApiResponse<{ deleted: boolean }>).data)?.deleted ?? false;
  },

  /** 记忆条数 */
  count: async (): Promise<number> => {
    const response = await api.get<ApiResponse<{ count: number }>>('/memory/count');
    return ((response as unknown as ApiResponse<{ count: number }>).data)?.count ?? 0;
  },
};
