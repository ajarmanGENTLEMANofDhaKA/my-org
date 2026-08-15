from pydantic import BaseModel, Field, validator
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_title: str = Field(..., min_length=1)
    project_created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('project_title')
    def project_title_validator(cls, v):
        # Allow alphanumeric, spaces, hyphens, and underscores
        # Strip leading/trailing whitespace
        v = v.strip()
        if not v:
            raise ValueError('Project title cannot be empty')
        # Check if contains at least some valid characters
        if not any(c.isalnum() for c in v):
            raise ValueError('Project title must contain at least one alphanumeric character')
        return v
    
    class Config:
        arbitrary_types_allowed = True
        
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("project_title", 1)],
                "name": "project_title_index_1",
                "unique": True
            }
        ]
        
