window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientselect: {
        input_image_select: function(_open, _close, _select, is_closed, select_content, select_id, loaded_image){
            if (!is_closed) {
                var activated = window.dash_clientside.callback_context.triggered[0]['prop_id'].split('.')[0];
                
                if (activated === 'close-input-btn') {
                    console.log("nothing");
                    return [loaded_image, !is_closed, loaded_image.uri];
                    }

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
        },
        zoom_select: function (clicks, images) {
            var activated = window.dash_clientside.callback_context.triggered[0]['prop_id'].split('.')[0];
            activated = JSON.parse(activated);
            var n_img = activated.index;
            return images[n_img][0].props.src;
        }
    },
    clientalgo: {
        vocab_enable: function(enable_state){
            return !enable_state;
        },
        reset_algo: function(_n) {
            return [1, "sift", false, 50];
        },
        open_algo_modal: function(_o){
            return false;
        }
    }
});
