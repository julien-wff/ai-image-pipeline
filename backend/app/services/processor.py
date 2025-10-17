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

        # Initialize results dictionary
        results = {}

        # Step 2: Image Classification (33%)
        await notify_progress(
            image_id, ProcessingStatus.PROCESSING, "Classifying image...", 0.33
        )
        results["classification"] = apply_image_classification(image.original_path)

        # Step 3: Denoising (66%)
        await notify_progress(
            image_id, ProcessingStatus.PROCESSING, "Applying denoising...", 0.66
        )
        processed_path = os.path.join(
            settings.PROCESSED_DIR, f"processed_{Path(image.original_path).name}"
        )
        results["denoising"] = apply_denoising(image.original_path, processed_path)

        # Step 4: Captioning (90%)
        await notify_progress(
            image_id, ProcessingStatus.PROCESSING, "Generating captions...", 0.9
        )
        results["captioning"] = apply_captionning(image.original_path)

        # Update database with results
        processing_time = time.time() - start_time
        image.status = ProcessingStatus.COMPLETED
        image.processed_path = processed_path
        image.processed_at = datetime.now()
        image.processing_time = processing_time
        image.model_results = json.dumps(results)
        db.commit()

        # Notify completion
        await notify_progress(
            image_id,
            ProcessingStatus.COMPLETED,
            "Processing completed successfully",
            1.0,
            results,
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
