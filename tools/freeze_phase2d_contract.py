"""Developer-only additive contract freeze. CI validates checked-in contracts, never regenerates them."""

import json
import re
from pathlib import Path
from typing import Annotated

from pydantic import Field, TypeAdapter

from foc_api.config import Settings
from foc_api.main import create_app
from foc_api.synthetic_contracts import FixtureSource, FutureModelSource

ROOT=Path(__file__).resolve().parents[1]
generated=create_app(Settings('postgresql://foc_api@db/foc_synthetic')).openapi()
path=ROOT/'docs/contracts/openapi.json';contract=json.loads(path.read_text())
operations=[('get','/status'),('post','/cases/{cid}/runs'),('get','/runs/{rid}'),('post','/runs/{rid}/cancellations'),('get','/cases/{cid}/leads'),('get','/leads/{lid}/comparison'),('get','/leads/{lid}/photos/{pid}/content'),('post','/leads/{lid}/reviews'),('get','/leads/{lid}/investigation'),('post','/leads/{lid}/assignments'),('post','/leads/{lid}/notes'),('post','/leads/{lid}/peer-review-requests'),('post','/leads/{lid}/independent-reviews'),('get','/leads/{lid}/audit')]
paths={};needed=set();prefix='/v1/staff/synthetic-workflow'
errors=contract['paths']['/v1/staff/cases']['get']['responses']
for index,(method,suffix) in enumerate(operations,1):
    full=prefix+suffix;operation=generated['paths'][full][method]
    operation['operationId']=f'synthetic_workflow_{index:02}'
    operation['security']=[{'StaffSession':[]}]
    operation['x-data-class']='synthetic';operation['x-operational-activation']=False
    operation['x-implementation-status']='implemented-phase-2d-synthetic-only'
    for code,entry in errors.items():
        if code!='200':operation['responses'][code]=entry
    if suffix.endswith('/content'):operation['responses']['200']={'description':'Authorized clean procedural derivative','content':{'image/png':{'schema':{'type':'string','format':'binary'}}}}
    paths[full]={method:operation}
needed.update(n for n in re.findall(r'#/components/schemas/([A-Za-z0-9_]+)',json.dumps(paths)) if n!='Error')
queue=list(needed)
while queue:
    for name in re.findall(r'#/components/schemas/([A-Za-z0-9_]+)',json.dumps(generated['components']['schemas'][queue.pop()])):
        if name not in needed:needed.add(name);queue.append(name)
def rename(value):
    text=json.dumps(value)
    for name in sorted(needed,key=len,reverse=True):text=text.replace('#/components/schemas/'+name+'"','#/components/schemas/SW'+name+'"')
    return json.loads(text)
contract['paths'].update(rename(paths))
for name in list(contract['components']['schemas']):
    if name.startswith('SW'):del contract['components']['schemas'][name]
for name in needed:contract['components']['schemas']['SW'+name]=rename(generated['components']['schemas'][name])
contract['components'].setdefault('securitySchemes',{})['StaffSession']={'type':'apiKey','in':'cookie','name':'__Host-foc-session'}
path.write_text(json.dumps(contract,indent=2)+'\n')
schema=TypeAdapter(Annotated[FixtureSource|FutureModelSource,Field(discriminator='kind')]).json_schema()
schema.update({'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Candidate provenance contract v1; future model branch is descriptive only','x-current-provider':'fixture_scenario','x-operational-activation':False})
(ROOT/'docs/contracts/synthetic-candidate-source-v1.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
print('Frozen fourteen synthetic operations; future model contract does not authorize a provider')
