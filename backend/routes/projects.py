from fastapi import APIRouter, status, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from models import ProjectModel, PaperModel, ChunkModel, SummaryModel
from models.db_schemas import Project
from .schema import ProjectRequest
from .schema.requests import RenameRequest
from utils.enums import ResponseSignals
from utils import PathUtils
import shutil
from pathlib import Path
import asyncio

from utils import get_logger
logger = get_logger(__name__)

def _serialize_project(project):
    project_dict = project.dict(by_alias=True, exclude_unset=True)
    project_dict["_id"] = str(project_dict["_id"])
    return project_dict

def _serialize_paper(paper):
    paper_dict = paper.dict(by_alias=True, exclude_unset=True)
    paper_dict["_id"] = str(paper_dict["_id"])
    paper_dict["paper_project_id"] = str(paper_dict["paper_project_id"])
    return paper_dict

def _serialize_summary(summary):
    summary_dict = summary.dict(by_alias=True, exclude_unset=True)
    summary_dict["_id"] = str(summary_dict["_id"])
    summary_dict["summary_project_id"] = str(summary_dict["summary_project_id"])
    summary_dict["summary_paper_id"] = str(summary_dict["summary_paper_id"])
    return summary_dict

project_router = APIRouter()

#List all projects in the database.
@project_router.get("/")
async def list_projects(request: Request):
    logger.info("Incoming request to list all projects.")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    projects = await project_model.get_all_projects()
    if not projects or len(projects) == 0:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "No projects found", "projects": []}
        )
    serialized_projects = [_serialize_project(project) for project in projects]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=serialized_projects
    )

# Create a new project.
@project_router.post("/create")
async def create(request: Request, project_request: ProjectRequest):
    logger.info(f"Incoming request to create project with title: {project_request.project_title}")
    
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    created_project  = await project_model.get_or_create_project(
        Project(project_title=project_request.project_title)
    )
    serialized_project = _serialize_project(created_project)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": ResponseSignals.PROJECT_CREATED_SUCCESS.value,
            "project": serialized_project
        }
    )
# Get project details by ID.
@project_router.get("/{project_id}")
async def get_project(request: Request, project_id: str):
    logger.info(f"Incoming request to get project by ID: {project_id}")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    
    serialized_project = _serialize_project(project)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=serialized_project
    )

# List all assets (papers and summaries) in a project.
@project_router.get('/{project_id}/assets')
async def get_project_assets(request: Request, project_id: str):
    logger.info(f"Incoming request to get assets for project ID: {project_id}")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    papers = await paper_model.get_project_papers(papers_project_id=project_id)

    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    summaries = await summary_model.get_project_summaries(summaries_project_id=project_id)
    
    papers_response = [_serialize_paper(paper) for paper in papers]
    summaries_response = [_serialize_summary(summary) for summary in summaries]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "papers": papers_response,
            "summaries": summaries_response
        }
    )

# Delete all projects.
@project_router.delete("/")
async def delete_all_projects(request: Request):
    logger.info("Incoming request to delete all projects.")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    chunk_model = await ChunkModel.get_instance(db_client=request.app.mongodb_client)
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)

    # Delete all projects, papers, chunks, and summaries
    await project_model.delete_all_projects()
    await paper_model.delete_all_papers()
    await chunk_model.delete_all_chunks()
    await summary_model.delete_all_summaries()

    # Delete all collections in the vector database
    await request.app.vectordb_client.delete_all_collections()
    logger.info("All projects and associated data deleted.")

    # Delete library directory
    path_utils = PathUtils()
    library_folder = path_utils.library_dir    # assets/library/
    if Path(library_folder).exists():
        logger.info(f"Deleting library directory: {library_folder}")
        await asyncio.to_thread(shutil.rmtree, library_folder, ignore_errors=True)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Delete a project.
@project_router.delete("/{project_id}")
async def delete_project(request: Request, project_id: str):
    logger.info(f"Incoming request to delete project by ID: {project_id}")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    chunk_model = await ChunkModel.get_instance(db_client=request.app.mongodb_client)
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    
    # Delete the project, its papers, chunks, and summaries
    await project_model.delete_project(project_id=project_id)
    await paper_model.delete_project_papers(papers_project_id=project_id)
    await chunk_model.delete_project_chunks(chunks_project_id=project_id)
    await summary_model.delete_project_summaries(summaries_project_id=project_id)

    # Delete the corresponding collection in the vdb
    collection_name = f"collection_{project_id}".strip()
    await request.app.vectordb_client.delete_collection(collection_name=collection_name)
    logger.info(f"Project and associated data deleted: {project_id}")

    # Delete project folder from filesystem
    path_utils = PathUtils()
    project_folder, _, _ = path_utils.get_project_dir(project.project_title)
    if Path(project_folder).exists():
        logger.info(f"Deleting project folder: {project_folder}")
        await asyncio.to_thread(shutil.rmtree, project_folder, ignore_errors=True)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Rename a project
@project_router.put("/{project_id}/rename")
async def rename_project(request: Request, project_id: str, rename_request: RenameRequest):
    logger.info(f"Incoming request to rename project: {project_id} to new title: {rename_request.new_name}")
    
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)

    # Check if project exists
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    
    # Check if project with new title already exists
    existing = await project_model.get_project_by_name(project_title=rename_request.new_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with title '{rename_request.new_name}' already exists. Please choose another title."
        )
    
    path_utils = PathUtils()
    old_project_path, _, _ = path_utils.get_project_dir(project.project_title)    # assets/library/{project_title}
    new_project_path, _, _ = path_utils.get_project_dir(rename_request.new_name)

    if Path(new_project_path).exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with title '{rename_request.new_name}' already exists"
        )
    if not Path(old_project_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project folder for '{project.project_title}' does not exist"
        )
    
    try:
        # Rename project folder in filesystem
        await asyncio.to_thread(Path(old_project_path).rename, new_project_path)
        logger.info(f"Project folder renamed successfully: {old_project_path} → {new_project_path}")
        
        # Update project title in database
        project.project_title = rename_request.new_name
        await project_model.update_project(project)
        logger.info(f"Project renamed successfully to {rename_request.new_name}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": ResponseSignals.PROJECT_UPDATED_SUCCESS.value,
                "project": _serialize_project(project)
            }
        )
    except Exception as e:
        logger.error(f"Error renaming project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseSignals.PROJECT_RENAME_FAILED.value
        )