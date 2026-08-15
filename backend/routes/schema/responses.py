from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    """Schema for user response."""
    username: str
    email: EmailStr
