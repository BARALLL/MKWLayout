from dataclasses import dataclass

import numpy as np
import pandas as pd

import json
import pathlib
import struct
from itertools import chain
from time import time
from typing import Dict, List


@dataclass
class TypeHandler:
    format: str
    byte_size: int
    field_count: int
    dtype: np.generic


TYPE_REGISTRY: Dict[str, TypeHandler] = {
    "u8": TypeHandler("B", 1, 1, np.uint8),
    "u16": TypeHandler("H", 2, 1, np.uint16),
    "u32": TypeHandler("I", 4, 1, np.uint32),
    "float": TypeHandler("f", 4, 1, np.float32),
    "vec3": TypeHandler("3f", 12, 3, np.float32),
    "quat": TypeHandler("4f", 16, 4, np.float32),
}


@dataclass
class FieldSpec:
    type_name: str
    start: int
    end: int
    handler: TypeHandler


# TODO: could optimize this, maybe doing it column-wise (less cache friendly but could vectorize with numpy)
class BinaryParser:
    def __init__(self, json_file: str | pathlib.Path | bytes):
        self.config = self._load_config(json_file)
        self.headers = self.config["header"].split(",")
        self.formats = self.config["format"].split(",")
        self.num_players = len(self.config["players"])

        self.field_specs = self._generate_field_specs()
        self.struct_size = self.field_specs[-1].end if self.field_specs else 0
        self._validate_header_length()

        self.row_size = self.num_players * self.struct_size

        # precompute struct format
        self.struct_format = ">" + "".join(
            spec.handler.format for spec in self.field_specs
        )
        # self.field_counts = [spec.handler.field_count for spec in self.field_specs]
        # self.total_fields_per_player = sum(self.field_counts)

        self.column_names = [
            f"{header}_{i}"
            for i in range(1, self.num_players + 1)
            for header in self.headers
        ]

        df_dtypes = [
            spec.handler.dtype
            for _ in range(self.num_players)
            for spec in self.field_specs
            for _ in range(spec.handler.field_count)
        ]
        self.df_dtypes = {
            col_name: dtype for col_name, dtype in zip(self.column_names, df_dtypes)
        }

    def _load_config(self, json_file: str | pathlib.Path | bytes) -> Dict:
        return json.loads(json_file)

    def _generate_field_specs(self) -> List[FieldSpec]:
        specs = []
        current_offset = 0

        for type_name in self.formats:
            if type_name not in TYPE_REGISTRY:
                raise ValueError(f"Unsupported type: {type_name}")

            handler = TYPE_REGISTRY[type_name]
            specs.append(
                FieldSpec(
                    type_name=type_name,
                    start=current_offset,
                    end=current_offset + handler.byte_size,
                    handler=handler,
                )
            )
            current_offset += handler.byte_size

        return specs

    def _validate_header_length(self):
        expected_struct_fields = sum(
            TYPE_REGISTRY[fmt].field_count for fmt in self.formats
        )

        if len(self.headers) != expected_struct_fields:
            raise ValueError(
                f"Header length mismatch. Expected {expected_struct_fields}, "
                f"got {len(self.headers)}"
            )

    def parse_binary(self, binary_file: str | pathlib.Path | bytes) -> pd.DataFrame:
        if isinstance(binary_file, (str, pathlib.Path)):
            binary_path = pathlib.Path(binary_file)
            if binary_path.exists():
                with open(binary_path, "rb") as f:
                    data = f.read()
            else:
                raise FileNotFoundError(f"The file at {binary_file} does not exist.")
        elif isinstance(binary_file, bytes):
            data = binary_file  # directly the content
        else:
            raise TypeError(
                "Unsupported type for input image. Expected str, pathlib.Path, or bytes."
            )

        if len(data) % self.struct_size != 0:
            # raise ValueError("Binary data length doesn't match struct size")
            max_valid = len(data) // self.struct_size # drop last struct
            data = data[:max_valid*self.struct_size+1]

        num_rows = len(data) // self.row_size
        row_data = []

        # if a line is not complete, wont write it
        for i in range(
            num_rows
        ):  # ? unpack all rows at once is not even that faster from what i've tried?
            row_chunk = data[i * self.row_size : (i + 1) * self.row_size]
            row_values = self._parse_row(row_chunk)
            row_data.append(row_values)

        start_time = time()
        rd = np.array(
            row_data
        )  # divide time for pd.Dataframe by almost 2 from 0.55 to 0.3
        ddddf = pd.DataFrame(rd, columns=self.column_names)  # .astype(self.df_dtypes)
        print("time to transform to df:", time() - start_time)
        return ddddf

    def _parse_row(self, chunk: bytes) -> List:
        players = []
        for i in range(
            self.num_players
        ):  # ? unpack full row is not even that faster from what i've tried?
            player_chunk = chunk[i * self.struct_size : (i + 1) * self.struct_size]
            values = struct.unpack(self.struct_format, player_chunk)
            players.append(values)

        return list(chain.from_iterable(players))
