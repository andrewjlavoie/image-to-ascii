"""Core API for ASCII art conversion."""

from ascii_bg.core.character_sets import CharacterSet
from ascii_bg.core.color_handler import ColorHandler, ColorMode, parse_color
from ascii_bg.core.converter import AsciiArt, AsciiConverter
from ascii_bg.core.image_processor import ImageProcessor
from ascii_bg.core.renderer import (
    ImageRenderer,
    JSONExporter,
    add_border,
    add_border_to_colors,
)

__all__ = [
    "AsciiConverter",
    "AsciiArt",
    "CharacterSet",
    "ImageProcessor",
    "ColorHandler",
    "ColorMode",
    "parse_color",
    "ImageRenderer",
    "JSONExporter",
    "add_border",
    "add_border_to_colors",
]
