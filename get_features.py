
import pandas as pd
from numpy.random import randint, choice
import shutil

import os

TRAINING_IMAGES: int = 50
TEST_IMAGES    : int = 10

df = pd.read_csv("train.csv")
samples = df.groupby('label').sample(TRAINING_IMAGES + TEST_IMAGES, replace = False).reset_index()
samples['train'] = True
samples.loc[samples.groupby('label').sample(TEST_IMAGES, replace = False).index, 'train'] = False

for _, row in samples.iterrows():
    if not os.path.exists(f"images/{row['label']}"): 
        os.mkdir(f"images/{row['label']}")
        print("Making Dir:", f"images/{row['label']}")
    shutil.copy(f"archive(1)/128x128/{row['label']}/{row['image_name']}", f"images/{row['label']}/{row['image_name']}")

samples.to_csv("images_meta.csv")