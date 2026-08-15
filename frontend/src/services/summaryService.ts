import { apiClient } from './api';
import { API_ENDPOINTS } from '@/config/api';
import type { Summary, GenerateSummaryRequest, UpdateSummaryRequest } from '@/types/api';

/**
 * Summary Service
 * Handles summary-related API calls
 */
export const summaryService = {
    /**
     * Get all summaries for a project
     */
    async getAll(projectId: string): Promise<Summary[]> {
        // Get summaries from the assets endpoint which returns both papers and summaries
        const response = await apiClient.get<{ papers: any[]; summaries: Summary[] }>(`/projects/${projectId}/assets`);
        return response.summaries || [];
    },

    /**
     * Get a single summary by ID
     */
    async getById(projectId: string, paperId: string, summaryId: string): Promise<Summary> {
        return apiClient.get<Summary>(
            API_ENDPOINTS.summaryById(projectId, paperId, summaryId)
        );
    },

    /**
     * Generate a new summary
     */
    async generate(projectId: string, paperId: string, request: GenerateSummaryRequest): Promise<any> {
        const response = await apiClient.post<any>(
            `/projects/${projectId}/papers/${paperId}/summaries/create`,
            request
        );
        return response.summary || response;
    },

    /**
     * Update an existing summary
     */
    async update(
        projectId: string,
        paperId: string,
        summaryId: string,
        data: UpdateSummaryRequest
    ): Promise<Summary> {
        return apiClient.put<Summary>(
            API_ENDPOINTS.summaryById(projectId, paperId, summaryId),
            data
        );
    },

    /**
     * Delete a summary
     */
    async delete(projectId: string, paperId: string, summaryId: string): Promise<void> {
        return apiClient.delete<void>(
            API_ENDPOINTS.summaryById(projectId, paperId, summaryId)
        );
    },

    /**
     * Rename a summary
     */
    async rename(projectId: string, paperId: string, summaryId: string, newName: string): Promise<Summary> {
        return apiClient.put<Summary>(
            `/projects/${projectId}/papers/${paperId}/summaries/${summaryId}/rename`,
            { new_name: newName }
        );
    },

    /**
     * View/download summary content
     */
    async view(projectId: string, paperId: string, summaryId: string): Promise<string> {
        return apiClient.get<string>(
            `/projects/${projectId}/papers/${paperId}/summaries/view/${summaryId}`
        );
    },
};
