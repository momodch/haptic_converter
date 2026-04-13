# processing/audio_utils.py
import numpy as np
from scipy.signal import butter, filtfilt
from scipy.fft import rfft, rfftfreq
import scipy.io.wavfile as wav

def read_wav(path):
    sample_rate, data = wav.read(path)
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    elif data.dtype == np.uint8:
        data = (data.astype(np.float32) - 128) / 128.0
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    return sample_rate, data

def compute_envelope(signal, sample_rate, win_duration=0.01):
    win_size = int(win_duration * sample_rate)
    envelope = np.abs(signal)
    smoothed = np.convolve(envelope, np.ones(win_size)/win_size, mode='same')
    return smoothed

def lowpass_filter(signal, sample_rate, cutoff=150.0, order=4):
    nyquist = 0.5 * sample_rate
    norm_cutoff = cutoff / nyquist
    b, a = butter(order, norm_cutoff, btype='low')
    return filtfilt(b, a, signal)

def get_dominant_freq(segment, sample_rate):
    N = len(segment)
    if N < 2:
        return 0.0
    yf = rfft(segment)
    xf = rfftfreq(N, 1 / sample_rate)
    idx = np.argmax(np.abs(yf))
    return xf[idx]
