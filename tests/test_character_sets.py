"""Tests for character set functionality."""

import pytest

from ascii_bg.core.character_sets import (
    BLOCK_SET,
    EXTENDED_SET,
    MINIMAL_SET,
    SIMPLE_SET,
    CharacterSet,
)


class TestCharacterSet:
    """Test CharacterSet class."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        charset = CharacterSet()
        assert len(charset) > 0
        assert str(charset) == EXTENDED_SET

    def test_init_custom(self) -> None:
        """Test custom character set."""
        custom = " .:#@"
        charset = CharacterSet(custom)
        assert str(charset) == custom
        assert len(charset) == 5

    def test_init_empty_raises(self) -> None:
        """Test that empty charset raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            CharacterSet("")

    def test_get_char_min_brightness(self) -> None:
        """Test character for minimum brightness (0.0)."""
        charset = CharacterSet(SIMPLE_SET)
        char = charset.get_char(0.0)
        assert char == " "  # First character (lightest)

    def test_get_char_max_brightness(self) -> None:
        """Test character for maximum brightness (1.0)."""
        charset = CharacterSet(SIMPLE_SET)
        char = charset.get_char(1.0)
        assert char == "@"  # Last character (darkest)

    def test_get_char_mid_brightness(self) -> None:
        """Test character for middle brightness (0.5)."""
        charset = CharacterSet(SIMPLE_SET)
        char = charset.get_char(0.5)
        # Should return middle character
        assert char in SIMPLE_SET

    def test_get_char_clamps_values(self) -> None:
        """Test that brightness values are clamped to 0.0-1.0."""
        charset = CharacterSet(SIMPLE_SET)

        # Test below range
        char_low = charset.get_char(-0.5)
        assert char_low == " "  # Should clamp to 0.0

        # Test above range
        char_high = charset.get_char(1.5)
        assert char_high == "@"  # Should clamp to 1.0

    def test_invert(self) -> None:
        """Test character set inversion."""
        charset = CharacterSet(SIMPLE_SET)
        inverted = charset.invert()

        # Check reversed
        assert str(inverted) == SIMPLE_SET[::-1]

        # Verify brightness mapping is reversed
        assert charset.get_char(0.0) == inverted.get_char(1.0)
        assert charset.get_char(1.0) == inverted.get_char(0.0)

    def test_from_preset_simple(self) -> None:
        """Test creating from 'simple' preset."""
        charset = CharacterSet.from_preset("simple")
        assert str(charset) == SIMPLE_SET

    def test_from_preset_extended(self) -> None:
        """Test creating from 'extended' preset."""
        charset = CharacterSet.from_preset("extended")
        assert str(charset) == EXTENDED_SET

    def test_from_preset_block(self) -> None:
        """Test creating from 'block' preset."""
        charset = CharacterSet.from_preset("block")
        assert str(charset) == BLOCK_SET

    def test_from_preset_minimal(self) -> None:
        """Test creating from 'minimal' preset."""
        charset = CharacterSet.from_preset("minimal")
        assert str(charset) == MINIMAL_SET

    def test_from_preset_case_insensitive(self) -> None:
        """Test preset names are case insensitive."""
        charset1 = CharacterSet.from_preset("SIMPLE")
        charset2 = CharacterSet.from_preset("Simple")
        assert str(charset1) == str(charset2) == SIMPLE_SET

    def test_from_preset_invalid(self) -> None:
        """Test invalid preset name raises ValueError."""
        with pytest.raises(ValueError, match="Invalid preset"):
            CharacterSet.from_preset("invalid")

    def test_len(self) -> None:
        """Test __len__ method."""
        charset = CharacterSet(" .:#@")
        assert len(charset) == 5

    def test_repr(self) -> None:
        """Test __repr__ method."""
        charset = CharacterSet(SIMPLE_SET)
        repr_str = repr(charset)
        assert "CharacterSet" in repr_str
        assert "length" in repr_str
