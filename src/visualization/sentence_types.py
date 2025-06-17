# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is part of the data visualisation pipeline for the Criminal Justice System
statistics quarterly: December 2024 Outcomes by Offence dataset.

It provides a standardised column chart for each Police Force Area (PFA) to show:
    * The number of women who received a:
        - Community sentence
        - Suspended sentence
        - Sentence of immediate custody
"""

import logging
from typing import List

import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio

from src import utilities as utils
from src.visualization import prt_theme

utils.setup_logging()

config = utils.read_config()
pio.templates.default = "prt_template"

INPUT_FILENAME = config['data']['datasetFilenames']['group_pfa_sentence_outcome']
OUTPUT_PATH = config['viz']['filePaths']['sentence_types']


class SentenceTypeChart:
    """
    A class for generating and visualizing bar charts of women's sentencing outcomes by year and Police Force Area (PFA).
    Attributes:
        pfa (str): The Police Force Area to filter data for.
        df (pd.DataFrame): The input DataFrame containing sentencing data.
        pfa_df (pd.DataFrame): A filtered DataFrame showing data for the pfa.
        trace_list (List[go.Bar]): List of Plotly Bar traces for each outcome.
        annotations (list[dict]): List of annotation dictionaries for the chart.
        max_y_val (int): Maximum y-axis value across all traces.
        fig (go.Figure): The Plotly Figure object for the chart.
        pfa_df_sentence (pd.DataFrame): DataFrame filtered for the current PFA and sentence type.
    Methods:
        __init__(pfa: str, df: pd.DataFrame):
            Initializes the chart with a PFA and DataFrame.
        create_traces():
            Creates Plotly Bar traces for each unique sentencing outcome in the selected PFA.
        chart_params():
            Sets layout parameters for the chart, including title, margins, axes, and legend.
        chart_annotations():
            Adds source and y-axis label annotations to the chart.
        set_yaxis():
            Sets the y-axis and x-axis ranges based on data and predefined intervals.
        _prepare_chart():
            Internal method to ensure traces, layout, and annotations are prepared before output or saving.
        save_chart(folder: str, filetype: str = 'pdf'):
            Saves the chart as an image file (default PDF) in the specified folder.
        output_chart() -> None:
            Displays the chart in an interactive window.
    """

    def __init__(self, pfa: str, df: pd.DataFrame):
        self.pfa = pfa
        self.df = df
        self.pfa_df = self.df[self.df["pfa"] == self.pfa]
        self.trace_list: List[go.Bar] = []
        self.annotations: list[dict] = []
        self.max_y_val = 0
        self.fig = go.Figure()
        self.pfa_df_sentence = pd.DataFrame()

    def create_traces(self):
        """
        Generates bar chart traces for each unique outcome in the DataFrame filtered by the specified 'pfa' value.
        This method filters the main DataFrame (`self.df`) to include only rows where the 'pfa' column matches `self.pfa`.
        For each unique value in the 'outcome' column, it creates a Plotly Bar trace representing the frequency ('freq')
        of that outcome per year. The traces are appended to `self.trace_list` and then added to the figure (`self.fig`).
        The hover template displays the frequency and the outcome (in lowercase) for each bar.
        Side Effects:
            - Modifies `self.trace_list` by appending new traces.
            - Adds all traces in `self.trace_list` to `self.fig`.
        Returns:
            None
        """

        for i in self.df["outcome"].unique():  # Creating a for loop to extract unique values from the dataframe and make traces
            self.pfa_df_sentence = self.pfa_df[self.pfa_df["outcome"] == i]

            trace = go.Bar(
                x=self.pfa_df_sentence["year"],
                y=self.pfa_df_sentence["freq"],
                name=str(self.pfa_df_sentence["outcome"].iloc[0]),
                customdata=self.pfa_df_sentence["outcome"].str.lower(),
                hovertemplate="%{y} %{customdata}<extra></extra>",
            )

            self.trace_list.append(trace)

        self.fig.add_traces(self.trace_list)

    def chart_params(self):
        """
        Updates the layout parameters of the chart figure for grouped bar mode and customizes axis ticks, legend position, and hover behaviour.

        This method sets:
        - Bar mode to "group" for grouped bar charts.
        - Y-axis to start at 0 and formats tick labels with comma separators and no decimals.
        - X-axis ticks to increment by 2, starting at 2010.
        - Legend to be shown above the chart, anchored to the top-right.
        - Hover mode to "x" for displaying data across all traces at a given x-value.

        Assumes `self.fig` is a Plotly figure object.
        Returns:
            None
        """

        self.fig.update_layout(
            margin=dict(r=20),
            barmode="group",
            yaxis_tick0=0,
            yaxis_tickformat=",.0f",
            xaxis_dtick=2,
            xaxis_tick0=2010,
            showlegend=True,
            hovermode="x",
            legend=dict(
                yanchor="top",
                y=1.05,
                xanchor="right",
                x=1,
            )
        )

    def set_title(self):
        """
        Sets the chart title to reflect the use of sentences for women in a specific PFA
        (Police Force Area) over a range of years. The title is dynamically generated based on the
        PFA name and the minimum and maximum years present in the data.
        The title is then added to the chart using the prt_theme.add_title method.

        Returns:
            None
        """

        min_year, max_year = utils.get_year_range(self.pfa_df)
        title = (
            f'Sentencing of women in<br>'
            f'{self.pfa_df_sentence["pfa"].iloc[0]}, {min_year}—{max_year}'
        )
        logging.info("Setting title...")
        prt_theme.add_title(
            self.fig,
            title=title,
            width=70
        )

    def set_source(self):
        """
        Adds a source annotation to the chart using the prt_theme's add_annotation method.
        The annotation specifies "Ministry of Justice, Criminal justice statistics" as the data source
        and sets the annotation type to "source".
        Returns:
            None
        """
        logging.info("Setting source annotation...")
        self.annotations = (
            prt_theme.add_annotation(
                self.annotations,
                text="Ministry of Justice, Criminal justice statistics",
                annotation_type="source",
            )
        )

    def set_yaxis_label(self):
        """
        Adds a y-axis annotation to the chart indicating that the axis represents the number of
        women sentenced.

        This method uses the `prt_theme.add_annotation` function to append an annotation to the chart's
        annotations list, specifying the label text and annotation type for the y-axis.
        """
        logging.info("Setting y-axis annotation...")
        self.annotations = (
            prt_theme.add_annotation(
                self.annotations,
                text="Women sentenced",
                annotation_type="y-axis",
            )
        )

    def chart_annotations(self):
        """
        Adds annotations and labels to the chart.

        This method performs the following actions:
        - Sets trace labels for the chart.
        - Sets the chart title.
        - Adds a source annotation.
        - Sets the y-axis label.
        - Updates the figure layout with the collected annotations.

        Logs the process at the start and upon successful completion.
        """
        logging.info("Adding chart annotations...")
        self.set_title()
        self.set_source()
        self.set_yaxis_label()

        self.fig.update_layout(annotations=self.annotations)
        logging.info("Annotations added successfully.")

    def set_axes(self):
        """
        Sets the y-axis range for the figure based on the maximum y-value across all traces.
        Finds the maximum y-value among all data traces in the figure, then selects an appropriate
        upper bound for the y-axis from a predefined list of intervals.

        Also determines the x-axis range based on the minimum and maximum years present in the data.

        Updates the y-axis and x-axis ranges accordingly.

        Returns:
            None
        """

        for _, data in enumerate(self.fig.data):
            max_trace = (data.y).max()
            self.max_y_val = max(self.max_y_val, max_trace)

        y_intervals = [52, 101, 203, 305, 405, 540, 606, 830, 909, 1210, 1550, 2080, 3100]
        y_max_idx = min(range(len(y_intervals)), key=lambda i: abs(y_intervals[i] - self.max_y_val))
        y_max = y_intervals[y_max_idx + 1] if y_intervals[y_max_idx] <= self.max_y_val else y_intervals[y_max_idx]

        self.fig.update_yaxes(range=[0, y_max])

        min_year, max_year = utils.get_year_range(self.pfa_df)
        xaxis_range = [min_year - 0.5, max_year + 0.5]
        self.fig.update_xaxes(range=xaxis_range)

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
            self.create_traces()
            self.chart_params()
            self.chart_annotations()
            self.set_axes()

    def save_chart(self, path: str, filetype: str):
        """
        Saves the current chart to a specified path and file type.

        This method prepares the chart and exports it as an image file to the designated
        output directory. The output path is constructed using the current working directory,
        a configured output path, the specified folder, and file type. The filename is derived
        from the first value in the 'pfa' column of the 'pfa_df_sentence' DataFrame.

        Args:
            path (str): The name of the folder where the chart will be saved.
            filetype (str): The file type/extension for the saved chart (e.g., 'png', 'jpg', 'svg').

        Raises:
            Any exceptions raised by Path operations or self.fig.write_image will propagate.
        """
        self._prepare_chart()

        filename = f"{self.pfa_df_sentence['pfa'].iloc[0]}.{filetype}"
        path = config['data']['outPath'] + path

        utils.safe_save_chart(
            fig=self.fig,
            path=path,
            filename=filename,
        )

    def output_chart(self) -> None:
        """
        Generates and displays the prepared chart.

        This method prepares the chart by calling the internal _prepare_chart method,
        and then displays the resulting figure using the fig.show() method.
        """
        self._prepare_chart()
        return self.fig.show()


def make_pfa_sentence_type_charts(
        filename: str,
        path: str,
        status='processed',
        output: str = 'save',
        filetype: str = 'emf'):
    """
    Generates and outputs sentence type charts for each unique PFA in the dataset.
    Parameters:
        filename (str): Name of the data file to load.
        path (str): Directory path where charts will be saved if output is 'save'.
        status (str, optional): Status of the data to load (default is 'processed').
        output (str, optional): Determines whether to save ('save') or display ('show') the charts (default is 'save').
        filetype (str, optional): File type for saving charts (default is 'emf').
    Raises:
        ValueError: If the output parameter is not 'save' or 'show'.
    Side Effects:
        Saves or displays charts for each unique PFA in the dataset.
        Logs a message when charts are ready.
    """

    df = utils.load_data(status, filename)
    for pfa in df['pfa'].unique():
        chart = SentenceTypeChart(pfa, df)
        if output == 'save':
            chart.save_chart(path, filetype)
        elif output == 'show':
            chart.output_chart()
        else:
            raise ValueError("output must be 'save' or 'show'.")
    logging.info("Charts ready")


def test_chart(pfa: str = 'Gwent'):
    """
    Test function to generate and display a sample chart for a specific PFA.

    This function creates a sample DataFrame with sentence length data for a specific PFA
    and generates a chart using the SentenceLengthChart class. It is intended for testing
    purposes to ensure that the chart generation works as expected.
    """
    df = utils.load_data("processed", INPUT_FILENAME)
    chart = SentenceTypeChart(pfa, df)
    chart.output_chart()
    # chart.save_chart(OUTPUT_PATH, 'pdf')


def main():
    """
    Main function to execute the chart generation process.

    This function calls the make_pfa_sentence_type_charts function with predefined parameters
    to generate and save sentence type charts for each PFA in the dataset.
    """
    make_pfa_sentence_type_charts(
        filename=INPUT_FILENAME,
        path=OUTPUT_PATH,
        filetype='pdf'
    )


if __name__ == "__main__":
    main()
