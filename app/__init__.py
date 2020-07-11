import dash
from flask import Flask

server = Flask(__name__)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(server=server, external_stylesheets=external_stylesheets)

app.title = 'System Monitor App'

from app import layout, system_stats
