"""
Main FastAPI Application
backend/main.py

Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import complaint

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-powered Customer Complaint Management System for Pharmaceutical Manufacturing"
)

# ========== CORS MIDDLEWARE ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ROUTES ==========
app.include_router(complaint.router)

# ========== ROOT ENDPOINT ==========
@app.get("/")
async def root():
    return {
        "message": "🚀 AI-powered Customer Complaint Management System",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "docs": "/docs",
            "process_text": "POST /api/complaints/process-text",
            "process_document": "POST /api/complaints/process-document",
            "refine": "POST /api/complaints/refine",
            "commit": "POST /api/complaints/commit",
            "list": "GET /api/complaints/list",
            "get_one": "GET /api/complaints/{id}",
            "delete": "DELETE /api/complaints/{id}"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "groq_api_key_configured": bool(settings.GROQ_API_KEY),
        "database": settings.DATABASE_URL.split("://")[0]
    }

# ========== ERROR HANDLERS ==========
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {
        "error": str(exc),
        "detail": "An error occurred processing your request"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )