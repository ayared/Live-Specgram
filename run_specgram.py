"""
run_specgram.py
Created By Alexander Yared (akyared@gmail.com)

Main Script for the Live Spectrogram project, a real time spectrogram
visualization tool

Dependencies: matplotlib, numpy and the mic_read.py module
"""
from typing import Tuple

import pyaudio
from matplotlib.mlab import window_hanning, specgram
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LogNorm
import numpy as np

import mic_read

# SAMPLES_PER_FRAME = 10  # Number of mic reads concatenated within a single window
SAMPLES_PER_FRAME = 4
nfft = 1024  # 256#1024  # NFFT value for spectrogram
overlap = 1000  # 512  # overlap value for spectrogram
rate = mic_read.RATE  # sampling rate


def get_sample(stream: pyaudio.Stream) -> np.ndarray:
    """
    gets the audio data from the microphone
    inputs: audio stream and PyAudio object
    outputs: int16 array
    """
    return mic_read.get_data(stream)


def get_specgram(signal: np.ndarray, rate: int) -> Tuple[
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
    arr2D, freqs, bins = specgram(signal, window=window_hanning,
                                  Fs=rate, NFFT=nfft, noverlap=overlap)
    return arr2D, freqs, bins


def make_plot(
    stream: pyaudio.Stream,
    arr2D: np.ndarray,
    freqs: np.ndarray,
    bins: np.ndarray,
):
    # Initialize Plot
    fig = plt.figure()

    # Set up the plot parameters
    extent = (bins[0], bins[-1]*SAMPLES_PER_FRAME, freqs[-1], freqs[0])
    im = plt.imshow(arr2D, aspect='auto', extent=extent, interpolation='none',
                    cmap='jet', norm=LogNorm(vmin=.01, vmax=1))
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Real Time Spectogram')
    plt.gca().invert_yaxis()
    # plt.colorbar()  # enable if you want to display a color bar

    def update_fig(n: int):
        """
        updates the image, just adds on samples at the start until the maximum size is
        reached, at which point it 'scrolls' horizontally by determining how much of the
        data needs to stay, shifting it left, and appending the new data.
        inputs: iteration number
        outputs: updated image
        """
        data = get_sample(stream)
        arr2D, freqs, bins = get_specgram(data, rate)
        im_data = im.get_array()
        if n < SAMPLES_PER_FRAME:
            im_data = np.hstack((im_data, arr2D))
            im.set_array(im_data)
        else:
            keep_block = arr2D.shape[1] * (SAMPLES_PER_FRAME - 1)
            im_data = np.delete(im_data, np.s_[:-keep_block], 1)
            im_data = np.hstack((im_data, arr2D))
            im.set_array(im_data)
        return im,

    # Animate
    animation.FuncAnimation(fig, update_fig, blit=False,
                            interval=mic_read.CHUNK_SIZE/1000)


def main():
    # Launch the stream and the original spectrogram
    stream, pa = mic_read.open_mic()

    try:
        data = get_sample(stream)
        arr2D, freqs, bins = get_specgram(data, rate)

        make_plot(stream, arr2D, freqs, bins)
        plt.show()
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()


if __name__ == '__main__':
    main()
