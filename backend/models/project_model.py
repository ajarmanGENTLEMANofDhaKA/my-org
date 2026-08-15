from .base_model import BaseModel
from .db_schemas import Project
from utils.enums import DatabaseEnums
from bson import ObjectId
from typing import List
from utils import get_logger
logger = get_logger(__name__)

class ProjectModel(BaseModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnums.PROJECT_COLLECTION_NAME.value]

    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.ensure_indexes()
        logger.info("ProjectModel instance created and indexes ensured.")
        return instance

    async def ensure_indexes(self):
        await self.create_indexes(self.collection, Project.get_indexes())

    async def create_project(self, project: Project) -> Project:
        try:
            res= await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
            project.id = res.inserted_id
            logger.info(f"Project created with ID: {project.id} and title: {project.project_title}")
            return project
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise

    async def get_project_by_name(self, project_title: str):
        """Get a project by its title"""
        try:
            record = await self.collection.find_one({"project_title": project_title})
            if not record:
                logger.warning(f"Project not found: {project_title}")
                return None
            logger.info(f"Project found with title: {project_title}")
            return Project(**record)
        except Exception as e:
            logger.error(f"Error retrieving project by name {project_title}: {e}")
            raise
    
    async def get_project_by_id(self, project_id: str):
        """Get a project by its ID"""
        try:
            record = await self.collection.find_one({"_id": ObjectId(project_id)})
            if not record:
                logger.warning(f"Project not found: {project_id}")
                return None
            logger.info(f"Project found with ID: {project_id}")
            return Project(**record)
        except Exception as e:
            logger.error(f"Error retrieving project {project_id}: {e}")
            raise
    
    async def get_or_create_project(self, Project: Project) -> Project:
        """Get a project by its project_id and if the project does not exist, create one"""
        try:
            project = await self.get_project_by_name(Project.project_title)
            if not project:
                logger.info(f"Creating new project with title: {Project.project_title}")
                project = await self.create_project(Project)
                return project
            return project
        except Exception as e:
            logger.error(f"Error in get_or_create_project: {e}")
            raise
    
    async def get_all_projects(self, page: int=0, limit: int=10):
        try:
            cursor = self.collection.find().skip(page * limit).limit(limit)
            projects = []
            async for document in cursor:
                projects.append(Project(**document))

            if not projects or len(projects) == 0:
                logger.warning("No projects found in the database.")
                return []
            
            logger.info(f"Retrieved {len(projects)} projects from the database.")
            return projects
        except Exception as e:
            logger.error(f"Error retrieving all projects: {e}")
            raise

    async def delete_all_projects(self):
        try:
            result = await self.collection.delete_many({})
            if result.deleted_count == 0:
                logger.warning("No projects found to delete.")
            
            logger.info(f"All projects deleted successfully. Count: {result.deleted_count}")
        except Exception as e:
            logger.error(f"Error deleting all projects: {e}")
            raise

    async def delete_project(self, project_id: str):
        try:
            result = await self.collection.delete_one({"_id": ObjectId(project_id)})
            if result.deleted_count == 0:
                logger.warning(f"Project not found for deletion with ID: {project_id}")

            logger.info(f"Project {project_id} deleted successfully.")
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            raise

    async def update_project(self, project: Project):
        try:
            result = await self.collection.update_one(
                {"_id": project.id},
                {"$set": project.dict(by_alias=True, exclude={"id"}, exclude_unset=True)}
            )
            if result.modified_count == 0:
                logger.info(f"Project {project.id} matched but no fields were changed.")
            
            logger.info(f"Project {project.id} updated successfully.")
        except Exception as e:
            logger.error(f"Error updating project {project.id}: {e}")
            raise
