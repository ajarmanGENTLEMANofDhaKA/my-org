from .base_model import BaseModel
from .db_schemas import Paper
from utils.enums import DatabaseEnums, AssetTypeEnums
from bson import ObjectId
from utils import get_logger
logger = get_logger(__name__)

class PaperModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnums.PAPER_COLLECTION_NAME.value]
    
    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.ensure_indexes()
        logger.info("PaperModel instance created and indexes ensured.")
        return instance
    
    async def ensure_indexes(self):
        await self.create_indexes(self.collection, Paper.get_indexes())

    async def create_paper(self, Paper: Paper) -> Paper:
        try:
            res = await self.collection.insert_one(Paper.dict(by_alias=True, exclude_unset=True))
            Paper.id = res.inserted_id
            logger.info(f"Paper created with ID: {str(Paper.id)} and name: {Paper.paper_name}")
            return Paper
        except Exception as e:
            logger.error(f"Error creating paper with ID: {str(Paper.id)} and name: {Paper.paper_name}")
            raise

    async def get_paper_by_name(self, paper_project_id: str, paper_name: str):
        try:
            record = await self.collection.find_one(
                {"paper_project_id": ObjectId(paper_project_id),
                "paper_name": paper_name})
            if record is None:
                logger.warning(f"Paper not found: {paper_name} in project {paper_project_id}")
                return None
            logger.info(f"Paper found: {paper_name} in project {paper_project_id}")
            return Paper(**record)
        except Exception as e:
            logger.error(f"Error retrieving paper '{paper_name}' for project '{paper_project_id}': {e}")
            raise

    async def get_paper_by_id(self, paper_project_id: str, paper_id: str):
        try:
            record = await self.collection.find_one(
                {"_id": ObjectId(paper_id),
                "paper_project_id": ObjectId(paper_project_id)
                }
            )
            if not record:
                logger.warning(f"Paper not found with ID: {paper_id} in project {paper_project_id}")
                return None
            logger.info(f"Paper found with ID: {paper_id} in project {paper_project_id}")
            return Paper(**record)
        except Exception as e:
            logger.error(f"Error retrieving paper by ID '{paper_id}' for project '{paper_project_id}': {e}")
            raise

    async def get_or_create_paper(self, Paper: Paper) -> Paper:
        try:
            paper = await self.get_paper_by_name(str(Paper.paper_project_id), Paper.paper_name)
            if not paper:
                logger.info(f"Creating new paper with name: {Paper.paper_name}")
                paper = await self.create_paper(Paper)
                return paper
            return paper
        except Exception as e:
            logger.error(f"Error in get_or_create_paper for {Paper.paper_name}: {e}")
            raise

    async def get_project_papers(self, papers_project_id: str):
        try:    
            query = {"paper_project_id": ObjectId(papers_project_id)}
            records = await self.collection.find(query).to_list(length=None)
            papers = [Paper(**record) for record in records]
            if len(papers) == 0:
                logger.warning(f"No papers found for the project {papers_project_id}.")
                return []
            logger.info(f"Fetched {len(papers)} papers for project {papers_project_id}.")
            return papers
        except Exception as e:
            logger.error(f"Error fetching papers for project {papers_project_id}: {e}")
            raise

    async def delete_all_papers(self):
        try:
            result = await self.collection.delete_many({})
            if result.deleted_count == 0:
                logger.warning("No papers found to delete.")
            
            logger.info(f"All papers deleted successfully. Count: {result.deleted_count}")
        except Exception as e:
            logger.error(f"Error deleting all papers: {e}")
            raise

    async def delete_project_papers(self, papers_project_id: str):
        try:
            result = await self.collection.delete_many({"paper_project_id": ObjectId(papers_project_id)})
            if result.deleted_count == 0:
                logger.warning(f"No papers found to delete for project {papers_project_id}.")
                
            logger.info(f"Deleted {result.deleted_count} papers from project {papers_project_id}.")
        except Exception as e:
            logger.error(f"Error deleting papers for project {papers_project_id}: {e}")
            raise

    async def delete_paper(self, paper_project_id:str, paper_id: str):
        try:
            result = await self.collection.delete_one(
                {"paper_project_id": ObjectId(paper_project_id),
                "_id": ObjectId(paper_id)}
            )
            if result.deleted_count == 0:
                logger.warning(f"Paper not found for deletion with ID: {paper_id} in project {paper_project_id}")

            logger.info(f"Paper {paper_id} deleted successfully from project {paper_project_id}.")
        except Exception as e:
            logger.error(f"Error deleting paper {paper_id} from project {paper_project_id}: {e}")
            raise

    async def update_paper(self, paper: Paper):
        try:
            result = await self.collection.update_one(
                {"_id": paper.id},
                {"$set": paper.dict(by_alias=True, exclude={"id"}, exclude_unset=True)}
            )
            if result.modified_count == 0:
                logger.info(f"Paper {str(paper.id)} matched but no fields were changed.")

            logger.info(f"Paper {str(paper.id)} updated successfully.")
        except Exception as e:
            logger.error(f"Error updating paper {str(paper.id)}: {e}")
            raise