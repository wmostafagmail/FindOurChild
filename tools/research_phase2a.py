"""Manual primary-source text refresh only; never downloads weights/datasets or executes targets."""
import hashlib,json,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'docs/phase2a/research';root.mkdir(parents=True,exist_ok=True)
repos={
'insightface':('deepinsight/insightface','c6c3af7bd2d0a0bf4b78c78437357f3521aa5d52',['README.md','python-package/README.md','python-package/insightface/app/face_analysis.py','python-package/insightface/model_zoo/arcface_onnx.py']),
'adaface':('mk-minchul/AdaFace','c60eaa786a42c03444f3df7096dbaf9d57ae010d',['README.md','LICENSE','inference.py','face_alignment/align.py']),
'deepface':('serengil/deepface','b748cb4e3622d3beaca9a3b60abcc2ee77617a8a',['README.md','LICENSE','deepface/models/facial_recognition/onnx/ArcFace.py','deepface/models/facial_recognition/onnx/SFace.py','deepface/modules/modeling.py','deepface/commons/weight_utils.py']),
'opencv_zoo':('opencv/opencv_zoo','48b10fa505aeb51fbd127fc60a5c660040e823b7',['LICENSE','models/face_recognition_sface/README.md','models/face_recognition_sface/LICENSE','models/face_recognition_sface/sface.py','models/face_detection_yunet/README.md','models/face_detection_yunet/LICENSE'])}
records=[]
for key,(repo,sha,paths) in repos.items():
 for path in paths:
  url=f'https://raw.githubusercontent.com/{repo}/{sha}/{path}'
  try:
   data=urllib.request.urlopen(url,timeout=30).read(150000)
   assert len(data)<150000
   local=key+'/'+path;dest=root/local;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
   records.append({'candidate':key,'repository':repo,'commit':sha,'path':path,'url':url,'local':local,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'status':'retrieved_text_only'})
  except Exception as e: records.append({'candidate':key,'repository':repo,'commit':sha,'path':path,'status':'unavailable','reason':type(e).__name__})
info=json.load(urllib.request.urlopen('https://huggingface.co/api/models/fal/AuraFace-v1',timeout=30));sha=info['sha']
for path in ['README.md','LICENSE.md']:
 url=f'https://huggingface.co/fal/AuraFace-v1/raw/{sha}/{path}';data=urllib.request.urlopen(url,timeout=30).read(150000);assert len(data)<150000
 local='auraface/'+path;dest=root/local;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 records.append({'candidate':'auraface','repository':'fal/AuraFace-v1','commit':sha,'path':path,'url':url,'local':local,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'status':'retrieved_text_only'})
(root/'source-lock.json').write_text(json.dumps({'scope':'Documentation and selected source only; no weights, datasets, image samples or executable dependencies downloaded','sources':records},indent=2)+'\n')
print(json.dumps({'files':len(records),'unavailable':[r for r in records if r['status']=='unavailable'],'auraface_revision':sha}))
