from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from app.database import ProcessingStatus


class ImageUploadResponse(BaseModel):
    id: int
    filename: str
    status: ProcessingStatus
    message: str


class ImageResponse(BaseModel):
    id: int
    filename: str
    original_path: str
    processed_path: Optional[str]
    status: ProcessingStatus
    uploaded_at: datetime
    processed_at: Optional[datetime]
    processing_time: Optional[float]
    error_message: Optional[str]
    model_results: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ProcessingUpdate(BaseModel):
    image_id: int
    status: ProcessingStatus
    message: str
    progress: Optional[float] = None
    model_results: Optional[Dict[str, Any]] = None
