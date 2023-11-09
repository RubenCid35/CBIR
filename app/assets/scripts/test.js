
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    testside: {
        func_test:function(_open, _close, _select, is_closed, select_content, select_id, loaded_image){
            if (!is_closed) {
                var activated = window.dash_clientside.callback_context.triggered[0]['prop_id'].split('.')[0];
                
                if (activated === 'close-input-btn.n_clicks') {
                    console.log("nothing");
                    return [loaded_image, !is_closed, loaded_image.uri];
                    }

                console.log(activated);
                activated = JSON.parse(activated);
                let n_img = activated.index;
                
                let newLoad = {
                    uri: select_content[n_img][0].props.src,
                    label: "none"
                };

                return [newLoad, !is_closed, newLoad.uri];
            } else {
                return [loaded_image, !is_closed, loaded_image.uri];
            }
        }
    }
});

