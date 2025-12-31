import numpy as np


def put_pixel(
    pixels: np.ndarray,
    pixel_x: int,
    pixel_y: int,
    width: int = 512,
    height: int = 512,
    brush_size: int = 3,
    brush_color: tuple = (255, 0, 0, 100),
) -> None:
    if not (0 <= pixel_x < width and 0 <= pixel_y < height):
        return

    # calculate the bounding box for the brush
    x_min = max(0, pixel_x - brush_size)
    x_max = min(width - 1, pixel_x + brush_size)
    y_min = max(0, pixel_y - brush_size)
    y_max = min(height - 1, pixel_y + brush_size)

    # generate coordinate grids for the brush area
    x_coords = np.arange(x_min, x_max + 1)
    y_coords = np.arange(y_min, y_max + 1)
    xx, yy = np.meshgrid(x_coords, y_coords, indexing="xy")

    dx = xx - pixel_x
    dy = yy - pixel_y
    distances = np.sqrt(dx**2 + dy**2)

    mask = distances <= brush_size

    if not np.any(mask):
        return

    alpha = (brush_color[3] * (1 - (distances / brush_size) ** 0.5)).astype(np.int16)
    alpha = np.clip(alpha, 0, 255)

    alpha[~mask] = 0
    roi = pixels[y_min : y_max + 1, x_min : x_max + 1]

    r = roi[:, :, 0]
    g = roi[:, :, 1]
    b = roi[:, :, 2]

    inv_alpha = 255 - alpha
    new_r = ((brush_color[0] * alpha + r * inv_alpha) // 255).astype(np.uint8)
    new_g = ((brush_color[1] * alpha + g * inv_alpha) // 255).astype(np.uint8)
    new_b = ((brush_color[2] * alpha + b * inv_alpha) // 255).astype(np.uint8)

    roi[:, :, 0][mask] = new_r[mask]
    roi[:, :, 1][mask] = new_g[mask]
    roi[:, :, 2][mask] = new_b[mask]
    roi[:, :, 3][mask] = 255


def find_pixels_to_color(
    df, bbox, scale_x, scale_y, min_img_x, min_img_z, img_size=512
):
    positions_x = df["Position X_1"].values
    positions_z = df["Position Z_1"].values

    pixel_x = (positions_x - bbox[0]) * scale_x + min_img_x  # ).astype(int)
    pixel_y = (positions_z - bbox[1]) * scale_y + min_img_z  # ).astype(int)

    pixels = np.column_stack((pixel_x, pixel_y))

    in_bounds = ((pixels >= 0) & (pixels < img_size)).all(axis=1)

    valid_pixels = pixels[in_bounds]
    print(len(valid_pixels))
    if len(valid_pixels) == 0:
        return []

    # not the best "filtering" algo but would require to change to a non vectorized solution
    
    # diffs = np.diff(valid_pixels.astype(int), axis=0)
    # dists = np.sum(diffs * diffs, axis=1)

    # distance_mask = np.ones(len(valid_pixels), dtype=bool)
    # distance_mask[1:] = dists >= 1

    # final_pixels = valid_pixels[distance_mask]
    # print(len(final_pixels))

    return valid_pixels
