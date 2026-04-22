import api from './api';

export interface KnowledgeBaseInfo {
  id: string;
  name: string;
  description?: string;
  document_count: number;
}

export interface KBRecommendation {
  knowledge_base: KnowledgeBaseInfo;
  reason: string;
  confidence: number;
}

export interface KBSelectionRequest {
  query: string;
  selected_kb_names?: string[];
}

export interface KBSelectionResponse {
  has_knowledge_bases: boolean;
  user_selected: boolean;
  recommendations: KBRecommendation[];
  analysis: string;
  all_knowledge_bases?: KnowledgeBaseInfo[];
  selected_kb_names?: string[];
}

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export const agentApi = {
  selectKnowledgeBases: async (request: KBSelectionRequest): Promise<KBSelectionResponse> => {
    const response = await api.post<ApiResponse<KBSelectionResponse>>(
      '/agent/kb-selector',
      request
    );
    console.log('Agent API raw response:', response);
    return (response as unknown as ApiResponse<KBSelectionResponse>).data;
  },
};
