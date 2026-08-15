from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from bson.objectid import ObjectId

class Chunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_project_id: ObjectId
    chunk_paper_id: ObjectId
    chunk_section_id: ObjectId
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_index_in_paper: int = Field(..., ge=0)
    
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index_1",
                "unique": False
            }
            ,
            {
                "key": [("chunk_paper_id", 1)],
                "name": "chunk_paper_id_index_1",
                "unique": False
            },
            {
                "key": [("chunk_section_id", 1)],
                "name": "chunk_section_id_index_1",
                "unique": False
            },
            {
                "key": [("chunk_project_id", 1), ("chunk_paper_id", 1)],
                "name": "chunk_project_paper_index_1_1",
                "unique": False
            },
            {
                "key": [("chunk_paper_id", 1), ("chunk_section_id", 1)],
                "name": "chunk_paper_section_index_1_1",
                "unique": False
            },
            {
                "key": [("chunk_project_id", 1), ("chunk_paper_id", 1), ("chunk_section_id", 1)],
                "name": "chunk_project_paper_section_index_1_1_1",
                "unique": False
            }
        ]
    
class RetrievedChunks(BaseModel):
    score: float
    text: str
    metadata: Optional[Dict[str, Any]] = None