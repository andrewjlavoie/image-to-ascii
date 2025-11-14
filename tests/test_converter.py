"""Tests for ASCII art converter."""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ascii_bg.core.character_sets import SIMPLE_SET, CharacterSet
from ascii_bg.core.converter import AsciiArt, AsciiConverter


@pytest.fixture
def test_image_path(tmp_path: Path) -> Path:
    """Create a simple test image."""
    # Create a small 10x10 gradient image for quick tests
    img = Image.new("RGB", (10, 10))
    pixels = img.load()

    for y in range(10):
        for x in range(10):
            # Create gradient from black to white
            value = int((x + y) / 2 * 255 / 10)
            pixels[x, y] = (value, value, value)

    path = tmp_path / "test_image.png"
    img.save(path)
    return path


class TestAsciiArt:
    """Test AsciiArt container class."""

    def test_init(self) -> None:
        """Test initialization."""
        char_grid = [["a", "b"], ["c", "d"]]
        color_grid = np.zeros((2, 2, 3), dtype=np.uint8)

        art = AsciiArt(char_grid, color_grid, 2, 2)

        assert art.width == 2
        assert art.height == 2
        assert art.char_grid == char_grid
        assert isinstance(art.color_grid, np.ndarray)

    def test_to_plain_text(self) -> None:
        """Test conversion to plain text."""
        char_grid = [["a", "b", "c"], ["d", "e", "f"]]
        color_grid = np.zeros((2, 3, 3), dtype=np.uint8)

        art = AsciiArt(char_grid, color_grid, 3, 2)
        text = art.to_plain_text()

        assert text == "abc\ndef"

    def test_str(self) -> None:
        """Test __str__ method."""
        char_grid = [["x", "y"]]
        color_grid = np.zeros((1, 2, 3), dtype=np.uint8)

        art = AsciiArt(char_grid, color_grid, 2, 1)

        assert str(art) == "xy"

    def test_repr(self) -> None:
        """Test __repr__ method."""
        char_grid = [["a"]]
        color_grid = np.zeros((1, 1, 3), dtype=np.uint8)

        art = AsciiArt(char_grid, color_grid, 100, 50)
        repr_str = repr(art)

        assert "AsciiArt" in repr_str
        assert "100" in repr_str
        assert "50" in repr_str


class TestAsciiConverter:
    """Test AsciiConverter class."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        converter = AsciiConverter()

        assert converter.resolution == (1920, 1080)
        assert isinstance(converter.charset, CharacterSet)
        assert converter.processor.brightness == 0
        assert converter.processor.contrast == 0

    def test_init_custom_resolution_tuple(self) -> None:
        """Test initialization with custom resolution tuple."""
        converter = AsciiConverter(resolution=(100, 50))

        assert converter.resolution == (100, 50)

    def test_init_custom_resolution_string(self) -> None:
        """Test initialization with resolution string."""
        converter = AsciiConverter(resolution="4k")

        assert converter.resolution == (3840, 2160)

    def test_init_custom_charset_string(self) -> None:
        """Test initialization with custom charset string."""
        custom = " .:#@"
        converter = AsciiConverter(charset=custom)

        assert str(converter.charset) == custom

    def test_init_custom_charset_object(self) -> None:
        """Test initialization with CharacterSet object."""
        charset = CharacterSet(SIMPLE_SET)
        converter = AsciiConverter(charset=charset)

        assert converter.charset is charset

    def test_init_with_invert(self) -> None:
        """Test initialization with invert=True."""
        converter = AsciiConverter(charset=SIMPLE_SET, invert=True)

        # Should be inverted
        assert str(converter.charset) == SIMPLE_SET[::-1]

    def test_init_brightness_contrast(self) -> None:
        """Test initialization with brightness and contrast."""
        converter = AsciiConverter(brightness=50, contrast=-30)

        assert converter.processor.brightness == 50
        assert converter.processor.contrast == -30

    def test_init_aspect_correct(self) -> None:
        """Test initialization with aspect_correct."""
        converter1 = AsciiConverter(aspect_correct=True)
        assert converter1.processor.aspect_correct is True

        converter2 = AsciiConverter(aspect_correct=False)
        assert converter2.processor.aspect_correct is False

    def test_convert(self, test_image_path: Path) -> None:
        """Test basic conversion."""
        converter = AsciiConverter(resolution=(10, 10))
        art = converter.convert(test_image_path)

        assert isinstance(art, AsciiArt)
        assert art.width == 10
        assert len(art.char_grid) > 0
        assert len(art.char_grid[0]) == 10

    def test_convert_produces_valid_chars(self, test_image_path: Path) -> None:
        """Test that conversion produces valid characters."""
        converter = AsciiConverter(
            resolution=(5, 5),
            charset=SIMPLE_SET,
        )
        art = converter.convert(test_image_path)

        # Check all characters are from charset
        for row in art.char_grid:
            for char in row:
                assert char in SIMPLE_SET

    def test_convert_with_effects(self, test_image_path: Path) -> None:
        """Test conversion with brightness and contrast."""
        converter = AsciiConverter(
            resolution=(5, 5),
            brightness=20,
            contrast=10,
        )
        art = converter.convert(test_image_path)

        assert isinstance(art, AsciiArt)
        assert len(art.char_grid) > 0

    def test_set_resolution_tuple(self) -> None:
        """Test updating resolution with tuple."""
        converter = AsciiConverter()
        converter.set_resolution((640, 480))

        assert converter.resolution == (640, 480)

    def test_set_resolution_string(self) -> None:
        """Test updating resolution with string."""
        converter = AsciiConverter()
        converter.set_resolution("1080p")

        assert converter.resolution == (1920, 1080)

    def test_set_charset_string(self) -> None:
        """Test updating charset with string."""
        converter = AsciiConverter()
        converter.set_charset(SIMPLE_SET)

        assert str(converter.charset) == SIMPLE_SET

    def test_set_charset_object(self) -> None:
        """Test updating charset with CharacterSet."""
        converter = AsciiConverter()
        new_charset = CharacterSet(SIMPLE_SET)
        converter.set_charset(new_charset)

        assert converter.charset is new_charset

    def test_set_brightness(self) -> None:
        """Test updating brightness."""
        converter = AsciiConverter()
        converter.set_brightness(75)

        assert converter.processor.brightness == 75

    def test_set_brightness_clamps(self) -> None:
        """Test brightness is clamped."""
        converter = AsciiConverter()
        converter.set_brightness(150)

        assert converter.processor.brightness == 100

    def test_set_contrast(self) -> None:
        """Test updating contrast."""
        converter = AsciiConverter()
        converter.set_contrast(-50)

        assert converter.processor.contrast == -50

    def test_set_contrast_clamps(self) -> None:
        """Test contrast is clamped."""
        converter = AsciiConverter()
        converter.set_contrast(-150)

        assert converter.processor.contrast == -100

    def test_repr(self) -> None:
        """Test __repr__ method."""
        converter = AsciiConverter(resolution=(1920, 1080))
        repr_str = repr(converter)

        assert "AsciiConverter" in repr_str
        assert "1920" in repr_str
        assert "1080" in repr_str
