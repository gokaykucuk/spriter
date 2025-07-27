import os
from pathlib import Path
import click
from PIL import Image, ImageDraw

# A list of common image file extensions to look for.
SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')

def create_feathered_image(image: Image.Image, square: bool, offset_x: int, offset_y: int, feather: int, shape: str, shape_padding: int) -> Image.Image:
    """
    Crops an image and applies a feathered transparency effect.

    Args:
        image (Image.Image): The input Pillow image object.
        square (bool): If True, crop to the largest possible square.
        offset_x (int): Horizontal offset for the crop.
        offset_y (int): Vertical offset for the crop.
        feather (int): The width of the feather/gradient in pixels.
        shape (str): The shape of the feathered area ('circle' or 'rectangle').
        shape_padding (int): Padding from the edge of the crop to the start of the solid shape.

    Returns:
        Image.Image: The processed image with feathering, in RGBA mode.
    """
    # --- 1. Crop the image ---
    if square:
        width, height = image.size
        crop_size = min(width, height)
        # Calculate box for a centered crop
        left = (width - crop_size) / 2
        top = (height - crop_size) / 2
        right = (width + crop_size) / 2
        bottom = (height + crop_size) / 2
        # Apply user-defined offsets
        crop_box = (left + offset_x, top + offset_y, right + offset_x, bottom + offset_y)
        cropped_image = image.crop(crop_box)
    else:
        # If not squaring, use the whole image
        cropped_image = image.copy()

    # Ensure the image is in RGBA format to work with transparency
    cropped_image = cropped_image.convert("RGBA")

    # --- 2. Create the alpha mask ---
    # Create a new, black 'L' (grayscale) image. Black means fully transparent.
    mask = Image.new('L', cropped_image.size, 0)
    draw = ImageDraw.Draw(mask)

    # The bounding box for the final opaque shape, inside the padding
    mask_width, mask_height = mask.size
    solid_shape_box = (
        shape_padding,
        shape_padding,
        mask_width - shape_padding,
        mask_height - shape_padding
    )

    # --- 3. Draw the feathering gradient on the mask ---
    # Draw concentric shapes from transparent to opaque
    for i in range(feather):
        # The color value goes from 0 (black) to 255 (white)
        color = int(255 * (i / feather))

        # The inset determines how far from the edge this layer is.
        # It starts from the outside of the feather and moves inward.
        inset = feather - i

        feather_box = (
            solid_shape_box[0] - inset,
            solid_shape_box[1] - inset,
            solid_shape_box[2] + inset,
            solid_shape_box[3] + inset,
        )

        if shape == 'circle':
            draw.ellipse(feather_box, fill=color)
        else: # 'rectangle'
            draw.rectangle(feather_box, fill=color)

    # --- 4. Draw the solid (fully opaque) center on the mask ---
    # This is drawn on top of the gradient to ensure it's solid white (255)
    if shape == 'circle':
        draw.ellipse(solid_shape_box, fill=255)
    else: # 'rectangle'
        draw.rectangle(solid_shape_box, fill=255)

    # --- 5. Apply the mask to the image's alpha channel ---
    cropped_image.putalpha(mask)

    return cropped_image


@click.command()
@click.option("--images_folder_path",
              prompt="Images Folder Path",
              help="The path of the input images folder.",
              type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path))
@click.option('--square/--no-square',
              default=True,
              help="Crop to the largest possible square from the center. Default is --square.")
@click.option("--offset_x",
              default=0,
              type=int,
              help="Crop offset on the X-axis (horizontal).")
@click.option("--offset_y",
              default=0,
              type=int,
              help="Crop offset on the Y-axis (vertical).")
@click.option("--feather",
              default=30,
              type=click.IntRange(min=1),
              help="The width of the feather/gradient in pixels.")
@click.option("--shape",
              default="circle",
              type=click.Choice(['circle', 'rectangle'], case_sensitive=False),
              help="The crop shape after feathering.")
@click.option("--shape_padding",
              default=40,
              type=click.IntRange(min=1),
              help="Padding from image edge to the solid shape. Must be larger than feather.")
def process(images_folder_path: Path, square: bool, offset_x: int, offset_y: int, feather: int, shape: str, shape_padding: int):
    """
    A script to batch process images: it crops them, then applies a feathered
    transparency effect to the edges.
    """
    # --- Input Validation ---
    if shape_padding <= feather:
        raise click.BadParameter("Shape padding must be larger than the feather value for the effect to work correctly.")

    # --- Setup Paths ---
    output_folder_path = images_folder_path / "processed"
    output_folder_path.mkdir(exist_ok=True)
    click.echo(f"Input folder: {images_folder_path}")
    click.echo(f"Outputting processed images to: {output_folder_path}\n")

    # --- Find and Process Images ---
    image_files = [p for p in images_folder_path.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]

    if not image_files:
        click.echo("No supported image files found in the specified folder.")
        return

    with click.progressbar(image_files, label="Processing images") as bar:
        for image_path in bar:
            try:
                with Image.open(image_path) as img:
                    processed_image = create_feathered_image(
                        image=img,
                        square=square,
                        offset_x=offset_x,
                        offset_y=offset_y,
                        feather=feather,
                        shape=shape,
                        shape_padding=shape_padding
                    )

                    # --- Save the result ---
                    # Use the original filename but save in the output folder.
                    # Force PNG format to ensure the alpha channel (transparency) is saved.
                    output_path = output_folder_path / f"{image_path.stem}.png"
                    processed_image.save(output_path, "PNG")

            except Exception as e:
                click.echo(f"\nCould not process {image_path.name}: {e}", err=True)

    click.echo("\nProcessing complete!")


if __name__ == '__main__':
    process()