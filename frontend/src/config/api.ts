// Use environment variable if available, fallback to localhost for local development
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
    // Projects
    projects: '/projects',
    createProject: '/projects/create',
    projectById: (id: string) => `/projects/${id}`,

    // Papers
    papers: (projectId: string) => `/projects/${projectId}/papers`,
    paperById: (projectId: string, paperId: string) => `/projects/${projectId}/papers/${paperId}`,
    paperUpload: (projectId: string) => `/projects/${projectId}/papers/upload-paper`,

    // Summaries
    summaries: (projectId: string, paperId: string) => `/projects/${projectId}/papers/${paperId}/summaries`,
    summaryById: (projectId: string, paperId: string, summaryId: string) =>
        `/projects/${projectId}/papers/${paperId}/summaries/${summaryId}`,

    // RAG/Chat
    chatAnswer: (projectId: string) => `/projects/${projectId}/chat/answer`,
    vdbIndex: (projectId: string) => `/projects/${projectId}/vdb/index`,
    vdbSearch: (projectId: string) => `/projects/${projectId}/vdb/search`,

    // Translator
    translate: '/translator/translate',

    // Explainer
    explain: '/explainer/explain',

    // Welcome
    health: '/welcome',
} as const;
