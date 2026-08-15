import { apiClient } from './api';
import { API_ENDPOINTS } from '@/config/api';
import type { TranslateRequest, TranslateResponse, ExplainRequest, ExplainResponse } from '@/types/api';

/**
 * Translator Service
 * Handles text translation
 */
export const translatorService = {
    /**
     * Translate text to target language
     */
    async translate(request: TranslateRequest): Promise<TranslateResponse> {
        return apiClient.post<TranslateResponse>(API_ENDPOINTS.translate, request);
    },
};

/**
 * Explainer Service
 * Handles text explanation
 */
export const explainerService = {
    /**
     * Explain text with optional context
     */
    async explain(request: ExplainRequest): Promise<ExplainResponse> {
        return apiClient.post<ExplainResponse>(API_ENDPOINTS.explain, request);
    },
};
