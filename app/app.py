import dash
import plotly.express as px

from dash import dcc, html

from components.header import header_layout


# Script tailwind para el estilo
external_script = ["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}]

app = dash.Dash(
   name =  __name__,
    title = "Content-Based Image Retrival",
    external_scripts=external_script,
)

app.scripts.config.serve_locally = True

# Layout

app.layout = html.Div([
    # Header
    header_layout
    # Image Query + Stats
    

    # Image Results

], className="")


if __name__ == "__main__":
    app.run_server(debug=True)