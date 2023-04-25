# CHART 1: USE OF IMPRISONMENT FOR WOMEN BY PFA

##Importing libraries
import pandas as pd
import textwrap
import plotly.graph_objs as go
import plotly.io as pio
import itertools
from pathlib import Path #To create unique filenames for each PFA chart

##Setting template
pio.templates
prt_template = go.layout.Template(
    layout=go.Layout(
        title_font=dict(family="Helvetica Neue, Arial", size=17),
        font_color="#54565B",
        font_family="Helvetica Neue, Arial",
        font_size=12,
        paper_bgcolor="#FBFAF7",
        plot_bgcolor="#FBFAF7",
        colorway=("#A01D28", "#499CC9", "#F9A237", "#6FBA3A", "#573D6B"),
    )
)

config = dict(
    {
        "scrollZoom": False,
        "displayModeBar": False,
        "editable": False,
        "displaylogo": False,
        "showAxisDragHandles": False,
    }
)

##Reading in data
df = pd.read_csv('../../data/interim/PFA_2009-21_women_cust_sentence_len.csv')
#Replacing 6 months and under 12 months to something more chart friendly
df['sentence_len'] = df['sentence_len'].str.replace("6 months and under 12 months", "6 months–<br>under 12 months")

##FUNCTIONS: Checking for overlapping trace labels

def annotation_yvals():
    y_list = [fig.data[i]['y'][-1] for i in range(len(fig.data))] #selecting last y value for each trace 
    return y_list

def check_overlap(l, space):
    return all(x2-x1 >= space for x1,x2 in itertools.pairwise(sorted(l)))

def adjust_overlap(l, space):
    for (idx1,num1), (idx2,num2) in itertools.permutations(enumerate(l), 2):
        difference = abs(l[idx1] - l[idx2])
        if difference < space:
            largest = max((idx1,num1), (idx2,num2), key=lambda x:x[1])
            largest_index = largest[0]
            l[largest_index] = l[largest_index] + (space - difference)
            annotations[largest_index]['y'] = l[largest_index]

## CHART CONSTRUCTION

#Building chart traces loop
for pfa in df['pfa'].unique():
    pfa_df = df[df["pfa"] == pfa]
    trace_list = [] # Need to empty my trace_list with every loop through each PFA so that charts are plotted separately
    fig = go.Figure() # Need to also instantiate the figure with every loop in order to clear fig.data values

    for i in pfa_df["sentence_len"].unique():  # Creating a for loop to extract unique values from the dataframe and make traces
        pfa_df_sentence = pfa_df[pfa_df["sentence_len"] == i]
        
        trace = go.Scatter(
            x=pfa_df_sentence["year"],
            y=pfa_df_sentence["freq"],
            mode="lines",
            name=str(pfa_df_sentence["sentence_len"].iloc[0]),
            meta=pfa_df_sentence["pfa"].iloc[0],   # Adding name of PFA in metadata to ensure data relates to only one area 
            hovertemplate="%{y}<extra></extra>"
        )

        trace_list.append(trace)

    fig.add_traces(trace_list)


    ##Chart title and formatting
    title = textwrap.wrap(f'<b>Use of immediate imprisonment for women in {pfa_df_sentence["pfa"].iloc[0]} 2009–2021</b>', width=45)

    fig.update_layout(
        margin=dict(l=63, b=75, r=100),
        title="<br>".join(title),
        title_y=0.94,
        title_yanchor="bottom",
        yaxis_title="",
        yaxis_tickformat=",.0f",
        yaxis_tick0=0,
        yaxis_nticks=9,
        xaxis_dtick=2,
        xaxis_tick0=2009,    
        xaxis_showgrid=False,
        xaxis_tickcolor="#54565B",
        template=prt_template,
        showlegend=False,
        hovermode="x",
        modebar_activecolor="#A01D28",
        width=655,
        height=500,
    )

    ##Chart annotations
    annotations = []

    #Trace annotations
    for j in range(0, len(trace_list)):
        annotations.append(
            dict(
                xref="x",
                yref="y",
                x=fig.data[j].x[-1],
                y=fig.data[j].y[-1],
                text=str(fig.data[j].name),
                xanchor="left",
                align="left",
                showarrow=False,
                font_color=prt_template.layout.colorway[j],
                font_size=10,
            )
        )

    #Source label
    annotations.append(
        dict(
            xref="paper",
            yref="paper",
            x=-0.08,
            y=-0.19,
            align="left",
            showarrow=False,
            text="<b>Source: Ministry of Justice, Criminal justice statistics</b>",
            font_size=12,
        )
    )

    #Y-axis label
    annotations.append(
        dict(
            xref="x",
            yref="paper",
            x=df['year'].iloc[0],
            y=1.04,
            align="left",
            xanchor="left",
            showarrow=False,
            text="Women sentenced to custody",
            font_size=12,
        )
    )
    
    #Checking for overlapping annotations on trace labels
    y_vals = annotation_yvals()
    
    space = 5
    if check_overlap(y_vals, space) == False:
        adjust_overlap(y_vals, space)
    
    #Adding final annotations to chart layout
    fig.update_layout(annotations=annotations)

    ##Setting chart axis ranges
    for i in range(len(fig.data)):
        max_trace = (fig.data[i].y).max()
    
    fig.update_yaxes(range=[0, max_trace + (max_trace * 0.2)])
    fig.update_xaxes(range=[2008.7, 2021.3])
   
    ## Exporting to static image

    # Save results to ../reports/figures/custody_sentence_lengths, generate if does not exist.
    export_path = Path.joinpath(Path.cwd().parent.parent, "reports", "figures", "custody_sentence_lengths")
    export_path.mkdir(parents=True, exist_ok=True)

    # Setting filename variable and full path
    filename = str(pfa_df_sentence["pfa"].iloc[0])
    export_svg_path = Path.joinpath(export_path, f'{filename}' + '.svg')

    fig.write_image(export_svg_path)