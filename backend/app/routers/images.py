from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from pathlib import Path

from app.database import get_db, ImageRecord, ProcessingStatus
from app.schemas import ImageUploadResponse, ImageResponse
from app.config import settings
from app.services.processor import process_image

router = APIRouter()


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload an image for processing"""

    # Validate file extension
    file_ext = Path(file.filename or "").suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}",
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Save file
    try:
        contents = await file.read()

        # Check file size
        if len(contents) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024 * 1024)}MB",
            )

        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create database record
    db_image = ImageRecord(
        filename=file.filename, original_path=file_path, status=ProcessingStatus.PENDING
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    # Schedule background processing
    background_tasks.add_task(process_image, db_image.id)

    return ImageUploadResponse(
        id=db_image.id,
        filename=db_image.filename,
        status=db_image.status,
        message="Image uploaded successfully and queued for processing",
    )


@router.get("/", response_model=List[ImageResponse])
async def list_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all images"""
    images = db.query(ImageRecord).offset(skip).limit(limit).all()

    # Parse model_results from JSON string
    result = []
    for img in images:
        img_dict = {
            "id": img.id,
            "filename": img.filename,
            "original_path": img.original_path,
            "processed_path": img.processed_path,
            "status": img.status,
            "uploaded_at": img.uploaded_at,
            "processed_at": img.processed_at,
            "processing_time": img.processing_time,
            "error_message": img.error_message,
            "model_results": None,
        }

        if img.model_results:
            import json

            try:
                img_dict["model_results"] = json.loads(img.model_results)
            except json.JSONDecodeError:
                img_dict["model_results"] = None

        result.append(ImageResponse(**img_dict))

    return result


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    """Get a specific image by ID"""
    image = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Parse model_results
    img_dict = {
        "id": image.id,
        "filename": image.filename,
        "original_path": image.original_path,
        "processed_path": image.processed_path,
        "status": image.status,
        "uploaded_at": image.uploaded_at,
        "processed_at": image.processed_at,
        "processing_time": image.processing_time,
        "error_message": image.error_message,
        "model_results": None,
    }

    if image.model_results:
        import json

        try:
            img_dict["model_results"] = json.loads(image.model_results)
        except json.JSONDecodeError:
            img_dict["model_results"] = None

    return ImageResponse(**img_dict)


@router.delete("/{image_id}")
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    """Delete an image"""
    image = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete files
    try:
        if os.path.exists(image.original_path):
            os.remove(image.original_path)
        if image.processed_path and os.path.exists(image.processed_path):
            os.remove(image.processed_path)
    except Exception as e:
        print(f"Error deleting files: {e}")

    # Delete from database
    db.delete(image)
    db.commit()

    return {"message": "Image deleted successfully"}
