import scipy.signal as s

taps = s.firwin(31, 75000, fs=400000)
print(taps)