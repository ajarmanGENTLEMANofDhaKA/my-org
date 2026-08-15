import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
    DropdownMenuSeparator
} from "@/components/ui/dropdown-menu";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { BookOpen, Upload, FileText, MessageSquare, Search, Sparkles, MoreVertical, ArrowLeft, Loader2, Trash2, Download, FileType, Languages, Lightbulb, ChevronDown, Edit } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { usePapers, useUploadPaper, useDeletePaper, useRenamePaper } from "@/hooks/usePapers";
import { useSummaries, useGenerateSummary, useDeleteSummary } from "@/hooks/useSummaries";
import { useChat } from "@/hooks/useChat";
import { useProject } from "@/hooks/useProjects";
import { translatorService, explainerService, paperService } from "@/services";
import type { Paper, Summary } from "@/types/api";

const Workspace = () => {
    const { workspaceId } = useParams();
    const { toast } = useToast();
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Fetch project details
    const { data: project } = useProject(workspaceId || "");

    // Fetch papers and summaries from API
    const { data: papers, isLoading: loadingPapers, error: papersError } = usePapers(workspaceId || "");
    const { data: summaries, isLoading: loadingSummaries } = useSummaries(workspaceId || "");
    const uploadPaper = useUploadPaper(workspaceId || "");
    const deletePaper = useDeletePaper(workspaceId || "");
    const renamePaper = useRenamePaper(workspaceId || "");

    // Chat functionality
    const { messages, sendMessage, isLoading: chatLoading } = useChat(workspaceId || "");

    const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
    const [selectedItem, setSelectedItem] = useState<{ type: 'paper' | 'summary'; id: string; name: string } | null>(null);
    const [inputMessage, setInputMessage] = useState("");
    const [searchQuery, setSearchQuery] = useState("");
    const [paperToDelete, setPaperToDelete] = useState<Paper | null>(null);
    const [summaryToDelete, setSummaryToDelete] = useState<Summary | null>(null);
    const [isGenerateSummaryDialogOpen, setIsGenerateSummaryDialogOpen] = useState(false);
    const [summaryName, setSummaryName] = useState("");
    const [pdfUrl, setPdfUrl] = useState<string | null>(null);
    const [isLoadingPdf, setIsLoadingPdf] = useState(false);
    const [isRenamePaperDialogOpen, setIsRenamePaperDialogOpen] = useState(false);
    const [paperToRename, setPaperToRename] = useState<Paper | null>(null);
    const [newPaperName, setNewPaperName] = useState("");

    // Toggle states for collapsible sections
    const [isPapersExpanded, setIsPapersExpanded] = useState(true);
    const [isSummariesExpanded, setIsSummariesExpanded] = useState(true);

    // Text selection context menu state
    const [selectedText, setSelectedText] = useState("");
    const [contextMenuPosition, setContextMenuPosition] = useState<{ x: number; y: number } | null>(null);
    const [showTranslateDialog, setShowTranslateDialog] = useState(false);
    const [showExplainDialog, setShowExplainDialog] = useState(false);
    const [targetLanguage, setTargetLanguage] = useState("es");
    const [translatedText, setTranslatedText] = useState("");
    const [explanation, setExplanation] = useState("");
    const [isTranslating, setIsTranslating] = useState(false);
    const [isExplaining, setIsExplaining] = useState(false);

    const generateSummary = useGenerateSummary(workspaceId || "", selectedPaper?._id || "");
    const deleteSummary = useDeleteSummary(workspaceId || "", selectedPaper?._id || "");

    // Load PDF when paper is selected
    const loadPdf = async (paper: Paper) => {
        if (!workspaceId) return;

        setIsLoadingPdf(true);
        try {
            const blob = await paperService.view(workspaceId, paper._id);
            const url = URL.createObjectURL(blob);

            // Revoke previous URL to prevent memory leaks
            if (pdfUrl) {
                URL.revokeObjectURL(pdfUrl);
            }

            setPdfUrl(url);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to load PDF. Please try again.",
                variant: "destructive"
            });
        } finally {
            setIsLoadingPdf(false);
        }
    };

    // Handle paper selection
    const handleSelectPaper = (paper: Paper) => {
        setSelectedPaper(paper);
        setSelectedItem({ type: 'paper', id: paper._id, name: paper.paper_name });
        loadPdf(paper);
    };

    // Handle paper download
    const handleDownloadPaper = async (paper: Paper) => {
        if (!workspaceId) return;

        try {
            const blob = await paperService.view(workspaceId, paper._id);
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `${paper.paper_name}.pdf`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);

            toast({
                title: "Success",
                description: "Paper downloaded successfully!",
            });
        } catch (error) {
            toast({
                title: "Download failed",
                description: error instanceof Error ? error.message : "Failed to download paper.",
                variant: "destructive",
            });
        }
    };

    // Handle rename paper dialog open
    const handleOpenRenamePaperDialog = (paper: Paper) => {
        setPaperToRename(paper);
        setNewPaperName(paper.paper_name);
        setIsRenamePaperDialogOpen(true);
    };

    // Handle paper rename
    const handleRenamePaper = async () => {
        if (!paperToRename) return;

        if (!newPaperName.trim()) {
            toast({
                title: "Error",
                description: "Paper name is required.",
                variant: "destructive",
            });
            return;
        }

        try {
            await renamePaper.mutateAsync({
                paperId: paperToRename._id,
                newName: newPaperName
            });

            // Update selected paper if it was renamed
            if (selectedPaper?._id === paperToRename._id) {
                setSelectedPaper({ ...selectedPaper, paper_name: newPaperName });
                setSelectedItem({ type: 'paper', id: selectedPaper._id, name: newPaperName });
            }

            toast({
                title: "Success",
                description: "Paper renamed successfully!",
            });
            setIsRenamePaperDialogOpen(false);
            setPaperToRename(null);
            setNewPaperName("");
        } catch (error) {
            toast({
                title: "Rename failed",
                description: error instanceof Error ? error.message : "Failed to rename paper.",
                variant: "destructive",
            });
        }
    };

    const handleSendMessage = () => {
        if (!inputMessage.trim()) return;

        sendMessage(inputMessage);
        setInputMessage("");
    };

    const handleTextSelection = () => {
        const selection = window.getSelection();
        const text = selection?.toString().trim();

        if (text && text.length > 0) {
            setSelectedText(text);
            const range = selection?.getRangeAt(0);
            const rect = range?.getBoundingClientRect();

            if (rect) {
                setContextMenuPosition({
                    x: rect.left + rect.width / 2,
                    y: rect.bottom + window.scrollY + 10
                });
            }
        } else {
            setContextMenuPosition(null);
        }
    };

    const handleTranslate = async () => {
        if (!selectedText) return;

        setShowTranslateDialog(true);
        setIsTranslating(true);

        try {
            const result = await translatorService.translate({
                text: selectedText,
                target_language: targetLanguage
            });
            setTranslatedText(result.translated_text || "Translation completed");
        } catch (error) {
            toast({
                title: "Translation Failed",
                description: error instanceof Error ? error.message : "Failed to translate text",
                variant: "destructive"
            });
        } finally {
            setIsTranslating(false);
            setContextMenuPosition(null);
        }
    };

    const handleExplain = async () => {
        if (!selectedText) return;

        setShowExplainDialog(true);
        setIsExplaining(true);

        try {
            const result = await explainerService.explain({
                text: selectedText,
                context: selectedItem?.name || ""
            });
            setExplanation(result.explanation || "Explanation completed");
        } catch (error) {
            toast({
                title: "Explanation Failed",
                description: error instanceof Error ? error.message : "Failed to explain text",
                variant: "destructive"
            });
        } finally {
            setIsExplaining(false);
            setContextMenuPosition(null);
        }
    };

    const closeContextMenu = () => {
        setContextMenuPosition(null);
        window.getSelection()?.removeAllRanges();
    };

    // Close context menu on scroll or click outside
    useEffect(() => {
        const handleClickOutside = () => {
            if (contextMenuPosition) {
                closeContextMenu();
            }
        };

        document.addEventListener('click', handleClickOutside);
        document.addEventListener('scroll', closeContextMenu);

        return () => {
            document.removeEventListener('click', handleClickOutside);
            document.removeEventListener('scroll', closeContextMenu);
        };
    }, [contextMenuPosition]);

    const handleUpload = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        if (file.type !== "application/pdf") {
            toast({
                title: "Invalid file type",
                description: "Please upload a PDF file.",
                variant: "destructive",
            });
            return;
        }

        try {
            await uploadPaper.mutateAsync(file);
            toast({
                title: "Success",
                description: `${file.name} uploaded successfully!`,
            });
            // Reset file input
            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        } catch (error) {
            toast({
                title: "Upload failed",
                description: error instanceof Error ? error.message : "Failed to upload paper.",
                variant: "destructive",
            });
        }
    };

    // Set first paper as selected when papers load
    useEffect(() => {
        if (papers && papers.length > 0 && !selectedPaper) {
            setSelectedPaper(papers[0]);
        }
    }, [papers]);

    // Handle paper deletion
    const handleDeletePaper = async () => {
        if (!paperToDelete) return;

        try {
            await deletePaper.mutateAsync(paperToDelete._id);

            // If the deleted paper was selected, clear selection
            if (selectedPaper?._id === paperToDelete._id) {
                setSelectedPaper(null);
                setSelectedItem(null);
            }

            toast({
                title: "Success",
                description: "Paper deleted successfully!",
            });
            setPaperToDelete(null);
        } catch (error) {
            toast({
                title: "Delete failed",
                description: error instanceof Error ? error.message : "Failed to delete paper.",
                variant: "destructive",
            });
        }
    };

    // Handle summary generation
    const handleOpenGenerateSummaryDialog = () => {
        setSummaryName("");
        setIsGenerateSummaryDialogOpen(true);
    };

    const handleGenerateSummary = async () => {
        if (!summaryName.trim()) {
            toast({
                title: "Error",
                description: "Please enter a summary name.",
                variant: "destructive",
            });
            return;
        }

        try {
            await generateSummary.mutateAsync({ summary_name: summaryName });
            toast({
                title: "Success",
                description: "Summary generated successfully!",
            });
            setIsGenerateSummaryDialogOpen(false);
            setSummaryName("");
        } catch (error) {
            toast({
                title: "Generation failed",
                description: error instanceof Error ? error.message : "Failed to generate summary.",
                variant: "destructive",
            });
        }
    };

    // Handle summary deletion
    const handleDeleteSummary = async () => {
        if (!summaryToDelete) return;

        try {
            await deleteSummary.mutateAsync(summaryToDelete._id);

            // If the deleted summary was selected, clear selection
            if (selectedItem?.type === 'summary' && selectedItem.id === summaryToDelete._id) {
                setSelectedItem(null);
            }

            toast({
                title: "Success",
                description: "Summary deleted successfully!",
            });
            setSummaryToDelete(null);
        } catch (error) {
            toast({
                title: "Delete failed",
                description: error instanceof Error ? error.message : "Failed to delete summary.",
                variant: "destructive",
            });
        }
    };

    // Filter items based on search
    const filteredPapers = papers?.filter(paper =>
        (paper.title || paper.paper_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (paper.filename || paper.paper_name || '').toLowerCase().includes(searchQuery.toLowerCase())
    ) || [];

    const filteredSummaries = summaries?.filter(summary =>
        summary.summary_name.toLowerCase().includes(searchQuery.toLowerCase())
    ) || [];

    // Set first paper as selected when papers load
    useEffect(() => {
        if (papers && papers.length > 0 && !selectedPaper) {
            handleSelectPaper(papers[0]);
        }
    }, [papers]);

    // Cleanup PDF URL on unmount
    useEffect(() => {
        return () => {
            if (pdfUrl) {
                URL.revokeObjectURL(pdfUrl);
            }
        };
    }, [pdfUrl]);

    return (
        <div className="min-h-screen bg-background flex flex-col">
            {/* Hidden file input */}
            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
            />

            {/* Header */}
            <header className="border-b border-border bg-card px-4 py-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link to="/dashboard">
                            <Button variant="ghost" size="icon">
                                <ArrowLeft className="w-5 h-5" />
                            </Button>
                        </Link>
                        <Link to="/" className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                                <BookOpen className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                                Inquiro
                            </span>
                        </Link>
                    </div>
                    <div className="absolute left-1/2 transform -translate-x-1/2">
                        <h1 className="text-lg font-semibold text-foreground">
                            {project?.project_title ? `${project.project_title} Workspace` : "Loading..."}
                        </h1>
                    </div>
                </div>
            </header>

            {/* Main Content - 3 Column Layout */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left: File Explorer (Papers & Summaries) */}
                <div className="w-80 border-r border-border bg-card flex flex-col">
                    <div className="p-4 border-b border-border space-y-3">
                        <Button
                            onClick={handleUpload}
                            disabled={uploadPaper.isPending}
                            className="w-full bg-primary hover:bg-primary-hover"
                        >
                            {uploadPaper.isPending ? (
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                                <Upload className="w-4 h-4 mr-2" />
                            )}
                            Upload Paper
                        </Button>
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                            <Input
                                placeholder="Search files..."
                                className="pl-10"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                    </div>

                    <ScrollArea className="flex-1">
                        {loadingPapers || loadingSummaries ? (
                            <div className="flex items-center justify-center py-8">
                                <Loader2 className="w-6 h-6 animate-spin text-primary" />
                            </div>
                        ) : papersError ? (
                            <div className="p-4 text-center text-sm text-destructive">
                                Failed to load files
                            </div>
                        ) : filteredPapers.length === 0 && filteredSummaries.length === 0 ? (
                            <div className="p-4 text-center text-sm text-muted-foreground">
                                {searchQuery ? "No files found" : "No papers yet. Upload your first paper!"}
                            </div>
                        ) : (
                            <div className="p-4 space-y-4">
                                {/* Papers Section */}
                                {filteredPapers.length > 0 && (
                                    <div>
                                        <h3 className="text-xs font-semibold text-muted-foreground uppercase mb-2 px-2">
                                            Papers ({filteredPapers.length})
                                        </h3>
                                        <div className="space-y-2">
                                            {filteredPapers.map((paper) => (
                                                <Card
                                                    key={paper._id}
                                                    className={`cursor-pointer transition-all hover:shadow-md ${selectedItem?.type === 'paper' && selectedItem.id === paper._id
                                                        ? 'border-primary bg-primary/5'
                                                        : ''
                                                        }`}
                                                >
                                                    <CardContent className="p-3">
                                                        <div className="flex items-start gap-2">
                                                            <div
                                                                className="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/20 flex items-center justify-center flex-shrink-0"
                                                                onClick={() => handleSelectPaper(paper)}
                                                            >
                                                                <FileText className="w-4 h-4 text-red-600 dark:text-red-400" />
                                                            </div>
                                                            <div
                                                                className="flex-1 min-w-0"
                                                                onClick={() => handleSelectPaper(paper)}
                                                            >
                                                                <h4 className="font-medium text-xs truncate">{paper.paper_name}</h4>
                                                                <span className="text-[10px] text-muted-foreground">
                                                                    PDF • {(paper.paper_size / 1024 / 1024).toFixed(1)} MB
                                                                </span>
                                                            </div>
                                                            <DropdownMenu>
                                                                <DropdownMenuTrigger asChild>
                                                                    <Button
                                                                        variant="ghost"
                                                                        size="icon"
                                                                        className="h-6 w-6"
                                                                        onClick={(e) => e.stopPropagation()}
                                                                    >
                                                                        <MoreVertical className="w-3 h-3" />
                                                                    </Button>
                                                                </DropdownMenuTrigger>
                                                                <DropdownMenuContent align="end">
                                                                    <DropdownMenuItem onClick={() => handleDownloadPaper(paper)}>
                                                                        <Download className="w-4 h-4 mr-2" />
                                                                        Download
                                                                    </DropdownMenuItem>
                                                                    <DropdownMenuItem onClick={() => handleOpenRenamePaperDialog(paper)}>
                                                                        <Edit className="w-4 h-4 mr-2" />
                                                                        Rename
                                                                    </DropdownMenuItem>
                                                                    <DropdownMenuSeparator />
                                                                    <DropdownMenuItem
                                                                        className="text-destructive focus:text-destructive"
                                                                        onClick={() => setPaperToDelete(paper)}
                                                                    >
                                                                        <Trash2 className="w-4 h-4 mr-2" />
                                                                        Delete
                                                                    </DropdownMenuItem>
                                                                </DropdownMenuContent>
                                                            </DropdownMenu>
                                                        </div>
                                                    </CardContent>
                                                </Card>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Summaries Section */}
                                {filteredSummaries.length > 0 && (
                                    <div>
                                        <h3 className="text-xs font-semibold text-muted-foreground uppercase mb-2 px-2">
                                            Summaries ({filteredSummaries.length})
                                        </h3>
                                        <div className="space-y-2">
                                            {filteredSummaries.map((summary) => (
                                                <Card
                                                    key={summary._id}
                                                    className={`cursor-pointer transition-all hover:shadow-md ${selectedItem?.type === 'summary' && selectedItem.id === summary._id
                                                        ? 'border-primary bg-primary/5'
                                                        : ''
                                                        }`}
                                                >
                                                    <CardContent className="p-3">
                                                        <div className="flex items-start gap-2">
                                                            <div
                                                                className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center flex-shrink-0"
                                                                onClick={() => {
                                                                    setSelectedItem({ type: 'summary', id: summary._id, name: summary.summary_name });
                                                                }}
                                                            >
                                                                <FileType className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                                                            </div>
                                                            <div
                                                                className="flex-1 min-w-0"
                                                                onClick={() => {
                                                                    setSelectedItem({ type: 'summary', id: summary._id, name: summary.summary_name });
                                                                }}
                                                            >
                                                                <h4 className="font-medium text-xs truncate">{summary.summary_name}</h4>
                                                                <span className="text-[10px] text-muted-foreground">
                                                                    MD • {(summary.summary_size / 1024).toFixed(1)} KB
                                                                </span>
                                                            </div>
                                                            <DropdownMenu>
                                                                <DropdownMenuTrigger asChild>
                                                                    <Button
                                                                        variant="ghost"
                                                                        size="icon"
                                                                        className="h-6 w-6"
                                                                        onClick={(e) => e.stopPropagation()}
                                                                    >
                                                                        <MoreVertical className="w-3 h-3" />
                                                                    </Button>
                                                                </DropdownMenuTrigger>
                                                                <DropdownMenuContent align="end">
                                                                    <DropdownMenuItem onClick={() => {
                                                                        setSelectedItem({ type: 'summary', id: summary._id, name: summary.summary_name });
                                                                    }}>
                                                                        <FileType className="w-4 h-4 mr-2" />
                                                                        View Summary
                                                                    </DropdownMenuItem>
                                                                    <DropdownMenuItem>
                                                                        <Download className="w-4 h-4 mr-2" />
                                                                        Download
                                                                    </DropdownMenuItem>
                                                                    <DropdownMenuSeparator />
                                                                    <DropdownMenuItem
                                                                        className="text-destructive focus:text-destructive"
                                                                        onClick={() => setSummaryToDelete(summary)}
                                                                    >
                                                                        <Trash2 className="w-4 h-4 mr-2" />
                                                                        Delete
                                                                    </DropdownMenuItem>
                                                                </DropdownMenuContent>
                                                            </DropdownMenu>
                                                        </div>
                                                    </CardContent>
                                                </Card>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </ScrollArea>
                </div>

                {/* Middle: File Viewer */}
                <div className="flex-1 flex flex-col bg-background">
                    {selectedItem ? (
                        <>
                            <div className="p-4 border-b border-border flex items-start justify-between">
                                <div className="flex-1">
                                    <h2 className="font-semibold text-lg truncate">{selectedItem.name}</h2>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {selectedItem.type === 'paper' && selectedPaper ? (
                                            `PDF Document • Uploaded ${selectedPaper.created_at ? new Date(selectedPaper.created_at).toLocaleDateString() : 'recently'} • ${(selectedPaper.paper_size / 1024 / 1024).toFixed(2)} MB`
                                        ) : (
                                            'Markdown Summary'
                                        )}
                                    </p>
                                </div>
                                {selectedItem.type === 'paper' && selectedPaper && (
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="ml-4"
                                        onClick={handleOpenGenerateSummaryDialog}
                                        disabled={generateSummary.isPending}
                                    >
                                        {generateSummary.isPending ? (
                                            <>
                                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                                Generating...
                                            </>
                                        ) : (
                                            <>
                                                <Sparkles className="w-4 h-4 mr-2" />
                                                Generate Summary
                                            </>
                                        )}
                                    </Button>
                                )}
                            </div>

                            <ScrollArea className="flex-1 p-6">
                                {selectedItem.type === 'paper' ? (
                                    isLoadingPdf ? (
                                        <div className="flex items-center justify-center h-full">
                                            <Loader2 className="w-12 h-12 animate-spin text-primary" />
                                        </div>
                                    ) : pdfUrl ? (
                                        <div className="h-full w-full">
                                            <iframe
                                                src={pdfUrl}
                                                className="w-full h-full rounded-lg border border-border"
                                                title={selectedItem.name}
                                                style={{ minHeight: '600px' }}
                                            />
                                        </div>
                                    ) : (
                                        <div
                                            className="rounded-lg bg-muted border border-border p-8"
                                            onMouseUp={handleTextSelection}
                                        >
                                            <div className="text-center text-muted-foreground">
                                                <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                                                    <FileText className="w-10 h-10 text-primary" />
                                                </div>
                                                <h3 className="font-semibold text-lg mb-2">PDF Viewer</h3>
                                                <p className="text-sm mb-2 font-medium text-foreground">📄 {selectedItem.name}</p>
                                                {selectedPaper && (
                                                    <p className="text-xs mb-4">
                                                        Size: {(selectedPaper.paper_size / 1024 / 1024).toFixed(2)} MB •
                                                        Uploaded: {selectedPaper.created_at ? new Date(selectedPaper.created_at).toLocaleDateString() : 'recently'}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    )
                                ) : (
                                    <div
                                        className="rounded-lg bg-muted border border-border p-8"
                                        onMouseUp={handleTextSelection}
                                    >
                                        <div className="text-center text-muted-foreground">
                                            <div className="w-20 h-20 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
                                                <FileType className="w-10 h-10 text-accent" />
                                            </div>
                                            <h3 className="font-semibold text-lg mb-2">Summary Viewer</h3>
                                            <p className="text-sm mb-4 font-medium text-foreground">📝 {selectedItem.name}</p>
                                        </div>
                                    </div>
                                )}
                            </ScrollArea>
                        </>
                    ) : (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center text-muted-foreground">
                                <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                                <h3 className="font-semibold text-lg mb-2">No File Selected</h3>
                                <p className="text-sm">Select a paper or summary from the file explorer to view its details</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right: AI Chat */}
                <div className="w-96 border-l border-border bg-card flex flex-col">
                    <div className="p-4 border-b border-border">
                        <h3 className="font-semibold flex items-center gap-2">
                            <MessageSquare className="w-5 h-5 text-primary" />
                            Inquiro Assistant
                        </h3>
                    </div>

                    <ScrollArea className="flex-1 p-4">
                        <div className="space-y-4">
                            {messages.map((message, index) => (
                                <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div
                                        className={`max-w-[85%] rounded-2xl px-4 py-3 ${message.role === 'user'
                                            ? 'bg-primary text-primary-foreground'
                                            : 'bg-secondary text-foreground'
                                            }`}
                                    >
                                        <p className="text-sm leading-relaxed">{message.content}</p>
                                    </div>
                                </div>
                            ))}
                            {chatLoading && (
                                <div className="flex justify-start">
                                    <div className="bg-secondary text-foreground rounded-2xl px-4 py-3">
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                    </div>
                                </div>
                            )}
                        </div>
                    </ScrollArea>

                    <div className="p-4 border-t border-border">
                        <div className="flex gap-2">
                            <Input
                                placeholder="Ask about your papers..."
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && !chatLoading && handleSendMessage()}
                                disabled={chatLoading}
                            />
                            <Button
                                onClick={handleSendMessage}
                                disabled={chatLoading || !inputMessage.trim()}
                                className="bg-primary hover:bg-primary-hover"
                            >
                                {chatLoading ? (
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                    <MessageSquare className="w-4 h-4" />
                                )}
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Delete Paper Confirmation Dialog */}
            <AlertDialog open={!!paperToDelete} onOpenChange={(open) => !open && setPaperToDelete(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Delete Paper</AlertDialogTitle>
                        <AlertDialogDescription>
                            Are you sure you want to delete "{paperToDelete?.paper_name}"? This action cannot be undone.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={handleDeletePaper}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            disabled={deletePaper.isPending}
                        >
                            {deletePaper.isPending ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Deleting...
                                </>
                            ) : (
                                'Delete'
                            )}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

            {/* Delete Summary Confirmation Dialog */}
            <AlertDialog open={!!summaryToDelete} onOpenChange={(open) => !open && setSummaryToDelete(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Delete Summary</AlertDialogTitle>
                        <AlertDialogDescription>
                            Are you sure you want to delete "{summaryToDelete?.summary_name}"? This action cannot be undone.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={handleDeleteSummary}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            disabled={deleteSummary.isPending}
                        >
                            {deleteSummary.isPending ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Deleting...
                                </>
                            ) : (
                                'Delete'
                            )}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

            {/* Generate Summary Dialog */}
            <Dialog open={isGenerateSummaryDialogOpen} onOpenChange={setIsGenerateSummaryDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Generate Summary</DialogTitle>
                        <DialogDescription>
                            Enter a name for the summary that will be generated from this paper.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="summary-name">Summary Name *</Label>
                            <Input
                                id="summary-name"
                                placeholder="e.g., Research Summary, Key Findings"
                                value={summaryName}
                                onChange={(e) => setSummaryName(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && !generateSummary.isPending && handleGenerateSummary()}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsGenerateSummaryDialogOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleGenerateSummary} disabled={generateSummary.isPending || !summaryName.trim()}>
                            {generateSummary.isPending ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-4 h-4 mr-2" />
                                    Generate
                                </>
                            )}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Rename Paper Dialog */}
            <Dialog open={isRenamePaperDialogOpen} onOpenChange={setIsRenamePaperDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Rename Paper</DialogTitle>
                        <DialogDescription>
                            Enter a new name for this paper.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="paper-name">Paper Name *</Label>
                            <Input
                                id="paper-name"
                                placeholder="e.g., Research Paper, Article"
                                value={newPaperName}
                                onChange={(e) => setNewPaperName(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && !renamePaper.isPending && handleRenamePaper()}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsRenamePaperDialogOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleRenamePaper} disabled={renamePaper.isPending || !newPaperName.trim()}>
                            {renamePaper.isPending ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Renaming...
                                </>
                            ) : (
                                <>
                                    <Edit className="w-4 h-4 mr-2" />
                                    Rename
                                </>
                            )}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Text Selection Context Menu */}
            {contextMenuPosition && (
                <div
                    className="fixed z-50 bg-card border border-border rounded-lg shadow-lg p-1"
                    style={{
                        left: `${contextMenuPosition.x}px`,
                        top: `${contextMenuPosition.y}px`,
                        transform: 'translateX(-50%)'
                    }}
                    onClick={(e) => e.stopPropagation()}
                >
                    <Button
                        variant="ghost"
                        size="sm"
                        className="w-full justify-start"
                        onClick={handleTranslate}
                    >
                        <Languages className="w-4 h-4 mr-2" />
                        Translate
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        className="w-full justify-start"
                        onClick={handleExplain}
                    >
                        <Lightbulb className="w-4 h-4 mr-2" />
                        Explain
                    </Button>
                </div>
            )}

            {/* Translation Dialog */}
            <Dialog open={showTranslateDialog} onOpenChange={setShowTranslateDialog}>
                <DialogContent className="sm:max-w-[600px]">
                    <DialogHeader>
                        <DialogTitle>Translation</DialogTitle>
                        <DialogDescription>
                            Translate the selected text to your preferred language
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label>Selected Text</Label>
                            <div className="p-3 bg-muted rounded-md text-sm max-h-32 overflow-y-auto">
                                {selectedText}
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="target-language">Target Language</Label>
                            <Select value={targetLanguage} onValueChange={setTargetLanguage}>
                                <SelectTrigger id="target-language">
                                    <SelectValue placeholder="Select language" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="es">Spanish</SelectItem>
                                    <SelectItem value="fr">French</SelectItem>
                                    <SelectItem value="de">German</SelectItem>
                                    <SelectItem value="it">Italian</SelectItem>
                                    <SelectItem value="pt">Portuguese</SelectItem>
                                    <SelectItem value="ru">Russian</SelectItem>
                                    <SelectItem value="zh">Chinese</SelectItem>
                                    <SelectItem value="ja">Japanese</SelectItem>
                                    <SelectItem value="ko">Korean</SelectItem>
                                    <SelectItem value="ar">Arabic</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        {isTranslating ? (
                            <div className="flex items-center justify-center py-8">
                                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                            </div>
                        ) : translatedText ? (
                            <div className="space-y-2">
                                <Label>Translation</Label>
                                <div className="p-3 bg-primary/10 border border-primary/20 rounded-md text-sm max-h-64 overflow-y-auto">
                                    {translatedText}
                                </div>
                            </div>
                        ) : null}
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowTranslateDialog(false)}>
                            Close
                        </Button>
                        {!isTranslating && !translatedText && (
                            <Button onClick={handleTranslate}>
                                <Languages className="w-4 h-4 mr-2" />
                                Translate
                            </Button>
                        )}
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Explanation Dialog */}
            <Dialog open={showExplainDialog} onOpenChange={setShowExplainDialog}>
                <DialogContent className="sm:max-w-[600px]">
                    <DialogHeader>
                        <DialogTitle>Explanation</DialogTitle>
                        <DialogDescription>
                            AI-powered explanation of the selected text
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label>Selected Text</Label>
                            <div className="p-3 bg-muted rounded-md text-sm max-h-32 overflow-y-auto">
                                {selectedText}
                            </div>
                        </div>
                        {isExplaining ? (
                            <div className="flex items-center justify-center py-8">
                                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                            </div>
                        ) : explanation ? (
                            <div className="space-y-2">
                                <Label>Explanation</Label>
                                <div className="p-3 bg-accent/10 border border-accent/20 rounded-md text-sm max-h-64 overflow-y-auto whitespace-pre-wrap">
                                    {explanation}
                                </div>
                            </div>
                        ) : null}
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowExplainDialog(false)}>
                            Close
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Workspace;
