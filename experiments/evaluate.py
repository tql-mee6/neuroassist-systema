import sys, json; sys.path.insert(0,'.')
import numpy as np
from sklearn.model_selection import GroupKFold
from neuroassist.config import *
from neuroassist.sources import SimulatedHeadset
from neuroassist.decoder import run_calibration
from neuroassist.classifier import MIClassifier
from neuroassist.engine import Engine
from experiments.tune import online
R={}
def cv(seed,noise=8.0,chs=(0,1,2),classes=(0,1,2,3)):
    cfg=Config(classes=classes); s=SimulatedHeadset(cfg,seed=seed,noise_uv=noise)
    X,y=run_calibration(s,cfg,30,np.random.default_rng(seed)); X=X[:,list(chs),:]
    g=np.repeat(np.arange(len(y)//5),5)
    return np.mean([(MIClassifier(cfg.fs,classes=classes).fit(X[a],y[a]).predict(X[b])==y[b]).mean() for a,b in GroupKFold(5).split(X,y,g)])
R['cv4']=[cv(s) for s in range(8)]
R['cv3_noRest']=[cv(s,classes=(0,1,2)) for s in range(8)]
R['cv_2ch_C3C4_3cls']=[cv(s,chs=(0,2),classes=(0,1)) for s in range(8)]
R['noise']={n:float(np.mean([cv(s,noise=n) for s in range(5)])) for n in (4,8,12,16,24)}
on=[online(s,6,0.8) for s in range(5)]
R['online']={'fp_per_min':float(np.mean([o[0] for o in on])),'correct':float(np.mean([o[1] for o in on])),'latency_s':float(np.mean([o[2] for o in on]))}
sp=[]
for seed in range(5):
    e=Engine(seed=seed); e.calibrate(30); e.start_demo("привет"); n=len(e.plan)
    for i in range(5000):
        e.step()
        if e.scanner.text.strip()=="привет": break
    sp.append((n,e.sent,e.t))
R['typing']={'plan_cmds':sp[0][0],'sent_mean':float(np.mean([x[1] for x in sp])),'time_s_mean':float(np.mean([x[2] for x in sp])),'chars_per_min':float(6/(np.mean([x[2] for x in sp])/60))}
json.dump(R,open('experiments/results/results.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(R,ensure_ascii=False,indent=1))
