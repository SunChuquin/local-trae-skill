import api from './api';

export interface CleanPreviewItem {
  name: string;
  size: number;
  updated_at: number;
}

export interface CleanPreviewContent {
  name: string;
  kind: 'original' | 'cleaned';
  content: string;
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export const cleanPreviewApi = {
  /** 列出所有可对比的 PDF 剔除预览（按更新时间倒序） */
  list: async (): Promise<CleanPreviewItem[]> => {
    const response = await api.get<ApiResponse<CleanPreviewItem[]>>('/clean-preview/list');
    return (response as unknown as ApiResponse<CleanPreviewItem[]>)?.data ?? [];
  },

  /** 获取单个文件的剔除前（original）或剔除后（cleaned）文本 */
  content: async (name: string, kind: 'original' | 'cleaned'): Promise<string> => {
    const response = await api.get<ApiResponse<CleanPreviewContent>>('/clean-preview/content', {
      params: { name, kind },
    });
    const data = (response as unknown as ApiResponse<CleanPreviewContent>)?.data;
    return data?.content ?? '';
  },
};
