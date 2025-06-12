# Custom Plotly template for all charts in this project
# Created by Alex Hewson
# Last updated 12 March 2025
"""
This module provides utilities for creating and customizing Plotly visualizations
with a standardized template and additional helper functions for annotations,
titles, axis range adjustments, and text wrapping.

Features:
---------
1. A custom Plotly template (`prt_template`) designed for consistent styling
    across charts in the project.
2. Functions to add annotations to charts, including source labels, y-axis labels,
    trace-specific labels, and generic labels.
3. A utility to add wrapped and styled titles to Plotly figures.
4. A helper function to wrap text labels for better readability in visualizations.
5. A function to set axis ranges dynamically based on data or manually provided values.

Modules:
--------
- `add_annotation`: Adds annotations to a Plotly chart with various customization options.
- `add_title`: Adds a styled and wrapped title to a Plotly figure.
- `wrap_labels`: Wraps text labels to a specified maximum character width.
- `set_axis_range`: Dynamically or manually sets the range of x or y axes in a Plotly figure.

Dependencies:
-------------
- pandas
- plotly
- textwrap
"""

import textwrap
from typing import List, Literal, Optional, Union

import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio

# PRT standard template
pio.templates["prt_template"] = go.layout.Template(
    layout=go.Layout(
        title_font=dict(family="Helvetica Neue, Arial", size=20),
        title_y=0.94,
        title_yanchor="bottom",
        font_color="#54565B",
        font_family="Helvetica Neue, Arial",
        font_size=14,
        paper_bgcolor="rgba(1,1,1,0)",
        plot_bgcolor="rgba(1,1,1,0)",
        colorway=("#A01D28", "#499CC9", "#F9A237", "#6FBA3A", "#573D6B"),
        modebar_activecolor="#A01D28",
        showlegend=False,
        xaxis_showgrid=False,
        xaxis_ticks='inside',
        xaxis_tickcolor="#54565B",
        xaxis_gridcolor="rgba(84, 86, 91, 0.15)",
        yaxis_gridcolor="rgba(84, 86, 91, 0.15)",
        width=655,
        height=360,
        margin=dict(l=63, b=75, r=100),
        dragmode=False,
    )
)
pio.templates["prt_template"].data.scatter = [
    go.Scatter(
        line_width=4,
        marker_size=10
        )
        ]


# Chart annotations
def add_annotation(
    annotations_list: Optional[List[dict]] = None,
    text: Optional[str] = None,
    x: Optional[Union[float, List[float]]] = None,
    y: Optional[Union[float, List[float]]] = None,
    xref: str = "paper",
    yref: str = "paper",
    xanchor: str = "left",
    yanchor: str = "top",
    align: Optional[str] = None,
    showarrow: bool = False,
    font_size: int = 14,
    font_color: Optional[str] = None,
    annotation_type: Optional[str] = None,
    dataframe: Optional[pd.DataFrame] = None,
    dataframe_column: Optional[str] = None,
    trace_list: Optional[List] = None,
    trace_list_idx: Optional[Union[int, List[int]]] = None,
    x_pad: float = 0
) -> List[dict]:
    """
    Add an annotation to a Plotly chart.

    Parameters:
    ----------
    annotations_list : list, optional
        A list to which the annotation dictionary will be appended.
        If not provided, a new list is created.

    text : str, optional
        The text to display in the annotation. Required for "source" and "label" annotation types.

    x : float or list of floats, optional
        The x-coordinate(s) for the annotation(s).
        If not specified, defaults are used based on `annotation_type`.

    y : float or list of floats, optional
        The y-coordinate(s) for the annotation(s).
        If not specified, defaults are used based on `annotation_type`.

    xref : str, default="paper"
        The reference for the x-coordinate.
        Can be "paper" (relative to the plot area) or "x" (data coordinates).

    yref : str, default="paper"
        The reference for the y-coordinate.
        Can be "paper" (relative to the plot area) or "y" (data coordinates).

    xanchor : str, default="left"
        The horizontal alignment of the annotation. Options include "left", "center", and "right".

    yanchor : str, default="top"
        The vertical alignment of the annotation. Options include "top", "middle", and "bottom".

    align : str, optional
        The alignment of the text within the annotation box.
        Options include "left", "center", and "right".

    showarrow : bool, default=False
        Whether to display an arrow pointing to the annotation's coordinates.

    font_size : int, default=14
        The font size of the annotation text.

    font_color : str, optional
        The color of the annotation text. If not specified, a default color is used.

    annotation_type : str, required
        The type of annotation. Must be one of:
        - "source": Adds a source label to the chart.
        - "y-axis": Adds a label near the y-axis.
        - "trace_label": Adds annotations to specific traces.
        - "label": Adds a generic label annotation.

    dataframe : pandas.DataFrame, optional
        A DataFrame to extract values for certain annotations (e.g., "y-axis").

    dataframe_column : str, optional
        The column in `dataframe` to use for the annotation's x-coordinate
        (used with "y-axis" type).

    trace_list : list, optional
        A list of Plotly traces to annotate (used with "trace_label" type).

    trace_list_idx : int or list of ints, optional
        The indices of traces in `trace_list` to annotate.
        If not provided, all traces are annotated.

    x_pad : float, default=0
        An optional padding to apply to the x-coordinate of the annotation(s).
        Useful for adjusting placement.

    Raises:
    -------
    ValueError
        If `annotation_type` is not one of the predefined types.
        If required arguments (e.g., `text`, `trace_list`) are missing for certain annotation types.

    """
    # Ensure annotations_list is initialized
    annotations_list = annotations_list or []

    annotation_types = {"source", "y-axis", "trace_label", "label"}
    if annotation_type not in annotation_types:
        raise ValueError(f"Invalid annotation_type: {annotation_type}. Must be one of {annotation_types}")

    if annotation_type == "source":
        if not text:
            raise ValueError("Text must be provided for source annotation.")
        text = f"Source: {text}"
        x, y = x or 0, y or -0.1
        font_size, align = 12, "left"

    elif annotation_type == "y-axis":
        if dataframe is not None and dataframe_column is not None:
            x = dataframe[dataframe_column].iloc[0]
            xref = "x"
        else:
            x = x or 0
        y, yanchor = y or 1, "bottom"

    elif annotation_type == "trace_label":
        if not trace_list:
            raise ValueError("trace_list is required for trace_label annotations.")

        trace_list_idx = (
            list(range(len(trace_list))) if trace_list_idx is None
            else [trace_list_idx] if isinstance(trace_list_idx, int)
            else trace_list_idx
        )

        for j in trace_list_idx:
            trace = trace_list[j]
            annotations_list.append({
                "xref": "x",
                "yref": "y",
                "xanchor": xanchor,
                "yanchor": yanchor,
                "x": (x[j] if isinstance(x, list) else trace.x[-1]) + x_pad,
                "y": y[j] if isinstance(y, list) else trace.y[-1],
                "align": align,
                "showarrow": showarrow,
                "text": str(trace.name),
                "font_size": font_size,
                "font_color": font_color or pio.templates['prt_template'].layout.colorway[j]
            })

        return annotations_list

    elif annotation_type == "label":
        if not text:
            raise ValueError("Text must be provided.")
        x, y, align = x or 0.5, y or 0.5, "center"

    # Apply padding if x is set
    x = x + x_pad if x is not None else None

    # Append the annotation
    annotations_list.append({
        "xref": xref,
        "yref": yref,
        "xanchor": xanchor,
        "yanchor": yanchor,
        "x": x,
        "y": y,
        "align": align,
        "showarrow": showarrow,
        "text": text,
        "font_size": font_size,
        "font_color": font_color
    })

    return annotations_list


def add_title(
        fig,
        title,
        width=80,
        bold=True):
    """Adds a styled title to a Plotly figure.

    Parameters:
        fig (plotly.graph_objects.Figure): The Plotly figure to which the title will be added.
        title (str): The text of the title to be displayed.
        width (int, optional): The maximum width of the title in characters before wrapping.
        Defaults to 80.
        bold (bool, optional): Whether the title text should be bold. Defaults to True.

    Returns:
        None: The function modifies the figure in place.
    """
    wrapped_title = "<br>".join(textwrap.wrap(title, width=width))
    if bold:
        wrapped_title = f"<b>{wrapped_title}</b>"

    fig.update_layout(
        title=wrapped_title,
        title_automargin=True,
        title_yref='container',
        title_xanchor='left',
        title_x=0)


def wrap_labels(text, max_chars=20):
    """
    Wraps text with specified max characters per line and replaces newlines with <br>.

    Args:
        text (str): The text to wrap.
        max_chars (int): The maximum number of characters per line.

    Returns:
        str: Text with wrapped lines and <br> instead of newline characters.
    """
    # Wrap the text with textwrap and replace newlines with <br>
    return textwrap.fill(text, width=max_chars).replace('\n', '<br>')


def set_axis_range(
    fig: go.Figure,
    axis: Literal["x", "y"],
    dataframe: Optional[pd.DataFrame] = None,
    dataframe_column: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> None:
    """
    Sets the axis range manually or based on a dataframe's column.

    Parameters
    ----------
    fig : go.Figure
        Target Plotly figure.

    axis : Literal["x", "y"]
        Axis to apply the range transformation ('x' or 'y').

    dataframe : pd.DataFrame, optional
        DataFrame for automatic calculation of min and/or max value if not provided.

    dataframe_column : str, optional
        Column in the DataFrame to calculate the axis range from.

    min_value : float, optional
        Minimum value for the axis range. Automatically calculated if not provided.

    max_value : float, optional
        Maximum value for the axis range. Automatically calculated if not provided.

    Raises
    ------
    ValueError
        If `min_value` or `max_value` is not provided
        and `dataframe` or `dataframe_column` is missing.
    """

    axis_update_funcs = {
        "x": fig.update_xaxes,
        "y": fig.update_yaxes
    }

    if min_value is None or max_value is None:
        if dataframe is None or dataframe_column is None:
            raise ValueError(
                "Both dataframe and dataframe_column must be provided "
                "if min_value or max_value is None."
            )

        column_max = dataframe[dataframe_column].max()
        column_min = dataframe[dataframe_column].min()
        column_len = len(dataframe[dataframe_column])
        padding = (column_max - column_min) / column_len
        min_value = dataframe[dataframe_column].min() - padding if min_value is None else min_value
        max_value = dataframe[dataframe_column].max() + padding if max_value is None else max_value

    if axis in axis_update_funcs:
        axis_update_funcs[axis](range=[min_value, max_value])
