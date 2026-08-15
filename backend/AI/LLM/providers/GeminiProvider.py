from ..LLMInterface import LLMInterface
from ..LLMEnums import GeminiEnums, DocumentTypeEnum
from google import genai
from google.genai.types import EmbedContentConfig, GenerateContentConfig, GenerationConfig, Content, Part
from utils import get_logger
logger = get_logger(__name__)

class GeminiProvider(LLMInterface):
    def __init__(self, api_key: str,
                default_max_input_characters: int = 1000,
                default_max_output_tokens: int = 1000,
                default_temperature: float = 0.7):

        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)

        self.default_max_input_characters = default_max_input_characters
        self.default_max_output_tokens = default_max_output_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None
        self.summarization_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.enums = GeminiEnums
        self.logger = get_logger(__name__)

    async def set_generation_model(self, generation_model_id: str):
        self.generation_model_id = generation_model_id

    async def set_summarization_model(self, summarization_model_id: str):
        self.summarization_model_id = summarization_model_id

    async def set_embedding_model(self, embedding_model_id: str, embedding_size: int):
        self.embedding_model_id = embedding_model_id
        self.embedding_size = embedding_size

    async def process_text(self, text: str):
        return text[:self.default_max_input_characters].strip()

    async def generate_text(
        self,
        user_prompt: str,
        system_prompt: str,
        temperature: float = None,
        max_output_tokens: int = None
    ):

        if not self.generation_model_id:
            self.logger.error("Generation model for Gemini was not set")
            raise Exception("Generation model for Gemini was not set")

        try:
            config = GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature or self.default_temperature,
                max_output_tokens=max_output_tokens or self.default_max_output_tokens,
            )

            chat = self.client.aio.chats.create(model=self.generation_model_id)
            response=await chat.send_message(
                message=user_prompt,
                config=config
            )
            if not response or not response.text:
                self.logger.error("No response from Gemini chat completion")
                return None
            
            self.logger.info(f"Received response from Gemini")
            return response.text

        except Exception as e:
            self.logger.error(f"Error in chat completion with Gemini: {str(e)}")
            raise

    async def embed_text(self, text: str, document_type: str = None):
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Gemini was not set")
            raise Exception("Embedding model for Gemini was not set")

        try:
            task_type = self.enums.DOCUMENT.value
            if document_type == DocumentTypeEnum.QUERY.value:
                task_type = self.enums.QUERY.value

            config = EmbedContentConfig(task_type=task_type, 
                                        output_dimensionality=self.embedding_size)
            
            results = await self.client.aio.models.embed_content(
                model=self.embedding_model_id,
                contents=text,
                config=config
            )

            if not results:
                self.logger.error("Error while embedding text with Gemini")
                return None

            return results.embeddings[0].values

        except Exception as e:
            self.logger.error(f"Error embedding text with Gemini: {str(e)}")
            raise

    async def summarize_text(self, user_prompt: str, system_prompt: str = "", temperature: float = None, max_output_tokens: int = None):
        if not self.summarization_model_id:
            self.logger.error("No model set for summarization with Gemini")
            raise Exception("summarization model for Gemini was not set")
        
        try:
            config = GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_output_tokens
            )

            summary = await self.client.aio.models.generate_content(
                model=self.summarization_model_id,
                contents=user_prompt,
                config=config
            )
            return summary.text
        
        except Exception as e:
            self.logger.error(f"Error summarizing text with Gemini: {str(e)}")
            raise

    async def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "parts": prompt
        }