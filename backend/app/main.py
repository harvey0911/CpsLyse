import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from pathlib import Path

load_dotenv() 

if not os.getenv("DB_USER"):
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
from app.database import init_db
from app.routers import audit





@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔍 Initializing CpsLyse Audit Engine...")
    try:
        # Build your tables (decret_reference, cps_articles, legal_mismatches)
        init_db()
        print("✅ Database ready.")
    except Exception as e:
        print(f"❌ Database error: {e}")
    yield

app = FastAPI(
    title="CpsLyse Audit API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only one router needed for your workflow
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])

@app.get("/")
def health_check():
    return {
        "status": "online",
        "workflow": "1. Upload -> 2. OCR -> 3. Decree Comparison"
    }