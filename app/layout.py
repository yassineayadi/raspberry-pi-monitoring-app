from app import app
from app.system_stats import get_disk_usage, get_cpu_usage, get_memory_usage, get_current_processes, get_current_pi_revision, create_system_table

import time
import pandas as pd
from collections import deque

import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output


import dash_table
import dash_table.FormatTemplate as FormatTemplate

df = create_system_table()

pi_model = get_current_pi_revision()
X = deque(maxlen=60)
Y = deque(maxlen=60)

# application layout setup
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(className='row',
        children=[
            html.H1(children='Raspberry Pi {model}'.format(model=pi_model['Model'], revision=pi_model['Revision'])) # ,
            # html.Div(children='Manufacturer: {manufacturer}'.format(manufacturer=pi_model['Manufacturer'])),
            # html.Div(children='A web application to monitor the Raspberry Pi system stats.')
    ])

numeric_l = lambda i: 'numeric' if i in ['cpu_percent','memory_percent'] else 'text'

app.layout = html.Div(
             children=[
            
            html.Div(className='row',children=[
                html.H1(children='Raspberry Pi {model}'.format(model=pi_model['Model'], revision=pi_model['Revision'])),
                html.Div(children='Manufacturer: {manufacturer}'.format(manufacturer=pi_model['Manufacturer'])),
                html.Div(children='A web application to monitor the Raspberry Pi system stats.')
            ]),
            
            html.Div(className='row',children=[
                dcc.Graph(id='cpu-graph', animate=True, className='six columns', config={'displayModeBar': False}),
                dcc.Graph(id='memory-graph', animate=True, className='three columns', config={'displayModeBar': False}), 
                dcc.Graph(id='disk-graph', animate=True, className='three columns', config={'displayModeBar': False})               
            ]),

            html.Div(className='row',children=[
                html.H4(children='Processes Currently Running'),
                dash_table.DataTable(
                    id='processes-table',

                    # format percentage currently defined for ALL columns. However only applied for numeric (as per DataTable documentation)
                    columns=[{"name": i, "id": i, "type": numeric_l(i), "format": FormatTemplate.percentage(2)} for i in df.columns],
                    data=df.to_dict('records'),
                    sort_action="native",
                    filter_action='native',
                    style_as_list_view=True,

                    # Note: DataTable style does not take external_stylesheet, needs to be explicetly defined
                    style_cell={'font-family':["Open Sans", "HelveticaNeue", "Helvetica Neue", "Helvetica", "Arial","sans-serif"]},
                    style_data_conditional=[
                        # memory_percent formatting
                        {
                            'if': {
                                'filter_query': '{memory_percent} >= 0.05',
                                'column_id': 'memory_percent'
                            },
                            'backgroundColor': 'rgb(95, 70, 144)',
                            'color': 'white',
                            'opacity': 0.8
                        },
                        {
                            'if': {
                                'filter_query': '{memory_percent} < 0.05 && {memory_percent} >= 0.02',
                                'column_id': 'memory_percent'
                            },
                            'backgroundColor': 'rgb(95, 70, 144)',
                            'color': 'white',
                            'opacity': 0.5
                        },
                        {
                            'if': {
                                'filter_query': '{memory_percent} < 0.02 && {memory_percent} >= 0.005',
                                'column_id': 'memory_percent'
                            },
                            'backgroundColor': 'rgb(95, 70, 144)',
                            'color': 'white',
                            'opacity': 0.3
                        },
                        # cpu_percent formatting
                        {
                            'if': {
                                'filter_query': '{cpu_percent} >= 0.05',
                                'column_id': 'cpu_percent'
                            },
                            'backgroundColor': 'rgb(95, 70, 144)',
                            'color': 'white',
                            'opacity': 0.8
                        },
                        {
                            'if': {
                                'filter_query': '{cpu_percent} < 0.05 && {cpu_percent} >= 0.02',
                                'column_id': 'cpu_percent'
                            },
                            'backgroundColor': 'rgb(95, 70, 144)',
                            'color': 'white',
                            'opacity': 0.5
                        },                        
                    ]
                )
            ]),

            dcc.Interval(
                    id='update-graph',
                    interval=1000,
                    n_intervals=0   
                    )

]
)

# STATS UPDATE

# cpu graph implementation
@app.callback(Output(component_id='cpu-graph', component_property='figure'),
              [Input(component_id='update-graph', component_property='n_intervals')])
def update_cpu_graph(n):
    global X
    global Y

    cpu_monitor = get_cpu_usage()
    X.append(cpu_monitor[0])
    Y.append(cpu_monitor[1])

    x = list(X)
    y = list(Y)
    fig = px.line(x=x, y=y,
                 title='Cpu Usage %',
                 line_shape='spline',
                 labels= {'x':'time', 'y':'Cpu Usage %'},
                 range_x = [min(x), max(x)],
                 range_y = [min(y)*0.8, max(y)*1.1],
                 color_discrete_sequence=px.colors.qualitative.Prism
                )
    
    return fig

# memory graph implementation
@app.callback(Output(component_id='memory-graph', component_property='figure'),
              [Input(component_id='update-graph', component_property='n_intervals')])
def update_memory_graph(n):

    memory_monitor = get_memory_usage()

    x = ['', '']
    y = [memory_monitor['values']['total'], memory_monitor['values']['used']]
    customdata = [y[1]/y[0] for i in range(len(y))]

    fig = px.bar(x=x, y=y, text=y,
                barmode='overlay', 
                title='Memory Usage MB', 
                labels={'x':'Memory Used', 'y': 'Total Memory Available'},
                color_discrete_sequence=px.colors.qualitative.Prism
                )
    fig.update_traces(texttemplate='%{text:,2s} MB', hovertemplate='%{customdata:%} total usage', customdata=customdata)

    # remove hovermode for Chart
    # fig.layout.hovermode = True

    return fig

# disk graph implementation
@app.callback(Output(component_id='disk-graph', component_property='figure'),
              [Input(component_id='update-graph', component_property='n_intervals')])
def update_disk_graph(n):
    disk_monitor = get_disk_usage()

    df = pd.DataFrame.from_dict(disk_monitor['values'], orient='index',columns=['disk'])
    
    df.drop(index='total',inplace=True)

    fig=px.pie(data_frame=df,values='disk', title='Disk Usage %',
               color_discrete_sequence=px.colors.qualitative.Prism,
               opacity=0.8
               )

    fig.update_traces(hovertemplate='%{value} GB')
    # print(df.head())
    # print("plotly express hovertemplate:", fig.data[0].hovertemplate)
    # remove hovermode for Chart
    # fig.layout.hovermode = False

    return fig


@app.callback(Output(component_id='processes-table', component_property='data'),
              [Input(component_id='update-graph', component_property='n_intervals')])
def update_processes_table(n):
    df = create_system_table()

    return df.to_dict('records')

# if __name__ == '__main__':
#     app.run_server(debug=True)