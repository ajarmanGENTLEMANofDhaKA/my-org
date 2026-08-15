import { apiClient } from './api';
import { API_ENDPOINTS, API_BASE_URL } from '@/config/api';
import type { Paper, UploadPaperResponse } from '@/types/api';

/**
 * Paper Service
 * Handles all paper-related API calls
 */
export const paperService = {
    /**
     * Get all papers for a project
     */
    async getAll(projectId: string): Promise<Paper[]> {
        // Get papers from the assets endpoint which returns both papers and summaries
        const response = await apiClient.get<{ papers: Paper[]; summaries: any[] }>(`/projects/${projectId}/assets`);
        return response.papers || [];
    },

    /**
     * Get a single paper by ID
     */
    async getById(projectId: string, paperId: string): Promise<Paper> {
        return apiClient.get<Paper>(API_ENDPOINTS.paperById(projectId, paperId));
    },

    /**
     * Upload a new paper
     */
    async upload(projectId: string, file: File): Promise<UploadPaperResponse> {
        return apiClient.uploadFile<UploadPaperResponse>(
            API_ENDPOINTS.paperUpload(projectId),
            file
        );
    },

    /**
     * Delete a paper
     */
    async delete(projectId: string, paperId: string): Promise<void> {
        return apiClient.delete<void>(API_ENDPOINTS.paperById(projectId, paperId));
    },

    /**
     * Rename a paper
     */
    async rename(projectId: string, paperId: string, newName: string): Promise<Paper> {
        return apiClient.put<Paper>(
            `/projects/${projectId}/papers/${paperId}/rename`,
            { new_name: newName }
        );
    },

    /**
     * View/download a paper PDF
     */
    async view(projectId: string, paperId: string): Promise<Blob> {
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/papers/view/${paperId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch paper: ${response.statusText}`);
        }
        return response.blob();
    },
};
