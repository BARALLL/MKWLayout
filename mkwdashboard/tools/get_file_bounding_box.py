from PIL import Image
import collada
import numpy as np

import pathlib
from io import BytesIO
from typing import Tuple


def open_image(image_file: str | pathlib.Path | bytes):
    if isinstance(image_file, (str, pathlib.Path)):
        img_path = pathlib.Path(image_file)
        if img_path.exists():
            img = Image.open(img_path)
        else:
            raise FileNotFoundError(f"The file at {img_path} does not exist.")
    elif isinstance(image_file, bytes):
        img = Image.open(BytesIO(image_file))
    else:
        raise TypeError(
            f"Unsupported type for input image. Expected str, pathlib.Path, or bytes. Got {type(image_file)}."
        )
    return img


# trimesh was not able to open dae so using pycollada
def get_dae_bounding_box(
    dae_file: str | pathlib.Path | bytes,
) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    if isinstance(dae_file, (str, pathlib.Path)):
        if pathlib.Path(dae_file).exists():
            mesh = collada.Collada(
                dae_file, ignore=[collada.DaeBrokenRefError, collada.DaeIncompleteError]
            )  # collada.DaeError to ignore all
        else:
            raise FileNotFoundError(f"The file at {dae_file} does not exist.")
    elif isinstance(dae_file, bytes):
        if dae_file is not None and len(dae_file) > 0:
            mesh = collada.Collada(
                BytesIO(dae_file),
                ignore=[collada.DaeBrokenRefError, collada.DaeIncompleteError],
            )
        else:
            raise ValueError("The byte array for the Collada file is empty or None.")
    else:
        raise TypeError(
            f"Unsupported type for input DAE path. Expected str, pathlib.Path, or bytes. Got {type(dae_file)}."
        )
    try:
        vertices = []
        for geometry in mesh.geometries:
            for primitive in geometry.primitives:
                vertex_data = primitive.vertex
                vertices.extend(vertex_data)

        vertices = np.array(vertices)

        if len(vertices) == 0:
            raise ValueError("No vertices found in the DAE file")

        min_coords = np.min(vertices, axis=0)
        max_coords = np.max(vertices, axis=0)

        return (
            tuple(min_coords.tolist()),  # (min_x, min_y, min_z)
            tuple(max_coords.tolist()),  # (max_x, max_y, max_z)
        )

    except Exception as e:
        print(f"Error processing DAE file: {str(e)}")
        return None


def find_img_bounding_box(image_file: str | pathlib.Path | bytes):
    img = open_image(image_file)

    try:
        img = img.convert("RGBA")
    except Exception as e:
        print(f"Could not process file: {e}")
        return None

    img_array = np.array(img)

    alpha_channel = img_array[:, :, 3]
    non_transparent = alpha_channel > 15

    if not non_transparent.any():
        return None

    rows = np.any(non_transparent, axis=1)
    cols = np.any(non_transparent, axis=0)

    min_x = np.argmax(cols)
    max_x = len(cols) - 1 - np.argmax(cols[::-1])
    min_y = np.argmax(rows)
    max_y = len(rows) - 1 - np.argmax(rows[::-1])

    return ((min_x, min_y), (max_x, max_y))
