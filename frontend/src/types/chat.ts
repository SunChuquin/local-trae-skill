import { ApiResponse } from './knowledge_base';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatConfig {
  api_url: string;
  api_key: string;
  model: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  use_skill?: boolean;
  knowledge_base_name?: string;
  stream?: boolean;
}

export interface ChatResponse {
  content: string;
}

export type ChatConfigResponse = ApiResponse<ChatConfig>;

export type StreamChatEvent =
  | { type: 'chunk'; content: string }
  | { type: 'complete'; content: string }
  | { type: 'error'; error: string };

export type StreamChatCallback = (event: StreamChatEvent) => void;