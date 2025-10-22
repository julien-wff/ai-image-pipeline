"""
AI Model implementations for image processing pipeline.
These are placeholder implementations that you can replace with actual AI models.
"""

from PIL import Image
import time
from app.database import ImageLabel
from app.config import settings
import keras


classificationModel: keras.Model = keras.models.load_model(settings.CLASSIFIER_MODEL_PATH)
denoisingModel: keras.Model = keras.models.load_model(settings.DENOISER_MODEL_PATH)


class ImageClassificationResult:
    def __init__(self, label: ImageLabel, classes: dict[ImageLabel, float]):
        self.classes = classes
        self.label = label


def apply_image_classification(image_path: str) -> ImageClassificationResult:
    """
    Placeholder for image classification model.
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize((180, 180))
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = img_array.reshape((1, 180, 180, 3))

    preds = classificationModel.predict(img_array)
    labels = [label for label in ImageLabel]
    class_idx = preds.argmax()
    return ImageClassificationResult(
        labels[class_idx],
        {labels[i]: float(preds[0][i]) for i in range(len(labels))}
    )


class DenoisingResult:
    def __init__(self, success: bool, error: str | None = None):
        self.success = success
        self.error = error


def apply_denoising(input_path: str, output_path: str) -> DenoisingResult:
    """
    Placeholder for image denoising.
    """

    try:
        # Open and preprocess image
        img = Image.open(input_path).convert("RGB")
        img = img.resize((256, 256))
        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = img_array / 255.0
        img_array = img_array.reshape((1, 256, 256, 3))

        # Apply denoising model
        denoised_array = denoisingModel.predict(img_array)
        denoised_array = denoised_array.reshape((256, 256, 3))
        denoised_array = (denoised_array * 255).astype('uint8')

        # Save denoised image
        denoised_img = Image.fromarray(denoised_array)
        denoised_img.save(output_path)

        return DenoisingResult(success=True)
    except Exception as e:
        return DenoisingResult(success=False, error=str(e))


class CaptioningResult:
    def __init__(
        self, success: bool, caption: str | None = None, error: str | None = None
    ):
        self.success = success
        self.caption = caption
        self.error = error


def apply_captionning(image_path: str) -> CaptioningResult:
    """
    Placeholder for image captioning model.
    """
    time.sleep(1)  # Simulate processing time

    try:
        img = Image.open(image_path)

        # Get image dimensions
        width, height = img.size

        return CaptioningResult(
            success=True,
            caption=f"An image of size {width}x{height} pixels.",
        )
    except Exception as e:
        return CaptioningResult(success=False, error=str(e))
