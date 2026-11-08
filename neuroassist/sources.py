"""Источники сигнала: имитатор гарнитуры, воспроизведение записи, адаптер BrainFlow."""
import numpy as np
from scipy import signal
from .config import LEFT, RIGHT, FEET, REST

class BaseSource:
    def read(self, n):  # -> (channels, n) в мкВ
        raise NotImplementedError
    def set_intent(self, label):
        pass

def _bp(lo, hi, fs):
    return signal.butter(2, [lo, hi], btype="band", fs=fs)

class SimulatedHeadset(BaseSource):
    """Имитатор ЭЭГ: розовый шум + мю/бета-ритмы с ERD в контралатеральном
    полушарии + смешивание каналов + наводка 50 Гц + моргания."""
    def __init__(self, cfg, seed=0, erd_depth=0.30, noise_uv=8.0, blink_rate_hz=0.1, extra_noise_uv=0.0):
        self.cfg, self.fs = cfg, cfg.fs
        self.rng = np.random.default_rng(seed)
        self.nch = len(cfg.channels)
        self.erd, self.noise, self.blink_rate = erd_depth, noise_uv, blink_rate_hz
        self.intent, self.gain = REST, 1.0
        self.extra = extra_noise_uv
        self.mix = np.eye(self.nch) + 0.25 * self.rng.random((self.nch, self.nch))
        self.mix /= self.mix.sum(1, keepdims=True)
        self.filt = {}
        for name, (lo, hi) in {"mu": (8, 13), "beta": (14, 28), "pink": (1, 40)}.items():
            b, a = _bp(lo, hi, self.fs)
            self.filt[name] = (b, a, [signal.lfilter_zi(b, a) * 0 for _ in range(self.nch)])
        self.env = np.ones((2, self.nch))
        self.t = 0
        self.blink = 0

    def set_intent(self, label):
        if label != self.intent:
            self.gain = max(0.0, self.rng.normal(1.0, 0.45))
        self.intent = label

    def _band(self, name, n):
        b, a, zis = self.filt[name]
        out = np.empty((self.nch, n))
        for c in range(self.nch):
            out[c], zis[c] = signal.lfilter(b, a, self.rng.standard_normal(n), zi=zis[c])
        return out

    def read(self, n):
        mu = self._band("mu", n); beta = self._band("beta", n); pink = self._band("pink", n)
        target = np.ones((2, self.nch))  # 0 -> мю, 1 -> бета ; каналы C3,Cz,C4
        d = self.erd * self.gain
        if self.intent == LEFT:   target[:, 2] -= d * 1.6
        elif self.intent == RIGHT: target[:, 0] -= d * 1.6
        elif self.intent == FEET:  target[:, 1] -= d * 1.6
        target = np.clip(target, 0.05, 1.5)
        alpha = 1 - np.exp(-n / (0.4 * self.fs))
        self.env += alpha * (target - self.env)
        env = self.env[:, :, None]
        x = 5.5 * self.noise * (mu * env[0] + 0.7 * beta * env[1]) / 3.0 + 0.9 * self.noise * pink
        x = self.mix @ x
        tt = (self.t + np.arange(n)) / self.fs
        x += 4.0 * np.sin(2 * np.pi * 50 * tt)
        if self.extra: x += self.extra * self.rng.standard_normal(x.shape)
        for k in range(n):
            if self.blink > 0:
                x[:, k] += 60 * np.sin(np.pi * (1 - self.blink / 60)) ; self.blink -= 1
            elif self.rng.random() < self.blink_rate / self.fs:
                self.blink = 60
        self.t += n
        return x

class ReplaySource(BaseSource):
    """Воспроизведение готовой записи (например, BCI Competition IV 2a, PhysioNet)."""
    def __init__(self, data, loop=True):
        self.data, self.pos, self.loop = np.asarray(data), 0, loop
    def read(self, n):
        idx = (self.pos + np.arange(n)) % self.data.shape[1]
        self.pos += n
        return self.data[:, idx]

class BrainFlowSource(BaseSource):
    """Адаптер реальной гарнитуры через BrainFlow (board_id=-1 — синтетическая плата).
    На реальном оборудовании не проверялся."""
    def __init__(self, board_id=-1, channels=None, mac_or_serial="", picks=None):
        from brainflow.board_shim import BoardShim, BrainFlowInputParams
        p = BrainFlowInputParams()
        if mac_or_serial: p.mac_address = mac_or_serial; p.serial_number = mac_or_serial
        self.board = BoardShim(board_id, p)
        self.board.prepare_session(); self.board.start_stream()
        self.rows = picks or BoardShim.get_eeg_channels(board_id)
    def read(self, n):
        d = self.board.get_board_data(n)
        return d[self.rows, :]
