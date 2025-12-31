from datetime import timedelta
import json
import pathlib
from time import time
import dash
from dash import dcc, html, ctx
from dash.dependencies import Input, Output, State

from pathlib import Path

from dash import (
    html,
    dcc,
    callback,
    Input,
    Output,
    State,
    ALL,
    MATCH,
    no_update,
    clientside_callback,
)
from dash.exceptions import PreventUpdate

from mkwdashboard.assets.index_string import index_string
from mkwdashboard.tools.df_formatting import get_dropdown_options
from mkwdashboard.tools.file_handling import get_files_contents
from mkwdashboard.tools.file_handling import process_upload_content
from mkwdashboard.tools.formatting import format_ms
from mkwdashboard.tools.import_from_folder import search_folder_simple
from mkwdashboard.tools.plotly_obj_creation import generate_img_figure, generate_model_figure
from mkwdashboard.tools.clientside_callbacks import slider_time_formatting_callback

from mkwdashboard.assets.dash_styles import (
    upload_button_style,
    file_path_style,
    dropdown_style,
    button_style,
    label_style,
    container_style,
)

from mkwdashboard.config import app, tp, p, q, file_types, files, test_auto_load_folder

clientside_callback(
    slider_time_formatting_callback,
    Output("dummy-output", "children"),
    Input("time-slider", "value"),
)


app.index_string = index_string

test_auto_load_folder = Path(test_auto_load_folder)
if test_auto_load_folder and test_auto_load_folder.exists():
    found_files = search_folder_simple(test_auto_load_folder)
    files.update(found_files)

default_contents, default_filenames = get_files_contents(
    files
)  # for test purposes with dash in local

app.layout = html.Div(
    style={
        "fontFamily": "'Inter', sans-serif",
        "width": "100vw",
        "minHeight": "100vh",
        "background": "linear-gradient(135deg, #0f1115 0%, #1a1a2e 50%, #0f1115 100%)",
        "padding": "30px",
        "position": "relative",
    },
    children=[
        # Header
        html.Div(
            className="fade-in-up",
            style={
                "textAlign": "center",
                "marginBottom": "30px",
            },
            children=[
                html.H1(
                    "MKW Telemetry Visualizer",
                    style={
                        "fontSize": "2rem",
                        "fontWeight": "600",
                        "color": "white",
                        "margin": "0",
                        "letterSpacing": "-0.5px",
                    },
                ),
                # html.P(
                #     "Digital Twin Dashboard",
                #     style={
                #         "fontSize": "12px",
                #         "color": "rgba(255, 255, 255, 0.4)",
                #         "marginTop": "8px",
                #         "fontFamily": "'JetBrains Mono', monospace",
                #         "letterSpacing": "2px",
                #         "textTransform": "uppercase",
                #     },
                # ),
            ],
        ),
        # Main Layout Container
        html.Div(
            style={
                "display": "flex",
                "gap": "24px",
                "height": "calc(100vh - 160px)",
            },
            children=[
                # Left Sidebar - Controls
                html.Div(
                    className="glass-panel fade-in-up delay-1",
                    style={
                        "width": "400px",
                        "flexShrink": "0",
                        "padding": "24px",
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "24px",
                        "overflowY": "auto",
                    },
                    children=[
                        # File Upload Section
                        html.Div(
                            children=[
                                html.Div("File Upload", className="section-header"),
                                html.Div(
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "gap": "10px",
                                    },
                                    children=[
                                        dcc.Upload(
                                            id={"type": "upload-file", "index": i},
                                            children=html.Div(
                                                [
                                                    html.Span(
                                                        "📁", style={"fontSize": "16px"}
                                                    ),
                                                    html.Span(
                                                        f'Select {file_type["type"].upper()} File'
                                                    ),
                                                ],
                                                className="upload-button",
                                            ),
                                            multiple=False,
                                            accept=file_type["accept"],
                                        )
                                        for i, file_type in enumerate(file_types)
                                    ],
                                ),
                                html.Div(
                                    id="file-paths",
                                    className="file-path-display",
                                    style={"display": "none"},
                                ),
                            ],
                        ),
                        # Parameter Selection Section
                        html.Div(
                            children=[
                                html.Div("Parameters", className="section-header"),
                                # Column Dropdown
                                html.Div(
                                    style={"marginBottom": "5px"},
                                    children=[
                                        html.Label(
                                            "Select Columns", className="label-text"
                                        ),
                                        dcc.Dropdown(
                                            id="column-dropdown",
                                            options=[],
                                            multi=True,
                                            disabled=True,
                                            placeholder="Select columns...",
                                            className="dash-dropdown",
                                            style={"marginTop": "6px"},
                                        ),
                                        html.Div(
                                            style={
                                                "display": "flex",
                                                "gap": "8px",
                                                "marginTop": "10px",
                                            },
                                            children=[
                                                html.Button(
                                                    "Select All",
                                                    id="select-all-btn",
                                                    n_clicks=0,
                                                    className="secondary-button",
                                                    disabled=True,
                                                ),
                                                html.Button(
                                                    "Clear",
                                                    id="clear-btn",
                                                    n_clicks=0,
                                                    className="secondary-button",
                                                    disabled=True,
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        # Time Slider Section
                        html.Div(
                            children=[
                                html.Div("Time Range", className="section-header"),
                                html.Div(
                                    id="slider-container",
                                    style={"padding": "0px 0px"},
                                    children=[
                                        dcc.RangeSlider(
                                            id="time-slider",
                                            min=0,
                                            max=1,
                                            value=[0, 1],
                                            step=0.1,
                                            marks={
                                                0: {
                                                    "label": "0s",
                                                    "style": {
                                                        "color": "rgba(255,255,255,0.4)"
                                                    },
                                                },
                                                1: {
                                                    "label": "1s",
                                                    "style": {
                                                        "color": "rgba(255,255,255,0.4)"
                                                    },
                                                },
                                            },
                                            updatemode="drag",
                                            disabled=True,
                                            tooltip={
                                                "placement": "bottom",
                                                "always_visible": True,
                                            },
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        # 3D Toggle
                        html.Div(
                            children=[
                                dcc.Checklist(
                                    id="my-checkbox",
                                    options=[
                                        {"label": " Visualize in 3D", "value": "enable"}
                                    ],
                                    value=["enable"],
                                    className="custom-checklist",
                                ),
                            ],
                        ),
                        # Spacer
                        # html.Div(style={"flex": "1"}),
                        # Export Section
                        html.Div(
                            children=[
                                html.Div("Export", className="section-header"),
                                html.Div(
                                    style={
                                        "marginTop": "8px",
                                        "display": "flex",
                                        "gap": "10px",
                                        "alignItems": "center",
                                    },
                                    children=[
                                        dcc.Dropdown(
                                            id="file-format-dropdown",
                                            options=[
                                                {"label": "CSV", "value": "csv"},
                                                {"label": "Excel", "value": "excel"},
                                            ],
                                            value="excel",
                                            clearable=False,
                                            className="dash-dropdown",
                                            style={"flex": "1"},
                                        ),
                                        html.Button(
                                            [
                                                html.Span(
                                                    "⬇", style={"fontSize": "14px"}
                                                ),
                                                html.Span("Download"),
                                            ],
                                            id="download-btn",
                                            className="custom-button",
                                            style={"whiteSpace": "nowrap"},
                                        ),
                                    ],
                                ),
                                dcc.Download(id="download-dataframe"),
                            ],
                        ),
                        html.Div(id="output"),
                    ],
                ),
                # Right Side - Graph
                html.Div(
                    className="graph-container fade-in-up delay-2",
                    style={
                        "flex": "1",
                        "display": "flex",
                        "flexDirection": "column",
                        "minWidth": "0",
                    },
                    children=[
                        dcc.Graph(
                            id="main-graph",
                            style={
                                "width": "100%",
                                "height": "100%",
                                "minHeight": "500px",
                            },
                            config={
                                "displayModeBar": True,
                                "scrollZoom": True,
                                "displaylogo": False,
                                "doubleClickDelay": 500,
                                "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                            },
                            # Dark theme for plotly
                            figure={
                                "data": [],
                                "layout": {
                                    "paper_bgcolor": "rgba(0,0,0,0)",
                                    "plot_bgcolor": "rgba(0,0,0,0)",
                                    "font": {"color": "rgba(255,255,255,0.7)"},
                                    "xaxis": {
                                        "gridcolor": "rgba(255,255,255,0.1)",
                                        "zerolinecolor": "rgba(255,255,255,0.1)",
                                    },
                                    "yaxis": {
                                        "gridcolor": "rgba(255,255,255,0.1)",
                                        "zerolinecolor": "rgba(255,255,255,0.1)",
                                    },
                                },
                            },
                        ),
                    ],
                ),
            ],
        ),
        # Hidden Stores
        dcc.Store(
            id="default-files",
            data={"contents": default_contents, "filenames": default_filenames},
        ),
        dcc.Store(id="upload-trigger", data={}),
        dcc.Store(id="upload-trigger-late", data={}),
        # dcc.Store(id='upper-slider-tooltip-value'),
        # dcc.Store(id='lower-slider-tooltip-value'),
        # dcc.Store(id='dummy'),
        html.Div(id="dummy-output", style={"display": "none"}),
    ],
)


# prevent_initial_call=True
@callback(
    Output({"type": "upload-file", "index": ALL}, "children"),
    Output("file-paths", "children"),
    Output("upload-trigger", "data"),
    Input({"type": "upload-file", "index": ALL}, "contents"),
    State({"type": "upload-file", "index": ALL}, "filename"),
)
def update_output(contents_list, filename_list):
    """
    Updates the upload button labels and displays uploaded file paths.
    Handles both manual uploads and default file initialization.
    """
    button_children, file_paths = update_frontend_uploaded(contents_list, filename_list)

    return button_children, file_paths, {"timestamp": time()}


def update_frontend_columns(is_bin_present, col_names):
    if not is_bin_present:  # ?TODO move to a "update_bin" callback? + ugly af
        return [], True, True, True

    columns_display, columns = get_dropdown_options(col_names, tp.df)
    options = [
        {"label": label, "value": val} for label, val in zip(columns_display, columns)
    ]
    dd_opt, dd_disabled, all_btn, clear_btn = options, False, False, False
    return dd_opt, dd_disabled, all_btn, clear_btn


def update_frontend_uploaded(contents_list, filename_list):
    simulated_contents, simulated_filenames = get_files_contents(files)

    button_children = [None] * len(file_types)
    file_paths = [None] * len(file_types)

    for i, file_type in enumerate(file_types):
        type_name = file_type["type"]

        # Prioritize manually uploaded files
        if contents_list[i] is not None and filename_list[i] is not None:
            content = contents_list[i]
            filename = filename_list[i]
        else:
            content = simulated_contents[i]
            filename = simulated_filenames[i]

        if content is not None and filename is not None:
            button_children[i] = html.Button(
                f"{type_name.upper()} File selected: {filename}",
                style={
                    "flex": "auto",
                    "flexDirection": "column",
                    "width": "100%",
                    "gap": "10px",
                },
                className="custom-button",
            )
            file_paths[i] = html.Div(
                f'{type_name.upper()} File path: {found_files.get(type_name, "Unknown")}',
                style=file_path_style,
            )
        else:
            button_children[i] = html.Button(
                f"Select {type_name.upper()} File",
                className="upload-button",
            )
            file_paths[i] = html.Div(
                f"{type_name.upper()} File path: Not uploaded", style=file_path_style
            )

    return button_children, file_paths


@callback(
    Output("main-graph", "figure"),
    Output("upload-trigger-late", "data"),
    Output("column-dropdown", "options"),
    Output("column-dropdown", "disabled"),
    Output("select-all-btn", "disabled"),
    Output("clear-btn", "disabled"),
    Output("time-slider", "disabled"),
    Output("time-slider", "min"),
    Output("time-slider", "max"),
    Output("time-slider", "marks"),  # update marks
    Input("column-dropdown", "value"),
    Input("upload-trigger", "data"),
    Input("my-checkbox", "value"),
    Input("time-slider", "value"),
    State({"type": "upload-file", "index": ALL}, "contents"),
    State({"type": "upload-file", "index": ALL}, "filename"),
    State("default-files", "data"),
    State("time-slider", "disabled"),
    prevent_initial_call=True,
)
def main_update(
    selected_column,
    upload_trigger,
    visualize_in_3d,
    time_slider_value,
    contents_list,
    filename_list,
    default_files,
    time_slider_disabled,
):
    default_contents = default_files["contents"]
    default_filenames = default_files["filenames"]
    final_contents = []
    final_filenames = []
    for i, content in enumerate(contents_list):
        if content is None or filename_list[i] is None:
            final_contents.append(default_contents[i])
            final_filenames.append(default_filenames[i])
        else:
            final_contents.append(content)
            final_filenames.append(filename_list[i])

    if not all(final_contents):
        print(next(i for i, x in enumerate(final_contents) if not x))
        raise PreventUpdate

    # Process file uploads using the final contents and filenames
    decoded_json = process_upload_content(final_contents[0])
    if decoded_json is None:
        raise PreventUpdate
    json_file = {"content": decoded_json, "filename": final_filenames[0]}

    decoded_binary = process_upload_content(final_contents[1])
    if decoded_binary is None:
        raise PreventUpdate
    binary_file = {"content": decoded_binary, "filename": final_filenames[1]}

    decoded_img = process_upload_content(final_contents[2])
    if decoded_img is None:
        raise PreventUpdate
    img_file = {"content": decoded_img, "filename": final_filenames[2]}

    decoded_dae = process_upload_content(final_contents[3])
    if decoded_dae is None:
        raise PreventUpdate
    dae_file = {"content": decoded_dae, "filename": final_filenames[3]}

    encoded_image = final_contents[2]  # already in b64

    # Update processor with the new files
    tp.update(json_file, binary_file, img_file, dae_file)

    col_names = set(x.rsplit("_")[0] for x in tp.df.columns)
    is_bin_present = decoded_binary is not None  # TODO always true

    dd_opt, dd_disabled, all_btn, clear_btn = update_frontend_columns(
        is_bin_present, col_names
    )

    disable_time_slider = not (is_bin_present and "Time" in col_names)

    if not disable_time_slider:
        time_cols = [col for col in tp.df.columns if col.startswith("Time")]
        min_time = int(tp.df[time_cols].min(axis=1).min())
        max_time = int(
            tp.df[time_cols].max(axis=1).max()
        )  # should be sorted but we never know right

        time_slider_value = [
            max(min_time, min(time_slider_value[i], max_time)) for i in range(2)
        ]
    else:
        min_time = 0
        max_time = 1

    marks = {
        min_time: str(format_ms(min_time)),
        max_time: str(format_ms(max_time)),
    }

    if not visualize_in_3d:
        figure = generate_img_figure(
            tp.pixels, encoded_image, tp.image_height, tp.image_width
        )
    else:
        data_infos = (
            selected_column if selected_column else []
        )  # ['Time', 'Engine Speed']
        # print(set([x[:-2] for x in tp.df.columns]))
        j = json.loads(decoded_json)
        nump_player = len(j["players"])
        num_lap = j["maxLap"]
        player_ids = list(range(1, nump_player + 1))
        # df_time_limited = []

        # for player in player_ids:
        time_col = time_cols[0] if time_cols else None
        df_time_limited = (
            tp.df
            if disable_time_slider
            else tp.df[
                (tp.df[time_col] >= time_slider_value[0])
                & (tp.df[time_col] <= time_slider_value[1])
            ]
        )

        figure = generate_model_figure(
            df_time_limited, player_ids, num_lap, data_infos, decoded_dae, tp
        )

    return (
        figure,
        {"timestamp": time()},
        dd_opt,
        dd_disabled,
        all_btn,
        clear_btn,
        disable_time_slider,
        min_time,
        max_time,
        marks,
    )


@app.callback(
    Output("column-dropdown", "value"),
    Input("select-all-btn", "n_clicks"),
    Input("clear-btn", "n_clicks"),
    State("column-dropdown", "options"),
    prevent_initial_call=True,
)
def select_all_or_clear(select_all_clicks, clear_clicks, options):
    trigger = ctx.triggered_id

    if trigger == "select-all-btn":
        return [opt["value"] for opt in options]
    elif trigger == "clear-btn":
        return []
    return dash.no_update


@callback(Input("upload-trigger-late", "data"), prevent_initial_call=True)
def late_update(upload_trigger_late):
    # things we can do after the plot is returned
    tp.late_update()


@app.callback(
    Output("download-btn", "disabled"),
    Input({"type": "upload-file", "index": 1}, "filename"),  # Monitor index 1 upload
)
def toggle_download_button(csv_filename):
    print(csv_filename)
    if csv_filename:
        return False  # Enable button
    return True


@app.callback(
    Output("download-dataframe", "data"),
    Input("download-btn", "n_clicks"),
    State("file-format-dropdown", "value"),
    State({"type": "upload-file", "index": 1}, "filename"),  #! Assuming CSV is index 1
    prevent_initial_call=True,
)
def download_file(n_clicks, file_format, filename):
    print("download_file called")
    if not n_clicks:
        return no_update

    # Use the filename from the upload, or a default name
    base_filename = pathlib.Path(filename).stem if filename else "output"
    download_filename = f"{base_filename}.{file_format}"

    if file_format == "csv":
        return dcc.send_data_frame(tp.df.to_csv, download_filename, index=False)
    elif file_format == "excel":
        download_filename = f"{base_filename}.xlsx"
        return dcc.send_data_frame(
            tp.df.to_excel, download_filename, index=False, sheet_name="Sheet1"
        )
    else:
        return no_update


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
