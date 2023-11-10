import pandas as pd
import numpy as np

import cv2

def load_images(train: bool = True):
    """
    Loads a dataframe with the image metadata and a list with the images in RGB Format
    """
    if train: path = '../images/train.csv'
    else: path = '../images/test.csv'
    images_paths = pd.read_csv(path)
    images = []

    label_map = { "bell pepper" : 0, "brown bear" : 1, "bucket" : 2, "bullfrog" : 3, "espresso" : 4, "lemon" : 5, "school bus" : 6, "soda bottle" : 7, "sports car" : 8, "tarantula" : 9}


    for _, row in images_paths.iterrows():
        img = cv2.imread("../" + row['path'])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        images.append(img)
    
    images_paths['label_id'] = images_paths['label'].map(label_map)
    images_paths['image_id'] = images_paths.index
    return images_paths, images


def change_dtype(val):
    if np.issubdtype(val.dtype, np. integer):
        val = val.astype(np.uint8)
    else:
        val = val.astype(np.float32)

    return val
