export interface RetrievalResult {
  document_id: string;
  document_name: string;
  content: string;
  similarity: number;
  metadata: Record<string, any>;
}

export interface SkillConfig {
  name: string;
  description: string;
  top_k: number;
  similarity_threshold: number;
}

export interface RetrievalRequest {
  query: string;
  knowledge_base_name?: string;
  top_k?: number;
}

export interface SkillMetadata {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: {
      type: 'object';
      properties: {
        query: {
          type: 'string';
          description: string;
        };
        knowledge_base_name?: {
          type: 'string';
          description: string;
        };
        top_k?: {
          type: 'integer';
          default: number;
        };
      };
      required: string[];
    };
  };
}
