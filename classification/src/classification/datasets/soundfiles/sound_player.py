from pydub import AudioSegment
from pydub.playback import play
import simpleaudio as sa
import numpy as np
import os

os.chdir(r'C:\Users\Carabouille\Documents\LELEC210X\classification\src\classification\datasets\soundfiles')

def play_sounds(sound_list):
    sounds = []
    for sound_file, rms_db, start_fraction in sound_list:
        sound = AudioSegment.from_file(sound_file)
        start_time = int(len(sound) * start_fraction)
        sound = sound[start_time:]
        sound = sound.apply_gain(rms_db - sound.dBFS)
        sounds.append(sound)

    mixed_sound = sounds[0]
    for sound in sounds[1:]:
        mixed_sound = mixed_sound.overlay(sound)

    play(mixed_sound)

# Example usage
sound_list = [
    ('background.wav', -25, 0.0),
    ('gunshot_01.wav', -10, 0.0),
]

play_sounds(sound_list)