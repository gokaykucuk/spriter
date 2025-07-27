from pathlib import Path
import click

@click.command()
@click.option("--images_folder_path",
              prompt="Images Folder Path",
              help="The path of the input images folder.",
              type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path))
@click.option("--keep_every",
              default=10,
              type=int,
              help="Keep every N files in the given folder.")
def process(images_folder_path: Path, keep_every: int):
    """
    Keeps every N files in a given folder and deletes the rest.
    """
    if keep_every <= 0:
        click.echo(click.style("Error: 'keep_every' must be a positive integer.", fg="red"))
        return

    click.echo(f"Processing folder: {images_folder_path}")
    click.echo(f"Keeping every {keep_every} files and deleting the rest.")

    files = sorted([f for f in images_folder_path.iterdir() if f.is_file()])

    if not files:
        click.echo("No files found in the specified folder. Nothing to do.")
        return

    deleted_count = 0
    for i, file_path in enumerate(files):
        if (i + 1) % keep_every != 0:
            try:
                file_path.unlink()
                click.echo(f"Deleted: {file_path.name}")
                deleted_count += 1
            except OSError as e:
                click.echo(click.style(f"Error deleting {file_path.name}: {e}", fg="red"))
        else:
            click.echo(f"Keeping: {file_path.name}")

    if deleted_count > 0:
        click.echo(click.style(f"\nSuccessfully deleted {deleted_count} files.", fg="green"))
    else:
        click.echo("\nNo files were deleted (perhaps all files were kept or no files met the deletion criteria).")


if __name__ == '__main__':
    process()