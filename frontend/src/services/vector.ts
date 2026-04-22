import api from './api';

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export const vectorApi = {
  rebuild: async (kbId: string): Promise<void> => {
    await api.post(`/vectors/rebuild/${kbId}`);
  },

  retrieve: async (query: string, kbName?: string, topK?: number, contentLength: number = 0) => {
    const response = await api.get<ApiResponse<any>>('/vectors/retrieve', {
      params: { query, knowledge_base_name: kbName, top_k: topK, content_length: contentLength },
    });
    return (response as unknown as ApiResponse<any>).data;
  },

  backup: async (kbId: string): Promise<{ backup_path: string }> => {
    const response = await api.post<ApiResponse<{ backup_path: string }>>(`/vectors/backup/${kbId}`);
    return (response as unknown as ApiResponse<{ backup_path: string }>).data;
  },

  restore: async (kbId: string, backupPath: string): Promise<void> => {
    await api.post(`/vectors/restore/${kbId}`, null, {
      params: { backup_path: backupPath },
    });
  },

  listBackups: async () => {
    const response = await api.get<ApiResponse<any>>('/vectors/backups');
    return (response as unknown as ApiResponse<any>).data;
  },

  deleteBackup: async (backupName: string): Promise<void> => {
    await api.delete(`/vectors/backup/${backupName}`);
  },

  getStats: async (kbId: string) => {
    const response = await api.get<ApiResponse<any>>(`/vectors/stats/${kbId}`);
    return (response as unknown as ApiResponse<any>).data;
  },

  getDocumentVectors: async (kbId: string, documentId: string) => {
    const response = await api.get<ApiResponse<any>>(`/vectors/document/${kbId}/${documentId}`);
    return (response as unknown as ApiResponse<any>).data;
  },
};
