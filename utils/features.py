
from numpy.random import randint, choice
from typing import Callable, List, Tuple
from numpy.typing import NDArray
import numpy as np
import pandas as pd
import cv2

from tqdm.auto import tqdm
from .utils import change_dtype

def extract_features(
        feature_function: Callable[[NDArray[np.uint8]], List[NDArray[np.float]]], 
        images: List[NDArray[np.uint8]],
        min_features: int = -1,
        progress: bool = False
        ) -> Tuple[NDArray[np.float], List[int]]:
    """

    Parameters:
    - feature_function: Callable[[np.ndarray[np.uint8]], List[np.ndarray[np.float]]]

        Una función que dada un imagen devuelve una lista de vectores de características.

    - images: List[np.ndarray[np.uint8]]

        Lista de Imágenes sobre la que calcular todos los vectores:

    - min_features: int (3)

        Número mínimo de características por Imagen

    - progress: bool (False)

        Si se pone una barra de progreso o no

    Returns: Tuple[np.ndarray[np.float], List[int]]
        - np.ndarray[np.float]: 

        Mátriz con los vectores de características. Las filas son los vectores siendo cada columna una característica

        - List[int]

        Lista con la correspondencia entre una fila de la mátriz de características y una imagen
    """

    desclist = []
    indice_imagen = []

    image_number = len(images)
    image_iterator = tqdm(enumerate(images), total = image_number) if progress else enumerate(images)
    for idx, image in image_iterator:
        descs = feature_function(image)
        if isinstance(descs, np.ndarray) and len(descs) >= min_features:
            desclist.append(descs)
            indice_imagen += [idx] * descs.shape[0]

    desclist = np.concatenate(desclist)

    return desclist, indice_imagen

def save_features(features, index, meta, filename):
    """
    Saves the features vector to a csv with the metadata of each one.
    """
    if isinstance(features, list):
        features = np.concatenate(features)

    descs = pd.DataFrame(features)
    descs['image_id'] = index

    descs_save = pd.merge(descs, meta, how = "inner", left_on = "image_id", right_on = "image_id").drop(["train", "image_name", "label", "path"], axis = 1)
    descs_save.to_csv(f"../features/{filename}.csv", index = False)

def load_features(path: str):
    df = pd.read_csv(path)
    images_paths = df[['image_id', 'label_id']]
    
    features = df.drop(['image_id', 'label_id'], axis = 1).values
    features = change_dtype(features)

    return images_paths, features    

