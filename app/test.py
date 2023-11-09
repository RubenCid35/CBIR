from dash import Dash, html
from dash.dependencies import Output, Input, ClientsideFunction

# Create app.
app = Dash(prevent_initial_callbacks=True)
app.layout = html.Div([
    html.Button("Button 1", id="btn1"), html.Button("Button 2", id="btn2"), html.Div(id="log")
])
app.clientside_callback(ClientsideFunction('clientside', 'func_test'), Output("log", "children"), [Input("btn1", "n_clicks"), Input("btn2", "n_clicks")])

if __name__ == '__main__':
    app.run_server(debug = True)