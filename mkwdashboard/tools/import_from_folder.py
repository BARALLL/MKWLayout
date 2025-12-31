import pathlib

from mkwdashboard.tools.file_handling import get_file_struct


def search_folder_simple(folder: pathlib.Path):
    files = get_file_struct()
    if not folder.is_dir():
        raise ValueError(f"The path {folder} is not a valid directory")

    for file_path in folder.iterdir():
        suffix = file_path.suffix.lower()[1:]
        if suffix == "csv":
            files["binary"] = file_path
        else:
            if suffix in files and files[suffix] is None:
                files[suffix] = file_path
    return files
