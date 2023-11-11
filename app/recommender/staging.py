
import os
import cv2
import numpy  as np
import pandas as pd

from functools import partial

from sklearn.cluster import KMeans

from utils.utils import load_images
from utils.features import load_features, save_features, extract_features
from utils.matching import match_all_images
from sklearn.preprocessing import normalize

from json import dumps
from pickle import dump

from hashlib import sha256

TRAIN_META, TRAIN_IMAGES = load_images(True)
TEST_META, TEST_IMAGES = load_images(False)

PRECOMPUTED = None

def normalize_hist(vector):
    return vector / np.linalg.norm(vector)

def check_features_file(save_name):
    def check_name(file_name):
        file_name = file_name.split(".")[0]
        return save_name == file_name
    return any(map(check_name, os.listdir('../features')))
        
def sift_descriptor(image, octaves: int = 8, thress: float = 0.1):
    orb = cv2.SIFT_create(nfeatures = 50,  nOctaveLayers = octaves, contrastThreshold = thress, edgeThreshold = 10, sigma = 1.6  )
    img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, descs = orb.detectAndCompute(img, None)
    return descs

def orb_descriptor(image, wta = 4, score = cv2.ORB_HARRIS_SCORE):
    orb = cv2.ORB_create(nfeatures = 50, scoreType = score, WTA_K = wta)
    img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, descs = orb.detectAndCompute(img, None)
    return descs

def cch_descriptor(image, bins = 32):
    rbin = normalize_hist(np.histogram(image[:, :, 0], bins = bins, range = [0, 255])[0])
    gbin = normalize_hist(np.histogram(image[:, :, 1], bins = bins, range = [0, 255])[0])
    bbin = normalize_hist(np.histogram(image[:, :, 2], bins = bins, range = [0, 255])[0])

    return np.concatenate([rbin, gbin, bbin], axis = 0).reshape(1, -1).astype(np.float32) # Un Vector con solo columnas

def prepare_extraction(algo):
    algo_name = algo['method']
    if algo_name == 'sift':
        algorithm = partial(sift_descriptor, octaves = algo['config']['octaves'], thress = algo['config']['contrast'])
    elif algo_name == 'orb':
        score = cv2.ORB_HARRIS_SCORE if algo['config']['compute'] == 'harris' else cv2.ORB_FAST_SCORE
        algorithm = partial(orb_descriptor, score = score, wta = algo['config']['wta'])

    elif algo_name == 'hist':
        algorithm = partial(cch_descriptor, bins = algo['config']['bins'])

    else:
        # TODO Change To CNN
        algorithm = sift_descriptor # partial(sift_descriptor, octaves = algo['config']['octaves'], thress = algo['config']['contrast'])
        

    print(algo_name, dumps(algo['config'], sort_keys=True), dumps(algo['vocab']))
    return algorithm

def train(algo, images, save = True):
    # Extract Features
    algo_name = algo['method']
    config_phrase = dumps(algo['config'], sort_keys=True).encode('utf-8')
    config_phrase = sha256(config_phrase).hexdigest()

    algorithm = prepare_extraction(algo)
    
    save_name = algo_name + "-" + config_phrase
    if algo['vocab']['bins']:
        vocab_bin = algo['vocab']['bins']
        save_name = save_name + "-vocab-" + str(vocab_bin)

    if check_features_file(save_name): 
        if not algo['vocab']['bins']:
            return ('../features/' + save_name + '.csv', None)
        else: 
            return ('../features/' + save_name + '.csv', '../model/' + save_name + '.sav')
    
    save_name_model = None

    descriptores, index = extract_features(algorithm, images, min_features=-1)
    # Vocab
    vocab_on  = algo['vocab']['enable']
    if vocab_on:
        vocab_bin = algo['vocab']['bins']

        vocab_model = KMeans(n_clusters=vocab_bin, init = 'k-means++', random_state = 20010)
        vocab_model = vocab_model.fit(descriptores)
        descriptores = vocab_model.predict(descriptores)

        idxs = {}
        for i, item in enumerate(index):
            if item not in idxs: idxs[item] = []
            idxs[item].append(i)
        
        pairs = {}
        for image_id, idx in idxs.items():
            vocab = descriptores[idx]
            vocab = np.bincount(vocab, minlength=vocab_bin)
            pairs[image_id] = normalize( vocab.reshape((1, -1)) ).reshape((-1))

        ret = pd.DataFrame.from_dict(pairs, orient = 'index')
        if save:
            save_name_model = save_name + "-model.sav"
            dump(vocab_model, open("../model/" + save_name_model, 'wb'))        

            ret['image_id'] = ret.index
            ret['label_id'] = 0 # Not used
            ret.to_csv("../features/" + save_name + ".csv")

    else:
        ret = pd.DataFrame(descriptores)
        ret['image_id'] = index
        ret['label_id'] = 0 # Not used

        if save: ret.to_csv("../features/" + save_name + ".csv")


    return save_name + '.csv', save_name_model
