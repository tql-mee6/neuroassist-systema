"""Load numeric CSP/LDA parameters without executing a pickle."""
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from scipy.special import softmax
from .classifier import MIClassifier,CSPOvR

class PortableClassifier(MIClassifier):
    def __init__(self,path):
        p=json.loads(Path(path).read_text(encoding='utf8'))
        if p['format']!='neuroassist-csp-lda-v1':raise ValueError('Unknown model format')
        super().__init__(p['fs'],bands=p['bands'],classes=p['classes'])
        self.csp=[]
        for band in p['csp']:
            c=CSPOvR();c.W={int(k):np.asarray(v) for k,v in band.items()};self.csp.append(c)
        self.lda=SimpleNamespace(classes_=np.asarray(p['classes']))
        self.coef=np.asarray(p['coef']);self.intercept=np.asarray(p['intercept'])
    def predict_proba(self,X):
        return softmax(self._feats(np.asarray(X))@self.coef.T+self.intercept,axis=1)
