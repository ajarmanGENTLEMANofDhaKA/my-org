from .base_controller import BaseController
from utils import get_logger
logger = get_logger(__name__)

class ExplainController(BaseController):
    def __init__(self, generation_client, template_parser):
        super().__init__()
        self.generation_client = generation_client
        self.template_parser = template_parser

    async def explain_text(self, text: str, context: str = None):
        try:
            system_prompt = self.template_parser.get("explainer", "system_prompt")
            
            if context:
                document_prompt = self.template_parser.get(
                    "explainer", "document_prompt_with_context", {"text": text, "context": context}
                )
            else:
                document_prompt = self.template_parser.get(
                    "explainer", "document_prompt", {"text": text}
                )
            footer_prompt = self.template_parser.get("explainer", "footer_prompt")
            user_prompt = "\n\n".join([document_prompt, footer_prompt])

            explanation = await self.generation_client.generate_text(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.6 
            )

            if not explanation:
                logger.error("Failed to generate explanation")
                raise

            logger.info(f"Successfully explained text")
            return explanation.strip()

        except Exception as e:
            logger.error(f"Error explaining text: {e}")
            raise
        