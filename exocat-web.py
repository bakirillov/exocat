import os
import json
import time
import dash
import base64
import argparse
import numpy as np
from index import *
import pandas as pd
import pickle as pkl
import os.path as op
from tqdm import tqdm
from leitner import *
from datetime import datetime
from exocat import ExoCat, THECAT
import dash_core_components as dcc
import dash_html_components as html

cat = ExoCat()
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Experimental web-interface for exocat"
app.layout = html.Div(children=[
    html.Div([
        dcc.Tabs(id="tabs", value='study-tab', children=[
            dcc.Tab(label='Study', value='study-tab'),
            dcc.Tab(label='Overview', value='overview-tab'),
        ]),
        html.Div(id='tabs-content')
    ])
])
#app.config['suppress_callback_exceptions']=True

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'study-tab':
        return(study_layout)
    elif tab == 'overview-tab':
        return(overview_layout)
    #elif tab == "edit-tab":
    #    return(tab_3.tab_3_layout)

study_layout = html.Div([
    html.H1('Study'),
    dcc.Dropdown(
        id='page-1-dropdown',
        options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
        value='LA'
    ),
    html.Div(id='page-1-content')
])


#@app.callback(
#    Output("answer", "children"),
#    [Input("upload-data", "contents")])
def process_image(file):
    if file:
        content_type, content_string = file.split(',')
        file_string = base64.b64decode(content_string)
        fname = op.join(TEMP_DIR, "ololo.png")
        with open(fname, "wb") as oh:
            oh.write(file_string)
        answer = who_is_on_the_photo(fname)
        answer_string = ",".join([answer[a] for a in answer])
        return(answer_string)


app.run_server(debug=False)