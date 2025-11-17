"""Command-line interface for ASCII Background Generator."""

import sys
from pathlib import Path

import click

from ascii_bg.core import AsciiConverter, ColorHandler, ColorMode, parse_color
from ascii_bg.core.character_sets import CharacterSet
from ascii_bg.core.image_processor import ImageProcessor


@click.command()
@click.argument("image", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-r",
    "--resolution",
    default=None,
    help="Character grid resolution: preset (4k, 1080p, etc.) or WIDTHxHEIGHT (default: source image resolution)",
    show_default=False,
)
@click.option(
    "--output-resolution",
    default=None,
    help="Output image pixel resolution for wallpapers (e.g., 4k, 1080p, 3840x2160). Calculates optimal character grid.",
    show_default=False,
)
@click.option(
    "--scale",
    type=click.FloatRange(0.01, 2.0),
    default=None,
    help="Scale resolution by percentage (e.g., 0.5 for 50%, 0.25 for 25%)",
    show_default=False,
)
@click.option(
    "--charset",
    type=click.Choice(["simple", "extended", "block", "minimal"], case_sensitive=False),
    default="extended",
    help="Character set to use",
    show_default=True,
)
@click.option(
    "--custom-chars",
    default=None,
    help="Custom characters ordered from light to dark (e.g., ' .!?@' or '!@?')",
)
@click.option(
    "--brightness",
    type=click.IntRange(-100, 100),
    default=0,
    help="Brightness adjustment (-100 to 100)",
    show_default=True,
)
@click.option(
    "--contrast",
    type=click.IntRange(-100, 100),
    default=0,
    help="Contrast adjustment (-100 to 100)",
    show_default=True,
)
@click.option(
    "--invert",
    is_flag=True,
    help="Invert character density (swap dark/light)",
)
@click.option(
    "--no-aspect-correct",
    is_flag=True,
    help="Disable aspect ratio correction for terminal",
)
@click.option(
    "--color-mode",
    type=click.Choice(
        ["black-white", "source", "rainbow", "gradient", "solid"], case_sensitive=False
    ),
    default="black-white",
    help="Color mode (default: black-white)",
    show_default=True,
)
@click.option(
    "--gradient-colors",
    help="Comma-separated color list for gradient mode (e.g., #FF0000,#0000FF,#00FF00)",
)
@click.option(
    "--gradient-direction",
    type=click.Choice(["horizontal", "vertical", "diagonal"], case_sensitive=False),
    default="horizontal",
    help="Gradient direction (default: horizontal)",
    show_default=True,
)
@click.option(
    "--text-color",
    help="Text color for solid mode (hex #RRGGBB or name)",
)
@click.option(
    "--bg-color",
    help="Background color for solid mode (hex #RRGGBB or name)",
)
@click.option(
    "--border",
    type=click.Choice(["none", "simple"], case_sensitive=False),
    default="none",
    help="Border style (default: none)",
    show_default=True,
)
@click.option(
    "--border-char",
    default="#",
    help="Border character (default: #)",
    show_default=True,
)
@click.option(
    "--padding",
    type=click.IntRange(0, 10),
    default=0,
    help="Padding size (0-10, default: 0)",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output file (PNG, JPG, JSON, or TXT)",
)
@click.option(
    "--font-family",
    default="DejaVuSansMono",
    help="Font family for image output (default: DejaVuSansMono)",
    show_default=True,
)
@click.option(
    "--font-size",
    type=click.IntRange(4, 72),
    default=10,
    help="Font size for image output (default: 10)",
    show_default=True,
)
@click.option(
    "--terminal",
    is_flag=True,
    default=True,
    help="Display in terminal (default)",
)
@click.version_option(version="0.1.0", prog_name="ascii-bg")
def main(
    image: Path,
    resolution: str | None,
    output_resolution: str | None,
    scale: float | None,
    charset: str,
    custom_chars: str | None,
    brightness: int,
    contrast: int,
    invert: bool,
    no_aspect_correct: bool,
    color_mode: str,
    gradient_colors: str | None,
    gradient_direction: str,
    text_color: str | None,
    bg_color: str | None,
    border: str,
    border_char: str,
    padding: int,
    output: Path | None,
    font_family: str,
    font_size: int,
    terminal: bool,
) -> None:
    """Convert IMAGE to ASCII art.

    \b
    Examples:
        # Terminal output (uses source image resolution by default)
        ascii-bg image.jpg
        ascii-bg photo.png --resolution=4k --brightness=20

        # Create wallpapers with specific OUTPUT pixel dimensions
        ascii-bg image.jpg --output-resolution=4k -o wallpaper.png       # 3840×2160px
        ascii-bg photo.png --output-resolution=1080p -o bg.png           # 1920×1080px
        ascii-bg input.jpg --output-resolution=2560x1440 -o output.png   # Custom size

        # Scale down large images for terminal viewing
        ascii-bg large-photo.png --scale=0.5    # 50% of original size
        ascii-bg huge-image.jpg --scale=0.25    # 25% of original size

        # Custom character sets
        ascii-bg image.jpg --custom-chars " .!?@"         # Light to dark
        ascii-bg photo.png --custom-chars "!@?" -o out.png  # Only 3 chars
        ascii-bg input.jpg --custom-chars " .-=oO@" --scale=0.2

        # Color modes
        ascii-bg image.jpg --color-mode=rainbow --gradient-direction=diagonal
        ascii-bg photo.png --color-mode=gradient --gradient-colors=#FF0000,#00FF00,#0000FF
        ascii-bg input.jpg --color-mode=solid --text-color=cyan --bg-color=black

        # Wallpapers with colors and custom settings
        ascii-bg photo.jpg --output-resolution=4k --color-mode=source -o wall.png
        ascii-bg image.jpg --output-resolution=1080p --font-size=8 -o compact.png

        # Save as JSON (for LLM processing)
        ascii-bg image.jpg -o output.json

        # Borders and padding
        ascii-bg image.jpg --border=simple --padding=2 -o output.png
        ascii-bg photo.png --border=simple --border-char=* --padding=1
    """
    try:
        # Handle output resolution (for wallpapers - specifies output pixels)
        if output_resolution is not None:
            # Parse desired output pixel dimensions
            output_pixels = ImageProcessor.parse_resolution(output_resolution)
            output_width_px, output_height_px = output_pixels

            # Calculate character dimensions at given font size
            # Based on actual rendering measurements:
            # - Width: font_size * 0.6 pixels
            # - Height: font_size * 0.35 pixels (after aspect correction)
            # - Height without aspect correction: font_size * 0.7 pixels
            char_width_px = font_size * 0.6
            char_height_px = font_size * 0.35 if not no_aspect_correct else font_size * 0.7

            # Calculate character grid needed to achieve output resolution
            width = int(output_width_px / char_width_px)
            height = int(output_height_px / char_height_px)

            click.echo(
                f"Creating {output_width_px}×{output_height_px}px wallpaper "
                f"({width}×{height} char grid at {font_size}pt font)",
                err=True,
            )
        # Handle resolution and scaling
        elif resolution is None:
            # Use source image dimensions
            from PIL import Image

            with Image.open(image) as img:
                width, height = img.width, img.height
        else:
            # Parse the provided resolution
            parsed_res = ImageProcessor.parse_resolution(resolution)
            width, height = parsed_res

        # Apply scale if provided (unless output_resolution was used)
        if scale is not None and output_resolution is None:
            width = int(width * scale)
            height = int(height * scale)
            click.echo(f"Scaling to {scale:.0%}: {width}x{height}", err=True)

        # Convert to resolution string
        resolution = f"{width}x{height}"

        # Create character set
        if custom_chars is not None:
            # Use custom characters
            if len(custom_chars) < 2:
                click.echo(
                    "Error: Custom character set must have at least 2 characters",
                    err=True,
                )
                sys.exit(1)
            char_set = CharacterSet(custom_chars)
            click.echo(
                f"Using custom characters: '{custom_chars}' ({len(custom_chars)} chars)",
                err=True,
            )
        else:
            # Use preset
            char_set = CharacterSet.from_preset(charset)

        # Create color handler
        mode = ColorMode(color_mode)
        color_handler = None

        if mode != ColorMode.BLACK_WHITE:
            # Parse gradient colors if provided
            gradient_color_list = None
            if gradient_colors:
                try:
                    gradient_color_list = [
                        parse_color(c.strip()) for c in gradient_colors.split(",")
                    ]
                except ValueError as e:
                    click.echo(f"Error parsing gradient colors: {e}", err=True)
                    sys.exit(1)

            # Parse text and background colors if provided
            text_color_rgb = None
            bg_color_rgb = None

            if text_color:
                try:
                    text_color_rgb = parse_color(text_color)
                except ValueError as e:
                    click.echo(f"Error parsing text color: {e}", err=True)
                    sys.exit(1)

            if bg_color:
                try:
                    bg_color_rgb = parse_color(bg_color)
                except ValueError as e:
                    click.echo(f"Error parsing background color: {e}", err=True)
                    sys.exit(1)

            # Create color handler
            color_handler = ColorHandler(
                mode=mode,
                gradient_colors=gradient_color_list,
                gradient_direction=gradient_direction,
                text_color=text_color_rgb,
                bg_color=bg_color_rgb,
            )

        # Create converter
        converter = AsciiConverter(
            resolution=resolution,
            charset=char_set,
            brightness=brightness,
            contrast=contrast,
            invert=invert,
            aspect_correct=not no_aspect_correct,
            color_handler=color_handler,
        )

        # Convert image
        click.echo(f"Converting {image.name}...", err=True)
        art = converter.convert(image)

        # Apply border and padding if requested
        if border != "none" or padding > 0:
            from ascii_bg.core.renderer import add_border, add_border_to_colors

            art.char_grid = add_border(art.char_grid, border_char, padding)
            # For color grid, use white border for colored modes
            border_color = (255, 255, 255) if mode != ColorMode.BLACK_WHITE else (128, 128, 128)
            art.color_grid = add_border_to_colors(art.color_grid, border_color, padding)
            # Update dimensions
            art.height = len(art.char_grid)
            art.width = len(art.char_grid[0]) if art.char_grid else 0

        # Output results
        if terminal:
            # Display in terminal (with color if enabled)
            if mode != ColorMode.BLACK_WHITE:
                click.echo(art.to_colored_text())
            else:
                click.echo(art.to_plain_text())

        if output:
            # Save to file
            click.echo(f"Saving to {output}...", err=True)

            # Detect format from extension
            suffix = output.suffix.lower()

            if suffix in [".png", ".jpg", ".jpeg"]:
                # Save as image
                bg = (0, 0, 0) if bg_color is None else parse_color(bg_color)
                art.save_image(output, font_family, font_size, bg)
            elif suffix == ".json":
                # Save as JSON
                metadata = {
                    "source_image": str(image),
                    "resolution": resolution,
                    "charset": charset,
                    "color_mode": color_mode,
                }
                art.save_json(output, metadata)
            else:
                # Save as text file
                if mode != ColorMode.BLACK_WHITE:
                    output.write_text(art.to_colored_text())
                else:
                    output.write_text(art.to_plain_text())

            click.echo(f"✓ Saved to {output}", err=True)

        # Success message
        if not terminal and not output:
            click.echo("No output specified. Use --terminal or -o <file>", err=True)
            sys.exit(1)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
