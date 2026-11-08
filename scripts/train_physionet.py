import sys, json, hashlib, platform, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np, scipy, sklearn, mne
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, confusion_matrix
from neuroassist.classifier import MIClassifier
from neuroassist.dsp import preprocess
OUT=ROOT;OUT.mkdir(parents=True,exist_ok=True)
(OUT/'models').mkdir(exist_ok=True);(OUT/'results').mkdir(exist_ok=True)
DATA=ROOT/'data'; results=[]; replay=None
def epochs(s,r):
 p=DATA/f'S{s:03d}R{r:02d}.edf'
 raw=mne.io.read_raw_edf(str(p),preload=True,verbose='ERROR')
 names={x.strip('.').upper():x for x in raw.ch_names}
 fs=int(raw.info['sfreq']);assert fs==160
 x=raw.get_data(picks=[names[x] for x in ['C3','CZ','C4']])*1e6
 X=[];y=[];meta=[]
 for onset,duration,desc in zip(raw.annotations.onset,raw.annotations.duration,raw.annotations.description):
  if desc=='T0':label=3
  elif r in (4,8,12):label={'T1':0,'T2':1}.get(desc)
  else:label={'T2':2}.get(desc)
  if label is None or duration<2.5:continue
  a=int(round((onset+1)*fs)); b=a+240
  if b>x.shape[1]:continue
  X.append(preprocess(x[:,a:b],fs));y.append(label)
  meta.append(dict(subject=f'S{s:03d}',run=r,onset=float(onset),label=label))
 return np.asarray(X),np.asarray(y),meta
for s in range(1,6):
 train=[epochs(s,r) for r in (4,6,8,10)];test=[epochs(s,r) for r in (12,14)]
 X=np.concatenate([v[0] for v in train]); y=np.concatenate([v[1] for v in train]);T=np.concatenate([v[0] for v in test]);t=np.concatenate([v[1] for v in test])
 model=MIClassifier(160).fit(X,y);pred=model.predict(T)
 numeric=dict(format='neuroassist-csp-lda-v1',subject=f'S{s:03d}',fs=160,channels=['C3','Cz','C4'],classes=[0,1,2,3],bands=model.bands,n_filters=1,csp=[{str(c):w.tolist() for c,w in ob.W.items()} for ob in model.csp],coef=model.lda.coef_.tolist(),intercept=model.lda.intercept_.tolist(),preprocessing='notch 50 Hz; demean; Butterworth 8-30 Hz; filtfilt; epoch cue+1..2.5 s',train_runs=[4,6,8,10],test_runs=[12,14])
 (OUT/'models'/f'S{s:03d}.json').write_text(json.dumps(numeric,ensure_ascii=False,indent=2),encoding='utf8')
 row=dict(subject=f'S{s:03d}',train_n=len(y),test_n=len(t),train_counts=np.bincount(y,minlength=4).tolist(),test_counts=np.bincount(t,minlength=4).tolist(),accuracy=float(accuracy_score(t,pred)),balanced_accuracy=float(balanced_accuracy_score(t,pred)),macro_f1=float(f1_score(t,pred,average='macro')),confusion_matrix=confusion_matrix(t,pred,labels=[0,1,2,3]).tolist(),majority_accuracy=float(np.max(np.bincount(t))/len(t)),predictions=pred.tolist(),truth=t.tolist())
 results.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
 if s==1:
  np.savez_compressed(OUT/'results/replay_S001.npz',X=T,y=t,pred=pred,fs=160)
  replay=[m for v in test for m in v[2]]
summary=dict(dataset='PhysioNet EEGMMIDB 1.0.0',doi='10.13026/C28G6P',subjects='S001-S005 consecutive, no selection by accuracy',train_runs=[4,6,8,10],test_runs=[12,14],epoch='one non-overlapping 1.5 s epoch per event, starting 1 s after cue',classes={'0':'left hand','1':'right hand','2':'both feet','3':'rest'},channels=['C3','Cz','C4'],fs=160,mean_accuracy=float(np.mean([r['accuracy'] for r in results])),mean_balanced_accuracy=float(np.mean([r['balanced_accuracy'] for r in results])),mean_macro_f1=float(np.mean([r['macro_f1'] for r in results])),mean_majority_accuracy=float(np.mean([r['majority_accuracy'] for r in results])),versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,sklearn=sklearn.__version__,mne=mne.__version__),participants=results,limitations=['Small offline pilot, five healthy participants; not clinical validation.','Foot imagery is recorded in a different task run than unilateral hand imagery; task context is a confound.','Within-participant held-out runs, not transfer to a new participant or day.','Rest is more frequent; balanced accuracy and macro F1 are required.','No online command latency or typing-speed claim follows from this offline test.'])
(OUT/'results/physionet_results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'results/replay_events.json').write_text(json.dumps(replay,indent=2),encoding='utf8')
shutil.copyfile(DATA/'manifest.json',OUT/'results/data_manifest.json')
print('SUMMARY',json.dumps({k:v for k,v in summary.items() if k.startswith('mean_')}),flush=True)
