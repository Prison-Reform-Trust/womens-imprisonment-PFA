# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is part of the data visualisation pipeline for the Criminal Justice System
statistics quarterly: December 2024 Outcomes by Offence dataset.

It provides a sunburst chart for each Police Force Area (PFA) to show the number of women
who received a custodial sentence in 2024, broken down by offence group.
"""

import logging

import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio

from src import utilities as utils
from src.data.processing.filter_custody_offences import filter_offences
from src.visualization import prt_theme

utils.setup_logging()

config = utils.read_config()
pio.templates.default = "prt_template"

data_path = config['data']['clnFilePath']
filename_template = config['data']['datasetFilenames']['filter_custody_offences']
max_year = utils.get_latest_year_from_files(data_path, filename_template)

INPUT_FILENAME = filename_template.format(year=max_year)
OUTPUT_PATH = config['viz']['filePaths']['custody_offences']


class PfaOffencesChart:
    """
    PfaOffencesChart generates and manages a sunburst chart visualizing the proportion
    of women imprisoned by offence group for a specified Police Force Area (PFA).

    Attributes:
        pfa (str): The Police Force Area to visualize.
        df (pd.DataFrame): The input DataFrame containing offence data.
        pfa_df (pd.DataFrame): Filtered DataFrame for the selected PFA.
        annotations (list[dict]): List of annotation dictionaries for the chart.
        fig (go.Figure): Plotly Figure object for the chart.

    Methods:
        __init__(pfa: str, df: pd.DataFrame):
            Initializes the chart with a PFA and its corresponding data.

        create_traces():
            Creates and adds a sunburst trace to the figure, including aggregation
            of non-highlighted offences.

        chart_params():
            Sets chart layout parameters such as title, size, and margins.

        chart_annotations():
            Adds source and other annotations to the chart layout.

        save_chart(folder: str, filetype: str = 'pdf'):
            Saves the chart to a specified folder and file type (default: PDF).

        output_chart():
            Renders the chart in an interactive window.
    """

    def __init__(self, pfa: str, df: pd.DataFrame):
        self.pfa = pfa
        self.df = df
        self.pfa_df = self.df[self.df["pfa"] == self.pfa]
        self.annotations: list[dict] = []
        self.fig = go.Figure()

    def create_all_offences_group(self):
        """
        This method filters out the highlighted offences and aggregates the remaining offences
        into a single group. It then creates a new row in the DataFrame for "All other offences"
        with the sum of their proportions.
        """
        mask_filter = ~filter_offences(self.pfa_df)  # Filter out highlighted offences
        self.pfa_df = pd.concat([
            self.pfa_df,
            pd.DataFrame.from_records([{
                'pfa': self.pfa_df['pfa'].iloc[0],
                'offence': "All other offences",
                'proportion': self.pfa_df.loc[mask_filter, 'proportion'].sum(),
                'parent': "All offences",
                'plot_order': 0
            }])
        ], ignore_index=True).sort_values(by=['plot_order', 'proportion'], ascending=True)

    def create_traces(self, max_chars=16):
        """Creates a sunburst trace for the PFA offences chart, wrapping all labels and parents."""

        def wrap_series(series):
            return series.apply(lambda x: prt_theme.wrap_labels(x, max_chars=max_chars))

        wrapped_labels = wrap_series(self.pfa_df['offence'])
        wrapped_parents = wrap_series(self.pfa_df['parent'])

        sunburst_trace = go.Sunburst(
            labels=wrapped_labels,
            parents=wrapped_parents,
            values=self.pfa_df['proportion'],
            sort=False,
            branchvalues='total',
            texttemplate="%{label} <b>%{percentRoot: .0%}</b>",
            hovertemplate="<b>%{label}</b><br>%{percentParent: .0%} of %{parent}<extra></extra>",
            hoverinfo='label+percent parent',
            insidetextorientation='radial',
            rotation=300,
            domain_column=0,
            domain_row=0
        )

        self.fig.add_trace(sunburst_trace)

    def chart_params(self):
        """
        Configures the layout parameters for the chart.

        This method sets the chart's layout and size in addition to
        the default template values, using Plotly's `update_layout` method.

        Returns:
            None
        """
        self.fig.update_layout(
            margin=dict(t=75, l=0, r=0, b=0),
            width=630,
            height=630,
            uniformtext=dict(minsize=8, mode='hide')
        )

    def set_title(self):
        """
        Sets the chart title to reflect the proportion of women in a specific PFA
        (Police Force Area) who received a sentence of immediate imprisonment, by offence
        group, for the latest year available in the dataset.
        The title is dynamically generated based on the PFA name and the maximum
        year present in the data.
        The title is then added to the chart using the prt_theme.add_title method.

        Returns:
            None
        """

        title = (
            f'Imprisonment of women in {self.pfa_df["pfa"].iloc[0]}<br>'
            f'by offence group, {max_year}'
        )

        prt_theme.add_title(
            self.fig,
            title=title,
            wrap=False,
        )

    def set_source(self):
        """
        Adds a source annotation to the chart using the prt_theme's add_annotation method.
        The annotation specifies "Ministry of Justice, Criminal justice statistics" as the
        data source and sets the annotation type to "source".
        Returns:
            None
        """
        logging.info("Setting source annotation...")
        self.annotations = (
            prt_theme.add_annotation(
                self.annotations,
                text="Ministry of Justice, Criminal justice statistics",
                annotation_type="source",
                x=0.03,
                y=0.05,
            )
        )

    def chart_annotations(self):
        """
        Adds annotations and labels to the chart.

        This method performs the following actions:
        - Sets the chart title.
        - Adds a source annotation.

        - Updates the figure layout with the collected annotations.

        Logs the process at the start and upon successful completion.
        """
        logging.info("Adding chart annotations...")
        self.set_title()
        self.set_source()

        self.fig.update_layout(annotations=self.annotations)
        logging.info("Annotations added successfully.")

    def _prepare_chart(self):
        """
        Prepares the chart for visualization by initialising and configuring chart components
        if no traces exist.

        This method checks if the trace list is empty. If so, it sequentially:
            - Breaks trace labels for better readability.
            - Creates the necessary chart traces.
            - Sets chart parameters.
            - Adds chart annotations.

        Intended to be called before rendering or updating the chart to ensure all components are
        properly set up.
        """
        self.create_all_offences_group()
        self.create_traces()
        self.chart_params()
        self.chart_annotations()

    def save_chart(self, path: str, filetype: str):
        """
        Saves the current chart to a specified path and file type.

        This method prepares the chart and exports it as an image file to the designated
        output directory. The output path is constructed using the current working directory,
        a configured output path, the specified folder, and file type. The filename is derived
        from the first value in the 'pfa' column of the 'pfa_df' DataFrame.

        Args:
            path (str): The name of the folder where the chart will be saved.
            filetype (str): The file type/extension for the saved chart (e.g., 'png', 'jpg', 'svg').

        Raises:
            Any exceptions raised by Path operations or self.fig.write_image will propagate.
        """
        self._prepare_chart()

        filename = f"{self.pfa_df['pfa'].iloc[0]}.{filetype}"
        path = config['data']['outPath'] + path

        utils.safe_save_chart(
            fig=self.fig,
            path=path,
            filename=filename,
        )

    def output_chart(self) -> go.Figure:
        """
        Generates and returns the final chart figure.

        This method orchestrates the creation of chart traces, sets chart parameters,
        adds annotations, and returns the resulting Plotly figure object.

        Returns:
            plotly.graph_objs._figure.Figure: The generated chart figure.
        """
        self._prepare_chart()
        return self.fig


def make_pfa_offences_charts(
        filename: str,
        path: str,
        status='processed',
        output: str = 'save',
        filetype: str = 'emf'):
    """
    Generates and outputs offences charts for each unique PFA in the dataset.
    Parameters:
        filename (str): Name of the data file to load.
        path (str): Directory path where charts will be saved if output is 'save'.
        status (str, optional): Status of the data to load (default is 'processed').
        output (str, optional): Determines whether to save ('save') or display ('show')
        the charts (default is 'save').
        filetype (str, optional): File type for saving charts (default is 'emf').
    Raises:
        ValueError: If the output parameter is not 'save' or 'show'.
    Side Effects:
        Saves or displays charts for each unique PFA in the dataset.
        Logs a message when charts are ready.
    """

    df = utils.load_data(status, filename)
    for pfa in df['pfa'].unique():
        chart = PfaOffencesChart(pfa, df)
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
    chart = PfaOffencesChart(pfa, df)
    return chart.output_chart()
    # chart.save_chart(OUTPUT_PATH, 'pdf')


def dummy_chart():
    """
    Dummy function to create a chart with no data.
    This is used for testing purposes to ensure that the chart generation works without actual data.
    """
    df = pd.DataFrame({
        'pfa': ['Dummy PFA'],
        'offence': ['Dummy Offence'],
        'proportion': [0.5],
        'parent': ['All offences'],
        'plot_order': [0]
    })
    chart = PfaOffencesChart('Dummy PFA', df)
    return chart.output_chart()


def main():
    """
    Main function to produce all visualisations for the fact sheets.
    """
    make_pfa_offences_charts(
        filename=INPUT_FILENAME,
        path=OUTPUT_PATH,
        filetype='pdf'
    )


if __name__ == "__main__":
    main()
