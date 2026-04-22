import api from './api';
import {
  ChatRequest,
  ChatResponse,
  ChatConfig,
  StreamChatCallback,
} from '../types/chat';

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export const chatApi = {
  getConfig: async (): Promise<ChatConfig> => {
    const response = await api.get<ApiResponse<ChatConfig>>('/chat/config');
    return (response as unknown as ApiResponse<ChatConfig>).data;
  },

  updateConfig: async (
    apiUrl?: string,
    apiKey?: string,
    model?: string
  ): Promise<ChatConfig> => {
    const response = await api.put<ApiResponse<ChatConfig>>('/chat/config', null, {
      params: {
        api_url: apiUrl,
        api_key: apiKey,
        model: model,
      },
    });
    return (response as unknown as ApiResponse<ChatConfig>).data;
  },

  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ApiResponse<ChatResponse>>('/chat/chat', request);
    return (response as unknown as ApiResponse<ChatResponse>).data;
  },

  chatStream: async (request: ChatRequest, callback: StreamChatCallback): Promise<void> => {
    // 设置stream为true
    const streamRequest = { ...request, stream: true };
    
    try {
      const response = await fetch('/api/chat/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify(streamRequest),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('响应没有可读流');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (!trimmedLine || trimmedLine.startsWith(':')) continue;

          if (trimmedLine.startsWith('data: ')) {
            const dataStr = trimmedLine.substring(6); // 去掉"data: "前缀
            try {
              if (dataStr) {
                const eventData = JSON.parse(dataStr);
                if (eventData.error) {
                  callback({ type: 'error', error: eventData.error });
                } else if (eventData.type === 'chunk' && eventData.content) {
                  callback({ type: 'chunk', content: eventData.content });
                } else if (eventData.type === 'complete' && eventData.content) {
                  callback({ type: 'complete', content: eventData.content });
                }
              }
            } catch (error) {
              console.error('解析流式数据失败:', error);
            }
          }
        }
      }

      // 处理剩余的buffer
      if (buffer.trim()) {
        const trimmedLine = buffer.trim();
        if (trimmedLine.startsWith('data: ')) {
          const dataStr = trimmedLine.substring(6);
          try {
            if (dataStr) {
              const eventData = JSON.parse(dataStr);
              if (eventData.error) {
                callback({ type: 'error', error: eventData.error });
              } else if (eventData.type === 'chunk' && eventData.content) {
                callback({ type: 'chunk', content: eventData.content });
              } else if (eventData.type === 'complete' && eventData.content) {
                callback({ type: 'complete', content: eventData.content });
              }
            }
          } catch (error) {
            console.error('解析流式数据失败:', error);
          }
        }
      }

    } catch (error) {
      console.error('流式聊天请求失败:', error);
      callback({ type: 'error', error: error instanceof Error ? error.message : '未知错误' });
    }
  },
};
