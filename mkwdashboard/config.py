from pathlib import Path

import dash


app = dash.Dash(__name__)

p = 1
q = 12

from mkwdashboard.tools.file_handling import get_file_struct

files = get_file_struct()

file_types = [
    {"type": "json", "accept": ".json"},
    {"type": "binary", "accept": ".csv"},
    {"type": "png", "accept": ".png, .jpg, .jpeg"},
    {"type": "dae", "accept": ".dae"},
]

from mkwdashboard.processing.track_processor import TrackProcessor

SELF_PATH = Path(__file__).parent
CACHE_PATH = SELF_PATH / "cache"
CACHE_PATH.mkdir(exist_ok=True)
tp = TrackProcessor(CACHE_PATH)

# folder = Path("/mnt/c/Users/mathi/Desktop/mkw work folder/course_test/Jiyuu Village")

# for test purposes, give path to folder and it'll auto select/load needed files (json, csv, dae, png) from it
test_auto_load_folder = Path("/mnt/c/Users/mathi/Desktop/mkw work folder/course_test/Jiyuu Village")
