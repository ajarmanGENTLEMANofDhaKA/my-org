import { apiClient } from './api';
import { API_ENDPOINTS } from '@/config/api';
import type { Project, CreateProjectRequest } from '@/types/api';

/**
 * Project Service
 * Handles all project-related API calls
 */
export const projectService = {
    /**
     * Get all projects
     */
    async getAll(): Promise<Project[]> {
        const response = await apiClient.get<any>(API_ENDPOINTS.projects);
        console.log('Projects API response:', response);
        console.log('Is array?', Array.isArray(response));
        console.log('Has projects property?', response && 'projects' in response);

        // Backend returns an array directly when there are projects
        if (Array.isArray(response)) {
            return response;
        }
        // Backend returns {message: "...", projects: []} when there are no projects
        if (response && Array.isArray(response.projects)) {
            return response.projects;
        }
        // Return empty array as fallback
        console.warn('Unexpected projects response format:', response);
        return [];
    },

    /**
     * Get a single project by ID
     */
    async getById(id: string): Promise<Project> {
        return apiClient.get<Project>(API_ENDPOINTS.projectById(id));
    },

    /**
     * Create a new project
     */
    async create(data: CreateProjectRequest): Promise<Project> {
        const response = await apiClient.post<{ message: string; project: Project }>(
            API_ENDPOINTS.createProject,
            { project_title: data.project_title }
        );
        return response.project;
    },

    /**
     * Update an existing project
     */
    async update(id: string, data: Partial<CreateProjectRequest>): Promise<Project> {
        return apiClient.put<Project>(API_ENDPOINTS.projectById(id), data);
    },

    /**
     * Delete a project
     */
    async delete(id: string): Promise<void> {
        return apiClient.delete<void>(API_ENDPOINTS.projectById(id));
    },

    /**
     * Rename a project
     */
    async rename(id: string, newName: string): Promise<Project> {
        return apiClient.put<Project>(
            `/projects/${id}/rename`,
            { new_name: newName }
        );
    },
};
