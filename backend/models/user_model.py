from typing import Optional
from datetime import datetime
from .db_schemas import User
from .base_model import BaseModel
from bson import ObjectId
from utils.enums import DatabaseEnums
from utils import get_logger
logger = get_logger(__name__)

class UserModel(BaseModel):    
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = db_client[DatabaseEnums.USER_COLLECTION_NAME.value]

    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.ensure_indexes()
        logger.info("UserModel instance created and indexes ensured.")
        return instance
    
    async def ensure_indexes(self):
        await self.create_indexes(self.collection, User.get_indexes())

    async def create_user(self, user: User) -> dict:
        """Create a new user."""
        try:
            res = await self.collection.insert_one(user.dict(by_alias=True, exclude_unset=True))
            user.id = res.inserted_id
            logger.info(f"User created with ID: {str(user.id)} and username {user.username}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        user_data = await self.collection.find_one({"username": username})
        return User(**user_data) if user_data else None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_data = await self.collection.find_one({"email": email})
        return User(**user_data) if user_data else None    

    async def update_user(self, user_id: str, update_data: dict) -> Optional[User]:
        """Update user information."""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_data},
                return_document=True
            )
            return User(**result)
        except Exception as e:
            logger.error(f"Error updating user with ID {user_id}: {e}")
            return None
