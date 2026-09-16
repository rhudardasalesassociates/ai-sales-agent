from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn

from app.config import settings
from app.messenger.webhook import router as webhook_router
from app.services.conversation import ConversationService
from app.services.products import ProductService


app = FastAPI(
    title="AI Sales Agent",
    description="Facebook Messenger AI Sales Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router, prefix="/webhook")

conversation_service = ConversationService()
product_service = ProductService()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Sales Agent...")
    await product_service.load_products()
    logger.info("Products loaded successfully")


@app.get("/")
async def root():
    return {
        "name": settings.business_name,
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/stats")
async def get_stats():
    stats = conversation_service.get_stats()
    return stats


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )