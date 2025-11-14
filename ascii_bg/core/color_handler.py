"""Color handling for ASCII art output.

Provides various color modes including ANSI terminal colors, rainbow gradients,
custom gradients, source image colors, and solid colors.
"""

from enum import Enum
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray


class ColorMode(Enum):
    """Supported color modes."""

    BLACK_WHITE = "black-white"
    SOURCE = "source"
    RAINBOW = "rainbow"
    GRADIENT = "gradient"
    SOLID = "solid"


def rgb_to_ansi(r: int, g: int, b: int) -> str:
    """Convert RGB values to ANSI 24-bit color escape code.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        ANSI escape code for foreground color
    """
    return f"\033[38;2;{r};{g};{b}m"


def rgb_to_ansi_bg(r: int, g: int, b: int) -> str:
    """Convert RGB values to ANSI 24-bit background color escape code.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        ANSI escape code for background color
    """
    return f"\033[48;2;{r};{g};{b}m"


def reset_color() -> str:
    """Get ANSI reset code."""
    return "\033[0m"


def parse_color(color_str: str) -> tuple[int, int, int]:
    """Parse color string to RGB tuple.

    Supports hex format (#RRGGBB) and named colors.

    Args:
        color_str: Color string (e.g., "#FF0000", "red")

    Returns:
        RGB tuple (0-255 values)

    Raises:
        ValueError: If color format is invalid
    """
    # Handle hex colors
    if color_str.startswith("#"):
        hex_str = color_str[1:]
        if len(hex_str) != 6:
            raise ValueError(f"Invalid hex color: {color_str}. Use #RRGGBB format.")

        try:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return (r, g, b)
        except ValueError as e:
            raise ValueError(f"Invalid hex color: {color_str}") from e

    # Handle named colors
    named_colors = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "gray": (128, 128, 128),
        "grey": (128, 128, 128),
    }

    color_lower = color_str.lower()
    if color_lower in named_colors:
        return named_colors[color_lower]

    raise ValueError(
        f"Unknown color: {color_str}. Use hex (#RRGGBB) or named color "
        f"({', '.join(named_colors.keys())})"
    )


class ColorHandler:
    """Handle color application for ASCII art."""

    def __init__(
        self,
        mode: ColorMode = ColorMode.BLACK_WHITE,
        bg_color: tuple[int, int, int] | None = None,
        text_color: tuple[int, int, int] | None = None,
        gradient_colors: list[tuple[int, int, int]] | None = None,
        gradient_direction: str = "horizontal",
    ) -> None:
        """Initialize color handler.

        Args:
            mode: Color mode to use
            bg_color: Background color (for solid mode)
            text_color: Text color (for solid mode)
            gradient_colors: List of RGB tuples for gradient mode
            gradient_direction: Direction for gradients (horizontal, vertical, diagonal)
        """
        self.mode = mode
        self.bg_color = bg_color or (0, 0, 0)
        self.text_color = text_color or (255, 255, 255)
        self.gradient_colors = gradient_colors or [(255, 0, 0), (0, 0, 255)]
        self.gradient_direction = gradient_direction

    def generate_rainbow_gradient(self, width: int, height: int) -> "NDArray[np.uint8]":
        """Generate rainbow gradient color array.

        Args:
            width: Width in characters
            height: Height in characters

        Returns:
            3D numpy array of RGB colors (height, width, 3)
        """
        colors = np.zeros((height, width, 3), dtype=np.uint8)

        if self.gradient_direction == "horizontal":
            # Horizontal rainbow
            for x in range(width):
                hue = x / width
                r, g, b = self._hsv_to_rgb(hue, 1.0, 1.0)
                colors[:, x] = [r, g, b]

        elif self.gradient_direction == "vertical":
            # Vertical rainbow
            for y in range(height):
                hue = y / height
                r, g, b = self._hsv_to_rgb(hue, 1.0, 1.0)
                colors[y, :] = [r, g, b]

        elif self.gradient_direction == "diagonal":
            # Diagonal rainbow
            for y in range(height):
                for x in range(width):
                    hue = (x + y) / (width + height)
                    r, g, b = self._hsv_to_rgb(hue, 1.0, 1.0)
                    colors[y, x] = [r, g, b]

        return colors

    def generate_custom_gradient(self, width: int, height: int) -> "NDArray[np.uint8]":
        """Generate custom gradient from specified colors.

        Args:
            width: Width in characters
            height: Height in characters

        Returns:
            3D numpy array of RGB colors (height, width, 3)
        """
        colors = np.zeros((height, width, 3), dtype=np.uint8)
        num_colors = len(self.gradient_colors)

        if num_colors < 2:
            # Single color, fill with that
            colors[:, :] = self.gradient_colors[0]
            return colors

        if self.gradient_direction == "horizontal":
            for x in range(width):
                pos = x / (width - 1) if width > 1 else 0
                r, g, b = self._interpolate_colors(pos, num_colors)
                colors[:, x] = [r, g, b]

        elif self.gradient_direction == "vertical":
            for y in range(height):
                pos = y / (height - 1) if height > 1 else 0
                r, g, b = self._interpolate_colors(pos, num_colors)
                colors[y, :] = [r, g, b]

        elif self.gradient_direction == "diagonal":
            max_dist = width + height - 2
            for y in range(height):
                for x in range(width):
                    pos = (x + y) / max_dist if max_dist > 0 else 0
                    r, g, b = self._interpolate_colors(pos, num_colors)
                    colors[y, x] = [r, g, b]

        return colors

    def generate_solid_colors(self, width: int, height: int) -> "NDArray[np.uint8]":
        """Generate solid color array.

        Args:
            width: Width in characters
            height: Height in characters

        Returns:
            3D numpy array of RGB colors (height, width, 3)
        """
        colors = np.zeros((height, width, 3), dtype=np.uint8)
        colors[:, :] = self.text_color
        return colors

    def apply_colors(self, char_grid: list[list[str]], color_array: "NDArray[np.uint8]") -> str:
        """Apply ANSI colors to character grid.

        Args:
            char_grid: 2D list of ASCII characters
            color_array: 3D array of RGB colors (height, width, 3)

        Returns:
            String with ANSI color codes
        """
        if self.mode == ColorMode.BLACK_WHITE:
            # No colors, just return plain text
            return "\n".join("".join(row) for row in char_grid)

        lines = []
        for y, row in enumerate(char_grid):
            line = ""
            for x, char in enumerate(row):
                if y < color_array.shape[0] and x < color_array.shape[1]:
                    r, g, b = color_array[y, x]
                    color_code = rgb_to_ansi(r, g, b)
                    line += f"{color_code}{char}{reset_color()}"
                else:
                    line += char
            lines.append(line)

        return "\n".join(lines)

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> tuple[int, int, int]:
        """Convert HSV to RGB.

        Args:
            h: Hue (0.0 to 1.0)
            s: Saturation (0.0 to 1.0)
            v: Value (0.0 to 1.0)

        Returns:
            RGB tuple (0-255 values)
        """
        if s == 0.0:
            val = int(v * 255)
            return (val, val, val)

        h = h * 6.0
        i = int(h)
        f = h - i

        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))

        i = i % 6

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return (int(r * 255), int(g * 255), int(b * 255))

    def _interpolate_colors(self, pos: float, num_colors: int) -> tuple[int, int, int]:
        """Interpolate between gradient colors.

        Args:
            pos: Position in gradient (0.0 to 1.0)
            num_colors: Number of colors in gradient

        Returns:
            Interpolated RGB tuple
        """
        # Clamp position
        pos = max(0.0, min(1.0, pos))

        # Find segment
        segment_size = 1.0 / (num_colors - 1)
        segment = int(pos / segment_size)

        # Handle edge case
        if segment >= num_colors - 1:
            return self.gradient_colors[-1]

        # Interpolate between two colors
        local_pos = (pos - segment * segment_size) / segment_size
        color1 = self.gradient_colors[segment]
        color2 = self.gradient_colors[segment + 1]

        r = int(color1[0] + (color2[0] - color1[0]) * local_pos)
        g = int(color1[1] + (color2[1] - color1[1]) * local_pos)
        b = int(color1[2] + (color2[2] - color1[2]) * local_pos)

        return (r, g, b)
