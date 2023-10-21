
import cv2
import numpy as np
import pandas as pd
from scipy.spatial import KDTree

from typing import List, Tuple, Optional, Callable, Union
from numpy.typing import NDArray

def _drop_duplicate(lista: List[int]):
    ret = []
    seen_image = set()
    for l in lista:
        if l in seen_image: continue
        ret.append(l)
        seen_image.add(l)
    return ret

def minmin_retrival(
        query_desc: NDArray[np.float],
        base_features: NDArray[np.float],
        meta: Union[pd.DataFrame, List[int]],
        best_k: int = 10,
        distance_function = cv2.NORM_L2
    ) -> List[int]:
    """
    
    """
    assert best_k >= 1, "Tienes que coger al menos una imagen"
    
    if distance_function == cv2.NORM_L2 or distance_function == cv2.NORM_L1 or cv2.NORM_HAMMING or cv2.NORM_HAMMING:    
        matcher = cv2.BFMatcher_create(distance_function)
    else:
        matcher = cv2.BFMatcher_create()
    
    query_desc = query_desc.astype(base_features.dtype)

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