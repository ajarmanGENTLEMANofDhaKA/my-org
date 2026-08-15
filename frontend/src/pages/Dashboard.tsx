import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { BookOpen, Plus, FolderOpen, Settings, LogOut, Loader2, FileText, File, Trash2 } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { useProjects, useCreateProject, useDeleteProject } from "@/hooks/useProjects";
import { apiClient } from "@/services/api";

interface ProjectAssets {
    papers: number;
    summaries: number;
}

export default function Dashboard() {
    const navigate = useNavigate();
    const { toast } = useToast();
    const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [projectToDelete, setProjectToDelete] = useState<{ id: string; name: string } | null>(null);
    const [newProjectName, setNewProjectName] = useState("");
    const [projectAssets, setProjectAssets] = useState<Record<string, ProjectAssets>>({});
    const { data: projects, isLoading, error } = useProjects();
    const createProject = useCreateProject();
    const deleteProject = useDeleteProject();

    useEffect(() => {
        const fetchAssets = async () => {
            if (!projects || projects.length === 0) return;
            const assetsData: Record<string, ProjectAssets> = {};
            for (const project of projects) {
                try {
                    const response = await apiClient.get<{ papers: any[]; summaries: any[] }>(`/projects/${project._id}/assets`);
                    assetsData[project._id] = { papers: response.papers?.length || 0, summaries: response.summaries?.length || 0 };
                } catch (error) {
                    assetsData[project._id] = { papers: 0, summaries: 0 };
                }
            }
            setProjectAssets(assetsData);
        };
        fetchAssets();
    }, [projects]);

    const handleCreateWorkspace = async () => {
        if (!newProjectName.trim()) {
            toast({ title: "Error", description: "Workspace name is required.", variant: "destructive" });
            return;
        }
        try {
            await createProject.mutateAsync({ project_title: newProjectName });
            toast({ title: "Success", description: "Workspace created successfully!" });
            setIsCreateDialogOpen(false);
            setNewProjectName("");
        } catch (error) {
            toast({ title: "Error", description: error instanceof Error ? error.message : "Failed to create workspace.", variant: "destructive" });
        }
    };

    const handleDeleteWorkspace = async () => {
        if (!projectToDelete) return;
        try {
            await deleteProject.mutateAsync(projectToDelete.id);
            toast({ title: "Success", description: `Workspace "${projectToDelete.name}" deleted successfully!` });
            setIsDeleteDialogOpen(false);
            setProjectToDelete(null);
        } catch (error) {
            toast({ title: "Error", description: error instanceof Error ? error.message : "Failed to delete workspace.", variant: "destructive" });
        }
    };

    const openDeleteDialog = (e: React.MouseEvent, projectId: string, projectName: string) => {
        e.stopPropagation();
        setProjectToDelete({ id: projectId, name: projectName });
        setIsDeleteDialogOpen(true);
    };

    return (
        <div className="min-h-screen bg-background">
            <header className="border-b border-border bg-card">
                <div className="container mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <Link to="/" className="flex items-center gap-2">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                                <BookOpen className="w-6 h-6 text-white" />
                            </div>
                            <span className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Inquiro</span>
                        </Link>
                        <div className="flex items-center gap-4">
                            <Button variant="ghost" size="icon"><Settings className="w-5 h-5" /></Button>
                            <Button variant="ghost" size="icon" onClick={() => navigate("/")}><LogOut className="w-5 h-5" /></Button>
                        </div>
                    </div>
                </div>
            </header>
            <main className="container mx-auto px-4 py-12">
                <div className="mb-8 animate-fade-in">
                    <div className="flex items-center justify-between mb-2">
                        <h1 className="text-4xl font-bold">Your Workspaces</h1>
                        <Button onClick={() => setIsCreateDialogOpen(true)} className="bg-blue-600 hover:bg-blue-700 text-white">
                            <Plus className="w-4 h-4 mr-2" />Create Workspace
                        </Button>
                    </div>
                    <p className="text-muted-foreground text-lg">Select a workspace to start managing your research papers</p>
                </div>
                {isLoading && <div className="flex items-center justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>}
                {error && <div className="text-center py-20"><p className="text-destructive">Failed to load workspaces. Please try again.</p></div>}
                {!isLoading && !error && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {projects?.map((project, index) => {
                            const assets = projectAssets[project._id] || { papers: 0, summaries: 0 };
                            return (
                                <Card key={project._id} className="hover:shadow-lg transition-all cursor-pointer group relative" onClick={() => navigate(`/workspace/${project._id}`)}>
                                    <CardHeader>
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center mb-2">
                                                    <FolderOpen className="w-6 h-6 text-primary" />
                                                </div>
                                                <CardTitle className="group-hover:text-primary transition-colors">{project.project_title}</CardTitle>
                                                <CardDescription>{project.created_at ? `Created ${new Date(project.created_at).toLocaleDateString()}` : 'Research workspace'}</CardDescription>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-destructive/10 hover:text-destructive"
                                                onClick={(e) => openDeleteDialog(e, project._id, project.project_title)}
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-2">
                                            <div className="flex items-center justify-between text-sm">
                                                <span className="text-muted-foreground flex items-center gap-1"><FileText className="w-4 h-4" />Papers</span>
                                                <span className="font-semibold text-primary">{assets.papers}</span>
                                            </div>
                                            <div className="flex items-center justify-between text-sm">
                                                <span className="text-muted-foreground flex items-center gap-1"><File className="w-4 h-4" />Summaries</span>
                                                <span className="font-semibold text-accent">{assets.summaries}</span>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            );
                        })}
                        {projects?.length === 0 && (
                            <div className="col-span-full text-center py-20">
                                <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                                    <FolderOpen className="w-10 h-10 text-primary" />
                                </div>
                                <h3 className="text-xl font-semibold mb-2">No workspaces yet</h3>
                                <p className="text-muted-foreground mb-6">Create your first workspace to start organizing your research</p>
                                <Button onClick={() => setIsCreateDialogOpen(true)} className="bg-blue-600 hover:bg-blue-700 text-white">
                                    <Plus className="w-4 h-4 mr-2" />Create Your First Workspace
                                </Button>
                            </div>
                        )}
                    </div>
                )}
            </main>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Create New Workspace</DialogTitle>
                        <DialogDescription>Give your workspace a name to get started.</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Workspace Name *</Label>
                            <Input id="name" placeholder="e.g., Machine Learning Research" value={newProjectName} onChange={(e) => setNewProjectName(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !createProject.isPending) handleCreateWorkspace(); }} />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>Cancel</Button>
                        <Button onClick={handleCreateWorkspace} disabled={createProject.isPending} className="bg-blue-600 hover:bg-blue-700 text-white">
                            {createProject.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}Create Workspace
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Delete Workspace</DialogTitle>
                        <DialogDescription>
                            Are you sure you want to delete "{projectToDelete?.name}"? This action cannot be undone and will delete all associated papers, summaries, and data.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>Cancel</Button>
                        <Button
                            variant="destructive"
                            onClick={handleDeleteWorkspace}
                            disabled={deleteProject.isPending}
                        >
                            {deleteProject.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                            Delete
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
