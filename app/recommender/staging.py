
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

import torch
import torch.nn as nn 
from torchvision import models, transforms

from json import dumps as stringfy
from pickle import dump, load

from hashlib import sha256

TRAIN_META, TRAIN_IMAGES = load_images(True)
TEST_META, TEST_IMAGES = load_images(False)

CONFIG        = ""
PRECOMPUTED   = None
ML_MODEL      = ("", None)
VOCAB_MODEL   = None

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

def cnn_descriptor(image):
    global ML_MODEL

    image = image.transpose(2, 0, 1)
    image = torch.from_numpy(image).unsqueeze(0).float()

    # Definir la transformación para preprocesar la imagen
    preprocess = transforms.Compose([
        transforms.ToPILImage(),     # Convierte el tensor a una imagen de PIL
        transforms.Resize(256),      # Redimensiona la imagen a 256x256
        transforms.CenterCrop(224),  # Recorta la imagen al centro 224x224
        transforms.ToTensor(),       # Convierte la imagen de PIL a tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normaliza los valores de los píxeles
    ])
    # Aplicar la transformación a la imagen
    image = preprocess(image[0])
    with torch.no_grad():
        features = ML_MODEL[1](image.unsqueeze(0))
    return np.array(features)

    

def prepare_extraction(algo):
    global ML_MODEL

    algo_name = algo['method']
    if algo_name == 'sift':
        algorithm = partial(sift_descriptor, octaves = algo['config']['octaves'], thress = algo['config']['contrast'])
    elif algo_name == 'orb':
        score = cv2.ORB_HARRIS_SCORE if algo['config']['compute'] == 'harris' else cv2.ORB_FAST_SCORE
        algorithm = partial(orb_descriptor, score = score, wta = algo['config']['wta'])

    elif algo_name == 'hist':
        algorithm = partial(cch_descriptor, bins = algo['config']['bins'])

    else:
        if ML_MODEL[0] != algo['config']['name']:
            model_name = algo['config']['name']
            if model_name == 'vgg16':
                model = models.vgg16(weights = models.VGG16_Weights.DEFAULT)
            else:
                model = models.resnet18(weights = models.ResNet18_Weights.DEFAULT)
            ML_MODEL = (model_name, model)

        ML_MODEL[1].eval()
        algorithm = cnn_descriptor # partial(sift_descriptor, octaves = algo['config']['octaves'], thress = algo['config']['contrast'])
        

    print(algo_name, stringfy(algo['config'], sort_keys=True), stringfy(algo['vocab']))
    return algorithm

def train(algo, images, save = True):
    global ML_MODEL

    # Extract Features
    algo_name = algo['method']
    config_phrase = stringfy(algo['config'], sort_keys=True).encode('utf-8')
    config_phrase = sha256(config_phrase).hexdigest()

    algorithm = prepare_extraction(algo)
    
    save_name = algo_name + "-" + config_phrase
    if algo['vocab']['bins']:
        vocab_bin = algo['vocab']['bins']
        save_name = save_name + "-vocab-" + str(vocab_bin)

    CONFIG = save_name
    if check_features_file(save_name): 
        if not algo['vocab']['enable']:
            PRECOMPUTED = load_features('../features/' + save_name + '.csv')
            VOCAB_MODEL = None

            return ('../features/' + save_name + '.csv', None)
        else: 
            PRECOMPUTED = load_features('../features/' + save_name + '.csv')
            VOCAB_MODEL = load(open('../model/' + save_name + '.sav', 'rb'))
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
            # Store
            VOCAB_MODEL = vocab_model
            PRECOMPUTED = ret.copy()

    else:
        ret = pd.DataFrame(descriptores)
        ret['image_id'] = index
        ret['label_id'] = 0 # Not used

        if save: ret.to_csv("../features/" + save_name + ".csv")
        VOCAB_MODEL = None
        PRECOMPUTED = ret.copy()

    return save_name + '.csv', save_name_model
