import threading, time
import numpy as np
from collections import deque
from sklearn.model_selection import GroupKFold
from .config import *
from .sources import SimulatedHeadset
from .classifier import MIClassifier
from .decoder import run_calibration, OnlineDecoder
from .scanner import Scanner
from .dsp import signal_quality

class Engine:
    def __init__(self, cfg=None, source=None, seed=0):
        self.cfg = cfg or Config(); self.src = source or SimulatedHeadset(self.cfg, seed=seed)
        self.scanner = Scanner(); self.lock = threading.Lock()
        self.eeg = deque(maxlen=int(4 * self.cfg.fs)); self.cv = None
        self.clf = None; self.dec = None; self.plan = []; self.hold = 0.0
        self.last_cmd = None; self.last_cmd_t = 0.0; self.log = []; self.target = ""
        self.intent = REST; self.rest_until = 0.0; self.t = 0.0; self.sent = 0; self.ok = 0
    def calibrate(self, tp=None):
        X, y = run_calibration(self.src, self.cfg, tp, np.random.default_rng(1))
        g = np.repeat(np.arange(len(y) // 5), 5)
        acc = [(MIClassifier(self.cfg.fs).fit(X[a], y[a]).predict(X[b]) == y[b]).mean()
               for a, b in GroupKFold(5).split(X, y, g)]
        self.cv = float(np.mean(acc))
        self.clf = MIClassifier(self.cfg.fs).fit(X, y)
        self.dec = OnlineDecoder(self.clf, self.cfg)
        return self.cv
    def set_intent(self, c):
        self.intent = c; self.src.set_intent(c)
    def start_demo(self, text="привет"):
        self.scanner = Scanner(); self.target = text; self.plan = self.scanner.plan(text) or []
        self.sent = self.ok = 0
    def step(self):
        n = int(self.cfg.step_s * self.cfg.fs)
        if self.plan:
            if self.t - self.rest_until > 7.0: self.rest_until = self.t + 1.0   # пользователь «собирается заново»
            if self.t >= self.rest_until: self.set_intent(self.plan[0])
            else: self.set_intent(REST)
        elif self.target: self.set_intent(REST)
        x = self.src.read(n); self.t += self.cfg.step_s
        self.eeg.extend(x.T.tolist())
        cmd = self.dec.push(x) if self.dec else None
        if cmd is not None:
            self.last_cmd, self.last_cmd_t = cmd, self.t
            self.sent += 1
            if self.plan:
                if cmd == self.plan[0]: self.ok += 1
                self.scanner.press(cmd)
                self.plan = self.scanner.plan(self.target) or []
                self.rest_until = self.t + 1.5
            else:
                self.scanner.press(cmd)
        return cmd
    def state(self):
        arr = np.array(self.eeg).T if len(self.eeg) else np.zeros((3, 1))
        step = max(1, arr.shape[1] // 250)
        p = self.dec.last_p.tolist() if self.dec else [0] * 4
        q = signal_quality(arr[:, -500:], self.cfg.fs) if arr.shape[1] > 100 else [0, 0, 0]
        return {"kb": self.scanner.state(), "eeg": arr[:, ::step].round(1).tolist(), "channels": list(self.cfg.channels),
                "probs": p, "classes": [CLASS_RU[c] for c in self.cfg.classes], "quality": q,
                "last_cmd": CLASS_RU.get(self.last_cmd) if self.last_cmd is not None else None,
                "cmd_age": round(self.t - self.last_cmd_t, 1), "cv": self.cv, "intent": CLASS_RU[self.intent],
                "demo": bool(self.plan), "target": self.target, "sent": self.sent, "ok": self.ok, "t": round(self.t, 1)}
