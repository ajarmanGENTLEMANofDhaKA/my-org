from .base_controller import BaseController
from utils import get_logger
from utils.enums import ResponseSignals

logger = get_logger(__name__)
class TranslatorController(BaseController):
    def __init__(self, generation_client, template_parser):
        super().__init__()
        self.generation_client = generation_client
        self.template_parser = template_parser

    def validtext(self, text: str, target_language: str) -> bool:
        if not text or len(text.strip()) == 0:
            return False, ResponseSignals.INVALID_EMPTY_TEXT.value
        
        if len(text) > self.app_settings.TRANSLATION_MAX_INPUT_CHARACTERS:
            return False, ResponseSignals.INVALID_LONG_TEXT.value
        
        if target_language not in self.app_settings.TRANSLATION_SUPPORTED_LANGUAGES:
            return False, ResponseSignals.INVALID_TRANSLATION_LANGUAGE.value
        
        return True, ResponseSignals.VALID_TEXT.value

    async def translate_text(self, text: str, target_language: str):
        try:
            system_prompt = self.template_parser.get("translator", "system_prompt")
            document_prompt = self.template_parser.get(
                "translator", "document_prompt", {"text": text, "target_language": target_language}
            )
            footer_prompt = self.template_parser.get("translator", "footer_prompt")
            user_prompt = "\n\n".join([document_prompt, footer_prompt])

            translation = await self.generation_client.generate_text(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1  # Lower temperature for more consistent translations
            )
            if not translation:
                logger.error("Failed to generate translation")
                raise

            logger.info(f"Successfully translated text to {target_language}")
            return translation.strip()

        except Exception as e:
            logger.error(f"Error translating text: {e}")
            raise

    def map_languages(self, lang_code: str) -> str:
        language_map = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "ar": "Arabic",
            "zh": "Chinese",
            "ja": "Japanese",
            "ru": "Russian",
            "pt": "Portuguese",
            "hi": "Hindi",
            "ko": "Korean",
            "tr": "Turkish",
        }
        return language_map.get(lang_code, "English")
        