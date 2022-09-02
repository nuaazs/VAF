from locale import normalize
import numpy as np

def norm_numpy_array(wav):
    return wav / np.max(np.abs(wav))

def check_clip(wav,th):
    wav = np.array(wav)
    print(f"check clip: wav shape is {wav.shape}")
    data = norm_numpy_array(wav)
    if ((len(data[data>0.99])/data.shape[0])>th):
        return True
    return False