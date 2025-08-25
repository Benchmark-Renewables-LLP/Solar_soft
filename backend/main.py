import logging
logging.basicConfig(level=logging.DEBUG)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.controllers.auth import router as auth_router

app = FastAPI(title="Solar Dashboard Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth")

@app.get("/health")
def health_check():
    return {"status": "healthy"}