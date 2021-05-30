import psutil
import pandas as pd
from collections import deque
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output


def disk():
    disk = psutil.disk_usage('/')
    # Divide from Bytes -> KB -> MB -> GB
    free = round(disk.free / 1024.0 / 1024.0 / 1024.0, 1)
    total = round(disk.total / 1024.0 / 1024.0 / 1024.0, 1)
    used = total - free
    # return str(free) + 'GB free / ' + str(total) + 'GB total ( ' + str(disk.percent) + '% )'
    timestamp = datetime.now()

    disk = {"timestamp": timestamp,
            "values":
                {"total": total,
                 "used": used,
                 "free": free
                 }
            }

    return disk


def cpu_data():
    timestamp = datetime.now()
    cpu_percent = psutil.cpu_percent()

    return (timestamp, cpu_percent)


# def memory():
#     timestamp = datetime.now()
#     memory = psutil.virtual_memory()
#     available = round(memory.available / 1024.0 / 1024.0, 0)
#     total = round(memory.total / 1024.0 / 1024.0, 0)
#
#     return (timestamp, total, available)


def memory_data():
    timestamp = datetime.now()
    memory = psutil.virtual_memory()
    available = round(memory.available / 1024.0 / 1024.0, 0)
    total = round(memory.total / 1024.0 / 1024.0, 0)

    memory = {"timestamp": timestamp,
              "values":
                  {"available": available,
                   "total": total
                   }
              }

    return memory


X = deque(maxlen=60)
Y = deque(maxlen=60)


def generate_table(dataframe, max_rows=20):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


def current_processes():
    procs = {p.pid: p.info for p in psutil.process_iter(['name', 'username'])}
    return procs


# df = pd.DataFrame.from_dict(disk()['values'], orient='index',columns=['disk'])
# # df.reset_index(inplace=True)
# print(df)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

fig = px.line()

app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                     html.H1(children='Raspberry Pi 4 B System Stats'),

                     html.Div(children='A web application to monitor the Raspberry Pi system stats.')
                 ]),

        html.Div(className='row',
                 children=[
                     dcc.Graph(id='cpu-graph', animate=True, className='six columns', config={'displayModeBar': False}),
                     dcc.Graph(id='memory-graph', animate=True, className='three columns',
                               config={'displayModeBar': False}),
                     dcc.Graph(id='disk-graph', animate=True, className='three columns',
                               config={'displayModeBar': False})
                 ]
                 ),

        # remove the floating toolbar, provide the config parameter:
        # https://community.plotly.com/t/is-it-possible-to-hide-the-floating-toolbar/4911/6

        dcc.Interval(
            id='update-graph',
            interval=1000,
            n_intervals=0
        )
    ]

)


# cpu graph implementation
@app.callback(Output(component_id='cpu-graph', component_property='figure'),
              [Input(component_id='update-graph', component_property='n_intervals')])
def update_cpu_graph(n):
    global X
    global Y

    disk_monitor = cpu_data()
    X.append(disk_monitor[0])
    Y.append(disk_monitor[1])

    x = list(X)
    y = list(Y)
    fig = px.line(x=x, y=y,
                  title='cpu usage %',
                  line_shape='spline',
                  labels={'x': 'time', 'y': 'cpu usage %'},
                  range_x=[min(x), max(x)],
                  range_y=[min(y) * 0.8, max(y) * 1.1]
                  )

    return fig


# memory graph implementation
@app.callback(Output(component_id='memory-graph', component_property='figure'),
              [Input(component_id='update-graph', component_property='n_intervals')])
def update_memory_graph(n):
    memory_monitor = memory_data()

    x = ['', '']
    y = [memory_monitor['values']['total'], memory_monitor['values']['available']]

    # print('availabie = ', y[0] , 'total: =', y[1])
    fig = px.bar(x=x, y=y, text=y
                 , barmode='overlay', title='Memory Usage MB',
                 labels={'x': 'Memory Used', 'y': 'Total Memory Available'}
                 # , opacity=1

                 # use of colors in plotly:
                 # https://plotly.com/python/discrete-color/
                 # the color "theme" is a list defined either in the template (more here https://plotly.com/python/templates/)
                 # or can be choosen individually (see below)
                 # ,color_discrete_sequence=px.colors.qualitative.Bold
                 )

    # memory_monitor = memory()
    # df = pd.DataFrame.from_dict(memory_monitor['values'], orient='index',columns=['memory'])

    # # df.reset_index(inplace=True)

    # # if you want to pivot a datframe with only 1 column and 1 index, 1) reset the index 2) use the df.pivot_table function and only enter 
    # # the columns

    # # df = df.pivot_table(columns = 'index')

    # df = df.T

    # print(df)
    # print(df['total'].tolist()[0])
    # # x = ['', '']
    # # y = [memory_monitor[1], memory_monitor[2]]

    # # print('availabie = ', y[0] , 'total: =', y[1])
    # fig = px.bar(data_frame=df
    #             ,x=['', ''] ,y=[df['total'].tolist()[0], df['available'].tolist()[0]] 
    #             ,barmode='overlay', title='Memory Usage MB' # , labels={'x':'Memory Used', 'y': 'Total Memory Available'} 
    #             # , opacity=1 

    #             # use of colors in plotly:
    #             # https://plotly.com/python/discrete-color/
    #             # the color "theme" is a list defined either in the template (more here https://plotly.com/python/templates/)
    #             # or can be choosen individually (see below)
    #             # ,color_discrete_sequence=px.colors.qualitative.Bold
    #             )

    # remove howevermode for Chart
    fig.layout.hovermode = False

    return fig


# disk graph implementation
@app.callback(Output(component_id='disk-graph', component_property='figure'),
              [Input(component_id='update-graph', component_property='n_intervals')])
def update_disk_graph(n):
    disk_monitor = disk()

    df = pd.DataFrame.from_dict(disk_monitor['values'], orient='index', columns=['disk'])

    df.drop(index='total', inplace=True)

    fig = px.pie(data_frame=df
                 )
    fig = px.pie(data_frame=df, values='disk', title='Disk Usage %')

    # remove howevermode for Chart
    fig.layout.hovermode = False

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
