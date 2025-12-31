import numpy as np


def can_convert_to_lower_dtypes(series, input_type, output_type, decimal_places):
    try:
        output_type_info = (
            np.finfo(output_type) if np.issubdtype(output_type, np.floating) else None
        )

        if output_type_info:
            if (
                series.min() < output_type_info.min
                or series.max() > output_type_info.max
            ):
                return False

        series_converted = series.astype(output_type)
        series_back = series_converted.astype(input_type)

        return np.allclose(
            series, series_back, rtol=10 ** (-decimal_places), atol=1e-8, equal_nan=True
        )

    except Exception as e:
        print(f"Error converting column: {e}")
        return False


def lower_dtypes(df, input_type, output_type, decimal_places):
    num_col_changed = 0
    num_to_change = len(df.select_dtypes(include=[input_type]).columns)

    for col in df.select_dtypes(include=[input_type]).columns:
        if can_convert_to_lower_dtypes(
            df[col], input_type, output_type, decimal_places
        ):
            df[col] = df[col].astype(output_type)
            num_col_changed += 1

    print(
        f"Converted {num_col_changed}/{num_to_change} columns from {input_type} to {output_type}"
    )
    return df


def round_and_compact_df(df, decimal_places=4):
    df = df.round(decimal_places)

    types = [np.float64, np.float32, np.float16]

    for i in range(len(types) - 1):
        df = lower_dtypes(df, types[i], types[i + 1], decimal_places)

    return df
