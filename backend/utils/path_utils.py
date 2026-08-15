import os
from pathlib import Path

class PathUtils:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.assets_dir = self.base_dir / "assets"
        self.library_dir = self.assets_dir / "library"
        
        # Ensure base directories exist
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.library_dir, exist_ok=True)

    def get_project_dir(self, project_title: str):
        
        project_dir = self.library_dir / project_title
        papers_dir = project_dir / "papers"
        summaries_dir = project_dir / "summaries"

        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(papers_dir, exist_ok=True)
        os.makedirs(summaries_dir, exist_ok=True)
        
        return project_dir, papers_dir, summaries_dir

    def get_paper_path(self, project_title: str, paper_filename: str) -> Path:
        project_dir, papers_dir, _ = self.get_project_dir(project_title=project_title)
        return papers_dir / paper_filename

    def get_summary_path(self, project_title: str, summary_filename: str) -> Path:
        project_dir, _, summaries_dir = self.get_project_dir(project_title=project_title)    
        return summaries_dir / summary_filename

    def get_project_files(self, project_title: str):
        _, papers_dir, summaries_dir = self.get_project_dir(project_title)
        
        paper_files = [f.name for f in papers_dir.glob('*') if f.is_file()]
        summary_files = [f.name for f in summaries_dir.glob('*') if f.is_file()]
        
        return paper_files, summary_files