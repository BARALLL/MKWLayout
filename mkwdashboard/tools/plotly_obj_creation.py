import numpy as np

import plotly.graph_objs as go
import plotly.express as px

import collada
import io

from mkwdashboard.processing.track_processor import TrackProcessor
from mkwdashboard.tools.formatting import to_ordinal


def generate_img_figure(pixels, encoded_image, img_height, img_width):
    pixels[:, 1] = img_height - pixels[:, 1]

    trace = go.Scatter(
        x=pixels[:, 0],
        y=pixels[:, 1],
        mode="lines",
        name="pos",
        line=dict(color="red", width=1),
        line_shape="spline",
        visible=True,
        hovertext=None,
        hoverinfo="text",
    )

    traces = [trace]
    # for curve_name, (x, y) in curves.items():
    #     traces.append(go.Scatter(
    #         x=x,
    #         y=y,
    #         name=curve_name,
    #         mode='lines+markers',
    #         visible=True,
    #         line=dict(shape='linear')
    #     ))

    # title=f'Visualization (Integer: {selected_integer}, Column: {selected_column})',
    figure = {
        "data": traces,
        "layout": go.Layout(
            xaxis={
                "title": "X",
                "range": [0, img_width],
                "scaleanchor": "y",
                "scaleratio": 1,  # use 1:1 scaling in pixel space
                "constrain": "domain",
                "showgrid": False,
                "zeroline": False,
                "visible": False,
            },
            yaxis={
                "title": "Y",
                "range": [0, img_height],
                "constrain": "domain",
                "showgrid": False,
                "zeroline": False,
                "visible": False,
            },
            hovermode="closest",
            showlegend=True,
            legend=dict(
                x=1,
                y=0.9,
                # title='Select Traces',
                # bgcolor='rgba(255, 255, 255, 0.5)',
                # bordercolor='black',
                # borderwidth=1
            ),
            images=[
                dict(
                    source=encoded_image,
                    xref="x",
                    yref="y",
                    x=0,
                    y=img_height,
                    sizex=img_width,
                    sizey=img_height,
                    sizing="stretch",
                    opacity=1,
                    layer="below",
                )
            ],
            margin=dict(l=0, r=0, t=0, b=0),
            autosize=True,
            dragmode="zoom",
        ),
    }

    return figure


def add_3d_traces(player_df, player_id, rank, tp, scale_factor=1, color=None):
    data_positions = player_df[[f"Position {axis}" for axis in "XYZ"]].values

    player_min_x = data_positions[:, 0].min()
    player_min_z = data_positions[:, 2].min()

    data_positions[:, 0] -= player_min_x
    data_positions[:, 2] -= player_min_z

    data_positions[:, 0] += abs(player_min_x - tp.player_offset_x)
    data_positions[:, 2] += abs(player_min_z - tp.player_offset_z)

    data_positions = data_positions / scale_factor

    hover_columns = [
        col
        for col in player_df.columns
        if col not in ["Position X", "Position Y", "Position Z"]
    ]
    hover_text = player_df[hover_columns].apply(
        lambda row: "<br>".join([f"{col}: {round(value, 3)}" for col, value in row.items()]),
        axis=1,
    )

    # use a unique group ID for the legend so toggling one toggles both ghost line and visible line
    group_id = f"rank_{rank}_{player_id}"
    trace_name = f"{to_ordinal(rank)} Place"

    # visual trace (thin, pretty, non interactive)
    line_trace = go.Scatter3d(
        x=data_positions[:, 0],
        y=data_positions[:, 2],
        z=data_positions[:, 1],
        mode="lines",
        name=trace_name,
        line=dict(width=2, color=color),
        visible=True,
        hoverinfo="skip",
        legendgroup=group_id,
        showlegend=True,
    )

    # ghost trace (thick, invisible, interactive)
    ghost_trace = go.Scatter3d(
        x=data_positions[:, 0],
        y=data_positions[:, 2],
        z=data_positions[:, 1],
        mode="lines",
        name=trace_name,
        line=dict(width=30, color=color),
        opacity=0,
        visible=True,
        text=hover_text,
        hoverinfo="text",
        legendgroup=group_id,
        showlegend=False,
    )

    return [line_trace, ghost_trace]


def generate_model_figure(
    df, player_ids, num_lap, data_infos, dae_model, tp: TrackProcessor
):
    collada_mesh = collada.Collada(
        io.BytesIO(dae_model),
        ignore=[collada.DaeBrokenRefError, collada.DaeIncompleteError],
    )

    vertices = []
    faces = []
    vertex_offset = 0

    for geometry in collada_mesh.geometries:
        for primitive in geometry.primitives:
            if isinstance(primitive, collada.triangleset.TriangleSet):
                vertex_data = primitive.vertex
                vertex_index = primitive.vertex_index
                vertices.extend(vertex_data)
                faces.extend(vertex_index + vertex_offset)
                vertex_offset += len(vertex_data)

    vertices = np.array(vertices)
    faces = np.array(faces)

    vertices[:, 0] -= vertices[:, 0].min()
    vertices[:, 2] -= vertices[:, 2].min()

    scale_factor = 1000
    vertices = vertices / scale_factor

    mesh3d = go.Mesh3d(
        x=vertices[:, 0],
        z=vertices[:, 1],
        y=vertices[:, 2],
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        color="blue",
        opacity=0.8,
        hovertext=None,
        hovertemplate=None,
        hoverinfo="skip",
    )

    traces = [mesh3d]

    col_names = set(x.rsplit("_")[0] for x in df.columns)

    col_threshold_index = {}
    if "Race Completion %" in col_names:
        for i, player_id in enumerate(player_ids):
            race_comp_col = f"Race Completion %_{player_id}"
            arr = tp.df[race_comp_col].values
            idx = np.searchsorted(arr, num_lap, side="left")
            if idx < len(arr) and arr[idx] >= num_lap:
                col_threshold_index[player_id] = idx
            else:
                col_threshold_index[player_id] = len(arr) + 1

    sorted_cols = sorted(col_threshold_index.items(), key=lambda x: x[1])
    sorted_cols = [col for col, idx in sorted_cols]

    player_traces = []
    colors = px.colors.qualitative.Plotly
    for player_id in player_ids:
        col_names = set(x.rsplit("_")[0] for x in df.columns)
        data_infos = df_columns_from_dropdown_labels(data_infos, col_names)
        player_df = df[
            [f"{info}_{player_id}" for info in data_infos]
            + [f"Position {axis}_{player_id}" for axis in "XYZ"]
        ]
        player_df = player_df.rename(
            columns={
                f"{info}_{player_id}": f"{info}"
                for info in (data_infos + [f"Position {axis}" for axis in "XYZ"])
            }
        )
        [f"Position {axis}_{player_id}" for axis in "XYZ"]
        rank = sorted_cols[player_id - 1]
        assigned_color = colors[player_id % len(colors)]
        trace_pair = add_3d_traces(
            player_df,
            player_id,
            rank,
            tp,
            scale_factor=scale_factor,
            color=assigned_color,
        )
        player_traces.append((rank, trace_pair))


    player_traces.sort(key=lambda x: x[0])
    traces.extend([t for x in player_traces for t in x[1]])

    axis_color = "rgba(0, 240, 255, 0.4)"
    scene_background_color = "rgba(20, 20, 20, 1)"
    
    axis_background_color = "rgba(0, 0, 0, 0)"
    grid_color = "rgba(0, 0, 0, 0)"
    axis_line_color = "rgba(0, 0, 0, 0)"
    background_color = "rgba(0, 0, 0, 0)"

    axis_background_color = scene_background_color
    fig = go.Figure(data=traces)
    fig.update_layout(
        hovermode="closest",
        uirevision=True,
        hoverdistance=500,
        paper_bgcolor=background_color,
        scene=dict(
            xaxis=dict(
                title="X Axis",
                showspikes=False,
                showbackground=False,
                backgroundcolor=axis_background_color,
                color=axis_color,
                showline=False,
                linecolor=axis_line_color,
                showgrid=False,
                gridcolor=grid_color,
                zeroline=False,
            ),  # range=[vertices[:, 0].min(), vertices[:, 0].max()]
            yaxis=dict(
                title="Y Axis",
                showspikes=False,
                showbackground=False,
                backgroundcolor=axis_background_color,
                color=axis_color,
                showline=False,
                linecolor=axis_line_color,
                showgrid=False,
                gridcolor=grid_color,
                zeroline=False,
            ),  # range=[vertices[:, 2].min(), vertices[:, 2].max()]
            zaxis=dict(
                title="Z Axis",
                showspikes=False,
                showbackground=False,
                backgroundcolor=axis_background_color,
                color=axis_color,
                showline=False,
                linecolor=axis_line_color,
                showgrid=False,
                gridcolor=grid_color,
                zeroline=False,
            ),  # range=[vertices[:, 1].min(), vertices[:, 1].max()]
            aspectmode="data",
            bgcolor=scene_background_color,
        ),
        showlegend=True,
        legend=dict(
            x=0.875,
            y=0.85,
            bgcolor='rgba(0,0,0,0)',
            borderwidth=0,
            font=dict(color='#ffffff', size=12),
        ),
        margin=dict(l=0, r=0, b=0, t=0),

        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='#888888',
            activecolor='rgba(0, 240, 255, 1)',
        ),
    )

    return fig


def df_columns_from_dropdown_labels(data_infos, col_names):
    mutli_data_augmented = []
    for info in data_infos:
        is_axial = False
        for axis in "XYZW":
            if f"{info} {axis}" in col_names:
                mutli_data_augmented.append(f"{info} {axis}")
                is_axial = True
        if not is_axial:
            mutli_data_augmented.append(info)
    return mutli_data_augmented
