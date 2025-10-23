from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
import os

from app.database import init_db
from app.routers import images, websocket
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="AI Image Processing Pipeline",
    description="Upload images and apply multiple AI models for processing",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PROCESSED_DIR, exist_ok=True)

# Mount static files for serving processed images
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/processed", StaticFiles(directory=settings.PROCESSED_DIR), name="processed")

# Mount static files for frontend
app.mount("/_app", StaticFiles(directory=os.path.join(settings.STATIC_FILES_DIR, '_app')), name="app-files")

# Include routers
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root():
    index_path = os.path.join(settings.STATIC_FILES_DIR, "index.html")
    with open(index_path, "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(settings.STATIC_FILES_DIR, "favicon.ico")
    with open(favicon_path, "rb") as f:
        return HTMLResponse(content=f.read(), media_type="image/x-icon")

@app.get('/favicon.png', include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(settings.STATIC_FILES_DIR, "favicon.png")
    with open(favicon_path, "rb") as f:
        return HTMLResponse(content=f.read(), media_type="image/png")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
