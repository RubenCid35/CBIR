import dash
from dash import dcc, html, Input, Output, State, ctx, ALL, ClientsideFunction

from utils.utils import load_images
from recommender.staging import TEST_META,TRAIN_META
from recommender.recommend import recommend

NO_IMAGE_ICON: str = r"https://img.freepik.com/premium-vector/default-image-icon-vector-missing-picture-page-website-design-mobile-app-no-photo-available_87543-11093.jpg?w=826"

# TODO Remove Later
sample = TEST_META.sample(n = 40, random_state = 1010)

def generate_image_button(image_path, _id):
    _id = {
        'type': "relevant-image-img",
        "index": _id
    }
    
    return html.Button([
        html.Img(className = "object-fill w-[100%] min-w-[128px] aspect-square mx-auto", 
                 src = dash.get_asset_url(image_path))
    ], className = "w-[156px]", id = _id)





def output_callbacks(app: dash.Dash):
    app.clientside_callback(
        ClientsideFunction('clientselect', 'zoom_select'),
        Output("zoomed-image-img", "src"),
        Input({"type": "relevant-image-img", "index": ALL}, "n_clicks"),
        State({"type": "relevant-image-img", "index": ALL}, "children"),
        prevent_initial_call = True
    )

    @app.long_callback(
        Output("result-images-div", 'children'),
        inputs = [
            Input("search-relevant-images-btn", 'n_clicks'),
            State("query-image-data", 'data'),
            State("algo-data", 'data'),
            State("algo-data-paths", 'data')
        ],
        running= [(Output('search-relevant-images-btn', 'disabled'), True, False)],
        prevent_initial_call = True
    )
    def search_recommendations(btn, image_path, algo, paths):
        query = image_path['uri'].replace('/assets/', '../')
        relevant = recommend(query, algo, paths[0], paths[1])
        images = TRAIN_META.iloc[relevant]['path']
        ret = []
        for i, img in enumerate(images):
            btn_image = generate_image_button(img, i)
            ret.append(btn_image)
        return ret


def populate_images():
    ret = []
    for i, path in enumerate(sample['path']):
        ret.append(generate_image_button(path, i))

    return ret

zoomed_image = html.Div([
    html.Img(id = "zoomed-image-img", className = "object-fill max-w-[90%] w-[350px] min-w-[256px] rounded-lg aspect-square border-gray-500 border-2", src = NO_IMAGE_ICON )
], className = "w-full mx-auto flex justify-center overflow-hidden mt-[4vh]")


output_card = html.Div([
    html.Div([ 
        html.H1("Imágenes más Relevantes", className = "text-black text-4xl text-center text-bold my-3"),
        zoomed_image,
    ], className = "col-span-2"),
    html.Div(
        children = [],    
        className = "col-span-3 grid big:grid-cols-4 grid-cols-3 gap-2 mx-2 my-6 overflow-scroll h-[70vh] big:h-[60vh]", 
        id = "result-images-div")
], className = "col-span-6 grid grid-cols-5 border-gray-400 border-2 rounded-md")

