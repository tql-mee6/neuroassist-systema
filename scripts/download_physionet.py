from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlretrieve,urlopen,Request
import hashlib,json
root=Path(__file__).resolve().parents[1]/'data';root.mkdir(exist_ok=True)
def one(pair):
 s,r=pair; name=f'S{s:03d}R{r:02d}.edf';p=root/name
 url=f'https://physionet.org/files/eegmmidb/1.0.0/S{s:03d}/{name}'
 def valid():
  if not p.exists() or p.stat().st_size<256:return False
  h=p.open('rb').read(256)
  try:
   hb=int(h[184:192]);nr=int(h[236:244]);nc=int(h[252:256])
   with p.open('rb') as f:f.seek(256+nc*216);ns=f.read(nc*8)
   expected=hb+nr*sum(int(ns[i*8:i*8+8]) for i in range(nc))*2
   return p.stat().st_size==expected
  except:return False
 if valid():return dict(file=name,url=url,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 for attempt in range(20):
  try:
   offset=p.stat().st_size if p.exists() else 0
   request=Request(url,headers={'Range':f'bytes={offset}-','Accept-Encoding':'identity'}) if offset else Request(url)
   with urlopen(request,timeout=20) as response:
    mode='ab' if response.status==206 and offset else 'wb'
    with p.open(mode) as f:
     while chunk:=response.read(16384):f.write(chunk)
   if not valid():raise ValueError('Incomplete EDF')
   print(name,'OK',flush=True)
   break
  except Exception:
   if attempt==19:raise
 return dict(file=name,url=url,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
with ThreadPoolExecutor(max_workers=6) as pool:
 rows=list(pool.map(one,[(s,r) for s in range(1,6) for r in (4,6,8,10,12,14)]))
(root/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print('Downloaded',len(rows),'EDF files',sum(r['bytes'] for r in rows))
