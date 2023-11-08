import dash
from dash import html, dcc

# Banner with the name of the Project
banner = html.P( [
    html.A(["Content-Based Image Retrival"],
    href = "/", className = "")
], className="text-3xl p-5 col-span-5 ")

# Github Link
github = html.Div([
    html.A([
        html.Img(),
        "Github"
    ], href = "https://github.com/RubenCid35/CBIR")
], className = "text-black text-lg text-right pr-5 border-r-2 border-gray-300 hover:underline ") 

# Report PDF Link

report = html.Div([
    html.A([
        "Reporte del Projecto"
    ], href = "")
], className = "text-black text-lg text-center border-r-2 border-gray-300 hover:underline") 

# Autores
autores = html.Details([
    
    html.Summary(["Autores"], className=""),
    html.Ul([
        html.Li("Rubén Cid Costa"),
        html.Li("Rodrigo Durán Andrés"),
        html.Li("TODO"),
        html.Li("TODO"),
    ], className = "absolute bg-white border-gray-500 border-solid border-2 list-decimal px-10 py-2")
], className = "text-black text-lg text-left px-5")

# Full Header
header_layout = html.Header([
        html.Div([
            banner,
            html.Div( [
        
                github,
                report,
                autores
        
            ], className="col-start-6 col-end-11 p-5 grid grid-cols-3 ")
        
        ], className = "w-4/5 grid grid-cols-10 mx-auto py-3 "),
        
        html.Hr(className = "border-1.5 border-black mb-3"),
    ], className="z-40 w-full m-auto top-0 bg-white")

