import dash
from dash import dcc, html, Input, Output
import time

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Button("Start Computation", id="start-button"),
    html.Div(id="modal", children=[
        # Your modal content here
    ]),
    dcc.Interval(id="progress-interval", n_intervals=0, interval=1000),
    dcc.Loading(html.Div("Calculado sobre la Base de Datos"), id="loading-div"),
    dcc.Loading(dcc.Progress(id="progress-bar", max=100, value=0, striped=True, animated=True), id="loading-bar"),
    html.Div(id="output-div")
])

@app.callback(
    Output("modal", "hidden"),
    Output("loading-div", "hidden"),
    Output("loading-bar", "hidden"),
    Output("output-div", "children"),
    Output("progress-bar", "value"),
    Input("start-button", "n_clicks"),
    Input("progress-interval", "n_intervals"),
)
def start_computation(n_clicks, n_intervals):
    if n_clicks is None:
        return False, True, True, html.Div([]), 0  # Show modal, hide loading div, loading bar, and an empty content initially

    if n_intervals <= 100:
        return False, False, False, [], n_intervals

    time.sleep(5)  # Simulate some time-consuming computations

    return True, True, True, html.Div("Computation Complete"), 100

if __name__ == "__main__":
    app.run_server(debug=True)
