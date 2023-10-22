
import cv2
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from collections import OrderedDict

from typing import List, Tuple, Optional, Callable, Union
from numpy.typing import NDArray

from utils import change_dtype

def _drop_duplicate(lista: List[int]):
    ret = []
    seen_image = set()
    for l in lista:
        if l in seen_image: continue
        ret.append(l)
        seen_image.add(l)
    return ret


def minmin_retrival(
        query_desc: NDArray[Union[np.float, np.integer]],
        base_features: NDArray[Union[np.float, np.integer]],
        meta: Union[pd.DataFrame, List[int]],
        best_k: int = 10,
        distance_function = cv2.NORM_L2
    ) -> List[int]:
    """
    Calcula la distancia entre descriptores y devuelve una lista con las K imágenes con 
    descriptores más cercanas. 

    Parámetros:
    - query_desc: NDArray[Union[np.float, np.integer]]

        Mátriz con los descriptores como filas de una única imagen.

    - base_features: NDArray[Union[np.float, np.integer]] 

        Mátriz con los descriptores como filas. Se obtiene de la función `extract_features`

    - meta: Union[pd.DataFrame, List[int]]
    
        Lista de indices de imágenes o Dataframe usado para asociar cada descriptor de `base_features` con una imagen que devolver
        
    - best_k: int (default 10)

        Número de Imágenes a Devolver
    
    - distance_function: (Default `cv2.NORM_L2`)
    
        Norma usada para calcular la distancia. Tiene que ser una norma de OpenCV. No hace falta cambiarla
        en la mayoría de casos.

    Retorno:
    
    List[int]: Listando de Índices de Imágenes

    """
    assert best_k >= 1, "Tienes que coger al menos una imagen"
    
    if distance_function == cv2.NORM_L2 or distance_function == cv2.NORM_L1 or cv2.NORM_HAMMING or cv2.NORM_HAMMING:    
        matcher = cv2.BFMatcher_create(distance_function)
    else:
        matcher = cv2.BFMatcher_create()
    
    query_desc = query_desc.astype(base_features.dtype)

    query_desc = change_dtype(query_desc)
    assert query_desc.shape[1] == base_features.shape[1], "Los descriptores en la base de datos y los de consulta deben tener el mismo tamaño" 
    matches = matcher.knnMatch(query_desc.reshape(-1, base_features.shape[1]), base_features, 50)
    
    min_desc = []
    take = max(best_k, 20)
    for match in matches: # 
        if match is None: continue
        closes_matches = match[:take]
        min_desc.extend(closes_matches)

    min_desc = sorted(min_desc, key = lambda m: m.distance)
    map_desc_image = lambda m: meta.loc[m.trainIdx, 'image_id'] if isinstance(meta, pd.DataFrame) else meta[m.trainIdx]
    min_desc = list(map(map_desc_image, min_desc))

    return _drop_duplicate(min_desc)[:best_k]

def match_all_images(
        query_descs: NDArray[Union[np.float, np.integer]],
        query_meta: Union[pd.DataFrame, List[int]],
        base_features: NDArray[Union[np.float, np.integer]],
        meta: Union[pd.DataFrame, List[int]],
        best_k: int = 10,
        distance_function = cv2.NORM_L2
    ) -> List[List[int]]:
    """
    Calcula la distancia entre descriptores y devuelve una lista con las K imágenes con 
    descriptores más cercanas. 

    Parámetros:
    - query_desc: NDArray[Union[np.float, np.integer]]

        Mátriz con los descriptores como filas de una única imagen.

    - query_meta: Union[pd.DataFrame, List[int]]

        Lista de indices de imágenes o Dataframe usado para asociar cada descriptor de `base_features` con una imagen que devolver

    - base_features: NDArray[Union[np.float, np.integer]] 

        Mátriz con los descriptores como filas. Se obtiene de la función `extract_features`

    - meta: Union[pd.DataFrame, List[int]]
    
        Lista de indices de imágenes o Dataframe usado para asociar cada descriptor de `base_features` con una imagen que devolver
        
    - best_k: int (default 10)

        Número de Imágenes a Devolver
    
    - distance_function: (Default `cv2.NORM_L2`)
    
        Norma usada para calcular la distancia. Tiene que ser una norma de OpenCV. No hace falta cambiarla
        en la mayoría de casos.

    Retorno:
    
    List[List[int]]: Listado de los resultados de cada imagen.
    """
    ret = []
    if isinstance(query_meta, pd.DataFrame) and 'image_id' in query_meta.columns:
        for image in query_meta['image_id'].unique():
    
            indices = query_meta[query_meta['image_id'] == image].index.values
            img_desc = query_descs[indices]
    
            selected_images = minmin_retrival(img_desc, base_features, meta, best_k=best_k, distance_function=distance_function)
            ret.append(selected_images)
    
    elif isinstance(query_meta, list):

        indices = OrderedDict()
        for i, v in enumerate(query_meta):
            if v not in indices:
                indices[v] = [i]
            else:
                indices[v].append(i)


        for index in indices.values():
            img_desc = query_descs[index]
    
            selected_images = minmin_retrival(img_desc, base_features, meta, best_k=best_k, distance_function=distance_function)
            ret.append(selected_images)
    else: 
        raise ValueError("query_meta debe ser un dataframe o una lista con indices de imágens")

    return ret