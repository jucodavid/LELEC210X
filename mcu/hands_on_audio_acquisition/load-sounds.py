import pickle
import os
import numpy as np

os.chdir(r"C:\Users\Carabouille\Documents\LELEC210X\mcu\hands_on_audio_acquisition\Pickle")
with open("sound_list", "rb") as f:
    sound_list = pickle.load(f)

print(sound_list)
sounds = {}
for sound in sound_list:
    with open(sound, "rb") as f:
        sounds[sound] = np.array(pickle.load(f))

print(sounds)