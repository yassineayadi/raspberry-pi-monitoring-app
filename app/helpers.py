import dash_html_components as html
from collections import deque

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

numeric_l = lambda i: 'numeric' if i in ['cpu_percent','memory_percent'] else 'text'

class DequeHolder:
    def __init__(self):
        self.X = deque(maxlen=60)
        self.Y = deque(maxlen=60)
