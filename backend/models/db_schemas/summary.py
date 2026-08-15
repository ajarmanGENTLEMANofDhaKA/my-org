from pydantic import BaseModel, Field, validator
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime

class Summary(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    summary_project_id: ObjectId
    summary_paper_id: ObjectId
    summary_name: str = Field(..., min_length=1)
    summary_type: str = Field(..., min_length=1)
    summary_size: int = Field(ge=0, default=None)
    summary_created_at: datetime = Field(default=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("summary_project_id", 1)],
                "name": "summary_project_id_index_1",
                "unique": False
            },
            {
                "key": [("summary_project_id", 1), ("summary_paper_id", 1)],
                "name": "summary_project_id_paper_id_index_1",
                "unique": True
            },
            {
                "key": [("summary_project_id", 1), ("summary_paper_id", 1), ("id", 1)],
                "name": "summary_project_id_paper_id_id_index_1",
                "unique": True
            },
            {
                "key": [("summary_project_id", 1), ("summary_name", 1)],
                "name": "summary_project_id_name_index_1",
                "unique": True
            }
        ]