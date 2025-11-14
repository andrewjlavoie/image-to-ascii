"""Command-line interface for ASCII Background Generator."""

import sys
from pathlib import Path

import click

from ascii_bg.core import AsciiConverter
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
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output file path (for future image/JSON export)",
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
    output: Path | None,
    terminal: bool,
) -> None:
    """Convert IMAGE to ASCII art.

    \b
    Examples:
        ascii-bg image.jpg
        ascii-bg photo.png --resolution=4k --brightness=20
        ascii-bg input.jpg --charset=simple --invert
        ascii-bg image.jpg -r 1920x1080 --contrast=15 -o output.txt
    """
    try:
        # Create character set
        char_set = CharacterSet.from_preset(charset)

        # Create converter
        converter = AsciiConverter(
            resolution=resolution,
            charset=char_set,
            brightness=brightness,
            contrast=contrast,
            invert=invert,
            aspect_correct=not no_aspect_correct,
        )

        # Convert image
        click.echo(f"Converting {image.name}...", err=True)
        art = converter.convert(image)

        # Output results
        if terminal:
            # Display in terminal (plain text for now)
            click.echo(art.to_plain_text())

        if output:
            # Save to file
            click.echo(f"Saving to {output}...", err=True)
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
