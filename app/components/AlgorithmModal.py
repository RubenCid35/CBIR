
import dash
from dash import html, dcc
from dash import State, Input, Output, MATCH, ALL, ClientsideFunction
from dash.exceptions import PreventUpdate
from dash_daq import BooleanSwitch
from dash_svg import Svg, Path
from recommender.staging import train, TRAIN_IMAGES

import time

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

def algorithm_callbacks(app: dash.Dash):
    @app.callback(
        Output("algo-extract-form", "children"),
        Input("algo-extract-type-select", "value")
    )
    def change_extract_form(extract_type):

        ret = []
        if extract_type == "sift":
            get_octaves = html.Div(dcc.Slider(2, 10, step = 1, value = 6, id = {'type':'extract-config', 'index': 'sift-octaves'}), className = "w-[30em] min-w-[60%] ml-4")
            contrast_thress = html.Div(dcc.Slider(0.01, 0.1, 0.01, value = 0.05, id = {'type':'extract-config', 'index': 'sift-contrast'}), className = "w-[30em] min-w-[60%] ml-4")
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
                dcc.Dropdown([{'label': str(i), "value": i} for i in range(32, 257, 8)], value = 256, id = {'type':'extract-config', 'index': 'hist-bins'},
                className = "text-left",  clearable = False)
            ], className = "w-[30em] min-w-[60%] ml-4")

            ret = [
                    html.Div([ html.Label("Número de Discretizaciones: ", className = "text-center"), get_bins ], className = "flex text-center my-8"),
            ]
        elif extract_type == 'cnn':
            model_name = html.Div([
                dcc.Dropdown(options = [
                    {'label': 'RESTNET 18', 'value': 'resnet18'},
                    {'label': 'VGG 16', 'value': 'vgg16'},
                ], value = 'resnet18', id = {'type':'extract-config', 'index': 'cnn-name'}, className = 'text-left', clearable=False)
            ], className = "w-[30em] min-w-[60%] ml-4")
            ret = [
                    html.Div([ html.Label("Modelo Preentrenado: ", className = "text-center"), model_name ], className = "flex text-center my-8"),
            ]

        return html.Div(ret, className = "border-2 border-gray-300 rounded-md py-4 px-2")

    @app.long_callback(
        output = [
            Output("algo-data", 'data'),
            Output("algo-data-paths", 'data'),
            Output("algo-modal-div", "hidden", allow_duplicate=True)
        ],
        inputs = [
            Input("close-algo-btn", "n_clicks"),
            
            State({'type':'extract-config', 'index': ALL}, 'id'),
            State({'type':'extract-config', 'index': ALL}, 'value'),
            State('vocab-size', 'disabled'),
            State('vocab-size', 'value'),
            State('algo-data', 'data'),
        ],
        running=[
            (Output('algo-modal-progress', 'className'), "text-center align-center w-[95vw] h-[100%]", "hidden"),
            (Output('algo-modal-progress' , 'hidden'), False, True),
            (Output('algo-modal-content' , 'hidden'), True, False)
        ],
        prevent_initial_call = True,
    )
    def save_algorithm( _btn, extract_ids, extract_values, vocab_on, vocab_bins, prev_data):
        data = {'method': "", 'config': {}, 'vocab': { 'enable': False, 'bins': None}}
        for i, config_opt in enumerate(extract_ids):
            opt_name = config_opt['index']
            extract_algo, extract_config = opt_name.split("-")
            data['method'] = extract_algo
            data['config'][extract_config] = extract_values[i]
        
        data['vocab']['enable'] = not vocab_on
        if not vocab_on:  data['vocab']['bins'] = vocab_bins

        ret = train(data, TRAIN_IMAGES)
        return data, ret, True

    app.clientside_callback(
        ClientsideFunction('clientalgo', 'open_algo_modal'),
        Output("algo-modal-div", "hidden"),
        Input('change-algoritm-btn', 'n_clicks'),
        prevent_initial_call = True
    )

    app.clientside_callback(
        ClientsideFunction('clientalgo','vocab_enable'),
        Output('vocab-size', 'disabled'),
        Input("algo-vocab-enabled", "on")
    )

    app.clientside_callback(
        ClientsideFunction('clientalgo','reset_algo'),
        output = [
            Output('close-algo-btn', 'n_clicks'), 
            Output('algo-extract-type-select', 'value'),
            Output('algo-vocab-enabled', 'on'),
            Output('vocab-size', 'value'),
        ],
        inputs = [Input('reset-algo-btn', 'n_clicks')],
        prevent_initial_call = True
    )

algo_extract_types = html.Div([
    dcc.Dropdown([
        { "label":"Scale Invariant Feature Transform", "value": "sift" },
        { "label":"ORB", "value": "orb" },
        { "label":"Histograma de Color", "value": "hist" },
        { "label":"Red Convolucional", "value": "cnn" }
    ], value = "sift", id = "algo-extract-type-select", clearable = False,
    className = "text-left")
], className = "w-[30em] min-w-[60%] ml-4")


algoritm_modal = html.Div([

    html.Div([
        html.Div([
            html.H1("Método de Extracción de Características", className = "text-xl text-bold mb-2"),
            html.Div([ html.Label("Método: ", className = "text-center"), algo_extract_types ], className = "flex text-center mb-8"),
            html.Div(id = "algo-extract-form", className = "mr-4")
        ], className = "ml-5 mt-8 border-gray-300 border-r-4"),
        html.Div([
            html.Div([
                html.H1("Creación de Bolsa de Palabras (BOW)", className = "text-xl text-bold mb-2 mr-4 text-center"),
                html.Div(BooleanSwitch(id = "algo-vocab-enabled", on = False, className = ""), className = "mr-12 ml-auto"),
            ], className = "flex"),
            html.Div([
                html.Div([ 
                    html.Label("Número de Palabras: ", className = "text-center"), 
                    html.Div(dcc.Slider(10, 75, step = 5, value = 50, id = 'vocab-size', disabled = True), className = "w-[30em] min-w-[60%] ml-4")
                ], className = "flex text-center my-8"),
            ], className = "border-2 border-gray-300 rounded-md py-4 px-2")
        ], className = "ml-5 mt-8 mr-8")
    ], className = "grid grid-cols-2 gap-4"),


    html.Div([
        html.Button("Cerrar & Guardar", id = "close-algo-btn", className = "mx-auto flex text-center bg-gray-300 rounded-md px-12 py-1 mt-4"),
        html.Button("Reset  & Guardar", id = "reset-algo-btn", className = "mx-auto flex text-center bg-gray-300 rounded-md px-12 py-1 mt-4"),
        html.Span("Puede tardar unos minutos en actualizar si hay un vocabulario.", className = "text-center text-lg text-gray-400 table mx-auto")
    ], className = "align-middle justify-center absolute bottom-10 w-full")

], hidden = False, id = 'algo-modal-content')

algoritm_modal = html.Div([
    algoritm_modal,
    html.Div([
            html.Div([
                Svg([
                    Path(d = "M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z", fill="none"),
                    Path(d = "M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z", fill="currentFill"),
                ], className = "inline w-[30%] h-[30%] mr-2 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600", viewBox="0 0 100 101", fill="none", xmlns="http://www.w3.org/2000/svg"),
                html.Span("Loading ...", className = 'sr-only')
            ], role = 'status', className = "text-center align-center h-full translate-y-[35%]")
    ], id = "algo-modal-progress", className = "", hidden = True)
], hidden = True, id = "algo-modal-div", className = "absolute top-10 bg-white rounded-md w-[95vw] h-[90%] z-10 border-gray-500 border-4 left-[50%] translate-x-[-50%]")