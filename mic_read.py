"""
mic_read.py
Created By Alexander Yared (akyared@gmail.com)

Microphone controller module for the Live Spectrogram project, a real time
spectrogram visualization tool

Dependencies: pyaudio, numpy and matplotlib
"""

from typing import Tuple

import pyaudio
import numpy as np
import matplotlib.pyplot as plt


RATE = 16_000  # sample rate
FORMAT = pyaudio.paInt16  # conversion format for PyAudio stream
CHANNELS = 1  # microphone audio channels
CHUNK_SIZE = 8_192  # number of samples to take per read
SAMPLE_LENGTH = int(CHUNK_SIZE*1_000/RATE)  # length of each sample in ms


def open_mic() -> Tuple[pyaudio.Stream, pyaudio.PyAudio]:
    """
    creates a PyAudio object and initializes the mic stream
    inputs: none
    ouputs: stream, PyAudio object
    """
    pa = pyaudio.PyAudio()
    stream = pa.open(input=True,
                     format=FORMAT,
                     channels=CHANNELS,
                     rate=RATE,
                     frames_per_buffer=2*CHUNK_SIZE)
    return stream, pa


def get_data(stream: pyaudio.Stream) -> np.ndarray:
    """
    reads from the audio stream for a constant length of time, converts it to data
    inputs: stream, PyAudio object
    outputs: int16 data array
    """
    input_data = stream.read(CHUNK_SIZE)
    data = np.frombuffer(input_data, np.int16)
    return data


def make_10k() -> Tuple[np.ndarray, np.ndarray]:
    """
    creates a 10kHz test tone
    """
    x = np.linspace(-2*np.pi, 2*np.pi, 21_000)
    x = np.tile(x, int(SAMPLE_LENGTH/(4*np.pi)))
    y = np.sin(2*np.pi*5_000*x)
    return x, y


def show_freq():
    """
    plots the test tone for a sanity check
    """
    x, y = make_10k()
    plt.plot(x, y)
    plt.show()
