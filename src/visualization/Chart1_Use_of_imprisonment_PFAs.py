# CHART 1: USE OF IMPRISONMENT FOR WOMEN BY PFA

##Importing libraries
import pandas as pd
import textwrap
import plotly.graph_objs as go
import plotly.io as pio
from pathlib import Path #To create unique filenames for each PFA chart
import itertools

import src.data.utilities as utils
import src.visualization.prt_theme as prt_theme

## Reading config file and setting Plotly template
config = utils.read_config()
pio.templates.default = "prt_template"

##Functions
class SentenceLengthChart:
    
    def __init__(self, pfa:str, df:pd.DataFrame, labelIDX:int = 0, adjust:int = 0):

        self.pfa = pfa
        self.df = df
        self.labelIDX = labelIDX
        self.adjust = adjust
        self.trace_list = [] # Need to empty my trace_list with every loop through each PFA so that charts are plotted separately
        self.annotations: list[dict] = []  # Add this line to provide a type hint for self.annotations
        self.fig = go.Figure() # Need to also instantiate the figure with every loop in order to clear fig.data values
        self.pfa_df_sentence = pd.DataFrame()

    def createTraces(self):
        pfa_df = self.df[self.df["pfa"] == self.pfa]

        for i in pfa_df["sentence_length"].unique():  # Creating a for loop to extract unique values from the dataframe and make traces
            self.pfa_df_sentence = pfa_df[pfa_df["sentence_length"] == i]
            
            trace = go.Scatter(
                x=self.pfa_df_sentence["year"],
                y=self.pfa_df_sentence["freq"],
                mode="lines",
                name=str(self.pfa_df_sentence["sentence_length"].iloc[0]),
                meta=self.pfa_df_sentence["pfa"].iloc[0],   # Adding name of PFA in metadata to ensure data relates to only one area 
                hovertemplate="%{y}<extra></extra>"
            )
            self.trace_list.append(trace)

        self.fig.add_traces(self.trace_list)

    def chartParams(self):
    # Chart title
        title = textwrap.wrap(f'<b>Use of immediate imprisonment for women in {self.pfa_df_sentence["pfa"].iloc[0]} 2010–2022</b>', width=45)
    
    # Chart layout
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

    ## Chart annotations
    def chartAnnotations(self):

        # Adding trace annotations
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
        # Adding source label
        prt_theme.sourceAnnotation("Ministry of Justice, Criminal justice statistics", self.annotations)

        # Adding y-axis label
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

        if self.labelIDX is not None and self.adjust is not None:
            self.annotations[self.labelIDX]['y'] = int(self.adjust)
        
        self.annotations[1]['y'] = 0
            
        # Adding annotations to layout
        self.fig.update_layout(annotations=self.annotations)

    def setYAxis(self):

    ## Setting chart axis ranges
    
        for i in range(len(self.fig.data)):
            max_trace = (self.fig.data[i].y).max()
            if max_trace > self.max_y_val:
                self.max_y_val = max_trace

        y_intervals = [52, 103, 210, 305, 405, 606, 1210]
        y_max_idx = min(range(len(y_intervals)), key = lambda i: abs(y_intervals[i]-self.max_y_val))
        if y_intervals[y_max_idx] <= self.max_y_val:
            y_max = y_intervals[y_max_idx + 1]
        else: 
            y_max = y_intervals[y_max_idx]
        
        self.fig.update_yaxes(range=[0, y_max])
        self.fig.update_xaxes(range=[2009.7, 2022.3])
        
    def saveChart(self, filetype='pdf'):
        self.filetype = filetype

        export_path = Path.joinpath(Path.cwd(), f"{config['data']['outPath']}", "custody_sentence_lengths_2022")
        export_path.mkdir(parents=True, exist_ok=True) #generate if does not exist

        # Setting filename variable and full path
        filename = str(self.pfa_df_sentence["pfa"].iloc[0])
        export_path = Path.joinpath(export_path, f'{filename}.{self.filetype}')

        self.fig.write_image(export_path)

    def outputChart(self):
        self.createTraces()
        self.chartParams()
        self.chartAnnotations()
        self.setYAxis()
        self.fig.show()
    
def makePfaSentenceLengthCharts(filename:str, folder:str, status='interim'):
    df = utils.load_data(status, filename)
    for pfa in df['pfa'].unique():
        chart = SentenceLengthChart(pfa, df)
        chart.saveChart(folder)
    print("Charts ready")

if __name__ == "__main__":
    filename='women_cust_sentence_length_PFA_2010-2022.csv'
    folder='custody_sentence_lengths_2022'
    makePfaSentenceLengthCharts(filename, folder)