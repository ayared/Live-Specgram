"""
mic_read.py
Created By Alexander Yared (akyared@gmail.com)

Microphone controller module for the Live Spectrogram project, a real time
spectrogram visualization tool

Dependencies: pyaudio, numpy and matplotlib
"""
############### Import Libraries ###############
import pyaudio
import numpy as np
import matplotlib.pyplot as plt

############### Constants ###############
#RATE = 44100 #sample rate
RATE = 16000
FORMAT = pyaudio.paInt16 #conversion format for PyAudio stream
CHANNELS = 1 #microphone audio channels
CHUNK_SIZE = 8192 #number of samples to take per read
SAMPLE_LENGTH = int(CHUNK_SIZE*1000/RATE) #length of each sample in ms

############### Functions ###############
"""
open_mic:
creates a PyAudio object and initializes the mic stream
inputs: none
ouputs: stream, PyAudio object
"""
def open_mic():
    pa = pyaudio.PyAudio()
    stream = pa.open(format = FORMAT,
                     channels = CHANNELS,
                     rate = RATE,
                     input = True,
                     frames_per_buffer = CHUNK_SIZE)
    return stream,pa

"""
get_data:
reads from the audio stream for a constant length of time, converts it to data
inputs: stream, PyAudio object
outputs: int16 data array
"""
def get_data(stream,pa):
    input_data = stream.read(CHUNK_SIZE)
    data = np.fromstring(input_data,np.int16)
    return data

############### Test Functions ###############
"""
make_10k:
creates a 10kHz test tone
"""
def make_10k():
    x = np.linspace(-2*np.pi,2*np.pi,21000)
    x = np.tile(x,int(SAMPLE_LENGTH/(4*np.pi)))
    y = np.sin(2*np.pi*5000*x)
    return x,y

"""
show_freq:
plots the test tone for a sanity check
"""
def show_freq():
    x,y = make_10k()
    plt.plot(x,y)
    plt.show()
    
