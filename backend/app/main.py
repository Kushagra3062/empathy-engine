from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import api, health
from app.utils.logger import setup_logging
from app.database import init_db
from app import db_models # Ensure models are registered

setup_logging(settings.LOG_LEVEL)

# Initialize database tables
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise-grade emotion-aware voice synthesis engine.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix=settings.API_V1_STR)
app.include_router(health.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
