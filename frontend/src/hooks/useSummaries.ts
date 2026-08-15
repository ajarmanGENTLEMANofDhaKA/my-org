import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { summaryService } from '@/services';
import type { GenerateSummaryRequest, UpdateSummaryRequest } from '@/types/api';

export const useSummaries = (projectId: string) => {
    return useQuery({
        queryKey: ['projects', projectId, 'summaries'],
        queryFn: () => summaryService.getAll(projectId),
        enabled: !!projectId,
    });
};

export const useSummary = (projectId: string, paperId: string, summaryId: string) => {
    return useQuery({
        queryKey: ['projects', projectId, 'papers', paperId, 'summaries', summaryId],
        queryFn: () => summaryService.getById(projectId, paperId, summaryId),
        enabled: !!projectId && !!paperId && !!summaryId,
    });
};

export const useGenerateSummary = (projectId: string, paperId: string) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (request: GenerateSummaryRequest) => summaryService.generate(projectId, paperId, request),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'summaries'] });
            queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers', paperId, 'summaries'] });
        },
    });
};

export const useUpdateSummary = (projectId: string, paperId: string) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ summaryId, data }: { summaryId: string; data: UpdateSummaryRequest }) =>
            summaryService.update(projectId, paperId, summaryId, data),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers', paperId, 'summaries'] });
            queryClient.invalidateQueries({
                queryKey: ['projects', projectId, 'papers', paperId, 'summaries', variables.summaryId]
            });
        },
    });
};

export const useDeleteSummary = (projectId: string, paperId: string) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (summaryId: string) => summaryService.delete(projectId, paperId, summaryId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers', paperId, 'summaries'] });
        },
    });
};

export const useRenameSummary = (projectId: string, paperId: string) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ summaryId, newName }: { summaryId: string; newName: string }) =>
            summaryService.rename(projectId, paperId, summaryId, newName),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'summaries'] });
            queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers', paperId, 'summaries'] });
        },
    });
};
