import os
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import librosa
from joblib import Parallel, delayed
from scipy.spatial.distance import cdist

# ================= CONFIGURATION =================
NUM_SONGS = 14905 # Ensure this matches your uploaded data count
os.environ["CUDA_VISIBLE_DEVICES"] = "-1" # Force CPU for Cloud stability

print("--> [Lyra Cloud] Loading Neural Engine...")
model = hub.load('https://tfhub.dev/google/yamnet/1')

# --- PATHS (Adjusted for Cloud) ---
# '.' means "Look in the current folder"
songpath = './datasongs/' 
outputpath = 'static/music/'

def getScore(dists):
    """
    ORIGINAL LOGIC: Greedy Match & Delete.
    """
    score = 0
    L = dists.shape[0]
    ct = 0
    scorelist = np.zeros((L,))
    
    for n in range(0, L):
        if dists.shape[1] == 0: break 
        
        currentscore = dists[n]
        i = np.argmin(currentscore)
        
        val = np.min(currentscore)
        score = score + val
        scorelist[ct] = val
        
        # Delete matched frame
        dists = np.delete(dists, i, axis=1)
        ct = ct + 1
        
    scorelist = scorelist[0:ct]
    return np.median(scorelist) if len(scorelist) > 0 else 100.0

def clean_filename_for_search(raw_name):
    """Clean 'Artist####Title####ID.mp3' -> 'Artist Title'"""
    name = raw_name.replace('.mp3', '')
    if '####' in name:
        parts = name.split('####')
        name = f"{parts[0]} {parts[1]}" if len(parts) > 1 else parts[0]
    return name.replace('_', ' ').strip()

# Check for input
if os.path.exists("static/music/query1.mp3"):
    print("--> Extracting Input Signature...")
    try:
        y, sr = librosa.load("static/music/query1.mp3", sr=16000, duration=60)
        scores, currentE, spectrogram = model(y)
        currentE = np.float16(currentE)
        sig1 = currentE
    except Exception as e:
        print(f"Error: {e}")
        sig1 = None

    if sig1 is not None:
        print(f"--> Scanning {NUM_SONGS} signatures...")
        
        def process_one(ID2):
            try:
                # Use relative path for signatures
                sig2 = np.load(f'./signatures/sig-{ID2}.npz')['currentE']
                dists = cdist(sig1, sig2, metric='cosine') 
                return getScore(dists)
            except:
                return 100.0 

        opscore = Parallel(n_jobs=4, backend="loky", verbose=0)(
            delayed(process_one)(ID2) for ID2 in range(NUM_SONGS)
        )

        recolist = np.argsort(opscore)[:10]

        try:
            with open('datasongs/mp3list.txt', 'r') as f:
                content = f.readlines()
        except:
            print("Error: Could not read ./datasongs/mp3list.txt")
            content = []

        print("--> Saving Search List...")
        
        recopath = 'static/music/recommended.txt'
        with open(recopath, 'w') as f:
            for song_idx in recolist:
                if song_idx < len(content):
                    raw_name = content[song_idx].strip()
                    # Clean the name before saving
                    clean_name = clean_filename_for_search(raw_name)
                    f.write(clean_name + '\n')

    print("--> Analysis Complete.")
else:
    print("Error: static/music/query1.mp3 not found")