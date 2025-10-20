import time
from datetime import datetime
import os
from typing import Optional
import json

from app.database import SessionLocal, ImageRecord, ProcessingStatus
from app.config import settings
from app.services.websocket_manager import manager
from app.schemas import ImageResponse

from app.services.ai_models import (
    apply_image_classification,
    apply_denoising,
    apply_captionning,
)


async def notify_progress(
        image: ImageRecord,
        msg: str | None = None,
        progress: float | None = None,
):
    """Send progress update via WebSocket"""
    update = {
        "image": json.loads(ImageResponse.from_model(image).model_dump_json()),
        "message": msg,
        "progress": progress,
    }
    await manager.broadcast(update)


async def process_image(image_id: int):
    """Process image through AI pipeline"""
    db = SessionLocal()
    start_time = time.time()
    image: Optional[ImageRecord] = None

    try:
        # Get image record
        image = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
        if not image:
            return

        # Update status to processing
        image.status = ProcessingStatus.PROCESSING
        db.commit()
        await notify_progress(image, "Classifying image...", .3)

        # Step 1: Image Classification
        image.label = apply_image_classification(image.upload_path)
        db.commit()
        await notify_progress(image, "Applying denoising...", .6)

        # Step 2: Denoising
        processed_path = os.path.join(settings.PROCESSED_DIR, image.filename)
        denoising_result = apply_denoising(image.upload_path, processed_path)

        if not denoising_result.success:
            raise Exception(denoising_result.error or "Denoising failed")

        image.denoised_path = processed_path
        db.commit()

        await notify_progress(image, "Captioning image...", .9)

        # Step 3: Captioning
        captioning_results = apply_captionning(image.upload_path)

        if not captioning_results.success:
            raise Exception(
                captioning_results.error or "Captioning failed: Unknown error"
            )

        image.caption = captioning_results.caption or ""
        processing_time = time.time() - start_time
        image.status = ProcessingStatus.COMPLETED
        image.processed_path = processed_path
        image.processed_at = datetime.now()
        image.processing_time = processing_time
        db.commit()

        # Notify completion
        await notify_progress(image, None, 1.0)

    except Exception as e:
        # Handle errors
        if image:
            image.status = ProcessingStatus.FAILED
            image.error_message = str(e)
            image.processed_at = datetime.now()
            db.commit()

        await notify_progress(image, f"Processing failed: {str(e)}")

    finally:
        db.close()
