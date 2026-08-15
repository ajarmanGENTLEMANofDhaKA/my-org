from utils import get_logger, get_settings

logger = get_logger(__name__)
class BaseModel:
    def __init__(self, db_client):
        self.db_client = db_client
        self.settings = get_settings()

    async def create_indexes(self, collection, indexes_list):
        """Generic method to create indexes from a list of index definitions"""
        all_indexes = await collection.index_information()
        for index in indexes_list:
            if index["name"] not in all_indexes:
                try:
                    await collection.create_index(
                        index["key"],
                        name=index["name"],
                        unique=index.get("unique", False)
                    )
                    logger.info(f"Created index: {index['name']}")
                except Exception as e:
                    logger.error(f"Error creating index {index['name']}: {e}")