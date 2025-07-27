import click
from skimage import io
from pyxelate import Pyx
from pathlib import Path

@click.command()
@click.option("--images_folder_path",
              prompt="Images Folder Path",
              help="The path of the input images folder.",
              type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("--square",
              default=1,
              type=int,
              help="Crop images to a square from the center (1=True, 0=False).")
@click.option("--offset_x",
              default=0,
              type=int,
              help="Crop offset on the X-axis (horizontal).")
@click.option("--offset_y",
              default=0,
              type=int,
              help="Crop offset on the Y-axis (vertical).")
@click.option("--palette_no_colors",
              default=16,
              help="Total number of colors in the generated palette.")
@click.option("--downsample_ratio",
              default=1,
              help="Downsampling factor. Higher values create a more pixelated effect.")
def process(images_folder_path, square, offset_x, offset_y, palette_no_colors, downsample_ratio):
    """
    Processes all images in a given folder, converting them to pixel art
    and saving them in a new 'pixelated' subfolder.
    """
    # Use pathlib for robust path handling
    input_path = Path(images_folder_path)
    output_path = input_path / "pixelated"

    # Create the output directory if it doesn't exist
    output_path.mkdir(exist_ok=True)
    click.echo(f"Output will be saved to: {output_path}")

    # Define allowed image extensions
    allowed_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}

    # Find all image files in the input folder
    image_files = [f for f in input_path.glob('*') if f.suffix.lower() in allowed_extensions]

    if not image_files:
        click.echo(click.style("No images found in the specified folder.", fg="red"))
        return

    click.echo(f"Found {len(image_files)} image(s) to process.")

    # Process each image
    for image_file in image_files:
        try:
            click.echo(f"-> Processing {image_file.name}...")

            # Read the image using scikit-image
            # Note: io.imread loads gifs as multi-frame, we'll just use the first frame.
            image = io.imread(image_file)
            if image.ndim > 3 and image.shape[0] == 1: # Handle multi-frame gifs with one frame
                image = image[0]
            # Ensure image is in RGB format (removes alpha channel for pyxelate)
            if image.shape[2] == 4:
                image = image[:, :, :3]

            # --- Cropping Logic ---
            if square:
                h, w, _ = image.shape
                # Determine the side length of the square
                size = min(h, w)

                # Calculate top-left corner for a centered crop
                left = (w - size) // 2
                top = (h - size) // 2

                # Apply user-defined offsets
                left += offset_x
                top += offset_y

                # Ensure the crop is within image bounds
                if not (0 <= top < h and 0 <= left < w and top + size <= h and left + size <= w):
                    click.echo(click.style(f"  [Warning] Crop for {image_file.name} is out of bounds. Skipping crop.", fg="yellow"))
                    cropped_image = image
                else:
                    cropped_image = image[top:top+size, left:left+size]
            else:
                cropped_image = image

            # --- Pixelation Logic ---
            # Create a Pyx object with the desired downsampling factor and palette size
            pyx = Pyx(factor=downsample_ratio, palette=palette_no_colors)

            # Fit and transform the image to create the pixel art
            pixelated_image = pyx.fit_transform(cropped_image)

            # --- Saving Logic ---
            # Construct the full output path for the new image
            output_file_path = output_path / f"{image_file.stem}.png" # Save as PNG to preserve colors

            # Save the new image
            io.imsave(output_file_path, pixelated_image)
            click.echo(click.style(f"   Saved to {output_file_path.name}", fg="green"))

        except Exception as e:
            click.echo(click.style(f"  [Error] Could not process {image_file.name}: {e}", fg="red"))

    click.echo(click.style("\nProcessing complete!", fg="blue", bold=True))


if __name__ == '__main__':
    process()