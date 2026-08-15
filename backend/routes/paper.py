from fastapi import APIRouter, UploadFile, File, Depends, status, Request, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse
from controllers import PaperController
from models import ProjectModel, PaperModel, ChunkModel
from models.db_schemas import Paper, Chunk
from utils.enums import ResponseSignals, AssetTypeEnums
from routes.schema.requests import RenameRequest
import aiofiles
from pathlib import Path
from bson import ObjectId
from urllib.parse import quote
import os
from utils import get_settings, AppSettings
from utils import get_logger
logger = get_logger(__name__)

def _serialize_paper(paper):
    paper_dict = paper.dict(by_alias=True, exclude_unset=True)
    paper_dict["_id"] = str(paper_dict["_id"])
    paper_dict["paper_project_id"] = str(paper_dict["paper_project_id"])
    return paper_dict

paper_router = APIRouter()

@paper_router.post("/upload-paper")
async def upload_paper(request: Request, project_id: str, file: UploadFile = File(...),
                     app_settings: AppSettings = Depends(get_settings)):
    
    """
    Upload a file to a project.
    - Validates file type and size
    - Saves file to the project directory
    - Creates an paper record in the database
    - Generates chunks from the file 
    - saves chunks to the database
    """
    logger.info(f"Incoming request to upload file for project id: {project_id}")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    chunk_model = await ChunkModel.get_instance(db_client=request.app.mongodb_client)

    # Check if project exists
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    
    paper_controller = PaperController()
    isvalid, message = await paper_controller.validfile(file=file)
    if not isvalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    paper_name = Path(file.filename).stem
    paper_path = await paper_controller.paper_path(project_title=project.project_title, paper_name=paper_name)
    try:
        if not Path(paper_path).exists():
            async with aiofiles.open(paper_path, "wb") as f:
                while chunk:= await file.read(app_settings.CHUNK_SIZE):
                    await f.write(chunk)
            logger.info(f"File saved at {paper_path}")
        else:
            logger.warning(f"File already exists at {paper_path}, skipping save.")
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": ResponseSignals.FAILED_SAVING.value}
        )

    paper = await paper_model.get_or_create_paper(
        Paper(
            paper_project_id=project.id,
            paper_name=paper_name,
            paper_type=AssetTypeEnums.PDF.value,
            paper_size=os.path.getsize(paper_path)
        )
    )
    chunks = await paper_controller.create_chunks(
        project_title=project.project_title,
        paper_name=paper.paper_name,
        paper_path=paper_path,
        chunk_size=1000,
        chunk_overlap=150
    )
    if not chunks or len(chunks) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=ResponseSignals.NO_CHUNKS_CREATED.value
        )
    inserted_chunks = [
        Chunk(
            chunk_project_id=project.id,
            chunk_paper_id=paper.id,
            chunk_section_id=ObjectId(chunk['chunk_section_id']),
            chunk_text=chunk['chunk'],
            chunk_metadata=chunk['chunk_metadata'],
            chunk_index_in_paper=i
        ) for i, chunk in enumerate(chunks)
    ]
    chunks_ids = await chunk_model.insert_chunks(inserted_chunks)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": ResponseSignals.SUCCESS_UPLOAD.value,
            "paper": _serialize_paper(paper),
            "inserted_chunks_count": len(chunks_ids)
        }
    )

# List all papers by project
@paper_router.get("/")
async def list_papers(request: Request, project_id: str):
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    papers = await paper_model.get_project_papers(papers_project_id=project_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[_serialize_paper(paper) for paper in papers]
    )

# Get paper details by ID
@paper_router.get("/{paper_id}")
async def get_paper(request: Request, project_id: str, paper_id: str):
    paper_model = await PaperModel.get_instance(db_client= request.app.mongodb_client)
    paper = await paper_model.get_paper_by_id(paper_project_id=project_id, paper_id=paper_id)
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            details=ResponseSignals.PAPER_NOT_FOUND.value
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=_serialize_paper(paper)
    )

# Delete a paper
@paper_router.delete("/{paper_id}")
async def delete_paper(request: Request, project_id: str, paper_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    chunk_model = await ChunkModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    paper_controller = PaperController()
    paper = await paper_model.get_paper_by_id(paper_project_id=project_id, paper_id=paper_id)
    paper_path = await paper_controller.paper_path(project.project_title, paper.paper_name)
    if not paper:
         # Clean file if exists
        if Path(paper_path).exists():
            Path(paper_path).unlink()
            logger.warning(f"Deleted paper file at {paper_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.PAPER_NOT_FOUND.value
        )

    # Delete the paper from db and its chunks
    await paper_model.delete_paper(paper_project_id=project_id, paper_id=paper_id)
    await chunk_model.delete_paper_chunks(chunks_project_id=project_id, chunks_paper_id=paper_id)

    # Delete the paper embeddings from the vector database
    collection_name = f"collection_{project_id}".strip()
    await request.app.vectordb_client.delete_paper_embeddings(collection_name=collection_name, paper_id=paper_id)
    logger.info(f"Deleted paper and associated chunks and embeddings: {paper_id}")
    
    # Delete the paper file from the filesystem
    if Path(paper_path).exists():
        Path(paper_path).unlink()
        logger.info(f"Paper file deleted at {paper_path}")
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Serve PDF file
@paper_router.get("/view/{paper_id}")
async def serve_paper_file(request: Request, project_id: str, paper_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    paper = await paper_model.get_paper_by_id(paper_project_id=project_id, paper_id=paper_id)
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PAPER_NOT_FOUND.value
    )
    paper_controller = PaperController()
    paper_path = await paper_controller.paper_path(project_title=project.project_title, paper_name=paper.paper_name)
    if not Path(paper_path).exists():
        logger.error(f"Paper file not found at {paper_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PAPER_FILE_NOT_FOUND.value
        )
    try:
        async def iter_file(path, chunk_size=1024*1024):
            async with aiofiles.open(path, "rb") as f:
                while chunk := await f.read(chunk_size):
                    yield chunk

        return StreamingResponse(
            iter_file(Path(paper_path)),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename*=UTF-8''{quote(paper.paper_name)}.pdf"}
        )
    except Exception as e:
        logger.error(f"Error displaying PDF file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=ResponseSignals.PAPER_DISPLAY_ERROR.value)

# Rename a paper
@paper_router.put("/{paper_id}/rename")
async def rename_paper(request: Request, project_id: str, paper_id: str, rename_request: RenameRequest):
    logger.info(f"Rename paper request for paper_id: {paper_id} to new name: {rename_request.new_name}")
    
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    
    # Check if project exists
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    
    # Check if paper exists
    paper = await paper_model.get_paper_by_id(paper_project_id=project_id, paper_id=paper_id)
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PAPER_NOT_FOUND.value
        )

    # Check if paper with new name exists
    existing = await paper_model.get_paper_by_name(paper_project_id=project_id, paper_name=rename_request.new_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Paper with name '{rename_request.new_name}' already exists in this project. Please choose another name."
        )

    paper_controller = PaperController()
    try:
        # Rename the file in filesystem
        await paper_controller.rename_paper_file(
            project_title=project.project_title,
            old_name=paper.paper_name,
            new_name=rename_request.new_name
        )
        
        # Update paper name in database
        paper.paper_name = rename_request.new_name
        await paper_model.update_paper(paper)
        logger.info(f"Paper renamed successfully to {rename_request.new_name}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": ResponseSignals.PAPER_RENAME_SUCCESS.value,
                "paper": _serialize_paper(paper)
            }
        )
    except Exception as e:
        logger.error(f"Error renaming paper {paper_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseSignals.PAPER_RENAME_ERROR.value
        )