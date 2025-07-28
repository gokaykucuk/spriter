import os
from PIL import Image

# Define the directory where the tiles are saved
DOWNLOAD_DIR = "map"

# Define the original coordinates used for downloading
X_START = 75433
X_STOP = 75536
Y_START = 50830
Y_STOP = 50879


def merge_map_tiles(output_filename="merged_map.jpg"):
    """
    Merges downloaded map tiles into a single JPEG image.
    Assumes tiles are named as '{x}_{y}.jpg' in the DOWNLOAD_DIR.
    """
    print("Starting map merging process...")

    # Calculate the number of tiles in each dimension
    num_x_tiles = X_STOP - X_START
    num_y_tiles = Y_STOP - Y_START

    if num_x_tiles == 0 or num_y_tiles == 0:
        print("No tiles to merge. Check X_START/STOP and Y_START/STOP.")
        return

    # Load the first tile to determine its dimensions
    # We assume all tiles have the same dimensions.
    try:
        first_tile_path = os.path.join(DOWNLOAD_DIR, f"{X_START}_{Y_START}.jpg")
        first_tile = Image.open(first_tile_path)
        tile_width, tile_height = first_tile.size
        first_tile.close()  # Close the image to free memory
    except FileNotFoundError:
        print(f"Error: First tile not found at {first_tile_path}. Make sure tiles are downloaded.")
        return
    except Exception as e:
        print(f"Error loading first tile: {e}")
        return

    print(f"Tile dimensions: {tile_width}x{tile_height}")

    # Calculate the dimensions of the final merged image
    merged_width = num_x_tiles * tile_width
    merged_height = num_y_tiles * tile_height

    # Create a new blank image to paste the tiles onto
    merged_image = Image.new('RGB', (merged_width, merged_height))

    print(f"Merging into a {merged_width}x{merged_height} image...")

    # Iterate through the tiles and paste them onto the merged image
    for i, y_coord in enumerate(range(Y_START, Y_STOP)):
        for j, x_coord in enumerate(range(X_START, X_STOP)):
            tile_filename = f"{x_coord}_{y_coord}.jpg"
            tile_path = os.path.join(DOWNLOAD_DIR, tile_filename)

            try:
                with Image.open(tile_path) as tile:
                    # Calculate the position to paste the current tile
                    # (j * tile_width) for X-coordinate (columns)
                    # (i * tile_height) for Y-coordinate (rows)
                    # Note: Y-coordinates typically increase downwards in image processing,
                    # so we map the y_coord directly to row 'i'.
                    paste_x = j * tile_width
                    paste_y = i * tile_height
                    merged_image.paste(tile, (paste_x, paste_y))
            except FileNotFoundError:
                print(f"Warning: Tile {tile_filename} not found. Skipping.")
                # You might want to paste a black or transparent square here
                # if you want to visibly indicate missing tiles.
            except Exception as e:
                print(f"Error processing tile {tile_filename}: {e}")

    # Save the merged image
    try:
        merged_image.save(output_filename, "JPEG")
        print(f"Merged map saved as {output_filename}")
    except Exception as e:
        print(f"Error saving merged image: {e}")


if __name__ == "__main__":
    # Ensure you've run the corrected download script first to populate map_tiles
    merge_map_tiles("final_merged_map.jpg")
