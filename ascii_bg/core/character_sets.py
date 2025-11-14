"""ASCII character set definitions for image conversion.

This module provides various character sets ordered by visual density,
used to map pixel brightness values to ASCII characters.
"""

from typing import Final

# Basic character set ordered by visual density (light to dark)
SIMPLE_SET: Final[str] = " .:-=+*#%@"

# Extended character set with more granularity for finer detail
EXTENDED_SET: Final[str] = (
    " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
)

# Block characters for solid fills
BLOCK_SET: Final[str] = " ░▒▓█"

# Minimal set for extreme simplicity
MINIMAL_SET: Final[str] = " .:#@"

# Default character set (extended)
DEFAULT_SET: Final[str] = EXTENDED_SET


class CharacterSet:
    """Manages ASCII character sets for conversion.

    Provides methods to get character sets and map brightness values
    to appropriate characters.
    """

    def __init__(self, charset: str = DEFAULT_SET) -> None:
        """Initialize character set.

        Args:
            charset: String of characters ordered from light to dark
        """
        if not charset:
            raise ValueError("Character set cannot be empty")

        self.charset = charset
        self.length = len(charset)

    def get_char(self, brightness: float) -> str:
        """Get character for given brightness value.

        Args:
            brightness: Normalized brightness value (0.0 to 1.0)

        Returns:
            ASCII character corresponding to brightness level
        """
        if not 0.0 <= brightness <= 1.0:
            brightness = max(0.0, min(1.0, brightness))

        # Map brightness to character index
        index = int(brightness * (self.length - 1))
        return self.charset[index]

    def invert(self) -> "CharacterSet":
        """Create inverted character set (dark to light).

        Returns:
            New CharacterSet with reversed order
        """
        return CharacterSet(self.charset[::-1])

    @classmethod
    def from_preset(cls, preset: str) -> "CharacterSet":
        """Create character set from preset name.

        Args:
            preset: Preset name ('simple', 'extended', 'block', 'minimal')

        Returns:
            CharacterSet instance

        Raises:
            ValueError: If preset name is invalid
        """
        presets = {
            "simple": SIMPLE_SET,
            "extended": EXTENDED_SET,
            "block": BLOCK_SET,
            "minimal": MINIMAL_SET,
        }

        if preset.lower() not in presets:
            available = ", ".join(presets.keys())
            raise ValueError(f"Invalid preset '{preset}'. Available: {available}")

        return cls(presets[preset.lower()])

    def __len__(self) -> int:
        """Get number of characters in set."""
        return self.length

    def __str__(self) -> str:
        """String representation of character set."""
        return self.charset

    def __repr__(self) -> str:
        """Detailed representation of character set."""
        return f"CharacterSet(length={self.length}, chars='{self.charset[:10]}...')"
