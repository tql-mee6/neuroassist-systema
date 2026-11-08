import numpy as np
from scipy import signal

def preprocess(x, fs, notch=50.0, band=(8, 30)):
    """Режекция 50 Гц, вычитание среднего, полосовой фильтр 8-30 Гц."""
    b, a = signal.iirnotch(notch, 30, fs=fs)
    x = signal.filtfilt(b, a, x, axis=1)
    x = x - x.mean(axis=1, keepdims=True)
    b, a = signal.butter(3, band, btype="band", fs=fs)
    return signal.filtfilt(b, a, x, axis=1)

def signal_quality(x, fs):
    """Простая оценка качества: размах и доля мощности 50 Гц. Возвращает 0..1 по каналам."""
    q = []
    for ch in x:
        p2p = np.ptp(ch)
        f, p = signal.welch(ch, fs=fs, nperseg=min(256, len(ch)))
        hum = p[(f > 48) & (f < 52)].sum() / (p.sum() + 1e-9)
        q.append(float(np.clip(1 - max((p2p - 100) / 200, 0) - hum * 2, 0, 1)))
    return q

def reject_artifact(x, thr_uv=100.0):
    return bool(np.ptp(x, axis=1).max() > thr_uv)
