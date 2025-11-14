"""Tests for image processing functionality."""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ascii_bg.core.image_processor import ImageProcessor


@pytest.fixture
def test_image_path(tmp_path: Path) -> Path:
    """Create a simple test image."""
    # Create a 100x100 RGB gradient image
    img = Image.new("RGB", (100, 100))
    pixels = img.load()

    for y in range(100):
        for x in range(100):
            # Create gradient from black to white
            value = int((x + y) / 2 * 255 / 100)
            pixels[x, y] = (value, value, value)

    path = tmp_path / "test_image.png"
    img.save(path)
    return path


class TestImageProcessor:
    """Test ImageProcessor class."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        processor = ImageProcessor()
        assert processor.brightness == 0
        assert processor.contrast == 0
        assert processor.aspect_correct is True

    def test_init_custom(self) -> None:
        """Test custom initialization."""
        processor = ImageProcessor(
            brightness=50,
            contrast=-30,
            aspect_correct=False,
        )
        assert processor.brightness == 50
        assert processor.contrast == -30
        assert processor.aspect_correct is False

    def test_init_clamps_brightness(self) -> None:
        """Test brightness is clamped to -100 to 100."""
        processor1 = ImageProcessor(brightness=150)
        assert processor1.brightness == 100

        processor2 = ImageProcessor(brightness=-150)
        assert processor2.brightness == -100

    def test_init_clamps_contrast(self) -> None:
        """Test contrast is clamped to -100 to 100."""
        processor1 = ImageProcessor(contrast=150)
        assert processor1.contrast == 100

        processor2 = ImageProcessor(contrast=-150)
        assert processor2.contrast == -100

    def test_load_image(self, test_image_path: Path) -> None:
        """Test loading image from file."""
        processor = ImageProcessor()
        img = processor.load_image(test_image_path)

        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"
        assert img.size == (100, 100)

    def test_load_image_not_found(self) -> None:
        """Test loading non-existent image raises FileNotFoundError."""
        processor = ImageProcessor()
        with pytest.raises(FileNotFoundError):
            processor.load_image("nonexistent.png")

    def test_resize_image_no_aspect_correction(self, test_image_path: Path) -> None:
        """Test resizing without aspect ratio correction."""
        processor = ImageProcessor(aspect_correct=False)
        img = processor.load_image(test_image_path)
        resized = processor.resize_image(img, 50, 50)

        assert resized.size == (50, 50)

    def test_resize_image_with_aspect_correction(self, test_image_path: Path) -> None:
        """Test resizing with aspect ratio correction."""
        processor = ImageProcessor(aspect_correct=True)
        img = processor.load_image(test_image_path)
        resized = processor.resize_image(img, 50, 50)

        # Height should be adjusted by CHAR_ASPECT_RATIO (0.5)
        expected_height = int(50 * processor.CHAR_ASPECT_RATIO)
        assert resized.size == (50, expected_height)

    def test_apply_brightness_zero(self, test_image_path: Path) -> None:
        """Test brightness adjustment of 0 returns same image."""
        processor = ImageProcessor(brightness=0)
        img = processor.load_image(test_image_path)
        adjusted = processor.apply_brightness(img)

        # Should be same image object
        assert adjusted is img

    def test_apply_contrast_zero(self, test_image_path: Path) -> None:
        """Test contrast adjustment of 0 returns same image."""
        processor = ImageProcessor(contrast=0)
        img = processor.load_image(test_image_path)
        adjusted = processor.apply_contrast(img)

        # Should be same image object
        assert adjusted is img

    def test_to_grayscale(self, test_image_path: Path) -> None:
        """Test conversion to grayscale array."""
        processor = ImageProcessor()
        img = processor.load_image(test_image_path)
        gray = processor.to_grayscale(img)

        assert isinstance(gray, np.ndarray)
        assert gray.ndim == 2
        assert gray.shape == (100, 100)
        assert gray.dtype == np.float32
        assert np.all(gray >= 0.0) and np.all(gray <= 1.0)

    def test_to_rgb_array(self, test_image_path: Path) -> None:
        """Test conversion to RGB array."""
        processor = ImageProcessor()
        img = processor.load_image(test_image_path)
        rgb = processor.to_rgb_array(img)

        assert isinstance(rgb, np.ndarray)
        assert rgb.ndim == 3
        assert rgb.shape == (100, 100, 3)
        assert rgb.dtype == np.uint8

    def test_process(self, test_image_path: Path) -> None:
        """Test full processing pipeline."""
        processor = ImageProcessor(brightness=10, contrast=5)
        grayscale, rgb = processor.process(test_image_path, (50, 50))

        # Check grayscale output
        assert isinstance(grayscale, np.ndarray)
        assert grayscale.ndim == 2
        assert np.all(grayscale >= 0.0) and np.all(grayscale <= 1.0)

        # Check RGB output
        assert isinstance(rgb, np.ndarray)
        assert rgb.ndim == 3
        assert rgb.shape[2] == 3

    def test_parse_resolution_preset_4k(self) -> None:
        """Test parsing '4k' preset."""
        width, height = ImageProcessor.parse_resolution("4k")
        assert (width, height) == (3840, 2160)

    def test_parse_resolution_preset_1080p(self) -> None:
        """Test parsing '1080p' preset."""
        width, height = ImageProcessor.parse_resolution("1080p")
        assert (width, height) == (1920, 1080)

    def test_parse_resolution_custom(self) -> None:
        """Test parsing custom resolution."""
        width, height = ImageProcessor.parse_resolution("1920x1080")
        assert (width, height) == (1920, 1080)

    def test_parse_resolution_case_insensitive(self) -> None:
        """Test resolution parsing is case insensitive."""
        w1, h1 = ImageProcessor.parse_resolution("4K")
        w2, h2 = ImageProcessor.parse_resolution("4k")
        assert (w1, h1) == (w2, h2)

        w3, h3 = ImageProcessor.parse_resolution("1920X1080")
        assert (w3, h3) == (1920, 1080)

    def test_parse_resolution_invalid_format(self) -> None:
        """Test invalid resolution format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid resolution format"):
            ImageProcessor.parse_resolution("invalid")

    def test_parse_resolution_invalid_numbers(self) -> None:
        """Test invalid numbers raise ValueError."""
        with pytest.raises(ValueError, match="Invalid resolution format"):
            ImageProcessor.parse_resolution("abcxdef")

    def test_parse_resolution_negative(self) -> None:
        """Test negative dimensions raise ValueError."""
        with pytest.raises(ValueError, match="Invalid resolution format"):
            ImageProcessor.parse_resolution("-100x100")
