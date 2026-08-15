from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from utils import AppSettings, get_settings

welcome_router = APIRouter()

@welcome_router.get("/welcome")
async def welcome(app_settings : AppSettings = Depends(get_settings)):

    project_name = app_settings.APP_NAME
    version = app_settings.APP_VERSION

    return JSONResponse(content={"message": f"Welcome to {project_name} {version}"})