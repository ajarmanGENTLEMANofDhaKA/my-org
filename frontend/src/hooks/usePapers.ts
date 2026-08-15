import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { paperService } from '@/services';

export const usePapers = (projectId: string) => {
    return useQuery({
        queryKey: ['projects', projectId, 'papers'],
        queryFn: () => paperService.getAll(projectId),
        enabled: !!projectId,
    });
};

export const usePaper = (projectId: string, paperId: string) => {
    return useQuery({
        queryKey: ['projects', projectId, 'papers', paperId],
        queryFn: () => paperService.getById(projectId, paperId),
        enabled: !!projectId && !!paperId,
    });
};

export const useUploadPaper = (projectId: string) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (file: File) => paperService.upload(projectId, file),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] });
        },
    });
};

export const useDeletePaper = (projectId: string) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (paperId: string) => paperService.delete(projectId, paperId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] });
        },
    });
};

export const useRenamePaper = (projectId: string) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ paperId, newName }: { paperId: string; newName: string }) =>
            paperService.rename(projectId, paperId, newName),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] });
        },
    });
};
