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

    def __init__(self, pfa: str, df: pd.DataFrame, label_idx: int | list = 0, adjust: int | list = 0):
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
        for i in range(len(self.fig.data)):
            max_trace = (self.fig.data[i].y).max()
            if max_trace > self.max_y_val:
                self.max_y_val = max_trace

        y_intervals = [52, 103, 210, 305, 405, 606, 1210]
        y_max_idx = min(range(len(y_intervals)), key=lambda i: abs(y_intervals[i] - self.max_y_val))
        y_max = y_intervals[y_max_idx + 1] if y_intervals[y_max_idx] <= self.max_y_val else y_intervals[y_max_idx]

        self.fig.update_yaxes(range=[0, y_max])
        self.fig.update_xaxes(range=[2009.7, 2022.3])
    
    def _prepare_chart(self):
        if not self.trace_list:
            self.break_trace_labels()
            self.create_traces()
            self.chart_params()
            self.chart_annotations()
            self.set_y_axis()

    def save_chart(self, folder: str, filetype: str = 'pdf'):
        self._prepare_chart()
        self.filetype = filetype
        self.folder = folder

        export_path = Path.joinpath(Path.cwd(), f"{config['data']['outPath']}", f"{self.folder}/{self.filetype}")
        export_path.mkdir(parents=True, exist_ok=True)

        filename = str(self.pfa_df_sentence["pfa"].iloc[0])
        export_path = Path.joinpath(export_path, f'{filename}.{self.filetype}')

        self.fig.write_image(export_path)
        print(f"Chart saved to: {export_path}")

    def output_chart(self) -> None:
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

def make_pfa_sentence_length_charts(filename: str, folder: str, status='interim', output: str = 'save', pfa_adjustments: Optional[List[Record]] = None):
    df = utils.load_data(status, filename)
    for pfa in df['pfa'].unique():
        adjusted = False
        if pfa_adjustments:
            for adjustment in pfa_adjustments:
                if pfa == adjustment.pfa_name:
                    chart = SentenceLengthChart(pfa=adjustment.pfa_name, 
                        df=df, 
                        label_idx=adjustment.label_idx, 
                        adjust=adjustment.adjust
                        )
                    adjusted = True
                    break
        if not adjusted:
            chart = SentenceLengthChart(pfa, df)
        if output == 'save':
            chart.save_chart(folder)
        elif output == 'show':
            chart.output_chart()
        else:
            raise ValueError("output must be 'save' or 'show'.")
    print("Charts ready")


if __name__ == "__main__":
    filename = 'women_cust_sentence_length_PFA_2010-2022.csv'
    folder = 'custody_sentence_lengths_2022'
    
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

    make_pfa_sentence_length_charts(filename, folder)