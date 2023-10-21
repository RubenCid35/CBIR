import pandas as pd
import numpy as np

from typing import List, Dict, Tuple
from numpy.typing import NDArray

from tqdm import tqdm


def calculate_metrics(
    test_results: List[List[int]],
    train_meta: pd.DataFrame,
    test_meta : pd.DataFrame,
    scores: Tuple[int] = (1, 5, 10),
    progress: bool = False,
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Calcula el Recall@K y Precision@K para unas queries. Se usa la etiqueta de las imágenes
    para ver si los resultados son relevantes. 

    Parámetros:
    test_results: List[List[int]]

        Listado de Resultados de Queries. Cada elemento de la primera lista es una lista de ids de imágenes resultantes

    train_meta: pd.DataFrmae
    
        Dataframe con información de etiqueta de cada imagen. El id de una imagen corresponde con su indice. Es el dataframe
        de las imágenes en la base de datos.

    test_meta: pd.DataFrmae
    
        Dataframe con información de etiqueta de cada imagen. El id de una imagen corresponde con su indice. Es el dataframe
        de las imágenes usadas para la query

    scores: Tuple[int]
    
        Tupla con los K para el cálculo del recall@K y precision@K. Si hay una K más alto del número de imágenes devueltas
        por query no se calcula.

    progress: bool (False)
    
        Barra de Progreso

    Retorno:
    - Diccionario de Recall@K
    - Diccionario de Precision@K

    Referencia:

    https://datascience.stackexchange.com/questions/92247/precisionk-and-recallk

    """
    if len(scores) == 0: scores = [1, 5, 10]

    ret_len = len(test_results[0])
    scores = list(filter(lambda k: ret_len >= k, scores))

    recalls = [[] for _ in scores]
    precisions = [[] for _ in scores]

    result_labels = []
    test_labels   = test_meta['label_id'].values.tolist()
    for result_images in test_results:
        result_labels.append(train_meta.loc[result_images, 'label_id'].values)

    iterator = tqdm(zip(test_labels, result_labels), total = len(test_labels)) if progress else zip(test_labels, result_labels)
    for true_label, pred_labels in iterator:
        relevant = list(map(lambda v: 1 if v == true_label else 0, pred_labels))
        total_relevant = sum(relevant)
        for i, k in enumerate(scores):
            rel = sum(relevant[:k])
            if total_relevant == 0: recall = 0
            else:
                recall = rel/total_relevant
            
            recalls[i].append(recall)
            precision = rel/k
            precisions[i].append(precision)


    recalls = {'Recall@' + str(k): round(np.mean(scores), 4) for k, scores in zip(scores, recalls)}
    precisions = {'Precision@' + str(k): round(np.mean(scores), 4) for k, scores in zip(scores, precisions)}

    return recalls, precisions
