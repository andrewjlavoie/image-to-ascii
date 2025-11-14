"""Tests for CLI functionality."""

from pathlib import Path

import pytest
from click.testing import CliRunner
from PIL import Image

from ascii_bg.cli import main


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def test_image(tmp_path: Path) -> Path:
    """Create a simple test image."""
    img = Image.new("RGB", (100, 100), color="white")
    pixels = img.load()

    # Create a simple gradient
    for y in range(100):
        for x in range(100):
            value = int((x + y) / 2 * 255 / 100)
            pixels[x, y] = (value, value, value)

    path = tmp_path / "test_image.png"
    img.save(path)
    return path


class TestCLI:
    """Test CLI command."""

    def test_basic_conversion(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test basic image conversion."""
        result = cli_runner.invoke(main, [str(test_image)])

        assert result.exit_code == 0
        # Should output ASCII art
        assert len(result.output) > 0
        # Should contain ASCII characters
        assert any(c in result.output for c in " .:;!>*+?%$#@")

    def test_version_flag(self, cli_runner: CliRunner) -> None:
        """Test --version flag."""
        result = cli_runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "ascii-bg" in result.output
        assert "0.1.0" in result.output

    def test_help_flag(self, cli_runner: CliRunner) -> None:
        """Test --help flag."""
        result = cli_runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Convert IMAGE to ASCII art" in result.output
        assert "--resolution" in result.output
        assert "--brightness" in result.output

    def test_missing_image(self, cli_runner: CliRunner) -> None:
        """Test error when image file is missing."""
        result = cli_runner.invoke(main, ["nonexistent.png"])

        assert result.exit_code != 0

    def test_resolution_preset(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test resolution preset."""
        result = cli_runner.invoke(main, [str(test_image), "--resolution=4k"])

        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_resolution_custom(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test custom resolution."""
        result = cli_runner.invoke(main, [str(test_image), "-r", "100x50"])

        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_charset_option(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test different charset options."""
        for charset in ["simple", "extended", "block", "minimal"]:
            result = cli_runner.invoke(main, [str(test_image), f"--charset={charset}"])

            assert result.exit_code == 0
            assert len(result.output) > 0

    def test_brightness_option(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test brightness adjustment."""
        result = cli_runner.invoke(main, [str(test_image), "--brightness=50"])

        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_contrast_option(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test contrast adjustment."""
        result = cli_runner.invoke(main, [str(test_image), "--contrast=-30"])

        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_brightness_out_of_range(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test brightness value out of range."""
        result = cli_runner.invoke(main, [str(test_image), "--brightness=150"])

        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_contrast_out_of_range(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test contrast value out of range."""
        result = cli_runner.invoke(main, [str(test_image), "--contrast=-150"])

        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_invert_flag(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test invert flag."""
        result = cli_runner.invoke(main, [str(test_image), "--invert"])

        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_no_aspect_correct_flag(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test no-aspect-correct flag."""
        result = cli_runner.invoke(main, [str(test_image), "--no-aspect-correct"])

        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_output_to_file(self, cli_runner: CliRunner, test_image: Path, tmp_path: Path) -> None:
        """Test saving output to file."""
        output_file = tmp_path / "output.txt"
        result = cli_runner.invoke(main, [str(test_image), "-o", str(output_file), "--terminal"])

        assert result.exit_code == 0
        assert output_file.exists()

        # Check file contents
        content = output_file.read_text()
        assert len(content) > 0
        assert any(c in content for c in " .:;!>*+?%$#@")

    def test_combined_options(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test multiple options combined."""
        result = cli_runner.invoke(
            main,
            [
                str(test_image),
                "-r",
                "200x100",
                "--charset=simple",
                "--brightness=10",
                "--contrast=5",
                "--invert",
            ],
        )

        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_status_messages(self, cli_runner: CliRunner, test_image: Path) -> None:
        """Test that status messages appear on stderr."""
        result = cli_runner.invoke(main, [str(test_image)])

        assert result.exit_code == 0
        # Status messages should mention the filename
        assert test_image.name in result.stderr or "Converting" in result.stderr

    def test_output_file_and_terminal(
        self, cli_runner: CliRunner, test_image: Path, tmp_path: Path
    ) -> None:
        """Test output to both file and terminal."""
        output_file = tmp_path / "output.txt"
        result = cli_runner.invoke(main, [str(test_image), "-o", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        # Should also output to stdout (terminal default)
        assert len(result.output) > 0
