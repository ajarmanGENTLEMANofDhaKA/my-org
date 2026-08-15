from pydantic import BaseModel, Field, validator
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime

class Paper(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    paper_project_id: ObjectId
    paper_name: str = Field(..., min_length=1)
    paper_type: str = Field(..., min_length=1)
    paper_size: int = Field(ge=0, default=None)
    paper_created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("paper_project_id", 1)],
                "name": "paper_project_id_index_1",
                "unique": False
            },
            {
                "key": [("paper_name", 1), ("paper_project_id", 1)],
                "name": "paper_project_id_name_index_1",
                "unique": True
            }
            
        ]