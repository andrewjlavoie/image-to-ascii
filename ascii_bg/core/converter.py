"""Main ASCII art conversion engine.

Coordinates image processing and character mapping to convert
images into ASCII art.
"""

from pathlib import Path

import numpy as np

from ascii_bg.core.character_sets import CharacterSet
from ascii_bg.core.image_processor import ImageProcessor


class AsciiArt:
    """Container for ASCII art output.

    Stores the character grid and color data for rendering in different formats.
    """

    def __init__(
        self,
        char_grid: list[list[str]],
        color_grid: np.ndarray,
        width: int,
        height: int,
    ) -> None:
        """Initialize ASCII art container.

        Args:
            char_grid: 2D list of ASCII characters
            color_grid: 3D numpy array of RGB colors (height, width, 3)
            width: Width in characters
            height: Height in characters
        """
        self.char_grid = char_grid
        self.color_grid = color_grid
        self.width = width
        self.height = height

    def to_plain_text(self) -> str:
        """Convert to plain text (no colors).

        Returns:
            ASCII art as plain text string
        """
        return "\n".join("".join(row) for row in self.char_grid)

    def __str__(self) -> str:
        """String representation (plain text)."""
        return self.to_plain_text()

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"AsciiArt(width={self.width}, height={self.height})"


class AsciiConverter:
    """Main ASCII art converter.

    Converts images to ASCII art by processing the image and mapping
    brightness values to characters.
    """

    def __init__(
        self,
        resolution: tuple[int, int] | str = (1920, 1080),
        charset: str | CharacterSet | None = None,
        brightness: int = 0,
        contrast: int = 0,
        invert: bool = False,
        aspect_correct: bool = True,
    ) -> None:
        """Initialize ASCII converter.

        Args:
            resolution: Target resolution as (width, height) tuple or preset string
            charset: Character set to use (string or CharacterSet instance)
            brightness: Brightness adjustment (-100 to 100)
            contrast: Contrast adjustment (-100 to 100)
            invert: Invert character density (swap dark/light)
            aspect_correct: Apply aspect ratio correction for terminal display
        """
        # Parse resolution if string
        if isinstance(resolution, str):
            self.resolution = ImageProcessor.parse_resolution(resolution)
        else:
            self.resolution = resolution

        # Set up character set
        if charset is None:
            self.charset = CharacterSet()
        elif isinstance(charset, str):
            self.charset = CharacterSet(charset)
        else:
            self.charset = charset

        # Apply inversion if requested
        if invert:
            self.charset = self.charset.invert()

        # Set up image processor
        self.processor = ImageProcessor(
            brightness=brightness,
            contrast=contrast,
            aspect_correct=aspect_correct,
        )

    def convert(self, image_path: str | Path) -> AsciiArt:
        """Convert image to ASCII art.

        Args:
            image_path: Path to source image

        Returns:
            AsciiArt object containing the conversion result
        """
        # Process image
        grayscale, rgb = self.processor.process(image_path, self.resolution)

        # Convert to character grid
        char_grid = self._grayscale_to_chars(grayscale)

        return AsciiArt(
            char_grid=char_grid,
            color_grid=rgb,
            width=self.resolution[0],
            height=grayscale.shape[0],  # Use actual height after aspect correction
        )

    def _grayscale_to_chars(self, grayscale: np.ndarray) -> list[list[str]]:
        """Convert grayscale array to character grid.

        Args:
            grayscale: 2D numpy array of brightness values (0.0 to 1.0)

        Returns:
            2D list of ASCII characters
        """
        height, width = grayscale.shape
        char_grid = []

        for y in range(height):
            row = []
            for x in range(width):
                brightness = grayscale[y, x]
                char = self.charset.get_char(brightness)
                row.append(char)
            char_grid.append(row)

        return char_grid

    def set_resolution(self, resolution: tuple[int, int] | str) -> None:
        """Update target resolution.

        Args:
            resolution: New resolution as (width, height) or preset string
        """
        if isinstance(resolution, str):
            self.resolution = ImageProcessor.parse_resolution(resolution)
        else:
            self.resolution = resolution

    def set_charset(self, charset: str | CharacterSet) -> None:
        """Update character set.

        Args:
            charset: New character set (string or CharacterSet instance)
        """
        if isinstance(charset, str):
            self.charset = CharacterSet(charset)
        else:
            self.charset = charset

    def set_brightness(self, brightness: int) -> None:
        """Update brightness adjustment.

        Args:
            brightness: Brightness adjustment (-100 to 100)
        """
        self.processor.brightness = max(-100, min(100, brightness))

    def set_contrast(self, contrast: int) -> None:
        """Update contrast adjustment.

        Args:
            contrast: Contrast adjustment (-100 to 100)
        """
        self.processor.contrast = max(-100, min(100, contrast))

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"AsciiConverter(resolution={self.resolution}, charset_length={len(self.charset)})"
