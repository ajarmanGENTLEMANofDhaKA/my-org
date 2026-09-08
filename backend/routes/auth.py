from fastapi import APIRouter, Depends, HTTPException, status, Request
from datetime import timedelta, datetime

from models.user_model import UserModel
from models.db_schemas import User

from .schema.responses import TokenResponse, UserResponse
from .schema.requests import RegisterRequest, LoginRequest

from utils.auth_utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)

from utils import get_settings, get_logger

logger = get_logger(__name__)

auth_router = APIRouter()


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(request: Request, user_data: RegisterRequest):
    logger.info("Incoming user registration request")

    user_model = await UserModel.get_instance(
        request.app.mongodb_client
    )

    # Check if username already exists
    existing_user = await user_model.get_user_by_username(
        user_data.username
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = await user_model.get_user_by_email(
        user_data.email
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create User schema object
    now = datetime.utcnow()

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        created_at=now,
        updated_at=now
    )

    # Save user to MongoDB
    user = await user_model.create_user(new_user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    logger.info(
        f"New user registered: {user.username}"
    )

    return UserResponse(
        username=user.username,
        email=user.email
    )


@auth_router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    request: Request,
    login_data: LoginRequest
):
    logger.info("Incoming user login request")

    user_model = await UserModel.get_instance(
        request.app.mongodb_client
    )

    # Try username first
    user = await user_model.get_user_by_username(
        login_data.username
    )

    # If not found, try email
    if not user:
        user = await user_model.get_user_by_email(
            login_data.username
        )

    # Verify user and password
    if not user or not verify_password(
        login_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    settings = get_settings()

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "email": user.email
        },
        expires_delta=access_token_expires
    )

    logger.info(
        f"User logged in: {user.username}"
    )

    return TokenResponse(
        access_token=access_token
    )


@auth_router.get(
    "/me",
    response_model=UserResponse
)
async def get_me(
    current_user: dict = Depends(get_current_user)
):
    """Get current user information."""

    return UserResponse(
        username=current_user["username"],
        email=current_user["email"]
    )