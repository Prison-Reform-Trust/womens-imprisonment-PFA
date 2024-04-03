# CHART 1: USE OF IMPRISONMENT FOR WOMEN BY PFA

import pandas as pd
import textwrap
import plotly.graph_objs as go
import plotly.io as pio
from plotly.graph_objs import Figure
from typing import List
from pathlib import Path
from src.data import utilities as utils
from src.visualization import prt_theme

config = utils.read_config()
pio.templates.default = "prt_template"

class SentenceLengthChart:

    def __init__(self, pfa: str, df: pd.DataFrame, label_idx: int = 0, adjust: int = 0):
        self.pfa = pfa
        self.df = df
        self.label_idx = label_idx
        self.adjust = adjust
        self.trace_list: List[go.Scatter] = []
        self.annotations: list[dict] = []
        self.fig = go.Figure()
        self.pfa_df_sentence = pd.DataFrame()
        self.max_y_val = 0  # Initialize max_y_val

    def break_trace_labels(self):
        self.df['sentence_length'] = self.df['sentence_length'].cat.rename_categories({'6 months to less than 12 months': '6 months—<br>less than 12 months'})

    def create_traces(self):
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
        title = textwrap.wrap(f'<b>Use of immediate imprisonment for women in {self.pfa_df_sentence["pfa"].iloc[0]} 2010–2022</b>', width=45)

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

        if self.label_idx != 0 and self.adjust != 0:
            self.annotations[self.label_idx]['y'] = int(self.adjust)

        self.annotations[1]['y'] = 0

        self.fig.update_layout(annotations=self.annotations)

    def set_y_axis(self):
        for i in range(len(self.fig.data)):
            max_trace = (self.fig.data[i].y).max()
            if max_trace > self.max_y_val:
                self.max_y_val = max_trace

        y_intervals = [52, 103, 210, 305, 405, 606, 1210]
        y_max_idx = min(range(len(y_intervals)), key=lambda i: abs(y_intervals[i] - self.max_y_val))
        y_max = y_intervals[y_max_idx + 1] if y_intervals[y_max_idx] <= self.max_y_val else y_intervals[y_max_idx]

        self.fig.update_yaxes(range=[0, y_max])
        self.fig.update_xaxes(range=[2009.7, 2022.3])

    def save_chart(self, folder: str, filetype: str = 'pdf'):
            self.filetype = filetype
            self.folder = folder

            if not self.trace_list:
                self.break_trace_labels()
                self.create_traces()
                self.chart_params()
                self.chart_annotations()
                self.set_y_axis()

            export_path = Path.joinpath(Path.cwd(), f"{config['data']['outPath']}", f"{self.folder}/{self.filetype}")
            export_path.mkdir(parents=True, exist_ok=True)

            filename = str(self.pfa_df_sentence["pfa"].iloc[0])
            export_path = Path.joinpath(export_path, f'{filename}.{self.filetype}')

            self.fig.write_image(export_path)

    def output_chart(self) -> None:
        self.break_trace_labels()
        self.create_traces()
        self.chart_params()
        self.chart_annotations()
        self.set_y_axis()
        self.fig.show()


def make_pfa_sentence_length_charts(filename: str, folder: str, status='interim'):
    df = utils.load_data(status, filename)
    for pfa in df['pfa'].unique():
        chart = SentenceLengthChart(pfa, df)
        chart.save_chart(folder)
    print("Charts ready")


if __name__ == "__main__":
    filename = 'women_cust_sentence_length_PFA_2010-2022.csv'
    folder = 'custody_sentence_lengths_2022'
    make_pfa_sentence_length_charts(filename, folder)