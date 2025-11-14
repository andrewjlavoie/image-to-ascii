"""Main ASCII art conversion engine.

Coordinates image processing and character mapping to convert
images into ASCII art.
"""

from pathlib import Path

import numpy as np

from ascii_bg.core.character_sets import CharacterSet
from ascii_bg.core.color_handler import ColorHandler, ColorMode
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
        color_handler: ColorHandler | None = None,
    ) -> None:
        """Initialize ASCII art container.

        Args:
            char_grid: 2D list of ASCII characters
            color_grid: 3D numpy array of RGB colors (height, width, 3)
            width: Width in characters
            height: Height in characters
            color_handler: Color handler for colored output
        """
        self.char_grid = char_grid
        self.color_grid = color_grid
        self.width = width
        self.height = height
        self.color_handler = color_handler

    def to_plain_text(self) -> str:
        """Convert to plain text (no colors).

        Returns:
            ASCII art as plain text string
        """
        return "\n".join("".join(row) for row in self.char_grid)

    def to_colored_text(self) -> str:
        """Convert to colored text with ANSI codes.

        Returns:
            ASCII art with ANSI color codes
        """
        if self.color_handler is None:
            return self.to_plain_text()

        return self.color_handler.apply_colors(self.char_grid, self.color_grid)

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
        color_handler: ColorHandler | None = None,
    ) -> None:
        """Initialize ASCII converter.

        Args:
            resolution: Target resolution as (width, height) tuple or preset string
            charset: Character set to use (string or CharacterSet instance)
            brightness: Brightness adjustment (-100 to 100)
            contrast: Contrast adjustment (-100 to 100)
            invert: Invert character density (swap dark/light)
            aspect_correct: Apply aspect ratio correction for terminal display
            color_handler: Color handler for colored output
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

        # Set up color handler
        self.color_handler = color_handler

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

        # Get actual dimensions (may differ due to aspect correction)
        actual_height, actual_width = grayscale.shape

        # Generate color grid based on color mode
        color_grid = self._generate_color_grid(rgb, actual_width, actual_height)

        return AsciiArt(
            char_grid=char_grid,
            color_grid=color_grid,
            width=self.resolution[0],
            height=actual_height,
            color_handler=self.color_handler,
        )

    def _generate_color_grid(self, source_rgb: np.ndarray, width: int, height: int) -> np.ndarray:
        """Generate color grid based on color mode.

        Args:
            source_rgb: Source image RGB array
            width: Target width
            height: Target height

        Returns:
            Color grid for output
        """
        if self.color_handler is None:
            return source_rgb

        mode = self.color_handler.mode

        if mode == ColorMode.SOURCE:
            # Use source image colors
            return source_rgb
        elif mode == ColorMode.RAINBOW:
            # Generate rainbow gradient
            return self.color_handler.generate_rainbow_gradient(width, height)
        elif mode == ColorMode.GRADIENT:
            # Generate custom gradient
            return self.color_handler.generate_custom_gradient(width, height)
        elif mode == ColorMode.SOLID:
            # Generate solid color
            return self.color_handler.generate_solid_colors(width, height)
        else:
            # BLACK_WHITE or unknown, use source
            return source_rgb

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
