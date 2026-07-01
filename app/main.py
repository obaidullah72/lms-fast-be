from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import Base, engine
from app.routes import auth

# Create database tables on startup (no Alembic needed for this simple setup)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LMS Authentication API",
    description="Cookie-based JWT authentication with FastAPI and SQLite",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "LMS API is running"}
