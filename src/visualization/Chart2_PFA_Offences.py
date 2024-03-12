#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import textwrap
import plotly.graph_objs as go
import plotly.io as pio
from pathlib import Path

from src.data import utilities as utils
from src.visualization import prt_theme

config = utils.read_config()
pio.templates.default = "prt_template"


class PfaOffencesChart:

    def __init__(self, pfa: str, df: pd.DataFrame):
        self.pfa = pfa
        self.df = df
        self.trace_list = []
        self.annotations: list[dict] = []
        self.fig = go.Figure()

    @staticmethod
    def custom_wrap(s: str, width=19):
        return "<br>".join(textwrap.wrap(s, width=width))

    def prepare_data(self):
        #Melting df from wide to long
        id_vars = ['pfa']
        value_vars = list(self.df.columns[1:])
        self.df = pd.melt(self.df, id_vars=id_vars, value_vars=value_vars, var_name='offence', value_name='proportion')

        highlighted_offence_groups = ['Theft offences', 'Drug offences', 'Violence against the person']
        self.filt = self.df['offence'].isin(highlighted_offence_groups)

        self.df['parent'] = ""
        self.df.loc[self.filt, 'parent'] = "All offences"
        self.df.loc[~self.filt, 'parent'] = "All other<br>offences"

        #Setting discreet plotting order
        plot_dict = {
            'All other offences': 0,
            'Theft offences': 1,
            'Drug offences': 2,
            'Violence against the person': 3
        }
        self.df['plot_order'] = self.df["offence"].map(plot_dict).fillna(0)

        #Wrapping longer offence text
        self.df.loc[self.filt, 'offence'] = self.df.loc[self.filt, 'offence'].map(
            (lambda x: self.custom_wrap(x, width=12)))
        self.df.loc[~self.filt, 'offence'] = self.df.loc[~self.filt, 'offence'].map(self.custom_wrap)

        return self.df

    def create_traces(self):
        self.df = self.df[self.df["pfa"] == self.pfa]
        self.df = pd.concat([
            self.df,
            pd.DataFrame.from_records([{
                'pfa': self.df['pfa'].iloc[0],
                'offence': "All other<br>offences",
                'proportion': self.df.loc[~self.filt, 'proportion'].sum(),
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
        self.prepare_data()
        self.create_traces()
        self.chart_params()
        self.chart_annotations()
        self.fig.show()


def make_pfa_offences_charts(filename: str, folder: str, status: str = 'processed', filetype: str = 'pdf'):
    df = utils.load_data(status, filename)
    df = df.rename({'Fraud Offences': 'Fraud offences'}, axis=1)
    for pfa in df['pfa'].unique():
        chart = PfaOffencesChart(pfa, df)
        chart.save_chart(folder, filetype)
    print("Charts ready")


if __name__ == "__main__":
    filename = 'PFA_2022_offences.csv'
    folder = 'custody_offences_2022'
    make_pfa_offences_charts(filename, folder)
