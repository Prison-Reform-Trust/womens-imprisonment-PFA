# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is part of the data visualisation pipeline for the Criminal Justice System
statistics quarterly: December 2024 Outcomes by Offence dataset.

It provides a sunburst chart for each Police Force Area (PFA) to show the number of women
who received a custodial sentence in 2024, broken down by offence group.
"""

import logging
import textwrap
from typing import List

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

    def __init__(self, pfa: str, df: pd.DataFrame):
        self.pfa = pfa
        self.df = df
        self.trace_list = []
        self.annotations: list[dict] = []
        self.fig = go.Figure()

    # NOTE: Currently here. Trying to unpick trace creation.
    def create_traces(self):
        self.df = self.df[self.df["pfa"] == self.pfa]
        self.df = pd.concat([
            self.df,
            pd.DataFrame.from_records([{
                'pfa': self.df['pfa'].iloc[0],
                'offence': "All other<br>offences",
                'proportion': self.df.loc[not filter_offences(self.df), 'proportion'].sum(),
                'parent': "All offences",
                'plot_order': 0
            }])
        ], ignore_index=True).sort_values(by=['plot_order', 'proportion'], ascending=True)

        sunburst_trace = go.Sunburst(
            labels=self.df['offence'],
            parents=self.df['parent'],
            values=self.df['proportion'],
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

        return self.fig.add_trace(sunburst_trace)

    def chart_params(self):
        title = textwrap.wrap(f'<b>Imprisonment of women in {self.df["pfa"].iloc[0]} by offence group in 2022</b>',
                              width=45)

        self.fig.update_layout(
            margin=dict(t=75, l=0, r=0, b=0),
            title="<br>".join(title),
            title_y=0.94,
            title_yanchor="bottom",
            width=630,
            height=630,
        )

    def chart_annotations(self):
        # Adding source label
        self.annotations.append(
            dict(
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                x=0.05,
                y=0.07,
                showarrow=False,
                text=f"Source: Ministry of Justice, Criminal justice statistics",
                font_size=12,
            )
        )

        # Adding annotations to layout
        return self.fig.update_layout(annotations=self.annotations)

    def save_chart(self, folder: str, filetype: str = 'pdf'):
        self.filetype = filetype
        self.folder = folder

        if not self.trace_list:
            self.prepare_data()
            self.create_traces()
            self.chart_params()
            self.chart_annotations()

        export_path = Path.joinpath(Path.cwd(), f"{config['data']['outPath']}", f"{self.folder}/{self.filetype}")
        export_path.mkdir(parents=True, exist_ok=True)

        filename = str(self.df["pfa"].iloc[0])
        export_path = Path.joinpath(export_path, f'{filename}.{self.filetype}')

        self.fig.write_image(export_path)

    def output_chart(self):
        self.create_traces()
        self.chart_params()
        self.chart_annotations()
        self.fig.show()


def make_pfa_offences_charts(filename: str, folder: str, status: str = 'processed', filetype: str = 'pdf'):
    df = utils.load_data(filename, status)
    for pfa in df['pfa'].unique():
        chart = PfaOffencesChart(pfa, df)
        chart.save_chart(folder, filetype)
    print("Charts ready")


def main():
    """
    Main function to produce all visualisations for the fact sheets.
    """
    # make_pfa_offences_charts(INPUT_FILENAME, OUTPUT_PATH)


if __name__ == "__main__":
    main()
