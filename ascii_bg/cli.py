"""Command-line interface for ASCII Background Generator."""

import sys
from pathlib import Path

import click

from ascii_bg.core import AsciiConverter, ColorHandler, ColorMode, parse_color
from ascii_bg.core.character_sets import CharacterSet


@click.command()
@click.argument("image", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-r",
    "--resolution",
    default="1920x1080",
    help="Resolution: preset (4k, 1080p, etc.) or WIDTHxHEIGHT",
    show_default=True,
)
@click.option(
    "--charset",
    type=click.Choice(["simple", "extended", "block", "minimal"], case_sensitive=False),
    default="extended",
    help="Character set to use",
    show_default=True,
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
    resolution: str,
    charset: str,
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
        # Terminal output
        ascii-bg image.jpg
        ascii-bg photo.png --resolution=4k --brightness=20

        # Color modes
        ascii-bg image.jpg --color-mode=rainbow --gradient-direction=diagonal
        ascii-bg photo.png --color-mode=gradient --gradient-colors=#FF0000,#00FF00,#0000FF
        ascii-bg input.jpg --color-mode=solid --text-color=cyan --bg-color=black

        # Save as PNG/JPG
        ascii-bg image.jpg -o output.png --font-size=12
        ascii-bg photo.png --color-mode=rainbow -o output.jpg --font-family=Courier

        # Save as JSON (for LLM processing)
        ascii-bg image.jpg -o output.json

        # Borders and padding
        ascii-bg image.jpg --border=simple --padding=2 -o output.png
        ascii-bg photo.png --border=simple --border-char=* --padding=1
    """
    try:
        # Create character set
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
