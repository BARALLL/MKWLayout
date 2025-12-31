from mkwdashboard.tools.reduce_df import round_and_compact_df
from mkwdashboard.tools.get_file_bounding_box import (
    find_img_bounding_box,
    get_dae_bounding_box,
    open_image,
)
from log_parsing.log_parser import BinaryParser #!! TODO move log parser and check if import paths are broken bc in new folder 
from mkwdashboard.processing.image_processing import find_pixels_to_color

import numpy as np
import pandas as pd

import json
import pathlib
from time import time
import hashlib


def generate_hash(*args):
    combined = "-".join(str(arg) for arg in args)
    hash_object = hashlib.sha256(combined.encode())
    return hash_object.hexdigest()


def _generate_cache_key(*files: bytes) -> str:
    """Generate unique hash based on file contents"""
    hash_obj = hashlib.sha1()
    for file in files:
        if isinstance(file, bytes):
            # Update the hash object with the bytes directly
            hash_obj.update(file)
        else:
            raise TypeError(f"All arguments must be bytes. Got {type(file)}")
    return hash_obj.hexdigest()[:32]


class TrackProcessor:
    def __init__(self, cache_dir: pathlib.Path = None):
        self.cache_dir = cache_dir or pathlib.Path(__file__).parent / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.df = None
        self.scale_x = 1
        self.scale_y = 1
        self.offset_x = 0
        self.offset_z = 0
        self.player_offset_x = 0
        self.player_offset_z = 0

        self.newer_file_comb = False

        self.json_file_path = None
        self.binary_file_path = None
        self.img_path = None
        self.dae_path = None

        self.image_width = -1
        self.image_height = -1

        self.max_world_x = -1
        self.min_world_x = -1
        self.max_world_z = -1
        self.min_world_z = -1

        self.pixels = None
        self.cur_cache_key = None
        self.need_late_update = False
        self.df_dtypes = None
        self.need_compact = False

    def __del__(self):
        self.save_df_to_cache()

    def update(self, json_file, binary_file, img_file, dae_file):
        start_time = time()
        self.update_img_file(img_file)
        print("update_img_file:", time() - start_time)
        start_time = time()
        self.update_dae_file(dae_file)
        print("update_dae_file:", time() - start_time)
        start_time = time()
        self.update_binary_file(binary_file, json_file)
        print("update_binary_file:", time() - start_time)
        print("bin done")

        return self.pixels

    def save_df_to_cache(self):
        if self.df is not None and self.cur_cache_key:
            self.cache_dir.mkdir(exist_ok=True)
            self.df.to_feather(self.cache_dir / f"{self.cur_cache_key}.feather")

    def late_update(self):
        # things we can do after the plot is returned
        if not self.need_late_update:
            return

        # start_time = time()
        if self.need_compact:
            self.df = round_and_compact_df(self.df)
        if self.df_dtypes is not None:
            self.df.astype(self.df_dtypes)
        self.need_late_update = False
        # print("late_update:", time() - start_time)
        # self.df

    def update_binary_file(self, binary_file, json_file):
        # ? _generate_cache_key is fast enough
        new_key = _generate_cache_key(binary_file["content"], json_file["content"])
        new_csv_file_path = self.cache_dir / f"{new_key}.feather"

        if new_key != self.cur_cache_key:
            self.need_late_update = True
            if self.df is not None:  # save current df before changing to new one
                self.save_df_to_cache()

            self.cur_cache_key = new_key

            if not (new_csv_file_path).exists():  # cache
                parser = BinaryParser(json_file["content"])
                self.df = parser.parse_binary(binary_file["content"])
                self.df_dtypes = parser.df_dtypes
                self.need_compact = True
                # start_time = time()
                # self.df = round_and_compact_df(self.df)
                # print("compact_df:", time() - start_time)
            else:
                start_time = time()
                self.df_dtypes = None
                self.need_compact = False
                self.df = pd.read_feather(new_csv_file_path)
                print("read_feather:", time() - start_time)

        self.update_param(json_file["content"])

        if (
            self.player_offset_z is None
            or self.player_offset_z is None
            or self.scale_x is None
            or self.scale_y is None
            or self.min_img_x is None
            or self.min_img_z is None
        ):
            self.pixels = np.zeros((1, 3), dtype=int)
            return

        col_name = generate_hash(
            self.player_offset_x,
            self.player_offset_z,
            self.scale_x,
            self.scale_y,
            self.min_img_x,
            self.min_img_z,
        )
        # print(col_name, f"{col_name}_x" in self.df, f"{col_name}_y" in self.df) #TODO => not saved in df yet

        if f"{col_name}_x" in self.df and f"{col_name}_y" in self.df:
            self.pixels = self.df[[f"{col_name}_x", f"{col_name}_y"]].values
        else:
            start_time = time()
            self.pixels = find_pixels_to_color(
                self.df,
                (self.player_offset_x, self.player_offset_z),
                self.scale_x,
                self.scale_y,
                self.min_img_x,
                self.min_img_z,
            )
            print("find_pixels_to_color:", time() - start_time)
            # self.df[f"{col_name}_x"] = self.pixels[:, 0]
            # self.df[f"{col_name}_y"] = self.pixels[:, 1]

    def update_dae_file(self, dae_file):
        self.dae_path = dae_file
        dae_bbx = get_dae_bounding_box(dae_file["content"])
        if dae_bbx:
            self.max_world_x = dae_bbx[1][0]
            self.min_world_x = dae_bbx[0][0]
            self.max_world_z = dae_bbx[1][2]
            self.min_world_z = dae_bbx[0][2]

    def update_img_file(self, img_file):
        self.img_path = img_file
        img_bbx = find_img_bounding_box(img_file["content"])
        with open_image(img_file["content"]) as img:
            self.image_width, self.image_height = img.size
        if img_bbx:
            self.max_img_x = img_bbx[1][0]
            self.min_img_x = img_bbx[0][0]
            self.max_img_z = img_bbx[1][1]
            self.min_img_z = img_bbx[0][1]

    def update_param(self, json_content):
        world_width = self.max_world_x - self.min_world_x
        world_height = self.max_world_z - self.min_world_z

        img_width_without_borders = self.max_img_x - self.min_img_x
        img_height_without_borders = self.max_img_z - self.min_img_z

        self.scale_x = img_width_without_borders / world_width
        self.scale_y = img_height_without_borders / world_height

        player_min_x = self.df["Position X_1"].min()
        player_min_z = self.df["Position Z_1"].min()
        target_bbox = (
            player_min_x,
            player_min_z,
            self.df["Position X_1"].max() - player_min_x,
            self.df["Position Z_1"].max() - player_min_z,
        )

        # with open(json_file_path, 'r') as f:
        #     track_const_data = json.load(f)
        track_const_data = json.loads(json_content)

        min_map_x, _, min_map_z = track_const_data["mapMinVolume"]
        # max_map_x, _, max_map_z = track_const_data['mapMaxVolume']

        player_bbox = (
            (player_min_x, player_min_z),
            (self.df["Position X_1"].max(), self.df["Position Z_1"].max()),
        )

        self.player_offset_x = 0
        self.player_offset_z = 0

        for ox, oz in [(self.min_world_x, self.min_world_z), (min_map_x, min_map_z)]:
            min_pixel_x = (player_bbox[0][0] - ox) * self.scale_x + self.min_img_x
            max_pixel_x = (player_bbox[1][0] - ox) * self.scale_x + self.min_img_x
            min_pixel_y = (player_bbox[0][1] - oz) * self.scale_y + self.min_img_z
            max_pixel_y = (player_bbox[1][1] - oz) * self.scale_y + self.min_img_z
            if (
                min_pixel_x > self.min_img_x
                and max_pixel_x < self.max_img_x
                and min_pixel_y > self.min_img_z
                and max_pixel_y < self.max_img_z
            ):
                self.player_offset_x = ox
                self.player_offset_z = oz
                break

        ox_valid = None
        for ox in [self.min_world_x, min_map_x]:
            min_pixel_x = (player_bbox[0][0] - ox) * self.scale_x + self.min_img_x
            max_pixel_x = (player_bbox[1][0] - ox) * self.scale_x + self.min_img_x
            if min_pixel_x > self.min_img_x and max_pixel_x < self.max_img_x:
                ox_valid = ox
                break

        oz_valid = None
        for oz in [self.min_world_z, min_map_z]:
            min_pixel_y = (player_bbox[0][1] - oz) * self.scale_y + self.min_img_z
            max_pixel_y = (player_bbox[1][1] - oz) * self.scale_y + self.min_img_z
            if min_pixel_y > self.min_img_z and max_pixel_y < self.max_img_z:
                oz_valid = oz
                break

        # ox_name = None
        # for name, o in [("dae", self.min_world_x), ("json", min_map_x)]:
        #     if self.player_offset_x == o:
        #         ox_name = name

        # print("x offset:", ox_name)

        # oz_name = None
        # for name, o in [("dae", self.min_world_z), ("json", min_map_z)]:
        #     if self.player_offset_z == o:
        #         oz_name = name

        # print("z offset:", oz_name)

        # print(self.min_world_x, self.min_img_z)
        # print(min_map_x, min_map_z)
        # print(self.player_offset_x, self.player_offset_z)

        print((ox_valid, oz_valid), (self.player_offset_x, self.player_offset_z))
        print(
            "new way:",
            (ox_valid, oz_valid) == (self.player_offset_x, self.player_offset_z),
        )
