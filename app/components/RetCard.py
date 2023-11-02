import dash
from dash import dcc, html, Input, Output, State, ctx, ALL

from utils.utils import load_images

NO_IMAGE_ICON: str = r"https://img.freepik.com/premium-vector/default-image-icon-vector-missing-picture-page-website-design-mobile-app-no-photo-available_87543-11093.jpg?w=826"

# TODO Remove Later
TEST_IMAGES, _ = load_images(train = False)
TEST_IMAGES = TEST_IMAGES.sample(n = 40, random_state = 1010)


zoomed_image = html.Div([
    html.Img(id = "zoomed-image-img", className = "object-fill max-w-[90%] w-[350px] min-w-[256px] rounded-lg aspect-square border-gray-500 border-2", src = NO_IMAGE_ICON )
], className = "w-full mx-auto flex justify-center overflow-hidden mt-[4vh]")



def output_callbacks(app: dash.Dash):

    @app.callback(
        Output("zoomed-image-img", "src"),
        Input({"type": "relevant-image-img", "index": ALL}, "n_clicks"),
        State({"type": "relevant-image-img", "index": ALL}, "children"),
        prevent_initial_call = True
    )
    def zoom_image(clicks, images):
        triggered = ctx.triggered_id
        n_img = triggered['index']
        uri = images[n_img][0]['props']['src']
        return uri

    return None


def generate_image_button(image_path, _id):
    _id = {
        'type': "relevant-image-img",
        "index": _id
    }
    
    return html.Button([
        html.Img(className = "object-fill w-[100%] min-w-[128px] aspect-square mx-auto", 
                 src = dash.get_asset_url(image_path))
    ], className = "w-[156px]", id = _id)

def populate_images():
    ret = []
    for i, path in enumerate(TEST_IMAGES['path']):
        ret.append(generate_image_button(path, i))

    return ret

# 
output_card = html.Div([
    html.Div([ 
        html.H1("Imágenes más Relevantes", className = "text-black text-4xl text-center text-bold my-3"),
        zoomed_image,
    ], className = "col-span-2"),
    html.Div(
        children = populate_images(),    
        className = "col-span-3 grid big:grid-cols-4 grid-cols-3 gap-2 mx-2 my-6 overflow-scroll h-[70vh] big:h-[60vh]", 
        id = "result-images-div")
], className = "col-span-6 grid grid-cols-5 border-gray-400 border-2 rounded-md")

