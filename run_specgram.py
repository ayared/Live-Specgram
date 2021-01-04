#!/usr/bin/env python3

"""
run_specgram.py
Created By Alexander Yared (akyared@gmail.com)

Main Script for the Live Spectrogram project, a real time spectrogram
visualization tool

Dependencies: matplotlib, numpy and the mic_read.py module
"""

import matplotlib.pyplot as plt
import numpy as np
import pyaudio
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LogNorm
from matplotlib.image import AxesImage
from matplotlib.mlab import window_hanning, specgram
from typing import Tuple

from mic_read import CHUNK_SIZE, RATE, get_data, open_mic

SAMPLES_PER_FRAME = 4  # Number of mic reads concatenated within a single window
N_FFT = 1_024  # NFFT value for spectrogram
OVERLAP = 1_000  # overlap value for spectrogram


def get_sample(stream: pyaudio.Stream) -> np.ndarray:
    """
    gets the audio data from the microphone
    inputs: audio stream and PyAudio object
    outputs: int16 array
    """
    return get_data(stream)


def get_specgram(signal: np.ndarray) -> Tuple[
    np.ndarray,  # 2D output array
    np.ndarray,  # Frequencies
    np.ndarray,  # Frequency bins
]:
    """
    takes the FFT to create a spectrogram of the given audio signal
    input: audio signal, sampling rate
    output: 2D Spectrogram Array, Frequency Array, Bin Array
    see matplotlib.mlab.specgram documentation for help
    """
    return specgram(signal, window=window_hanning,
                    Fs=RATE, NFFT=N_FFT, noverlap=OVERLAP)


def update_fig(frame: int, im: AxesImage, stream: pyaudio.Stream) -> Tuple[AxesImage]:
    """
    updates the image, just adds on samples at the start until the maximum size is
    reached, at which point it 'scrolls' horizontally by determining how much of the
    data needs to stay, shifting it left, and appending the new data.
    inputs: iteration number
    outputs: updated image
    """
    data = get_sample(stream)
    arr_2d, freqs, bins = get_specgram(data)
    im_data = im.get_array()

    if frame < SAMPLES_PER_FRAME:
        im_data = np.hstack((im_data, arr_2d))
        im.set_array(im_data)
    else:
        keep_block = arr_2d.shape[1] * (SAMPLES_PER_FRAME - 1)
        im_data = np.delete(im_data, np.s_[:-keep_block], 1)
        im_data = np.hstack((im_data, arr_2d))
        im.set_array(im_data)

    return im,


def make_plot(stream: pyaudio.Stream) -> FuncAnimation:
    # Initialize Plot
    fig = plt.figure()
    ax = fig.gca()

    # Data for first frame
    data = get_sample(stream)
    arr_2d, freqs, bins = get_specgram(data)

    # Set up the plot parameters
    extent = (bins[0], bins[-1]*SAMPLES_PER_FRAME, freqs[-1], freqs[0])
    im = ax.imshow(arr_2d, aspect='auto', extent=extent, interpolation='none',
                   cmap='jet', norm=LogNorm(vmin=.01, vmax=1))
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_title('Real-Time Spectogram')
    ax.invert_yaxis()
    # fig.colorbar()  # enable if you want to display a color bar

    # Animate
    return FuncAnimation(
        fig,
        func=update_fig, fargs=(im, stream),
        interval=CHUNK_SIZE/1000,
        blit=True,
    )


def main():
    # Launch the stream and the original spectrogram
    stream, pa = open_mic()

    try:
        animation = make_plot(stream)
        plt.show()
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()


if __name__ == '__main__':
    main()
