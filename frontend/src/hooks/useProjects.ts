import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectService } from '@/services';
import type { Project, CreateProjectRequest } from '@/types/api';

export const useProjects = () => {
    return useQuery({
        queryKey: ['projects'],
        queryFn: () => projectService.getAll(),
    });
};

export const useProject = (id: string) => {
    return useQuery({
        queryKey: ['projects', id],
        queryFn: () => projectService.getById(id),
        enabled: !!id,
    });
};

export const useCreateProject = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: CreateProjectRequest) => projectService.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
        },
    });
};

export const useUpdateProject = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<CreateProjectRequest> }) =>
            projectService.update(id, data),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
            queryClient.invalidateQueries({ queryKey: ['projects', variables.id] });
        },
    });
};

export const useDeleteProject = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: string) => projectService.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
        },
    });
};

export const useRenameProject = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, newName }: { id: string; newName: string }) =>
            projectService.rename(id, newName),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
            queryClient.invalidateQueries({ queryKey: ['projects', variables.id] });
        },
    });
};
