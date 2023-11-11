
import os
import cv2
import numpy  as np
import pandas as pd

from functools import partial

from sklearn.cluster import KMeans

from utils.utils import load_images
from utils.features import load_features, save_features, extract_features
from utils.matching import minmin_retrival
from sklearn.preprocessing import normalize

from json import dumps
from pickle import load

from hashlib import sha256
from .staging import TRAIN_IMAGES, TRAIN_META
from .staging import ML_MODEL, VOCAB_MODEL, PRECOMPUTED, CONFIG

from .staging import prepare_extraction
from .staging import cch_descriptor, sift_descriptor, orb_descriptor

def recommend(query_image, algo, train_desc_path, train_model_path):
    print( train_desc_path, train_model_path)
    if isinstance(query_image, str): 
        query_image = cv2.imread(query_image)
        query_image = cv2.cvtColor(query_image, cv2.COLOR_BGR2RGB)

    # Feature Extraction
    print("ALGORITHM:", dumps(algo))
    extraction = prepare_extraction(algo)
    features = extraction(query_image)
    print(extraction, algo)
    if features is None: return None

    if algo['vocab']['enable']:
        vocabulary = VOCAB_MODEL    
        words = vocabulary.predict(features)
        words = np.bincount(words, minlength=algo['vocab']['bins'])
        features = normalize( words.reshape((1, -1)) ).reshape((-1)).reshape((1, -1))

    # Load Database
    meta, precomputed = load_features('../features/' + train_desc_path, index = True)
    print(features.shape, precomputed.shape)
    print('USED FEAUTRES: ../features/' + train_desc_path)


    # Recommend
    recommended = minmin_retrival(features, precomputed, meta, best_k=20)
    return recommended