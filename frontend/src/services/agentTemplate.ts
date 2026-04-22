import api from './api';

export interface PromptTemplate {
  name: string;
  description: string;
  content: string;
  variables: string[];
  version: string;
  last_updated: string;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  type: string;
  templates: PromptTemplate[];
  status: string;
  created_at: string;
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export const agentTemplateApi = {
  list: async (): Promise<Agent[]> => {
    const response = await api.get<ApiResponse<Agent[]>>('/agent-templates');
    return (response as unknown as ApiResponse<Agent[]>).data || [];
  },

  getById: async (agentId: string): Promise<Agent> => {
    const response = await api.get<ApiResponse<Agent>>(`/agent-templates/${agentId}`);
    return (response as unknown as ApiResponse<Agent>).data;
  },
};
