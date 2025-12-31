import pandas as pd


def aggregate_and_align_data(
    tp_df, component_ids, col_names, time_slider_value=None, disable_time_slider=False
):
    component_data = {}

    max_rows = 0

    for component_id in component_ids:
        component_columns = [f"{col_name}_{component_id}" for col_name in col_names]
        df_component = tp_df[component_columns + [f"TimeSeconds_{component_id}"]]

        if not disable_time_slider:
            df_component = df_component[
                df_component[f"TimeSeconds_{component_id}"] <= time_slider_value
            ]

        component_data[component_id] = df_component
        max_rows = max(max_rows, len(df_component))

    aligned_data = []
    for component_id, df_component in component_data.items():
        if len(df_component) < max_rows:
            df_filled = df_component.reindex(range(max_rows), method="ffill")
        else:
            df_filled = df_component

        aligned_data.append(df_filled)

    result_df = pd.concat(aligned_data, axis=1)

    return result_df


def get_dropdown_options(col_names, df):
    columns_display = []
    columns = []
    seen = set()

    for col in df.columns:
        prefix = col.rsplit("_")[0]
        if prefix[-1] in "XYZW":
            prefix = prefix[:-2]
        if prefix not in seen:
            seen.add(prefix)
            if prefix == "Position":
                continue
            if f"{prefix} W" in col_names:
                columns_display.append(f"{prefix} (Quat)")
            elif f"{prefix} X" in col_names:
                columns_display.append(f"{prefix} (Vec)")
            else:
                columns_display.append(prefix)
            columns.append(prefix)
    return columns_display, columns
