import math
from pathlib import Path
import click
from PIL import Image

@click.command()
@click.option("--images_folder_path",
              prompt="Images Folder Path",
              help="The path of the input images folder.",
              type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path))
def process(images_folder_path: Path):
    """
    Accepts a path to a folder of 2D game sprites (PNGs) with the same dimensions.
    It merges all of them into a single NxN sprite sheet file named 'spritesheet.png'.
    """
    click.echo(f"Processing images in: {images_folder_path}")

    # 1. Find all PNG images in the folder
    image_paths = sorted(list(images_folder_path.glob('*.png')))

    if not image_paths:
        click.echo("Error: No PNG images found in the specified folder.")
        return

    num_images = len(image_paths)
    click.echo(f"Found {num_images} images to process.")

    # 2. Open the first image to get sprite dimensions
    with Image.open(image_paths[0]) as first_image:
        sprite_width, sprite_height = first_image.size
        click.echo(f"Detected sprite dimensions: {sprite_width}x{sprite_height} pixels.")

    # 3. Calculate the size of the output grid (NxN)
    # We need the smallest square that can fit all images.
    # This is the ceiling of the square root of the number of images.
    grid_size = math.ceil(math.sqrt(num_images))

    sheet_width = grid_size * sprite_width
    sheet_height = grid_size * sprite_height
    click.echo(f"Calculated spritesheet grid: {grid_size}x{grid_size}")
    click.echo(f"Output image dimensions: {sheet_width}x{sheet_height} pixels.")

    # 4. Create a new, blank image with a transparent background
    spritesheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

    # 5. Iterate through images and paste them onto the sheet
    for i, image_path in enumerate(image_paths):
        # Calculate the row and column for the current sprite
        row = i // grid_size
        col = i % grid_size

        # Calculate the top-left (x, y) coordinates for pasting
        x = col * sprite_width
        y = row * sprite_height

        with Image.open(image_path) as sprite:
            # Ensure the sprite is in RGBA mode to handle transparency correctly
            spritesheet.paste(sprite.convert('RGBA'), (x, y))

    # 6. Save the final spritesheet
    output_path = images_folder_path / "spritesheet.png"
    spritesheet.save(output_path)

    click.secho(f"\nSuccess! Spritesheet created at: {output_path}", fg="green")


if __name__ == '__main__':
    process()