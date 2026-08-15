from enum import Enum

class LLMModel(Enum):
    GEMINI="gemini"
class GeminiEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "model"

    DOCUMENT = "RETRIEVAL_DOCUMENT"
    QUERY = "RETRIEVAL_QUERY"

class DocumentTypeEnum(Enum):
    DOCUMENT = "document"
    QUERY = "query"

