##!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import textwrap # type: ignore
import plotly.graph_objs as go
import plotly.io as pio
from plotly.graph_objs import Figure
from typing import List # type: ignore
from pathlib import Path # type: ignore

from src.data import utilities as utils
from src.visualization import prt_theme

config = utils.read_config()
pio.templates.default = "prt_template"

class SentenceTypeChart:
    
    def __init__(self, pfa: str, df: pd.DataFrame):
        self.pfa = pfa
        self.df = df
        self.trace_list: List[go.Bar] = []
        self.annotations: list[dict] = []
        self.max_y_val = 0
        self.fig = go.Figure()

    def create_traces(self):
        pfa_df = self.df[self.df["pfa"] == self.pfa]

        for i in self.df["outcome"].unique():  # Creating a for loop to extract unique values from the dataframe and make traces
            self.pfa_df_outcome = pfa_df[pfa_df["outcome"] == i]
            
            trace = go.Bar(
                x=self.pfa_df_outcome["year"],
                y=self.pfa_df_outcome["freq"],
                name=str(self.pfa_df_outcome["outcome"].iloc[0]),
                customdata=self.pfa_df_outcome["outcome"].str.lower(),
                hovertemplate="%{y} %{customdata}<extra></extra>",
            )

            self.trace_list.append(trace)

        self.fig.add_traces(self.trace_list)

    def chart_params(self):
        title = textwrap.wrap(f'<b>Sentencing of women in {self.pfa_df_outcome["pfa"].iloc[0]} 2010–2022</b>', width=60)

        self.fig.update_layout(
            margin=dict(l=63, b=75, r=20),
            barmode="group",
            title="<br>".join(title),
            title_y=0.94,
            title_yanchor="bottom",
            yaxis_title="",
            yaxis_tick0=0,
            yaxis_tickformat=",.0f",
            xaxis_showgrid=False,
            xaxis_tickcolor="#54565B",
            xaxis_dtick=2,
            xaxis_tick0=2010,
            showlegend=True,
            hovermode="x",
            modebar_activecolor="#A01D28",
            width=655,
            height=360,
        )

        self.fig.update_layout(legend=dict(
            yanchor="top",
            y=1.05,
            xanchor="right",
            x=1,
        ))

    ## Chart annotations
    def chart_annotations(self):
        prt_theme.source_annotation("Ministry of Justice, Criminal justice statistics", self.annotations)

        # Adding y-axis label
        self.annotations.append(
            dict(
                xref="x",
                yref="paper",
                x=self.pfa_df_outcome["year"].iloc[0],
                y=1.04,
                align="left",
                xanchor="left",
                showarrow=False,
                text="Women sentenced",
                font_size=12,
            )
        )

        # Adding annotations to layout
        self.fig.update_layout(annotations=self.annotations)

    def set_yaxis(self):
        ## Setting chart axis ranges
    
        for i in range(len(self.fig.data)):
            max_trace = (self.fig.data[i].y).max()
            if max_trace > self.max_y_val:
                self.max_y_val = max_trace

        y_intervals = [52, 103, 208, 315, 420, 540, 640, 830, 909, 1550, 2080, 3100]
        y_max_idx = min(range(len(y_intervals)), key = lambda i: abs(y_intervals[i]-self.max_y_val))
        if y_intervals[y_max_idx] <= self.max_y_val:
            y_max = y_intervals[y_max_idx + 1]
        else: 
            y_max = y_intervals[y_max_idx]

        self.fig.update_yaxes(range=[0, y_max])
        self.fig.update_xaxes(range=[2009.3, 2022.8])

    def _prepare_chart(self):
        if not self.trace_list:
            self.create_traces()
            self.chart_params()
            self.chart_annotations()
            self.set_yaxis()

    def save_chart(self, folder: str, filetype: str = 'pdf'):
        self._prepare_chart()
        self.filetype = filetype
        self.folder = folder

        export_path = Path.joinpath(Path.cwd(), f"{config['data']['outPath']}", f"{self.folder}/{self.filetype}")
        export_path.mkdir(parents=True, exist_ok=True)

        filename = str(self.pfa_df_outcome["pfa"].iloc[0])
        export_path = Path.joinpath(export_path, f'{filename}.{self.filetype}')

        self.fig.write_image(export_path)
        print(f"Chart saved to: {export_path}")

    def output_chart(self) -> None:
        self._prepare_chart()
        self.fig.show()

def make_pfa_sentence_type_charts(filename: str, folder: str, status='interim'):
    df = utils.load_data(status, filename)
    for pfa in df['pfa'].unique():
        chart = SentenceTypeChart(pfa, df)
        chart.save_chart(folder)

if __name__ == "__main__":
    filename = 'sentencesByPFA.csv'
    folder = '3.sentence_types'
    make_pfa_sentence_type_charts(filename, folder, status='processed')