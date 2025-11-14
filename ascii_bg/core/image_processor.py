"""Image processing utilities for ASCII conversion.

Handles image loading, resizing, and preprocessing operations.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance


class ImageProcessor:
    """Process images for ASCII art conversion.

    Handles loading, resizing, and applying various image transformations
    like brightness, contrast adjustments, and aspect ratio correction.
    """

    # Terminal character aspect ratio (width/height)
    # Most terminal fonts are roughly twice as tall as they are wide
    CHAR_ASPECT_RATIO: float = 0.5

    def __init__(
        self,
        brightness: int = 0,
        contrast: int = 0,
        aspect_correct: bool = True,
    ) -> None:
        """Initialize image processor.

        Args:
            brightness: Brightness adjustment (-100 to 100)
            contrast: Contrast adjustment (-100 to 100)
            aspect_correct: Apply aspect ratio correction for terminal display
        """
        self.brightness = max(-100, min(100, brightness))
        self.contrast = max(-100, min(100, contrast))
        self.aspect_correct = aspect_correct

    def load_image(self, image_path: str | Path) -> Image.Image:
        """Load image from file.

        Args:
            image_path: Path to image file

        Returns:
            PIL Image object

        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If file is not a valid image
        """
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            img = Image.open(path)
            # Convert to RGB if needed (handles RGBA, grayscale, etc.)
            if img.mode != "RGB":
                img = img.convert("RGB")
            return img
        except Exception as e:
            raise ValueError(f"Failed to load image: {e}") from e

    def resize_image(
        self,
        image: Image.Image,
        target_width: int,
        target_height: int,
    ) -> Image.Image:
        """Resize image to target dimensions with aspect ratio correction.

        Args:
            image: PIL Image to resize
            target_width: Target width in characters
            target_height: Target height in characters

        Returns:
            Resized PIL Image
        """
        # Apply aspect ratio correction if enabled
        if self.aspect_correct:
            # Adjust height to compensate for character aspect ratio
            target_height = int(target_height * self.CHAR_ASPECT_RATIO)

        # Use LANCZOS for high-quality downsampling
        resized = image.resize(
            (target_width, target_height),
            Image.Resampling.LANCZOS,
        )

        return resized

    def apply_brightness(self, image: Image.Image) -> Image.Image:
        """Apply brightness adjustment to image.

        Args:
            image: PIL Image to adjust

        Returns:
            Brightness-adjusted image
        """
        if self.brightness == 0:
            return image

        # Convert brightness (-100 to 100) to enhancement factor (0.0 to 2.0)
        factor = 1.0 + (self.brightness / 100.0)
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    def apply_contrast(self, image: Image.Image) -> Image.Image:
        """Apply contrast adjustment to image.

        Args:
            image: PIL Image to adjust

        Returns:
            Contrast-adjusted image
        """
        if self.contrast == 0:
            return image

        # Convert contrast (-100 to 100) to enhancement factor (0.0 to 2.0)
        factor = 1.0 + (self.contrast / 100.0)
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    def to_grayscale(self, image: Image.Image) -> np.ndarray:
        """Convert image to grayscale brightness array.

        Args:
            image: PIL Image to convert

        Returns:
            2D numpy array of brightness values (0.0 to 1.0)
        """
        gray_img = image.convert("L")
        array = np.array(gray_img, dtype=np.float32)
        # Normalize to 0.0-1.0 range
        return array / 255.0

    def to_rgb_array(self, image: Image.Image) -> np.ndarray:
        """Convert image to RGB array.

        Args:
            image: PIL Image to convert

        Returns:
            3D numpy array of shape (height, width, 3) with RGB values (0-255)
        """
        return np.array(image, dtype=np.uint8)

    def process(
        self,
        image_path: str | Path,
        target_size: tuple[int, int],
    ) -> tuple[np.ndarray, np.ndarray]:
        """Process image for ASCII conversion.

        Loads image, applies all transformations, and returns both
        grayscale and color data.

        Args:
            image_path: Path to source image
            target_size: Target size as (width, height) in characters

        Returns:
            Tuple of (grayscale_array, rgb_array)
        """
        # Load and resize
        img = self.load_image(image_path)
        img = self.resize_image(img, target_size[0], target_size[1])

        # Apply effects
        img = self.apply_brightness(img)
        img = self.apply_contrast(img)

        # Convert to arrays
        grayscale = self.to_grayscale(img)
        rgb = self.to_rgb_array(img)

        return grayscale, rgb

    @staticmethod
    def parse_resolution(resolution_str: str) -> tuple[int, int]:
        """Parse resolution string to (width, height) tuple.

        Supports both presets (e.g., '4k', '1080p') and custom formats
        (e.g., '1920x1080').

        Args:
            resolution_str: Resolution string

        Returns:
            Tuple of (width, height)

        Raises:
            ValueError: If resolution format is invalid
        """
        # Resolution presets
        presets = {
            "8k": (7680, 4320),
            "4k": (3840, 2160),
            "1440p": (2560, 1440),
            "1080p": (1920, 1080),
            "720p": (1280, 720),
            "480p": (854, 480),
        }

        # Check if it's a preset
        if resolution_str.lower() in presets:
            return presets[resolution_str.lower()]

        # Parse custom format (WIDTHxHEIGHT)
        if "x" not in resolution_str.lower():
            raise ValueError(
                f"Invalid resolution format: '{resolution_str}'. "
                f"Use preset (4k, 1080p) or WIDTHxHEIGHT format."
            )

        try:
            parts = resolution_str.lower().split("x")
            width = int(parts[0])
            height = int(parts[1])

            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive")

            return width, height
        except (ValueError, IndexError) as e:
            raise ValueError(
                f"Invalid resolution format: '{resolution_str}'. "
                f"Use preset (4k, 1080p) or WIDTHxHEIGHT format."
            ) from e
