from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class User(BaseModel):
    """User schema in database."""
    id: Optional[ObjectId] = Field(None, alias="_id")
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True
        
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("username", 1)],
                "name": "username_index_1",
                "unique": True
            },
            {
                "key": [("email", 1)],
                "name": "email_index_1",
                "unique": True
            }
        ]

    
