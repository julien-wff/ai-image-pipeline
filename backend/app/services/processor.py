import time
import json
from datetime import datetime
from pathlib import Path
import os

from app.database import SessionLocal, ImageRecord, ProcessingStatus
from app.config import settings
from app.services.websocket_manager import manager
from app.services.ai_models import (
    apply_image_classification,
    apply_denoising,
    apply_captionning,
)


async def notify_progress(
    image_id: int,
    status: ProcessingStatus,
    message: str,
    progress: float | None = None,
    model_results: dict | None = None,
):
    """Send progress update via WebSocket"""
    update = {
        "type": "processing_update",
        "image_id": image_id,
        "status": status.value,
        "message": message,
        "progress": progress,
        "model_results": model_results,
        "timestamp": datetime.now().isoformat(),
    }
    await manager.broadcast(update)


async def process_image(image_id: int):
    """Process image through AI pipeline"""
    db = SessionLocal()
    start_time = time.time()
    image = None

    try:
        # Get image record
        image = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
        if not image:
            return

        # Update status to processing
        image.status = ProcessingStatus.PROCESSING
        db.commit()
        await notify_progress(
            image_id, ProcessingStatus.PROCESSING, "Starting processing...", 0
        )

        # Step 1: Image Classification
        image.label = apply_image_classification(image.upload_path)
        db.commit()
        await notify_progress(
            image_id, ProcessingStatus.PROCESSING, "Classifying image...", 0.33
        )

        # Step 2: Denoising
        processed_path = os.path.join(settings.PROCESSED_DIR, image.filename)
        denoising_result = apply_denoising(image.upload_path, processed_path)

        if not denoising_result.success:
            raise Exception(denoising_result.error or "Denoising failed")

        image.denoised_path = processed_path
        db.commit()

        await notify_progress(
            image_id, ProcessingStatus.PROCESSING, "Applying denoising...", 0.66
        )

        # Step 3: Captioning
        captionning_results = apply_captionning(image.upload_path)

        if not captionning_results.success:
            raise Exception(
                captionning_results.error or "Captioning failed: Unknown error"
            )

        image.caption = captionning_results.caption or ""
        db.commit()

        await notify_progress(
            image_id, ProcessingStatus.PROCESSING, "Generating captions...", 0.9
        )

        # Update database with results
        processing_time = time.time() - start_time
        image.status = ProcessingStatus.COMPLETED
        image.processed_path = processed_path
        image.processed_at = datetime.now()
        image.processing_time = processing_time
        db.commit()

        # Notify completion
        await notify_progress(
            image_id,
            ProcessingStatus.COMPLETED,
            "Processing completed successfully",
            1.0,
        )

    except Exception as e:
        # Handle errors
        if image:
            image.status = ProcessingStatus.FAILED
            image.error_message = str(e)
            image.processed_at = datetime.now()
            db.commit()

        await notify_progress(
            image_id, ProcessingStatus.FAILED, f"Processing failed: {str(e)}", None
        )

    finally:
        db.close()
