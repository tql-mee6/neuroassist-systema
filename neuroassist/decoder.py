import numpy as np
from .dsp import preprocess
from .config import REST

def make_windows(x, fs, win, step):
    n, s = int(win * fs), int(step * fs)
    return [x[:, i:i + n] for i in range(0, x.shape[1] - n + 1, s)]

def run_calibration(src, cfg, trials_per_class=None, rng=None):
    """Сбор калибровочных данных: пользователь по метке представляет движение."""
    rng = rng or np.random.default_rng(0)
    tp = trials_per_class or cfg.calib_trials_per_class
    order = [c for c in cfg.classes for _ in range(tp)]
    rng.shuffle(order)
    X, y = [], []
    for c in order:
        src.set_intent(c)
        raw = src.read(int(cfg.trial_s * cfg.fs))
        seg = raw[:, int(cfg.imagery_from_s * cfg.fs):int(cfg.imagery_to_s * cfg.fs)]
        seg = preprocess(seg, cfg.fs)
        for w in make_windows(seg, cfg.fs, 1.5, 0.25):
            X.append(w); y.append(c)
    src.set_intent(REST)
    return np.array(X), np.array(y)

class OnlineDecoder:
    def __init__(self, clf, cfg):
        self.clf, self.cfg = clf, cfg
        self.buf = np.zeros((len(cfg.channels), 0))
        self.probs = []
        self.blocked_until = 0.0
        self.t = 0.0
        self.last_p = np.zeros(len(cfg.classes))
    def push(self, chunk):
        self.buf = np.hstack([self.buf, chunk])[:, -int(self.cfg.window_s * self.cfg.fs):]
        self.t += chunk.shape[1] / self.cfg.fs
        if self.buf.shape[1] < int(self.cfg.window_s * self.cfg.fs):
            return None
        x = preprocess(self.buf, self.cfg.fs)[:, -int(1.5 * self.cfg.fs):]
        p = self.clf.predict_proba(x[None])[0]
        self.probs.append(p); self.probs = self.probs[-self.cfg.vote_k:]
        avg = np.mean(self.probs, axis=0); self.last_p = avg
        k = int(np.argmax(avg)); label = self.clf.lda.classes_[k]
        if self.t < self.blocked_until or label == REST or avg[k] < self.cfg.min_conf or len(self.probs) < self.cfg.vote_k:
            return None
        self.probs = []; self.blocked_until = self.t + self.cfg.refractory_s
        return int(label)
