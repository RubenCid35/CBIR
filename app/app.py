import sys
sys.path.append('../')

import os
import pathlib

import dash
import plotly.express as px

from dash import dcc, html
from dash.long_callback import DiskcacheLongCallbackManager

## Diskcache
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)


# Script tailwind para el estilo
external_script = [
    {"src": "./tailwind.config.js"}, 
    {"src": "https://cdn.tailwindcss.com"}, 
    {"src" : "https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.0.0/flowbite.min.js"}
]
external_stylesheet = [{"src": "https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.0.0/flowbite.min.css"}]

app = dash.Dash(
   name =  __name__,
    title = "Content-Based Image Retrival",
    external_scripts=external_script,
    external_stylesheets=external_stylesheet,
    assets_folder= str(pathlib.Path.cwd().parent.absolute()),
    long_callback_manager=long_callback_manager,
    serve_locally=True,
)

app.scripts.config.serve_locally = True

# No cambiar el lugar o da error
from components.header import header_layout
from components.InputCard import input_banner, input_callbacks
from components.RetCard import output_card, output_callbacks

# Layout

app.layout = html.Div([
    html.Script(src = "https://cdn.tailwindcss.com"),
    # Header
    header_layout,
    # Image Query + Stats
    html.Div([
        input_banner,
        output_card
    ], className = "grid grid-cols-10 w-full px-5 pt-2 gap-2")
    

    # Image Results

], className="")

# Active CallBack
input_callbacks(app)
output_callbacks(app)


if __name__ == "__main__":
    app.run_server(debug=True)