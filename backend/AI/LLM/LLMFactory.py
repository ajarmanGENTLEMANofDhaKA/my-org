from .LLMEnums import LLMModel
from AI.LLM import GeminiProvider

class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMModel.GEMINI.value:
            return GeminiProvider(
                api_key=self.config.GEMINI_API_KEY,
                default_max_input_characters=self.config.DEFAULT_MAX_INPUT_CHARACTERS,
                default_max_output_tokens=self.config.DEFAULT_MAX_TOKENS,
                default_temperature=self.config.DEFAULT_TEMPERATURE
            )

        return None