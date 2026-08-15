/**
 * API Type Definitions
 * Types matching the backend API schemas
 */

// Project Types
export interface Project {
    _id: string;
    project_title: string;
    created_at?: string;
    updated_at?: string;
}

export interface CreateProjectRequest {
    project_title: string;
}

// Paper Types
export interface Paper {
    _id: string;
    paper_project_id: string;
    paper_name: string;
    paper_type: string;
    paper_size: number;
    created_at?: string;
    updated_at?: string;

    // For display compatibility
    title?: string;
    filename?: string;
    file_size?: number;
    upload_date?: string;
}

export interface UploadPaperResponse {
    message: string;
    paper: Paper;
    inserted_chunks_count: number;
}

// Summary Types
export interface Summary {
    _id: string;
    summary_paper_id: string;
    summary_project_id: string;
    summary_name: string;
    summary_type: string;
    summary_size: number;
    created_at?: string;
    updated_at?: string;
}

export interface GenerateSummaryRequest {
    summary_name: string;
}

export interface UpdateSummaryRequest {
    content: string;
}

// Chat/RAG Types
export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: string;
}

export interface ChatRequest {
    query: string;
    limit?: number;
    RAGFusion?: boolean;
}

export interface ChatResponse {
    signal: string;
    answer: string;
}

// Translator Types
export interface TranslateRequest {
    text: string;
    target_language: string;
    source_language?: string;
}

export interface TranslateResponse {
    translated_text: string;
    source_language: string;
    target_language: string;
}

// Explainer Types
export interface ExplainRequest {
    text: string;
    context?: string;
}

export interface ExplainResponse {
    explanation: string;
}

// Health Check
export interface HealthResponse {
    status: string;
    message: string;
    version?: string;
}
