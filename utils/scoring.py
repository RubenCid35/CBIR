import pandas as pd
import numpy as np

from typing import List, Dict, Tuple
from numpy.typing import NDArray

from tqdm import tqdm

def precision_at_K(relevance_vector, K, _total_relevant):
    relevant_at_K = sum(relevance_vector[:K])
    return relevant_at_K / K if K > 0 else 0.0

def recall_at_K(relevance_vector, K, total_relevant):
    relevant_at_K = sum(relevance_vector[:K])
    return relevant_at_K / total_relevant if total_relevant > 0 else 0.0

def r_precision(relevance_vector, K, total_relevant):
    return precision_at_K(relevance_vector, K, total_relevant)


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
    - Diccionario de R-Precision@K

    Referencia:
    https://www.shaped.ai/blog/evaluating-recommendation-systems-part-1
    """
    if len(scores) == 0: scores = [1, 5, 10]

    ret_len = len(test_results[0])
    scores = list(filter(lambda k: ret_len >= k, scores))

    precision = [[] for _ in scores]
    recall = [[] for _ in scores]
    rprecision = [[] for _ in scores]

    result_labels = []
    test_labels   = test_meta['label_id'].values.tolist()
    for result_images in test_results:
        result_labels.append(train_meta.loc[result_images, 'label_id'].values)

    relevant_database = train_meta['label_id'].value_counts()


    iterator = tqdm(zip(test_labels, result_labels), total = len(test_labels)) if progress else zip(test_labels, result_labels)
    for true_label, pred_labels in iterator:
        relevant = list(map(lambda v: 1 if v == true_label else 0, pred_labels))
        total_relevant = relevant_database[true_label]
        for i, k in enumerate(scores):
            precision[i].append(precision_at_K(relevant, k, total_relevant))
            recall[i].append(recall_at_K(relevant, k, total_relevant))
            rprecision[i].append(r_precision(relevant, k, total_relevant))
                    

    recall = [ np.mean(rec) for rec in recall]
    precision = [ np.mean(pred) for pred in precision]
    rprecision = [ np.mean(pred) for pred in rprecision]

    ret = pd.DataFrame({
        'Precision@K': precision,
        'Recall@K': recall,
        'R-Precision@K': rprecision,

    }, index = scores)
    ret.index.name = 'K'
    return ret
