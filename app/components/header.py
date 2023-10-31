import dash
from dash import html, dcc

# Banner with the name of the Project
banner = html.P( [
    html.A(["Content-Based Image Retrival"],
    href = "/", className = "")
], className="text-3xl p-5 col-start-1 col-end-5 hover:underline")

# Github Link
github = html.Div([
    html.A([
        html.Img(),
        "Github"
    ], href = "https://github.com/RubenCid35/CBIR")
], className = "col-start-1 col-span-2 text-black text-lg flex content-center flex-col justify-center text-right hover:underline") 

# Report PDF Link

report = html.Div([
    html.A([
        "Reporte del Projecto"
    ], href = "")
], className = "col-start-3 col-span-2 text-black text-lg flex content-center flex-col justify-center text-center hover:underline") 

# Autores
autores = html.Div([
    html.Details([
        html.Summary(["Autores"], className=""),
        html.Ul([
            html.Li("Rubén Cid Costa"),
            html.Li("TODO"),
            html.Li("TODO"),
            html.Li("TODO"),
        ], className = "absolute bg-white border-gray border-solid border-2")
    ], className = "")
], className = "col-start-5 col-span-2 text-black text-lg flex content-center flex-col justify-center text-left")

# Full Header
header_layout = html.Header([
        html.Div([
            banner,
            html.Div( [
                github,
                report,
                autores
            ], className="col-span-4 p-5 grid grid-cols-7 col-start-6")
        ], className = "w-4/5 grid grid-cols-10 px-4 mx-auto py-3"),
        html.Hr(className = "border-1.5 border-black mb-3"),
    ], className="z-40 w-full m-auto top-0 bg-white")

