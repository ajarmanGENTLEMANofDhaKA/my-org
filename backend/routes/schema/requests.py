from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class RegisterRequest(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password")

class LoginRequest(BaseModel):
    """Schema for user login."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

class ProcessRequest(BaseModel):
    file_id: str = None
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0

class ProjectRequest(BaseModel):
    project_title: str

class SummaryRequest(BaseModel):
    summary_name: str

class PushRequest(BaseModel):
    do_reset: Optional[int] = 0

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    RAGFusion: Optional[bool] = False

class TranslateRequest(BaseModel):
    text: str
    target_language: str

class ExplainRequest(BaseModel):
    text: str
    context : str = None

class RenameRequest(BaseModel):
    new_name: str
