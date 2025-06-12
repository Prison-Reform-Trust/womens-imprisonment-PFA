##!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is part of the data visualisation pipeline for the Criminal Justice System
statistics quarterly: December 2024 Outcomes by Offence dataset.

It provides a standardised line chart for each Police Force Area to show:
    * The number of women who received an immediate custodial sentence of:
        - Less than 6 months
        - 6 months to less than 12 months
        - 12 months or more
"""

import textwrap
from pathlib import Path
from typing import List, Optional

import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio

from src import utilities as utils
from src.visualization import prt_theme

config = utils.read_config()
pio.templates.default = "prt_template"


class SentenceLengthChart:
    """
    A class for generating and visualizing sentence length trends for women sentenced to immediate
    imprisonment in a specified Police Force Area (PFA) using Plotly.

    The SentenceLengthChart class processes a pandas DataFrame containing sentencing data, creates
    formatted Plotly line charts for each sentence length category, and provides methods for
    customizing, annotating, and exporting the resulting visualizations.

    Attributes:
        pfa (str): The Police Force Area to visualize.
        df (pd.DataFrame): The input DataFrame containing sentencing data.
        label_idx (int | list): Index or indices of trace labels to adjust for annotation positioning.
        adjust (int | list): Adjustment value(s) for annotation y-positions.
        trace_list (List[go.Scatter]): List of Plotly Scatter traces for each sentence length group.
        annotations (list[dict]): List of annotation dictionaries for the chart.
        fig (go.Figure): The Plotly Figure object for the chart.
        pfa_df_sentence (pd.DataFrame): DataFrame filtered for the current PFA and sentence length.
        max_y_val (int): Maximum y-value across all traces, used for axis scaling.

    Methods:
        break_trace_labels():
            Renames sentence length categories for improved label formatting.

        create_traces():
            Generates Plotly Scatter traces for each unique sentence length group within the selected PFA.

        chart_params():
            Configures chart layout, including title, margins, axes, and figure size.

        chart_annotations():
            Adds and adjusts annotations for trace labels and source information.

        set_y_axis():
            Sets the y-axis range based on the maximum value across all traces.

        _prepare_chart():
            Prepares the chart by initializing and configuring all components if not already done.

        save_chart(folder: str, filetype: str):
            Saves the chart as an image file to the specified folder and file type.

        output_chart():
            Prepares and displays the chart using Plotly's show() method.

    Usage:
        Instantiate the class with a PFA and DataFrame, then call output_chart() to display or save_chart()
        to export the visualization.
    """

    def __init__(self, pfa: str, df: pd.DataFrame, label_idx: int | list = 0, adjust: int | list = 0):
        self.pfa = pfa
        self.df = df
        self.label_idx = label_idx
        self.adjust = adjust
        self.trace_list: List[go.Scatter] = []
        self.annotations: list[dict] = []
        self.fig = go.Figure()
        self.pfa_df_sentence = pd.DataFrame()
        self.max_y_val = 0

    def break_trace_labels(self):
        """
        Renames the categories of the 'sentence_length' column in the DataFrame to improve
        label formatting for visualisation.
        """
        self.df['sentence_length'] = self.df['sentence_length'].cat.rename_categories(
            {'6 months to less than 12 months': '6 months—<br>less than 12 months'})

    def create_traces(self):
        """
        Generates Plotly Scatter traces for each unique sentence length group within the selected
        PFA (Police Force Area) and appends them to the trace list. Each trace represents
        the frequency of imprisonment over years for a specific sentence length group.
        The traces are then added to the figure for visualisation.

        Assumes:
            - self.df: pandas DataFrame containing at least 'pfa', 'sentence_length', 'year',
            and 'freq' columns.
            - self.pfa: The selected PFA to filter the DataFrame.
            - self.trace_list: List to which the generated traces are appended.
            - self.fig: Plotly Figure object to which the traces are added.

        Returns:
            None
        """
        pfa_df = self.df[self.df["pfa"] == self.pfa]

        for i in pfa_df["sentence_length"].unique():
            self.pfa_df_sentence = pfa_df[pfa_df["sentence_length"] == i]

            trace = go.Scatter(
                x=self.pfa_df_sentence["year"],
                y=self.pfa_df_sentence["freq"],
                mode="lines",
                name=str(self.pfa_df_sentence["sentence_length"].iloc[0]),
                meta=self.pfa_df_sentence["pfa"].iloc[0],
                hovertemplate="%{y}<extra></extra>"
            )
            self.trace_list.append(trace)

        self.fig.add_traces(self.trace_list)

    def chart_params(self):
        """
        Configures the layout parameters for the chart.

        This method sets the chart's title, margins, axis formatting, tick intervals,
        hover mode, and figure dimensions using Plotly's `update_layout` method.
        The title is dynamically generated based on the PFA name from the dataframe
        and wrapped for better display.

        Returns:
            None
        """

        self.fig.update_layout(
            margin=dict(l=63, b=75, r=100),
            title="<br>".join(title),
            yaxis_title="",
            yaxis_tickformat=",.0f",
            yaxis_tick0=0,
            xaxis_dtick=2,
            xaxis_tick0=2010,
            hovermode="x",
            width=655,
            height=360,
        )

    def chart_annotations(self):
        """
        Adds and adjusts annotations for a Plotly chart to label traces and
        provide source information.
        This method:
        - Iterates over all traces in the figure and appends a corresponding annotation for each,
          positioning the label at the last data point of each trace.
        - Optionally adjusts the vertical position of specific annotations
        based on `self.adjust` and `self.label_idx`.
          - If both are lists, applies each adjustment to the corresponding label index.
          - If `self.adjust` is a single value, applies it to the annotation at `self.label_idx`.
        - Sets the y-position of the second annotation to zero.
        - Adds a source annotation using `prt_theme.source_annotation`.
        - Appends an additional annotation above the chart for context.
        - Updates the figure layout with the complete list of annotations.

        Assumes the following instance attributes exist:
        - self.fig: Plotly Figure object.
        - self.trace_list: List of traces in the figure.
        - self.annotations: List to store annotation dictionaries.
        - self.label_idx: Index or list of indices for labels to adjust.
        - self.adjust: Adjustment value(s) for annotation y-positions.
        - self.df: DataFrame containing at least a 'year' column.
        """
        print(f"Label index: {self.label_idx}, Adjustment: {self.adjust}")

        for j in range(0, len(self.trace_list)):
            self.annotations.append(
                dict(
                    xref="x",
                    yref="y",
                    x=self.fig.data[j].x[-1],
                    y=self.fig.data[j].y[-1],
                    text=str(self.fig.data[j].name),
                    xanchor="left",
                    yanchor="bottom",
                    align="left",
                    showarrow=False,
                    font_color=self.fig.layout.template.layout.colorway[j],
                    font_size=10,
                )
            )

        if isinstance(self.adjust, list) and isinstance(self.label_idx, list):
            print("Applying adjustment for multiple label indices and adjustments...")
            for idx, adjust in zip(self.label_idx, self.adjust):
                self.annotations[idx]['y'] += int(adjust)

        elif self.adjust != 0:
            print("Applying adjustment...")
            self.annotations[self.label_idx]['y'] += int(self.adjust)

        self.annotations[1]['y'] = 0
        # TODO: Replace with add_annotation() and updated logic
        prt_theme.source_annotation("Ministry of Justice, Criminal justice statistics", self.annotations)

        self.annotations.append(
            dict(
                xref="x",
                yref="paper",
                x=self.df['year'].iloc[0],
                y=1.04,
                align="left",
                xanchor="left",
                showarrow=False,
                text="Women sentenced to custody",
                font_size=12,
            )
        )

        self.fig.update_layout(annotations=self.annotations)

    def set_y_axis(self):
        """
        Sets the y-axis range for the figure based on the maximum y-value across all traces.
        Finds the maximum y-value among all data traces in the figure, then selects an appropriate
        upper bound for the y-axis from a predefined list of intervals. Updates the y-axis
        and x-axis ranges accordingly.

        Returns:
            None
        """
        for i in range(len(self.fig.data)):
            max_trace = (self.fig.data[i].y).max()
            if max_trace > self.max_y_val:
                self.max_y_val = max_trace

        y_intervals = [52, 103, 210, 305, 405, 606, 1210]
        y_max_idx = min(range(len(y_intervals)), key=lambda i: abs(y_intervals[i] - self.max_y_val))
        y_max = y_intervals[y_max_idx + 1] if y_intervals[y_max_idx] <= self.max_y_val else y_intervals[y_max_idx]

        self.fig.update_yaxes(range=[0, y_max])
        # TODO: Replace this with a dynamic date range based on the data
        self.fig.update_xaxes(range=[2009.7, 2022.3])

    def _prepare_chart(self):
        """
        Prepares the chart for visualization by initialising and configuring chart components
        if no traces exist.

        This method checks if the trace list is empty. If so, it sequentially:
            - Breaks trace labels for better readability.
            - Creates the necessary chart traces.
            - Sets chart parameters.
            - Adds chart annotations.
            - Configures the y-axis.

        Intended to be called before rendering or updating the chart to ensure all components are
        properly set up.
        """
        if not self.trace_list:
            self.break_trace_labels()
            self.create_traces()
            self.chart_params()
            self.chart_annotations()
            self.set_y_axis()

    def save_chart(self, folder: str, filetype: str):
        """
        Saves the current chart to a specified folder and file type.

        This method prepares the chart and exports it as an image file to the designated
        output directory. The output path is constructed using the current working directory,
        a configured output path, the specified folder, and file type. The filename is derived
        from the first value in the 'pfa' column of the 'pfa_df_sentence' DataFrame.

        Args:
            folder (str): The name of the folder where the chart will be saved.
            filetype (str): The file type/extension for the saved chart (e.g., 'png', 'jpg', 'svg').

        Raises:
            Any exceptions raised by Path operations or self.fig.write_image will propagate.
        """
        self._prepare_chart()
        self.filetype = filetype
        self.folder = folder
        self.filetype = filetype

        export_path = Path.joinpath(Path.cwd(), f"{config['data']['outPath']}", f"{self.folder}/{self.filetype}")
        export_path.mkdir(parents=True, exist_ok=True)

        filename = str(self.pfa_df_sentence["pfa"].iloc[0])
        export_path = Path.joinpath(export_path, f'{filename}.{self.filetype}')

        self.fig.write_image(export_path)
        print(f"Chart saved to: {export_path}")

    def output_chart(self) -> None:
        """
        Generates and displays the prepared chart.

        This method prepares the chart by calling the internal _prepare_chart method,
        and then displays the resulting figure using the fig.show() method.
        """
        self._prepare_chart()
        self.fig.show()

class Record:
    """Hold a record of PFAs which require some manual adjustment of trace labels.

    Parameters:
        pfa_name (str): The name of the PFA.
        label_idx (Union[int, List[int]]): The index of the annotation in the chart that needs adjustment. Should be an integer or a list of integers containing only the values 0 and 2.
        adjust (Union[int, List[int]]): The adjustment value to be applied to the annotation from its existing position. Should be an integer or a list of integers.

    Raises:
        ValueError: If label_idx and adjust are not both integers or both lists, or if label_idx contains values other than 0 and 2.

    Attributes:
        pfa_name (str): The name of the PFA.
        label_idx (Union[int, List[int]]): The index of the annotation in the chart that needs adjustment.
        adjust (Union[int, List[int]]): The adjustment value to be applied to the annotation from its existing position.
    """
    def __init__(self, pfa_name, label_idx, adjust):
        self.pfa_name = pfa_name
        if isinstance(label_idx, int) and isinstance(adjust, int):
            if label_idx not in [0, 2]:
                raise ValueError("label_idx must be 0 or 2.")
            self.label_idx = label_idx
            self.adjust = adjust
        elif isinstance(label_idx, list) and isinstance(adjust, list):
            if any(idx not in [0, 2] for idx in label_idx):
                raise ValueError("Values in label_idx list must be 0 or 2.")
            self.label_idx = label_idx
            self.adjust = adjust
        else:
            raise ValueError("label_idx and adjust must both be integers or both be lists of integers.")

    def __repr__(self) -> str:
        return f'{self.pfa_name} PFA adjustment'


def make_pfa_sentence_length_charts(
        filename: str,
        folder: str,
        status='interim',
        output: str = 'save',
        filetype: str = 'emf',
        pfa_adjustments: Optional[List[Record]] = None):
    """
    Generates and outputs sentence length charts for each PFA (Police Force Area) in the provided dataset.

    Parameters:
        filename (str): The name of the data file to load.
        folder (str): The directory where charts will be saved if output is set to 'save'.
        status (str, optional): The data status to use when loading data (e.g., 'interim', 'final'). Defaults to 'interim'.
        output (str, optional): Determines whether to save charts to disk ('save') or display them ('show'). Defaults to 'save'.
        filetype (str, optional): The file type for saving charts (e.g., 'emf', 'png'). Defaults to 'emf'.
        pfa_adjustments (Optional[List[Record]], optional): A list of adjustment records for specific PFAs. Each record should have attributes 'pfa_name', 'label_idx', and 'adjust'. Defaults to None.

    Raises:
        ValueError: If the 'output' parameter is not 'save' or 'show'.

    Side Effects:
        - Saves or displays sentence length charts for each unique PFA in the dataset.
        - Prints "Charts ready" upon completion.
    """
    df = utils.load_data(status, filename)
    for pfa in df['pfa'].unique():
        adjusted = False
        if pfa_adjustments:
            for adjustment in pfa_adjustments:
                if pfa == adjustment.pfa_name:
                    chart = SentenceLengthChart(
                        pfa=adjustment.pfa_name,
                        df=df,
                        label_idx=adjustment.label_idx,
                        adjust=adjustment.adjust
                        )
                    adjusted = True
                    break
        if not adjusted:
            chart = SentenceLengthChart(pfa, df)
        if output == 'save':
            chart.save_chart(folder, filetype)
        elif output == 'show':
            chart.output_chart()
        else:
            raise ValueError("output must be 'save' or 'show'.")
    print("Charts ready")


if __name__ == "__main__":
    filename = 'women_cust_sentence_length_PFA_2010-2022.csv'
    folder = '1.custody_sentence_lengths_2022'
    filetype = 'pdf'

    pfa_adjustments = [
        Record('Cambridgeshire', 0, 18),
        Record('Dorset', 2, 5),
        Record('Cumbria', 0, 7),
        Record('Derbyshire', 0, 15),
        Record('Dyfed-Powys', 0, 10),
        Record('Gloucestershire', 0, -2),
        Record('Gwent', [0, 2], [17, 12]),
        Record('Lancashire', 2, 20),
        Record('Merseyside', 2, -10),
        Record('North Yorkshire', 0, 7),
        Record('Northumbria', 0, -10),
        Record('South Yorkshire', 0, -10),
        Record('Suffolk', 0, 8),
        Record('Surrey', [0, 2], [7, 12]),
        Record('Sussex', 2, 20),
        Record('West Mercia', 2, 10),
        Record('West Midlands', 0, 50)]

    make_pfa_sentence_length_charts(filename, folder, filetype=filetype, pfa_adjustments=pfa_adjustments)