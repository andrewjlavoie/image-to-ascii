"""Rendering utilities for ASCII art output.

Handles rendering ASCII art to various formats including images (PNG/JPG)
and JSON for LLM processing.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from numpy.typing import NDArray


class ImageRenderer:
    """Render ASCII art to image files (PNG/JPG)."""

    def __init__(
        self,
        font_family: str = "DejaVuSansMono",
        font_size: int = 10,
        bg_color: tuple[int, int, int] = (0, 0, 0),
    ) -> None:
        """Initialize image renderer.

        Args:
            font_family: Font family name (monospace recommended)
            font_size: Font size in points
            bg_color: Background color RGB tuple
        """
        self.font_size = font_size
        self.bg_color = bg_color

        # Try to load the font
        try:
            # Try common monospace fonts
            self.font = ImageFont.truetype(font_family, font_size)
        except OSError:
            # Try with .ttf extension
            try:
                self.font = ImageFont.truetype(f"{font_family}.ttf", font_size)
            except OSError:
                # Try system font paths
                font_paths = [
                    f"/usr/share/fonts/truetype/dejavu/{font_family}.ttf",
                    f"/usr/share/fonts/TTF/{font_family}.ttf",
                    f"/System/Library/Fonts/{font_family}.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
                ]

                font_loaded = False
                for path in font_paths:
                    try:
                        self.font = ImageFont.truetype(path, font_size)
                        font_loaded = True
                        break
                    except OSError:
                        continue

                if not font_loaded:
                    # Fall back to default PIL font
                    self.font = ImageFont.load_default()

    def render(
        self,
        char_grid: list[list[str]],
        color_grid: "NDArray[np.uint8]",
        output_path: str | Path,
    ) -> None:
        """Render ASCII art to image file.

        Args:
            char_grid: 2D list of ASCII characters
            color_grid: 3D numpy array of RGB colors (height, width, 3)
            output_path: Path to save image file

        Raises:
            ValueError: If grids are empty or mismatched
        """
        if not char_grid or not char_grid[0]:
            raise ValueError("Character grid cannot be empty")

        height = len(char_grid)
        width = len(char_grid[0])

        if color_grid.shape[0] != height or color_grid.shape[1] != width:
            raise ValueError("Color grid dimensions must match character grid")

        # Calculate character dimensions
        # Use a sample character to measure size
        bbox = self.font.getbbox("M")
        char_width = int(bbox[2] - bbox[0])
        char_height = int(bbox[3] - bbox[1])

        # Create image
        img_width = width * char_width
        img_height = height * char_height
        image = Image.new("RGB", (img_width, img_height), self.bg_color)
        draw = ImageDraw.Draw(image)

        # Draw each character
        for y, row in enumerate(char_grid):
            for x, char in enumerate(row):
                # Get color from grid
                if y < color_grid.shape[0] and x < color_grid.shape[1]:
                    color = tuple(color_grid[y, x].tolist())
                else:
                    color = (255, 255, 255)

                # Calculate position
                pos_x = x * char_width
                pos_y = y * char_height

                # Draw character
                draw.text((pos_x, pos_y), char, fill=color, font=self.font)

        # Save image
        output_path = Path(output_path)
        image.save(output_path)


class JSONExporter:
    """Export ASCII art to JSON format for LLM processing."""

    @staticmethod
    def export(
        char_grid: list[list[str]],
        color_grid: "NDArray[np.uint8]",
        output_path: str | Path,
        metadata: dict | None = None,
    ) -> None:
        """Export ASCII art to JSON file.

        Args:
            char_grid: 2D list of ASCII characters
            color_grid: 3D numpy array of RGB colors (height, width, 3)
            output_path: Path to save JSON file
            metadata: Optional metadata dict to include

        Raises:
            ValueError: If grids are empty or mismatched
        """
        if not char_grid or not char_grid[0]:
            raise ValueError("Character grid cannot be empty")

        height = len(char_grid)
        width = len(char_grid[0])

        if color_grid.shape[0] != height or color_grid.shape[1] != width:
            raise ValueError("Color grid dimensions must match character grid")

        # Convert color grid to list of lists of color objects
        colors = []
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b = color_grid[y, x].tolist()
                row.append({"r": r, "g": g, "b": b, "hex": f"#{r:02x}{g:02x}{b:02x}"})
            colors.append(row)

        # Build JSON structure
        data = {
            "metadata": metadata
            or {
                "width": width,
                "height": height,
                "created_at": datetime.now().isoformat(),
            },
            "dimensions": {"width": width, "height": height},
            "grid": char_grid,
            "colors": colors,
        }

        # Save to file
        output_path = Path(output_path)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def add_border(
    char_grid: list[list[str]],
    border_char: str = "#",
    padding: int = 1,
) -> list[list[str]]:
    """Add border and padding to character grid.

    Args:
        char_grid: 2D list of ASCII characters
        border_char: Character to use for border
        padding: Padding size (spaces between content and border)

    Returns:
        New character grid with border and padding

    Raises:
        ValueError: If grid is empty or padding is negative
    """
    if not char_grid or not char_grid[0]:
        raise ValueError("Character grid cannot be empty")

    if padding < 0:
        raise ValueError("Padding must be non-negative")

    width = len(char_grid[0])

    # Calculate new dimensions
    new_width = width + 2 * (padding + 1)

    # Create new grid
    new_grid = []

    # Top border
    new_grid.append([border_char] * new_width)

    # Top padding
    for _ in range(padding):
        row = [border_char] + [" "] * (new_width - 2) + [border_char]
        new_grid.append(row)

    # Content with side borders and padding
    for row in char_grid:
        new_row = [border_char] + [" "] * padding + list(row) + [" "] * padding + [border_char]
        new_grid.append(new_row)

    # Bottom padding
    for _ in range(padding):
        row = [border_char] + [" "] * (new_width - 2) + [border_char]
        new_grid.append(row)

    # Bottom border
    new_grid.append([border_char] * new_width)

    return new_grid


def add_border_to_colors(
    color_grid: "NDArray[np.uint8]",
    border_color: tuple[int, int, int] = (255, 255, 255),
    padding: int = 1,
) -> "NDArray[np.uint8]":
    """Add border and padding to color grid.

    Args:
        color_grid: 3D numpy array of RGB colors (height, width, 3)
        border_color: RGB color for border
        padding: Padding size

    Returns:
        New color grid with border and padding

    Raises:
        ValueError: If padding is negative
    """
    if padding < 0:
        raise ValueError("Padding must be non-negative")

    height, width = color_grid.shape[:2]

    # Calculate new dimensions
    new_width = width + 2 * (padding + 1)
    new_height = height + 2 * (padding + 1)

    # Create new color grid
    new_colors = np.zeros((new_height, new_width, 3), dtype=np.uint8)

    # Fill borders with border color
    new_colors[0, :] = border_color  # Top
    new_colors[-1, :] = border_color  # Bottom
    new_colors[:, 0] = border_color  # Left
    new_colors[:, -1] = border_color  # Right

    # Copy original content
    offset = padding + 1
    new_colors[offset : offset + height, offset : offset + width] = color_grid

    return new_colors
