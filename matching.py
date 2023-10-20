
import cv2
import numpy as np
import pandas as pd
from scipy.spatial import KDTree

from typing import List, Tuple, Optional, Callable
from numpy.typing import NDArray

def minmin_retrival(
        query_desc: NDArray[np.float],
        base_features: NDArray[np.float],
        base_meta: List[int],
        best_k: int = 10,
        distance_function: Callable[[NDArray[np.float], NDArray[np.float]], float] = cv2.NORM_L2
    ) -> List[int]:
    """
    
    """
    

    return []