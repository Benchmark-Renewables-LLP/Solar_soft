from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.controllers.auth import router as auth_router  # Import auth routes

app = FastAPI(title="Solar Dashboard Backend")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # e.g., "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")  # Mount auth routes at /auth

@app.get("/health")
def health_check():
    return {"status": "healthy"}