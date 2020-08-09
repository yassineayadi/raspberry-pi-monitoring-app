import dash_html_components as html
from collections import deque
import pandas as pd

# currently not used
def generate_table(dataframe, max_rows=10):
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


def create_system_table(dict_data, sort_column='memory_percent') -> pd.DataFrame:
    df = pd.DataFrame.from_dict(dict_data, orient='index')
    df.sort_values(by= sort_column, ascending=False, inplace=True)
    df = df.head(20)
    return df


def convert_time_delta_to_string(timedelta):

    # total number of seconds
    s = timedelta.total_seconds()
    # hours
    hours = s // 3600
    # remaining seconds
    s = s - (hours * 3600)
    # minutes
    minutes = s // 60
    # remaining seconds
    seconds = s - (minutes * 60)
    # total time
    return '{:02}h: {:02}m: {:02}s'.format(int(hours), int(minutes), int(seconds))


# lambda function to define the datatype of each column for the DataTable
numeric_l = lambda i: 'numeric' if i in ['cpu_percent', 'memory_percent'] else 'text'


class DequeHolder:
    def __init__(self):
        self.X = deque(maxlen=60)
        self.Y = deque(maxlen=60)
