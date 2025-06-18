# !/usr/bin/env python3
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

import logging
from typing import List, Optional

import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio

from src import utilities as utils
from src.visualization import prt_theme

utils.setup_logging()

config = utils.read_config()
pio.templates.default = "prt_template"

INPUT_FILENAME = config['data']['datasetFilenames']['filter_sentence_length']
OUTPUT_PATH = config['viz']['filePaths']['custody_sentence_lengths']


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
        pfa_df (pd.DataFrame): A filtered DataFrame showing data for the pfa.
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
        self.pfa_df = self.df[self.df["pfa"] == self.pfa]
        self.label_idx = label_idx
        self.adjust = adjust
        self.trace_list: List[go.Scatter] = []
        self.annotations: list[dict] = []
        self.fig = go.Figure()
        self.pfa_df_sentence = pd.DataFrame()
        self.max_y_val = 0

    def create_traces(self):
        """
        Generates Plotly Scatter traces for each unique sentence length group within the selected
        PFA (Police Force Area) and appends them to the trace list. Each trace represents
        the frequency of imprisonment over years for a specific sentence length group.
        The traces are then added to the figure for visualisation.

        Assumes:
            - self.df: pandas DataFrame containing at least 'pfa', 'sentence_len', 'year',
            and 'freq' columns.
            - self.pfa: The selected PFA to filter the DataFrame.
            - self.trace_list: List to which the generated traces are appended.
            - self.fig: Plotly Figure object to which the traces are added.

        Returns:
            None
        """

        for i in self.pfa_df["sentence_len"].unique():
            self.pfa_df_sentence = self.pfa_df[self.pfa_df["sentence_len"] == i]

            trace = go.Scatter(
                x=self.pfa_df_sentence["year"],
                y=self.pfa_df_sentence["freq"],
                mode="lines",
                name=str(self.pfa_df_sentence["sentence_len"].iloc[0]),
                meta=self.pfa_df_sentence["pfa"].iloc[0],
                hovertemplate="%{y}<extra></extra>"
            )
            self.trace_list.append(trace)

        self.fig.add_traces(self.trace_list)

    def chart_params(self):
        """
        Configures the layout parameters for the chart.

        This method sets the chart's layout and axis formatting in addition to
        the default template values, using Plotly's `update_layout` method.

        Returns:
            None
        """
        min_year, _ = utils.get_year_range(self.pfa_df)

        self.fig.update_layout(
            yaxis_title="",
            yaxis_tickformat=",.0f",
            yaxis_tick0=0,
            xaxis_dtick=2,
            xaxis_tick0=min_year,
            hovermode="x",
        )

    def set_trace_labels(self):
        # NOTE: This method may be able to be replaced with prt_theme.add_annotation
        # However, it is important to refactor the other methods that use it to set
        # source and y-axis labels. This requires assignment of the annotations to self.annotations
        # see sentence_types.py for example
        """
        Adds annotation labels to the end of each trace in the plotly figure.

        This method iterates over all traces in `self.trace_list` and appends an annotation
        for each, positioning the label at the last data point of the trace. The label text
        is set to the trace's name, and the color is taken from the figure's colorway.

        If `self.adjust` and `self.label_idx` are lists, applies a vertical adjustment to the
        y-position of each specified label index. If `self.adjust` is a single value, applies
        the adjustment to the label at `self.label_idx`.

        Additionally, sets the y-position of the annotation at index 1 to 0.

        Logging is used to provide information about the labeling and adjustment process.
        """
        logging.info("Setting trace labels...")
        logging.info("Label index: %s, Adjustment: %s", self.label_idx, self.adjust)

        for i, trace in enumerate(self.trace_list):
            self.annotations.append(
                dict(
                    xref="x",
                    yref="y",
                    x=trace.x[-1],
                    y=trace.y[-1],
                    text=str(trace.name),
                    xanchor="left",
                    yanchor="bottom",
                    align="left",
                    showarrow=False,
                    font_color=self.fig.layout.template.layout.colorway[i],
                    font_size=10,
                )
            )

        if isinstance(self.adjust, list) and isinstance(self.label_idx, list):
            logging.info("Applying adjustment for multiple label indices and adjustments...")
            for idx, adjust in zip(self.label_idx, self.adjust):
                self.annotations[idx]['y'] += int(adjust)

        elif self.adjust != 0:
            logging.info("Applying adjustment...")
            self.annotations[self.label_idx]['y'] += int(self.adjust)

        # NOTE: Check whether this is still needed
        self.annotations[1]['y'] = 0

    def set_title(self):
        """
        Sets the chart title to reflect the use of immediate imprisonment for women in a specific PFA
        (Police Force Area) over a range of years. The title is dynamically generated based on the
        PFA name and the minimum and maximum years present in the data.
        The title is then added to the chart using the prt_theme.add_title method.

        Returns:
            None
        """

        min_year, max_year = utils.get_year_range(self.pfa_df)
        title = (
            f'Use of immediate imprisonment for women '
            f'{self.pfa_df_sentence["pfa"].iloc[0]}, {min_year}—{max_year}'
        )
        prt_theme.add_title(
            self.fig,
            title=title,
            width=40
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
        prt_theme.add_annotation(
            self.annotations,
            text="Ministry of Justice, Criminal justice statistics",
            annotation_type="source",
        )

    def set_yaxis_label(self):
        """
        Adds a y-axis annotation to the chart indicating that the axis represents the number of
        women sentenced to custody.

        This method uses the `prt_theme.add_annotation` function to append an annotation to the chart's
        annotations list, specifying the label text and annotation type for the y-axis.
        """
        prt_theme.add_annotation(
            self.annotations,
            text="Women sentenced to custody",
            annotation_type="y-axis",
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
        self.set_trace_labels()
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

        y_intervals = [52, 101, 203, 305, 405, 606, 1210]
        y_max_idx = min(range(len(y_intervals)), key=lambda i: abs(y_intervals[i] - self.max_y_val))
        y_max = y_intervals[y_max_idx + 1] if y_intervals[y_max_idx] <= self.max_y_val else y_intervals[y_max_idx]

        self.fig.update_yaxes(range=[0, y_max])

        min_year, max_year = utils.get_year_range(self.pfa_df)
        xaxis_range = [min_year - 0.3, max_year + 0.3]
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
        self.fig.show()


class Record:
    """
    A class representing a record for a PFA (Police Force Area) adjustment.

    Attributes:
        pfa_name (str): The name of the PFA.
        label_idx (int or list of int): The label index or indices.
        Must be 0 or 2, or a list containing only 0 and/or 2.
        adjust (int or list of int): The adjustment value(s).
        Must be an integer if label_idx is an integer, or a list of integers if label_idx is a list.

    Raises:
        ValueError: If label_idx and adjust are not both integers or both lists of integers.
        ValueError: If label_idx is an integer and not 0 or 2.
        ValueError: If label_idx is a list and contains values other than 0 or 2.

    Methods:
        __repr__(): Returns a string representation of the record.
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


def break_trace_labels(df):
    """
    Renames the categories of the 'sentence_len' column in the DataFrame to improve
    label formatting for visualisation.
    """
    if 'sentence_len' in df.columns and hasattr(df['sentence_len'], 'cat'):
        df['sentence_len'] = df['sentence_len'].cat.rename_categories(
            {'6 months to less than 12 months': '6 months—<br>less than 12 months'})
    return df


def generate_sentence_len_chart(
    df: pd.DataFrame,
    path: str,
    output: str = 'save',
    filetype: str = 'emf',
    pfa: Optional[str] = None,
    pfa_adjustments: Optional[List[Record]] = None
):
    """
    Generates and outputs sentence length charts for one or all PFAs.

    If pfa is provided, only that PFA is processed.
    """
    pfas = [pfa] if pfa else df['pfa'].unique()
    for pfa_name in pfas:
        adjusted = False
        if pfa_adjustments:
            for adjustment in pfa_adjustments:
                if pfa_name == adjustment.pfa_name:
                    chart = SentenceLengthChart(
                        pfa=adjustment.pfa_name,
                        df=df,
                        label_idx=adjustment.label_idx,
                        adjust=adjustment.adjust
                    )
                    adjusted = True
                    break
        if not adjusted:
            chart = SentenceLengthChart(pfa_name, df)
        if output == 'save':
            chart.save_chart(path, filetype)
        elif output == 'show':
            chart.output_chart()
        else:
            raise ValueError("output must be 'save' or 'show'.")
    logging.info("Charts ready")


def make_pfa_sentence_len_charts(
        filename: str,
        path: str,
        status='processed',
        output: str = 'save',
        filetype: str = 'emf',
        pfa_adjustments: Optional[List[Record]] = None,
        pfa: Optional[str] = None):
    """
    Generates and outputs sentence length charts for each (or a single) PFA.
    """
    df = (
        utils.load_data(status, filename)
        .pipe(break_trace_labels)
    )
    generate_sentence_len_chart(
        df=df,
        path=path,
        output=output,
        filetype=filetype,
        pfa=pfa,
        pfa_adjustments=pfa_adjustments
    )


def test_chart(pfa: str = 'Gwent', pfa_adjustments: Optional[List[Record]] = None):
    """
    Test function to generate and display a sample chart for a specific PFA,
    with optional PFA adjustments.
    """
    make_pfa_sentence_len_charts(
        filename=INPUT_FILENAME,
        path=OUTPUT_PATH,
        status="processed",
        output="save",
        filetype="pdf",
        pfa=pfa,
        pfa_adjustments=pfa_adjustments
    )


def main():
    """
    Main function to execute the chart generation process.

    This function calls the make_pfa_sentence_len_charts function with predefined parameters
    to generate and save sentence length charts for each PFA in the dataset.
    """
    make_pfa_sentence_len_charts(
        filename=INPUT_FILENAME,
        path=OUTPUT_PATH,
        filetype='pdf',
        pfa_adjustments=None,
    )


if __name__ == "__main__":
    FILETYPE = 'pdf'

    PFA_ADJUSTMENTS = [
        Record('Cambridgeshire', 2, 10),
        Record('Cumbria', 2, 2),
        Record('Derbyshire', 2, 10),
        Record('Durham', 2, 5),
        Record('Northamptonshire', 2, 3),
        Record('Suffolk', 2, -2),
        Record('Surrey', [0, 2], [4, 2]),
        Record('Warwickshire', 0, 7)]

    make_pfa_sentence_len_charts(
        filename=INPUT_FILENAME,
        path=OUTPUT_PATH,
        filetype=FILETYPE,
        pfa_adjustments=PFA_ADJUSTMENTS
        )
