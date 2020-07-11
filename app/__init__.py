import dash
from flask import Flask

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__) 

app = dash.Dash(server=server, external_stylesheets=external_stylesheets)

from app import layout, system_stats