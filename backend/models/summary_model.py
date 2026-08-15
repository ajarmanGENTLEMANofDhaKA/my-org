from .base_model import BaseModel
from .db_schemas import Summary
from bson import ObjectId
from utils.enums import DatabaseEnums
from utils import get_logger
logger = get_logger(__name__)

class SummaryModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnums.SUMMARY_COLLECTION_NAME.value]
    
    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.ensure_indexes()
        logger.info("SummaryModel instance created and indexes ensured.")
        return instance
    
    async def ensure_indexes(self):
        await self.create_indexes(self.collection, Summary.get_indexes())

    async def create_summary(self, Summary: Summary):
        try:
            res = await self.collection.insert_one(Summary.dict(by_alias=True, exclude_unset=True))
            Summary.id = res.inserted_id
            logger.info(f"Summary created with ID: {str(Summary.id)} and name {Summary.summary_name}")
            return Summary
        except Exception as e:
            logger.error(f"Error creating summary with ID: {str(Summary.id)} and name {Summary.summary_name}: {e}")
            raise

    async def get_summary_by_name(self, summary_project_id: str, summary_name: str):
        try:
            record = await self.collection.find_one(
                {"summary_project_id": ObjectId(summary_project_id),
                "summary_name": summary_name
                }
            )
            if record is None:
                logger.warning(f"Summary not found: {summary_name} in project {summary_project_id}")
                return None
            logger.info(f"Summary found: {summary_name} in project {summary_project_id}")
            return Summary(**record)
        except Exception as e:
            logger.error(f"Error retrieving summary '{summary_name}' for project '{summary_project_id}': {e}")
            raise
    
    async def get_summary_by_id(self, summary_project_id: str, summary_paper_id: str, summary_id: str):
        try:
            record = await self.collection.find_one(
                {"_id": ObjectId(summary_id),
                "summary_project_id": ObjectId(summary_project_id),
                "summary_paper_id": ObjectId(summary_paper_id)
                }
            )
            if not record:
                logger.warning(f"Summary not found with ID: {summary_id}")
                return None
            logger.info(f"Summary found with ID: {summary_id}")
            return Summary(**record)
        except Exception as e:
            logger.error(f"Error retrieving summary by ID '{summary_id}': {e}")
            raise

    async def get_or_create_summary(self, Summary: Summary) -> Summary:
        try:
            summary = await self.get_summary_by_name(str(Summary.summary_project_id), Summary.summary_name)
            if not summary:
                logger.info(f"Creating new summary with name: {Summary.summary_name}")
                summary = await self.create_summary(Summary)
                return summary
            return summary
        except Exception as e:
            logger.error(f"Error in get_or_create_summary for {Summary.summary_name}: {e}")
            raise

    async def get_paper_summary(self, summary_project_id: str, summary_paper_id: str):
        try:    
            query = {"summary_project_id": ObjectId(summary_project_id),
                     "summary_paper_id": ObjectId(summary_paper_id)}
                
            record = await self.collection.find(query).to_list(length=None)
            if not record:
                logger.warning(f"No summaries found for paper '{summary_paper_id}' in project '{summary_project_id}'")
                return None
            summaries = Summary(**record)
            return summaries
        except Exception as e:
            logger.error(f"Error retrieving summaries for paper '{summary_paper_id}' in project '{summary_project_id}': {e}")
            raise

    async def get_project_summaries(self, summaries_project_id: str, summary_type: str = None):
        try:    
            query = {"summary_project_id": ObjectId(summaries_project_id)}
            if summary_type:
                query["summary_type"] = summary_type
                
            records = await self.collection.find(query).to_list(length=None)
            summaries = [Summary(**record) for record in records]
            if len(summaries) == 0:
                logger.warning(f"No summaries found for project '{summaries_project_id}'")
                return []
            return summaries
        except Exception as e:
            logger.error(f"Error retrieving summaries for project '{summaries_project_id}' : {e}")
            raise

    async def delete_all_summaries(self):
        try:
            result = await self.collection.delete_many({})
            if result.deleted_count == 0:
                logger.warning("No summaries found to delete.")
                
            logger.info(f"All summaries deleted successfully. Count: {result.deleted_count}")
        except Exception as e:
            logger.error(f"Error deleting all summaries: {e}")
            raise

    async def delete_project_summaries(self, summaries_project_id: str):
        try:
            result = await self.collection.delete_many({"summary_project_id": ObjectId(summaries_project_id)})
            if result.deleted_count == 0:
                logger.warning(f"No summaries found to delete for project {summaries_project_id}.")

            logger.info(f"Deleted {result.deleted_count} summaries from project {summaries_project_id}.")
        except Exception as e:
            logger.error(f"Error deleting summaries for project {summaries_project_id}: {e}")
            raise

    async def delete_summary(self, summary_project_id: str, summary_paper_id: str, summary_id: str):
        try:
            result = await self.collection.delete_one(
                {"summary_project_id": ObjectId(summary_project_id),
                "summary_paper_id": ObjectId(summary_paper_id),
                "_id": ObjectId(summary_id)}
            )
            if result.deleted_count == 0:
                logger.warning(f"Summary not found for deletion with ID: {summary_id} in project {summary_project_id}")
            
            logger.info(f"Summary {summary_id} deleted successfully from project {summary_project_id}") 
        except Exception as e:
            logger.error(f"Error deleting summary {summary_id} from project {summary_project_id}: {e}")
            raise

    async def update_summary(self, summary: Summary):
        try:
            result = await self.collection.update_one(
                {"_id": summary.id},
                {"$set": summary.dict(by_alias=True, exclude={"id"}, exclude_unset=True)}
            )
            if result.modified_count == 0:  
                logger.info(f"Summary {str(summary.id)} matched but no fields were changed.")

            logger.info(f"Summary {str(summary.id)} updated successfully for paper {str(summary.summary_paper_id)}.")
        except Exception as e:
            logger.error(f"Error updating summary in DB: {e}")
            raise