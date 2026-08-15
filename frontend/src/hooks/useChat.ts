import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { chatService } from '@/services';
import type { ChatMessage } from '@/types/api';

/**
 * Hook to manage chat conversations
 */
export const useChat = (projectId: string) => {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: 'assistant',
            content: "Hello! I'm your AI research assistant. Ask me anything about your papers.",
            timestamp: new Date().toISOString(),
        },
    ]);

    const mutation = useMutation({
        mutationFn: (message: string) => chatService.sendMessage(projectId, message),
        onSuccess: (data, userMessageText) => {
            // Add user message
            const userMessage: ChatMessage = {
                role: 'user',
                content: userMessageText,
                timestamp: new Date().toISOString(),
            };

            // Add assistant response
            const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: data.answer,
                timestamp: new Date().toISOString(),
            };

            setMessages((prev) => [...prev, userMessage, assistantMessage]);
        },
    });

    const sendMessage = (message: string) => {
        mutation.mutate(message);
    };

    const clearMessages = () => {
        setMessages([
            {
                role: 'assistant',
                content: "Hello! I'm your AI research assistant. Ask me anything about your papers.",
                timestamp: new Date().toISOString(),
            },
        ]);
    };

    return {
        messages,
        sendMessage,
        clearMessages,
        isLoading: mutation.isPending,
        error: mutation.error,
    };
};
