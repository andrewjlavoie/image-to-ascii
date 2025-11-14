"""Tests for color handler functionality."""

import numpy as np
import pytest

from ascii_bg.core.color_handler import (
    ColorHandler,
    ColorMode,
    parse_color,
    reset_color,
    rgb_to_ansi,
    rgb_to_ansi_bg,
)


class TestColorUtilityFunctions:
    """Test color utility functions."""

    def test_rgb_to_ansi(self) -> None:
        """Test RGB to ANSI foreground color conversion."""
        result = rgb_to_ansi(255, 0, 0)
        assert result == "\033[38;2;255;0;0m"

    def test_rgb_to_ansi_bg(self) -> None:
        """Test RGB to ANSI background color conversion."""
        result = rgb_to_ansi_bg(0, 255, 0)
        assert result == "\033[48;2;0;255;0m"

    def test_reset_color(self) -> None:
        """Test color reset code."""
        assert reset_color() == "\033[0m"

    def test_parse_color_hex(self) -> None:
        """Test parsing hex color."""
        r, g, b = parse_color("#FF0000")
        assert (r, g, b) == (255, 0, 0)

    def test_parse_color_hex_lowercase(self) -> None:
        """Test parsing lowercase hex color."""
        r, g, b = parse_color("#00ff00")
        assert (r, g, b) == (0, 255, 0)

    def test_parse_color_named(self) -> None:
        """Test parsing named color."""
        r, g, b = parse_color("red")
        assert (r, g, b) == (255, 0, 0)

    def test_parse_color_named_case_insensitive(self) -> None:
        """Test named color is case insensitive."""
        r1, g1, b1 = parse_color("RED")
        r2, g2, b2 = parse_color("red")
        assert (r1, g1, b1) == (r2, g2, b2)

    def test_parse_color_invalid_hex(self) -> None:
        """Test parsing invalid hex color raises ValueError."""
        with pytest.raises(ValueError, match="Invalid hex color"):
            parse_color("#FF")

    def test_parse_color_invalid_hex_chars(self) -> None:
        """Test parsing hex color with invalid characters."""
        with pytest.raises(ValueError, match="Invalid hex color"):
            parse_color("#GGGGGG")

    def test_parse_color_unknown_name(self) -> None:
        """Test parsing unknown named color raises ValueError."""
        with pytest.raises(ValueError, match="Unknown color"):
            parse_color("notacolor")


class TestColorMode:
    """Test ColorMode enum."""

    def test_color_mode_values(self) -> None:
        """Test ColorMode enum values."""
        assert ColorMode.BLACK_WHITE.value == "black-white"
        assert ColorMode.SOURCE.value == "source"
        assert ColorMode.RAINBOW.value == "rainbow"
        assert ColorMode.GRADIENT.value == "gradient"
        assert ColorMode.SOLID.value == "solid"


class TestColorHandler:
    """Test ColorHandler class."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        handler = ColorHandler()
        assert handler.mode == ColorMode.BLACK_WHITE
        assert handler.bg_color == (0, 0, 0)
        assert handler.text_color == (255, 255, 255)

    def test_init_rainbow(self) -> None:
        """Test initialization with rainbow mode."""
        handler = ColorHandler(mode=ColorMode.RAINBOW)
        assert handler.mode == ColorMode.RAINBOW

    def test_generate_rainbow_gradient_horizontal(self) -> None:
        """Test horizontal rainbow gradient generation."""
        handler = ColorHandler(mode=ColorMode.RAINBOW, gradient_direction="horizontal")
        colors = handler.generate_rainbow_gradient(10, 5)

        assert colors.shape == (5, 10, 3)
        assert colors.dtype == np.uint8
        # All rows should be the same (horizontal gradient)
        assert np.array_equal(colors[0], colors[1])

    def test_generate_rainbow_gradient_vertical(self) -> None:
        """Test vertical rainbow gradient generation."""
        handler = ColorHandler(mode=ColorMode.RAINBOW, gradient_direction="vertical")
        colors = handler.generate_rainbow_gradient(5, 10)

        assert colors.shape == (10, 5, 3)
        # All columns should be the same (vertical gradient)
        assert np.array_equal(colors[:, 0], colors[:, 1])

    def test_generate_rainbow_gradient_diagonal(self) -> None:
        """Test diagonal rainbow gradient generation."""
        handler = ColorHandler(mode=ColorMode.RAINBOW, gradient_direction="diagonal")
        colors = handler.generate_rainbow_gradient(10, 10)

        assert colors.shape == (10, 10, 3)
        # Diagonal should have varying colors
        assert not np.array_equal(colors[0, 0], colors[5, 5])

    def test_generate_custom_gradient_horizontal(self) -> None:
        """Test custom gradient generation."""
        colors_list = [(255, 0, 0), (0, 0, 255)]
        handler = ColorHandler(
            mode=ColorMode.GRADIENT,
            gradient_colors=colors_list,
            gradient_direction="horizontal",
        )
        colors = handler.generate_custom_gradient(10, 5)

        assert colors.shape == (5, 10, 3)
        # First column should be close to red
        assert colors[0, 0, 0] > 200  # Red channel high
        # Last column should be close to blue
        assert colors[0, -1, 2] > 200  # Blue channel high

    def test_generate_custom_gradient_single_color(self) -> None:
        """Test custom gradient with single color."""
        colors_list = [(128, 128, 128)]
        handler = ColorHandler(mode=ColorMode.GRADIENT, gradient_colors=colors_list)
        colors = handler.generate_custom_gradient(5, 5)

        # Should fill with the single color
        assert np.all(colors == [128, 128, 128])

    def test_generate_solid_colors(self) -> None:
        """Test solid color generation."""
        text_color = (255, 0, 0)
        handler = ColorHandler(mode=ColorMode.SOLID, text_color=text_color)
        colors = handler.generate_solid_colors(10, 10)

        assert colors.shape == (10, 10, 3)
        # All should be the text color
        assert np.all(colors == text_color)

    def test_apply_colors_black_white(self) -> None:
        """Test applying colors in black-white mode."""
        handler = ColorHandler(mode=ColorMode.BLACK_WHITE)
        char_grid = [["a", "b"], ["c", "d"]]
        color_array = np.zeros((2, 2, 3), dtype=np.uint8)

        result = handler.apply_colors(char_grid, color_array)

        # Should return plain text
        assert result == "ab\ncd"
        assert "\033[" not in result

    def test_apply_colors_with_colors(self) -> None:
        """Test applying colors with color mode."""
        handler = ColorHandler(mode=ColorMode.SOURCE)
        char_grid = [["a", "b"]]
        color_array = np.array([[[255, 0, 0], [0, 255, 0]]], dtype=np.uint8)

        result = handler.apply_colors(char_grid, color_array)

        # Should contain ANSI codes
        assert "\033[38;2" in result
        assert "\033[0m" in result
        # Should contain the characters
        assert "a" in result
        assert "b" in result

    def test_hsv_to_rgb(self) -> None:
        """Test HSV to RGB conversion."""
        handler = ColorHandler()

        # Red
        r, g, b = handler._hsv_to_rgb(0.0, 1.0, 1.0)
        assert (r, g, b) == (255, 0, 0)

        # Green (approx)
        r, g, b = handler._hsv_to_rgb(1 / 3, 1.0, 1.0)
        assert g > 200  # Green should be high

        # White (no saturation)
        r, g, b = handler._hsv_to_rgb(0.0, 0.0, 1.0)
        assert (r, g, b) == (255, 255, 255)

    def test_interpolate_colors(self) -> None:
        """Test color interpolation."""
        colors_list = [(255, 0, 0), (0, 0, 255)]
        handler = ColorHandler(gradient_colors=colors_list)

        # Start position
        r, g, b = handler._interpolate_colors(0.0, 2)
        assert (r, g, b) == (255, 0, 0)

        # End position
        r, g, b = handler._interpolate_colors(1.0, 2)
        assert (r, g, b) == (0, 0, 255)

        # Middle position
        r, g, b = handler._interpolate_colors(0.5, 2)
        assert r > 100 and r < 200  # Should be a mix
        assert b > 100 and b < 200
