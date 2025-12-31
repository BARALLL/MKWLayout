import base64
import mimetypes


def get_file_struct():
    return {"binary": None, "json": None, "png": None, "dae": None}


from mkwdashboard.config import file_types


def get_file_contents(file_path):
    """
    Reads a file and encodes its contents to base64.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"
    except FileNotFoundError:
        return None


def get_files_contents(files: dict):
    """
    Retrieves base64-encoded contents for all files in found_files.
    Returns a list aligned with file_types.
    """
    contents = []
    filenames = []
    for file_type in file_types:
        type_name = file_type["type"]
        file_path = files.get(type_name)
        if file_path and file_path.exists():
            content = get_file_contents(file_path)
            if content:
                contents.append(content)
                filenames.append(file_path.name)
            else:
                contents.append(None)
                filenames.append(None)
        else:
            contents.append(None)
            filenames.append(None)
    return contents, filenames


def encode_image(image_file):
    if image_file is None:
        return None
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def process_upload_content(contents):
    if contents is None:
        return None
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    return decoded
