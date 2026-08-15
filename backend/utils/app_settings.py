from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    APP_NAME: str = "Inquiro"
    APP_VERSION: str = "0.1.0"

    ALLOWED_FILE_TYPES: list[str] = ["application/pdf"]
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    CHUNK_SIZE: int = 524288  # 512 KB

    MONGO_URL: str = "mongodb://admin:admin@localhost:27017/inquiro?authSource=admin"
    MONGO_DB: str = "inquiro"

    GENERATION_BACKEND: str = "gemini"
    EMBEDDING_BACKEND: str = "gemini"
    SUMMARY_BACKEND: str = "gemini"

    GEMINI_API_KEY: str = "" 

    GENERATION_MODEL_ID: str = "gemini-2.0-flash"
    EMBEDDING_MODEL_ID: str = "gemini-embedding-001"
    EMBEDDING_SIZE: int = 1024
    SUMMARY_MODEL_ID: str = "gemini-2.0-flash"

    DEFAULT_MAX_INPUT_CHARACTERS: int = 1024
    DEFAULT_MAX_TOKENS: int = 200
    DEFAULT_TEMPERATURE: float = 0.1

    VECTOR_DB_BACKEND: str = "qdrant"
    VECTOR_DB_HOST: str = "localhost"
    VECTOR_DB_PORT: int = 6333
    VECTOR_DB_GRPC_PORT: int = 6334
    VECTOR_DB_DISTANCE_METHOD: str = "cosine"

    LANG: str = "en"
    DEFAULT_LANG: str = "en"

    TRANSLATION_SUPPORTED_LANGUAGES: list[str] = ["English", "Spanish", "French", "German", "Arabic", "Italian"]
    TRANSLATION_MAX_INPUT_CHARACTERS: int = 5000
    
    # Authentication settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    class Config:
        env_file = "backend/.env"  

def get_settings() -> AppSettings:
    return AppSettings()
