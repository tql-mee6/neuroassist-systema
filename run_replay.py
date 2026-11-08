"""Replay held-out real EEG epochs through the classifier and original keyboard UI."""
import argparse,json,threading,time
from pathlib import Path
from http.server import ThreadingHTTPServer
import numpy as np
from neuroassist.config import Config,CLASS_RU,REST
from neuroassist.scanner import Scanner
from neuroassist.portable import PortableClassifier
from neuroassist.server import make_handler

ROOT=Path(__file__).resolve().parent
class ReplayEngine:
    def __init__(self):
        self.lock=threading.Lock();self.cfg=Config(fs=160);self.scanner=Scanner()
        z=np.load(ROOT/'results/replay_S001.npz');self.X=z['X'];self.y=z['y']
        self.clf=PortableClassifier(ROOT/'models/S001.json');self.index=-1;self.sent=0;self.t=0
        self.probs=np.zeros(4);self.label=REST;self.truth=REST;self.x=np.zeros((3,240));self.plan=[];self.target=''
        self.history=[];self.active=False
    def set_intent(self,c):pass
    def start_demo(self):
        self.index=-1;self.sent=0;self.scanner=Scanner();self.history=[];self.active=True
    def step(self):
        if not self.active:return
        if self.index+1>=len(self.y):self.active=False;return
        self.index+=1;self.x=self.X[self.index];self.truth=int(self.y[self.index])
        self.probs=self.clf.predict_proba(self.x[None])[0];self.label=int(self.probs.argmax())
        if self.label!=REST:self.scanner.press(self.label);self.sent+=1
        self.t+=1.5;self.history.append(dict(epoch=self.index,truth=self.truth,prediction=self.label))
    def state(self):
        n=len(self.history);acc=sum(h['truth']==h['prediction'] for h in self.history)/n if n else 0
        return dict(kb=self.scanner.state(),eeg=self.x[:,::2].round(2).tolist(),channels=list(self.cfg.channels),
            probs=self.probs.tolist(),classes=[CLASS_RU[c] for c in range(4)],quality=[0,0,0],last_cmd=CLASS_RU[self.label],
            cmd_age=0,cv=acc,intent=CLASS_RU[self.truth],demo=self.active,target='',sent=self.sent,ok=0,t=round(self.t,1),
            replay=True,epoch=max(0,self.index+1),total=len(self.y),truth=CLASS_RU[self.truth],prediction=CLASS_RU[self.label])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=8766);a=ap.parse_args()
    e=ReplayEngine()
    def loop():
        while True:
            with e.lock:e.step()
            time.sleep(2)
    threading.Thread(target=loop,daemon=True).start()
    print(f'Offline real EEG replay: http://127.0.0.1:{a.port}. Click Replay to start.')
    ThreadingHTTPServer(('127.0.0.1',a.port),make_handler(e,1)).serve_forever()
