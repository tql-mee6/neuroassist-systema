import sys; sys.path.insert(0,'.')
import numpy as np
from neuroassist.engine import Engine
from neuroassist.config import *
def online(seed, vote_k, conf, n_cmd=40, rest_s=1.0):
    cfg=Config(vote_k=vote_k,min_conf=conf); e=Engine(cfg,seed=seed); e.calibrate(30)
    rng=np.random.default_rng(seed)
    # ложные срабатывания в покое 120 с
    e.set_intent(REST); fp=0
    for _ in range(480):
        if e.step() is not None: fp+=1
    # команды
    ok=0; tot=0; lat=[]; 
    for _ in range(n_cmd):
        c=int(rng.integers(0,3)); e.dec.probs=[]; 
        for _ in range(int(rest_s/0.25)): e.set_intent(REST); e.step()
        e.set_intent(c); t=0; got=None
        while t<8:
            got=e.step(); t+=0.25
            if got is not None: break
        tot+=1
        if got==c: ok+=1; lat.append(t)
    return fp/2, ok/tot, np.mean(lat) if lat else 0
if __name__=="__main__":
    for vk,cf in [(6,0.8),(4,0.8),(4,0.7),(3,0.75)]:
        r=[online(s,vk,cf) for s in range(3)]
        print(vk,cf,"FP/мин %.1f верно %.2f задержка %.1f"%tuple(np.mean(r,axis=0)))
