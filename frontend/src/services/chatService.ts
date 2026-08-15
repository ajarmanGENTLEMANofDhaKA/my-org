import { apiClient } from './api';
import { API_ENDPOINTS } from '@/config/api';
import type { ChatRequest, ChatResponse } from '@/types/api';

/**
 * Chat Service
 * Handles RAG/chat-related API calls
 */
export const chatService = {
    /**
     * Send a chat message and get AI response
     */
    async sendMessage(projectId: string, query: string): Promise<ChatResponse> {
        const request: ChatRequest = {
            query,
            limit: 5,
            RAGFusion: false
        };
        return apiClient.post<ChatResponse>(API_ENDPOINTS.chatAnswer(projectId), request);
    },
};
