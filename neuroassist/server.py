"""Локальный веб-интерфейс (127.0.0.1): http://localhost:8765"""
import json, threading, time, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .engine import Engine
from .config import LEFT, RIGHT, FEET, REST

STATIC = os.path.join(os.path.dirname(__file__), "static")

def make_handler(eng, speed):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _json(self, o):
            b = json.dumps(o).encode(); self.send_response(200)
            self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(b)
        def do_GET(self):
            if self.path.startswith("/state"):
                with eng.lock: self._json(eng.state())
            elif self.path.startswith("/intent/"):
                with eng.lock: eng.set_intent(int(self.path.split("/")[-1]))
                self._json({"ok": 1})
            elif self.path.startswith("/demo"):
                with eng.lock: eng.start_demo()
                self._json({"ok": 1})
            elif self.path.startswith("/reset"):
                with eng.lock:
                    from .scanner import Scanner
                    eng.scanner = Scanner(); eng.plan = []; eng.target = ""; eng.set_intent(REST)
                self._json({"ok": 1})
            else:
                f = os.path.join(STATIC, "index.html"); b = open(f, "rb").read()
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers(); self.wfile.write(b)
    return H

def run(port=8765, speed=1.0, seed=0):
    eng = Engine(seed=seed); eng.calibrate(30)
    def loop():
        while True:
            with eng.lock: eng.step()
            time.sleep(eng.cfg.step_s / speed)
    threading.Thread(target=loop, daemon=True).start()
    print(f"NeuroAssist: http://localhost:{port}  (калибровка: точность {eng.cv:.2f})")
    ThreadingHTTPServer(("127.0.0.1", port), make_handler(eng, speed)).serve_forever()
