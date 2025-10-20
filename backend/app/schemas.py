from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from app.database import ImageRecord, ProcessingStatus, ImageLabel


class ImageResponse(BaseModel):
    # Technical fields
    id: int
    status: ProcessingStatus
    uploaded_at: datetime

    # File
    original_filename: str
    upload_path: str
    processed_path: Optional[str]

    # Processing details
    processed_at: Optional[datetime]
    processing_time: Optional[float]
    error_message: Optional[str]

    # Image attributes
    label: Optional[ImageLabel]
    caption: Optional[str]

    class Config:
        from_attributes = True

    @staticmethod
    def from_model(model: ImageRecord):
        return ImageResponse(
            id=model.id,
            status=model.status,
            uploaded_at=model.uploaded_at,
            original_filename=model.original_filename,
            upload_path=f'/uploads/{model.filename}',
            processed_path=f'/processed/{model.filename}' if model.processed_path else None,
            processed_at=model.processed_at,
            processing_time=model.processing_time,
            error_message=model.error_message,
            label=model.label,
            caption=model.caption,
        )


class ProcessingUpdate(BaseModel):
    image_id: int
    status: ProcessingStatus
    message: str
    progress: Optional[float] = None
    model_results: Optional[Dict[str, Any]] = None
