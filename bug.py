
import os
import shutil
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import librosa
import scipy
from joblib import Parallel,delayed
from scipy.spatial.distance import cdist


NUM_SONGS = 4243
with open('./3500.csv', 'r') as f:
    contentf = f.readlines()

def getScore(dists):
    score = 0
    L = dists.shape[0]
    ct=0
    scorelist = np.zeros((L,))
    for n in range(0,L):
        currentscore = dists[n]
        i = np.argmin(currentscore)
        score = score + np.min(currentscore)
        scorelist[ct]=np.min(currentscore)
        dists = np.delete(dists,i, axis=1)
        ct=ct+1
    scorelist = scorelist[0:ct]
    return np.median(scorelist)

# Disable GPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Load model
model = hub.load('https://tfhub.dev/google/yamnet/1')
