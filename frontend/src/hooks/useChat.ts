import { useState, useRef, useCallback } from 'react';
import { ChatMessage, ChatConfig } from '../types/chat';
import { KBSelectionResponse } from '../services/agent';

interface UseChatReturn {
  messages: ChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  inputMessage: string;
  setInputMessage: React.Dispatch<React.SetStateAction<string>>;
  useSkill: boolean;
  setUseSkill: React.Dispatch<React.SetStateAction<boolean>>;
  isLoading: boolean;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
  error: string;
  setError: React.Dispatch<React.SetStateAction<string>>;
  showConfig: boolean;
  setShowConfig: React.Dispatch<React.SetStateAction<boolean>>;
  config: ChatConfig;
  setConfig: React.Dispatch<React.SetStateAction<ChatConfig>>;
  showKBSelector: boolean;
  setShowKBSelector: React.Dispatch<React.SetStateAction<boolean>>;
  kbSelectionData: KBSelectionResponse | null;
  setKbSelectionData: React.Dispatch<React.SetStateAction<KBSelectionResponse | null>>;
  selectedKBs: string[];
  setSelectedKBs: React.Dispatch<React.SetStateAction<string[]>>;
  pendingQuery: string;
  setPendingQuery: React.Dispatch<React.SetStateAction<string>>;
  isSelectingKB: boolean;
  setIsSelectingKB: React.Dispatch<React.SetStateAction<boolean>>;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  scrollToBottom: () => void;
  clearChat: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [useSkill, setUseSkill] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  const [config, setConfig] = useState<ChatConfig>({
    api_url: '',
    api_key: '',
    model: 'gpt-4o-mini'
  });
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null!);
  
  const [showKBSelector, setShowKBSelector] = useState(false);
  const [kbSelectionData, setKbSelectionData] = useState<KBSelectionResponse | null>(null);
  const [selectedKBs, setSelectedKBs] = useState<string[]>([]);
  const [pendingQuery, setPendingQuery] = useState('');
  const [isSelectingKB, setIsSelectingKB] = useState(false);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError('');
    setShowKBSelector(false);
    setKbSelectionData(null);
    setSelectedKBs([]);
    setPendingQuery('');
  }, []);

  return {
    messages,
    setMessages,
    inputMessage,
    setInputMessage,
    useSkill,
    setUseSkill,
    isLoading,
    setIsLoading,
    error,
    setError,
    showConfig,
    setShowConfig,
    config,
    setConfig,
    showKBSelector,
    setShowKBSelector,
    kbSelectionData,
    setKbSelectionData,
    selectedKBs,
    setSelectedKBs,
    pendingQuery,
    setPendingQuery,
    isSelectingKB,
    setIsSelectingKB,
    messagesEndRef,
    scrollToBottom,
    clearChat
  };
}
