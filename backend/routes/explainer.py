from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from .schema import ExplainRequest 
from controllers import ExplainController    
from utils.enums import ResponseSignals
from utils import get_logger
logger = get_logger(__name__)

explainer_router = APIRouter()

@explainer_router.post("/explain")
async def explain_text(request: Request, explain_request: ExplainRequest):
    logger.info(f"Incoming request to explain text")

    try:
        explain_controller = ExplainController(
            generation_client=request.app.generation_client,
            template_parser=request.app.template_parser,
        )

        explanation = await explain_controller.explain_text(
            text=explain_request.text,
            context=explain_request.context,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignals.EXPLANATION_SUCCESS.value,
                "explanation": explanation,
            }
        )
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "signal": ResponseSignals.EXPLANATION_ERROR.value,
                "error": str(e)
            }
        )
