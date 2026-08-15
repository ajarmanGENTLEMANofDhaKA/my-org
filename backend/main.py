from AI.LLM import LLMProviderFactory, TemplateParser
from AI.VectorDB import VDBProviderFactory
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from routes import welcome, paper, projects, rag, summary, translator, explainer, auth
from utils import get_settings, get_logger
logger = get_logger(__name__)

app = FastAPI(
    title="Inquiro",
    description="Research Assistant API",
    version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db():
    settings= get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.mongodb_client = app.mongodb_conn[settings.MONGO_DB]

    llm_provider_factory = LLMProviderFactory(settings)
    vdb_provider_factory = VDBProviderFactory(settings) 

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    await app.generation_client.set_generation_model(generation_model_id = settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    await app.embedding_client.set_embedding_model(embedding_model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_SIZE)
    
    # summary client
    app.summary_client = llm_provider_factory.create(provider=settings.SUMMARY_BACKEND)
    await app.summary_client.set_summarization_model(summarization_model_id=settings.SUMMARY_MODEL_ID)

    app.template_parser = TemplateParser(lang=settings.LANG, default_lang=settings.DEFAULT_LANG)
    
    # vector db client
    app.vectordb_client = vdb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    await app.vectordb_client.connect()

@app.on_event("shutdown")
async def shutdown_db():
    app.mongodb_conn.close()
    await app.vectordb_client.disconnect()


app.include_router(auth.auth_router, prefix="/auth", tags=["authentication"])
app.include_router(welcome.welcome_router, prefix="", tags=["welcome"])
app.include_router(projects.project_router, prefix="/projects", tags=["projects"])
app.include_router(paper.paper_router, prefix="/projects/{project_id}/papers", tags=["papers"])
app.include_router(summary.summary_router, prefix="/projects/{project_id}/papers/{paper_id}/summaries", tags=["summaries"])
app.include_router(rag.rag_router, prefix="/projects/{project_id}", tags=["chat"])
app.include_router(translator.translator_router, prefix="/translator", tags=["translator"])
app.include_router(explainer.explainer_router, prefix="/explainer", tags=["explainer"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)