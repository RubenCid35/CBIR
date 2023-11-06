
import dash
from dash import html, dcc
from dash import State, Input, Output, MATCH, ALL
from dash.exceptions import PreventUpdate
from dash_daq import BooleanSwitch

from recommender.recommender import train, TRAIN_IMAGES

import time

algo_extract_types = html.Div([
    dcc.Dropdown([
        { "label":"Scale Invariant Feature Transform", "value": "sift" },
        { "label":"ORB", "value": "orb" },
        { "label":"Histograma de Color", "value": "hist" },
        { "label":"Red Convolucional", "value": "cnn" }
    ], value = "sift", id = "algo-extract-type-select", clearable = False,
    className = "text-left")
], className = "w-[30em] min-w-[60%] ml-4")

def algorithm_callbacks(app):
    @app.callback(
        Output("algo-extract-form", "children"),
        Input("algo-extract-type-select", "value")
    )
    def change_extract_form(extract_type):

        ret = []
        if extract_type == "sift":
            get_octaves = html.Div(dcc.Slider(2, 10, step = 1, value = 4, id = {'type':'extract-config', 'index': 'sift-octaves'}), className = "w-[30em] min-w-[60%] ml-4")
            contrast_thress = html.Div(dcc.Slider(0.01, 0.1, 0.01, value = 0.01, id = {'type':'extract-config', 'index': 'sift-contrast'}), className = "w-[30em] min-w-[60%] ml-4")
            ret = [
                    html.Div([ html.Label("Número de Octavas: ", className = "text-center"), get_octaves ], className = "flex text-center my-8"),
                    html.Div([ html.Label("Umbral de Contraste: ", className = "text-center"), contrast_thress ], className = "flex text-center mb-8"),
            ]

        elif extract_type == 'orb':
            get_wta = html.Div(dcc.Slider(2, 4, step = 1, value = 4, id = {'type':'extract-config', 'index': 'orb-wta'}), className = "w-[30em] min-w-[60%] ml-4")
            algo_drop = html.Div([
                dcc.Dropdown([
                    { "label":"FAST: Detector de Esquinas", "value": "fast" },
                    { "label":"Harris: Detector de Esquinas", "value": "harris" },
                ], value = "harris", id = {'type':'extract-config', 'index': 'orb-compute'},  clearable = False,
                className = "text-left")
            ], className = "w-[30em] min-w-[60%] ml-4")

            ret = [
                    html.Div([ html.Label("Método de Obteción de Puntos: ", className = "text-center"), algo_drop ], className = "flex text-center my-8"),
                    html.Div([ html.Label("Número de Puntos a Promediar: ", className = "text-center"), get_wta ], className = "flex text-center mb-8"),
                ]
            
        elif extract_type == 'hist':
            get_bins = html.Div([
                dcc.Dropdown([{'label': str(i), "value": i} for i in range(32, 257, 8)], value = "harris", id = {'type':'extract-config', 'index': 'hist-bins'},
                className = "text-left",  clearable = False)
            ], className = "w-[30em] min-w-[60%] ml-4")

            ret = [
                    html.Div([ html.Label("Número de Discretizaciones: ", className = "text-center"), get_bins ], className = "flex text-center my-8"),
            ]

        return html.Div(ret, className = "border-2 border-gray-300 rounded-md py-4 px-2")

    @app.callback(
        Output("algo-data", 'data'),
        Output("algo-modal-div", "hidden"),

        Input('change-algoritm-btn', 'n_clicks'),
        Input("close-algo-btn", "n_clicks"),
        
        State({'type':'extract-config', 'index': ALL}, 'id'),
        State({'type':'extract-config', 'index': ALL}, 'value'),
        State('vocab-size', 'disabled'),
        State('vocab-size', 'value'),
        State('algo-data', 'data'),
        
        State('algo-modal-div', 'hidden'),

        prevent_initial_call = True,
    )
    def save_algorithm(_open_btn, _btn, extract_ids, extract_values, vocab_on, vocab_bins, prev_data, is_hidden):
        if is_hidden: return prev_data, not is_hidden
        
        data = {'method': "", 'config': {}, 'vocab': { 'enable': False, 'bins': None}}
        for i, config_opt in enumerate(extract_ids):
            opt_name = config_opt['index']
            extract_algo, extract_config = opt_name.split("-")
            data['method'] = extract_algo
            data['config'][extract_config] = extract_values[i]
        
        data['vocab']['enable'] = not vocab_on
        if not vocab_on:  data['vocab']['bins'] = vocab_bins

        import json
        print(json.dumps(data, indent = 2))
        _ = train(data, TRAIN_IMAGES)
        return data, not is_hidden


    @app.callback(Output('vocab-size', 'disabled'),
                  Input("algo-vocab-enabled", "on"))
    def enabled_vocab_config(enable_state):
        return not enable_state


algoritm_modal = html.Div([

    html.Div([
        html.Div([
            html.H1("Método de Extracción de Características", className = "text-xl text-bold mb-2"),
            html.Div([ html.Label("Método: ", className = "text-center"), algo_extract_types ], className = "flex text-center mb-8"),
            html.Div(id = "algo-extract-form", className = "mr-4")
        ], className = "ml-5 mt-8 border-gray-300 border-r-4"),
        html.Div([
            html.Div([
                html.H1("Método de Extracción de Características", className = "text-xl text-bold mb-2 mr-4 text-center"),
                html.Div(BooleanSwitch(id = "algo-vocab-enabled", on = False, className = ""), className = "mr-12 ml-auto"),
            ], className = "flex"),
            html.Div([
                html.Div([ 
                    html.Label("Número de Palabras: ", className = "text-center"), 
                    html.Div(dcc.Slider(10, 75, step = 5, value = 4, id = 'vocab-size', disabled = True), className = "w-[30em] min-w-[60%] ml-4")
                ], className = "flex text-center my-8"),
            ], className = "border-2 border-gray-300 rounded-md py-4 px-2")
        ], className = "ml-5 mt-8 mr-8")
    ], className = "grid grid-cols-2 gap-4"),


    html.Div([
        html.Button("Cerrar & Guardar", id = "close-algo-btn", className = "mx-auto flex text-center bg-gray-300 rounded-md px-12 py-1 mt-4"),
        html.Span("Puede tardar unos segundos en actualizar.", className = "text-center text-lg text-gray-400")
    ], className = "align-middle justify-center absolute bottom-10 left-[40%]")

], hidden = True, id = "algo-modal-div", className = "absolute top-10 bg-white rounded-md w-[95vw] h-[90%] z-10 border-gray-500 border-4 left-[50%] translate-x-[-50%]"
)
