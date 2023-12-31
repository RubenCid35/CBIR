
import os

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from dash import State, Input, Output, MATCH, ALL, ctx, ClientsideFunction

from utils.utils import load_images
from .AlgorithmModal import algorithm_callbacks, algoritm_modal

import time

NO_IMAGE_ICON: str = r"https://img.freepik.com/premium-vector/default-image-icon-vector-missing-picture-page-website-design-mobile-app-no-photo-available_87543-11093.jpg?w=826"

# Load Test Image DataFrame
TEST_IMAGES, _ = load_images(False)
TEST_IMAGES = TEST_IMAGES# .sample(n = 40)


DEFAULT = { 
  "method": "sift",
  "config": {
    "octaves": 4,
    "contrast": 0.05
  },
  "vocab": {
    "enable": False,
    "bins": 50
  }
}


# Searh / Algorithm Adjust Zone
adjust = html.Div([
    html.Button("Buscar", id = "search-relevant-images-btn" ,  n_clicks=0     , className = "rounded-md bg-gray-300 mx-[20px] py-[5px] text-bold"),
    html.Button("Modificar Algoritmo", id = "change-algoritm-btn",  n_clicks=0, className = "rounded-md bg-gray-300 mx-[20px] py-[5px] text-bold")
], className='grid grid-cols-2 mx-auto mt-[5px]')

# Image / Button Zone
visual_zone = html.Div([
    adjust,
    html.Div([
        html.Button([
            html.Img( id = "query-image-visual", className = "object-fill w-[100%] rounded-lg bg-gray-300 border-[3px] aspect-square", src=NO_IMAGE_ICON)
        ], className="w-[100%]", id = "change-image-btn")
    ], className="w-[70%] mx-auto my-[10px] pt-5"),

    dcc.Store(id = "query-image-data", storage_type = "memory", data = {"uri": NO_IMAGE_ICON, "label": None}),
    dcc.Store(id = "algo-data", storage_type = "session", data = DEFAULT),
    dcc.Store(id = "algo-data-paths", storage_type = "session", data = ("sift-1b7852b855.csv", None))
], className="rounded-md border-gray-400 border-[2px] py-[10px]")

# Modal
def generate_image_button(image_path, _id):
    _id = {
        'type': "query-image-select-btn",
        "index": _id
    }
    
    return html.Button([
        html.Img(className = "object-fill w-[156px] rounded-lg bg-gray-300 border-[3px] aspect-square mx-auto", 
                 src = dash.get_asset_url(image_path))
    ], className = "w-[156px]", id = _id)



close_button = html.Div()
change_image_modal = html.Div([
    
    html.H1("Imagen de Búsqueda", className="text-4xl text-black mx-5 mt-2"),
    
    html.Div(
        [generate_image_button(row, i) for i, row in enumerate(TEST_IMAGES["path"]) ],
        className = "grid big:grid-cols-10 grid-cols-6 gap-5 mt-5 mx-5 h-[80%] overflow-scroll"
    ),
    
    html.Div([
        html.Button("Cerrar", id = "close-input-btn", className = "mx-auto flex text-center bg-gray-300 rounded-md px-12 py-1 mt-4")
    ], className = "flex align-middle justify-center")


], id = "image-input-modal", hidden = True, 
    className = "absolute top-10 bg-white rounded-md w-[95vw] h-[90%] z-10 border-gray-500 border-4 left-[50%] translate-x-[-50%]"
)

def input_callbacks(app: dash.Dash):

    algorithm_callbacks(app)
    app.clientside_callback(
        ClientsideFunction('clientselect', 'input_image_select'),
        [   Output("query-image-data", "data"),
            Output("image-input-modal", "hidden"),
            Output("query-image-visual", "src")
        ],
        [
            Input("change-image-btn", "n_clicks"),
            Input("close-input-btn", "n_clicks"),
            Input({"type": "query-image-select-btn", "index": ALL}, "n_clicks"),

            State("image-input-modal", "hidden"),
            State({"type": "query-image-select-btn", "index": ALL}, "children"),
            State({"type": "query-image-select-btn", "index": ALL}, "id"),
            State("query-image-data", "data"),
        ],
        prevent_initial_call = True

    )


# Input Zone
input_banner = html.Div([
    visual_zone,
    change_image_modal,
    algoritm_modal
], className = "col-span-4 min-w-[275px]")

