import api from './api';
import {
  SkillConfig,
  SkillMetadata,
  RetrievalRequest,
  RetrievalResult,
} from '../types/skill';

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export const skillApi = {
  getMetadata: async (): Promise<SkillMetadata> => {
    const response = await api.get<ApiResponse<SkillMetadata>>('/skill/metadata');
    return (response as unknown as ApiResponse<SkillMetadata>).data;
  },

  retrieve: async (data: RetrievalRequest): Promise<RetrievalResult[]> => {
    const response = await api.post<ApiResponse<RetrievalResult[]>>('/skill/retrieve', data);
    return (response as unknown as ApiResponse<RetrievalResult[]>).data;
  },

  getConfig: async (): Promise<SkillConfig> => {
    const response = await api.get<ApiResponse<SkillConfig>>('/skill/config');
    return (response as unknown as ApiResponse<SkillConfig>).data;
  },

  updateConfig: async (data: Partial<SkillConfig>): Promise<SkillConfig> => {
    const response = await api.put<ApiResponse<SkillConfig>>('/skill/config', data);
    return (response as unknown as ApiResponse<SkillConfig>).data;
  },

  test: async (query: string, kbName?: string, topK?: number) => {
    const response = await api.post('/skill/test', null, {
      params: { query, knowledge_base_name: kbName, top_k: topK },
    });
    return response.data;
  },
};
