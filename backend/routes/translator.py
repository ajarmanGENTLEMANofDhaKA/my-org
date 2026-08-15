from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from controllers import TranslatorController
from .schema import TranslateRequest
from utils.enums import ResponseSignals
from utils import get_logger

logger = get_logger(__name__)

translator_router = APIRouter()

@translator_router.post("/translate")
async def translate_text(request: Request, translate_request: TranslateRequest):
    logger.info("Incoming request to translate text")

    try:
        translator_controller = TranslatorController(
            generation_client=request.app.generation_client,
            template_parser=request.app.template_parser,
        )
        isvalid, message = translator_controller.validtext(translate_request.text, translate_request.target_language)
        if not isvalid:
            logger.error(f"Invalid translation request: {message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        translated_text = await translator_controller.translate_text(
            text=translate_request.text,
            target_language=translate_request.target_language,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignals.TRANSLATION_SUCCESS.value,
                "translated_text": translated_text,
            }
        )

    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= ResponseSignals.TRANSLATION_ERROR.value
        )
   