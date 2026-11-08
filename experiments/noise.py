import sys,json; sys.path.insert(0,'.')
import numpy as np
from sklearn.model_selection import GroupKFold
from neuroassist.config import *
from neuroassist.sources import SimulatedHeadset
from neuroassist.decoder import run_calibration
from neuroassist.classifier import MIClassifier
out={}
for ex in (0,10,20,30,45):
  for cl,name in (((0,1,2),"3cmd"),((0,1,2,3),"4cls")):
    r=[]
    for seed in range(6):
        cfg=Config(classes=cl); s=SimulatedHeadset(cfg,seed=seed,extra_noise_uv=ex)
        X,y=run_calibration(s,cfg,30,np.random.default_rng(seed)); g=np.repeat(np.arange(len(y)//5),5)
        r.append(np.mean([(MIClassifier(cfg.fs,classes=cl).fit(X[a],y[a]).predict(X[b])==y[b]).mean() for a,b in GroupKFold(5).split(X,y,g)]))
    out[f"{name}_{ex}"]=float(np.mean(r)); print(name,ex,round(np.mean(r),3),flush=True)
json.dump(out,open('experiments/results/noise.json','w'))
