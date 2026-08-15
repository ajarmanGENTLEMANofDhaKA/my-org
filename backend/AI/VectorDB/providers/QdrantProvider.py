from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from ..VDBInterface import VectorDBInterface
from models.db_schemas import RetrievedChunks
from typing import List, Optional, Dict
import uuid
from utils.app_logging import get_logger
logger = get_logger(__name__)

class QdrantProvider(VectorDBInterface):
    def __init__(self, host: str = "localhost", port: int = 6333, 
                 grpc_port: int = 6334, distance_metric: str="cosine"):
        self.host = host
        self.port = port
        self.grpc_port = grpc_port
        self.distance_metric = None
        self.client = None

        if distance_metric == "cosine":
            self.distance_metric = models.Distance.COSINE
        elif distance_metric == "dot":
            self.distance_metric = models.Distance.DOT

    async def connect(self):
        self.client = AsyncQdrantClient(
                host=self.host,
                port=self.port,
                prefer_grpc=False,  # Use HTTP instead of gRPC
        )
        logger.info("Connected to Qdrant database.")

    async def disconnect(self):
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Qdrant database.")

    async def is_collection_exist(self, collection_name):
        return await self.client.collection_exists(collection_name)

    async def list_all_collections(self):
        return await self.client.get_collections()

    async def get_collection_info(self, collection_name):
        if await self.client.collection_exists(collection_name):
            logger.info(f"Retrieving info for collection: {collection_name}")
            return await self.client.get_collection(collection_name=collection_name)
        else:
            logger.warning(f"Cannot retrieve info for collection '{collection_name}': does not exist.")
            return None

    async def delete_collection(self, collection_name):
        '''Delete the collection = Delete all project embedding chunks'''
        if await self.client.collection_exists(collection_name):
            await self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' deleted.")
        else:
            logger.warning(f"Collection '{collection_name}' does not exist.")
    
    async def delete_all_collections(self):
        collections = await self.list_all_collections()
        for collection in collections.collections:
            await self.delete_collection(collection.name)
        logger.info("All collections deleted.")

    async def delete_paper_embeddings(self, collection_name: str, paper_id: str):
        '''Delete all chunks embeddings related to a specific paper in a collection'''
        if not await self.client.collection_exists(collection_name):
            logger.warning(f"Collection '{collection_name}' does not exist.")
            raise Exception(f"Collection '{collection_name}' does not exist.")
        
        try:
            await self.client.delete(
                collection_name=collection_name,
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="paper_id",
                            match=models.MatchValue(value=paper_id)
                        )
                    ]
                )
            )
            logger.info(f"Deleted embeddings for paper_id '{paper_id}' in collection '{collection_name}'.")
        except Exception as e:
            logger.error(f"Error deleting embeddings for paper_id '{paper_id}' in collection '{collection_name}': {e}")
            raise

    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        try:
            if do_reset:
                await self.delete_collection(collection_name)

            if not await self.client.collection_exists(collection_name):
                await self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=embedding_size,
                        distance=self.distance_metric
                    )
                )
                logger.info(f"Collection '{collection_name}' created.")
            else:
                logger.warning(f"Collection '{collection_name}' already exists.")
        except Exception as e:
            logger.error(f"Error during create collection with name {collection_name}")
            raise

    async def insert_one(
        self,
        collection_name: str,
        chunk_id: str,
        text: str,
        vector: List[float],
        paper_id: str = None,
        metadata: Optional[Dict] = None
    ):

        if not await self.client.collection_exists(collection_name):
            logger.error(f"Collection '{collection_name}' does not exist.")
            raise Exception(f"Collection '{collection_name}' does not exist.")
        try:
            await self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=chunk_id,
                        vector=vector,
                        payload={"text": text, "paper_id": paper_id, **(metadata or {})}
                    )
                ]
            )
            logger.info(f"Inserted one document into collection '{collection_name}'.")

        except Exception as e:
            logger.error(f"Error inserting document into collection '{collection_name}': {e}")
            raise

    async def insert_many(
        self,
        collection_name: str,
        chunk_ids: List[str],
        texts: List[str],
        vectors: List[List[float]],
        paper_ids: List[str] = None,
        metadatas: Optional[List[Dict]] = None,
        batch_size: int = 50,
    ):
        if not await self.client.collection_exists(collection_name):
            logger.error(f"Collection '{collection_name}' does not exist.")
            raise Exception(f"Collection '{collection_name}' does not exist.")

        metadatas = metadatas or [{} for _ in range(len(texts))]

        try:
            for i in range(0, len(texts), batch_size):
                batch_points = []
                for j in range(i, min(i + batch_size, len(texts))):
                    payload = {"text": texts[j], "paper_id": paper_ids[j], **metadatas[j]}

                    point = models.PointStruct(
                        id=chunk_ids[j],
                        vector=vectors[j],
                        payload=payload
                    )
                    batch_points.append(point)

                await self.client.upsert(
                    collection_name=collection_name,
                    points=batch_points
                )

                logger.info(f"Inserted batch {i} to {i + len(batch_points)} into collection '{collection_name}'")

            logger.info(f"Inserted {len(texts)} documents into collection '{collection_name}'.")

        except Exception as e:
            logger.error(f"Error inserting into collection '{collection_name}': {e}")
            raise

    async def query_search(self, collection_name:str, query_vector:List[float],
            limit:int = 5, min_score:float = 0.7, return_metadata: bool = False
    ):
        if not await self.client.collection_exists(collection_name):
            logger.error(f"Collection '{collection_name}' does not exist.")
            raise Exception(f"Collection '{collection_name}' does not exist.")
        
        try:
            search_result = await self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=min_score
            )

            if not search_result or len(search_result) == 0:
                logger.warning(f"No results found in collection '{collection_name}'.")
                return []

            retrieved_result = [
                RetrievedChunks(**{
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "metadata": result.payload if return_metadata else None
                    }
                )
                for result in search_result
            ]

            logger.info(f"Search completed in collection '{collection_name}'.")
            return retrieved_result

        except Exception as e:
            logger.error(f"Error searching in collection '{collection_name}': {e}")
            raise