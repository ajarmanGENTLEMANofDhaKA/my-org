from fastapi import APIRouter, status, Request, HTTPException, Body, Response
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from controllers import SummaryController
from models import ProjectModel, PaperModel, SummaryModel, ChunkModel
from models.db_schemas import Summary
from utils.enums import ResponseSignals, AssetTypeEnums
from routes.schema.requests import RenameRequest, SummaryRequest
from pathlib import Path
import aiofiles
import os

from utils import get_logger 
logger = get_logger(__name__)

def _serialize_summary(summary):
    summary_dict = summary.dict(by_alias=True, exclude_unset=True)
    summary_dict["_id"] = str(summary_dict["_id"])
    summary_dict["summary_project_id"] = str(summary_dict["summary_project_id"])
    summary_dict["summary_paper_id"] = str(summary_dict["summary_paper_id"])
    return summary_dict

summary_router = APIRouter()

# Create a summary.
@summary_router.post("/create")
async def create_summary(request: Request, project_id: str, paper_id: str, summary_request: SummaryRequest):
    logger.info(f"Incoming request to create summary for project_id: {project_id} and paper_id: {paper_id}")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    chunk_model = await ChunkModel.get_instance(db_client=request.app.mongodb_client)

    # Check if the project exists
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.PAPER_NOT_FOUND.value
        )
    # Check if the paper exists
    paper = await paper_model.get_paper_by_id(paper_project_id=project_id, paper_id=paper_id)
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.PAPER_NOT_FOUND.value
        )
    
    # Check if summary of this paper exists
    summary = await summary_model.get_paper_summary(summary_project_id=project_id, summary_paper_id=paper_id)
    if summary:
        logger.warning(f"Summary already exists for paper_id: {paper_id} in project_id: {project_id}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": f"A summary for this paper already exists. Please delete the existing summary or choose a different paper."
            }
        )
    # Check if there is a summary with the new name
    summary = await summary_model.get_summary_by_name(summary_project_id=project_id, summary_name=summary_request.summary_name)
    if summary:
        logger.warning(f"Summary already exists with name: {summary_request.summary_name} in project_id: {project_id}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": f"A summary with name '{summary_request.summary_name}' already exists in this project. Please choose another name."
            }
        )
    summary_controller = SummaryController(
        summary_client=request.app.summary_client,
        template_parser=request.app.template_parser
    )
    # Check if summary file already exists
    summary_path = await summary_controller.summary_path(project.project_title, summary_request.summary_name)
    if Path(summary_path).exists():
        logger.warning(f"There is already a summary file at path: {summary_path}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": f"Summary file already exists at path: {summary_path}. Please choose another name."
            }
        )
        
    try:
        summary_content = await summary_controller.generate_summary(chunk_model=chunk_model, paper_id=paper_id, paper_name=paper.paper_name)
        await summary_controller.save_summary(summary_path, summary_content)

        summary = await summary_model.get_or_create_summary(
            Summary(
                summary_project_id=project.id,
                summary_paper_id=paper.id,
                summary_name=summary_request.summary_name,
                summary_type=AssetTypeEnums.MD.value,
                summary_size=os.path.getsize(summary_path),
            )
        )
        logger.info(f"Summary created successfully for paper: {paper.paper_name}")
    except Exception as e:
        logger.error(f"Failed to create summary: {e}")
        if Path(summary_path).exists():
            Path(summary_path).unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,         
            detail=ResponseSignals.SUMMARY_GENERATION_FAILED.value
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": ResponseSignals.SUMMARY_GENERATION_SUCCESS.value,
            "summary": _serialize_summary(summary)
        }
    )

# List all summaries by project
@summary_router.get("/")
async def list_summaries(request: Request, project_id: str):
    logger.info(f"Incoming request to list summaries for project_id: {project_id}")

    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    summaries = await summary_model.get_project_summaries(summaries_project_id=project_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[_serialize_summary(summary) for summary in summaries]
    )

# Get a summary by project
@summary_router.get("/{summary_id}")      
async def get_summary(request: Request, project_id: str, paper_id: str, summary_id: str):
    logger.info(f"Incoming request to get summary for project_id: {project_id}, paper_id: {paper_id} and summary_id: {summary_id}")

    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    summary = await summary_model.get_paper_summary(summary_project_id=project_id, summary_paper_id=paper_id, summary_id=summary_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.SUMMARY_NOT_FOUND.value
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=_serialize_summary(summary)  
    )

# Delete a summary by ID
@summary_router.delete("/{summary_id}")
async def delete_summary(request: Request, project_id: str, paper_id: str, summary_id: str):
    logger.info(f"Incoming request to delete summary for project_id: {project_id}, paper_id: {paper_id}, summary_id: {summary_id}")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    
    summary_controller = SummaryController(
            summary_client=request.app.summary_client,
            template_parser=request.app.template_parser
    )
    summary = await summary_model.get_summary_by_id(summary_project_id=project_id, summary_paper_id=paper_id, summary_id=summary_id)
    summary_path = await summary_controller.summary_path(project.project_title, summary.summary_name)
    if not summary:
        # Clean file if exists
        if Path(summary_path).exists():
            Path(summary_path).unlink()
            logger.warning(f"Deleted summary file at {summary_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.SUMMARY_NOT_FOUND.value
        )

    # Delete from DB
    await summary_model.delete_summary(project_summary_id=project_id, summary_paper_id=paper_id, summary_id=summary_id)
    logger.info(f"Summary with ID: {summary_id} deleted from database.")

    # Delete from filesystem   
    if Path(summary_path).exists():
        Path(summary_path).unlink()
        logger.info(f"Summary file deleted at {summary_path}")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Serve the summary file
@summary_router.get("/view/{summary_id}")
async def serve_summary_file(request: Request, project_id: str, paper_id: str, summary_id: str):    
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PROJECT_NOT_FOUND.value   
        )
    # if summary exists in db
    summary = await summary_model.get_summary_by_id(summary_project_id=project_id, summary_paper_id=paper_id, summary_id=summary_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.SUMMARY_NOT_FOUND.value
        )
    summary_controller = SummaryController(
        summary_client=request.app.summary_client,
        template_parser=request.app.template_parser
    )
    summary_path = await summary_controller.summary_path(project_title=project.project_title, summary_name= summary.summary_name)

    # if summary exists in filesystem
    if not Path(summary_path).exists():
        logger.error(f"Summary file not found at {summary_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.SUMMARY_FILE_NOT_FOUND.value
        )
    try:
        def iter_file(path, chunk_size=1024*1024):
            with open(path, "r", encoding="utf-8") as f:
                while chunk := f.read(chunk_size):
                    yield chunk

        return StreamingResponse(
            iter_file(Path(summary_path)),
            media_type="text/markdown",
            headers={"Content-Disposition": f'inline; filename="{summary.summary_name}.md"'}
        )
    except Exception as e:
        logger.error(f"Error displaying summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=ResponseSignals.SUMMARY_DISPLAY_ERROR.value
        )
# Update the summary file with new content
@summary_router.put("/{summary_id}", response_class=PlainTextResponse)
async def update_summary_file(request: Request, project_id: str, paper_id: str, summary_id: str,
    new_content: str = Body(..., media_type="text/markdown")):

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    summary = await summary_model.get_summary_by_id(summary_project_id=project_id, summary_paper_id=paper_id, summary_id=summary_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.SUMMARY_NOT_FOUND.value
        )
    
    summary_controller = SummaryController(
        summary_client=request.app.summary_client,
        template_parser=request.app.template_parser
    )
    summary_path = await summary_controller.summary_path(project.project_title, summary.summary_name)
    
    if not Path(summary_path).exists():
        logger.error(f"Summary file not found at: {summary_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.SUMMARY_FILE_NOT_FOUND.value
        )
    try:
        async with aiofiles.open(summary_path, 'w', encoding='utf-8') as f:
            await f.write(new_content)

        #update summary size
        summary.summary_size = os.path.getsize(summary_path)
        await summary_model.update_summary(summary)

        return PlainTextResponse(
            new_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'inline; filename="{summary.summary_name}.md"'}
        )
    except Exception as e:
        logger.error(f"Error updating summary {summary_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseSignals.SUMMARY_UPDATE_ERROR.value
        )

# Rename a summary
@summary_router.put("/{summary_id}/rename")
async def rename_summary(request: Request, project_id: str, paper_id: str, summary_id: str, rename_request: RenameRequest):
    logger.info(f"Rename summary request for summary_id: {summary_id} to new name: {rename_request.new_name}")
    
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    
    # Check if project exists
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    
    # Check if summary exists
    summary = await summary_model.get_summary_by_id(summary_project_id=project_id, summary_paper_id=paper_id, summary_id=summary_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.SUMMARY_NOT_FOUND.value
        )

    # Check if there is a summary with the new name
    existing = await summary_model.get_summary_by_name(summary_project_id=project_id, summary_name=rename_request.new_name)
    if existing:
        logger.warning(f"Summary with new name '{rename_request.new_name}' already exists.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= f"Summary with name '{rename_request.new_name}' already exists in this project. Please choose another name."

        )

    summary_controller = SummaryController(
        summary_client=request.app.summary_client,
        template_parser=request.app.template_parser
    )
    try:
        # Rename the summary file in the filesystem
        await summary_controller.rename_summary_file(
            project_title=project.project_title,
            old_name=summary.summary_name,
            new_name=rename_request.new_name
        )
        # Update summary name in database
        summary.summary_name = rename_request.new_name
        await summary_model.update_summary(summary)
        logger.info(f"Summary renamed successfully to {rename_request.new_name}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": ResponseSignals.SUMMARY_RENAME_SUCCESS.value,
                "summary": _serialize_summary(summary)
            }
    )
    except Exception as e:
        logger.error(f"Error renaming summary {summary_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseSignals.SUMMARY_RENAME_ERROR.value
        )