import argparse
from neuroassist.server import run
ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8765)
ap.add_argument("--speed", type=float, default=1.0); ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args(); run(a.port, a.speed, a.seed)
