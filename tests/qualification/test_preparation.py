import copy
import hashlib
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest
from foc_api.research.qualification import (ROOT, ARTIFACT, ARTIFACT_SHA256, MODEL_IDS, PROTOCOL_HASH, QualificationError, absent_subject_budget, authorize_synthetic_dataset, fixture_identity, load_registry, request_model_download, verify_registry, verify_synthetic_artifact, wilson_interval, zero_event_upper)
from foc_api.research.pipeline import digest
from foc_api.research.evaluation import Record, evaluate

NOW = datetime(2026, 10, 26, tzinfo=timezone.utc)


def dataset():
    rows=[]
    for h,(subject,family,event) in fixture_identity().items():
        i=int(event.rsplit('-',1)[1])
        if i not in [0,16]:continue
        rows.append(dict(image_hash=h,subject=subject,family=family,capture_event=event,partition='test',role='gallery' if i==0 else 'probe',registry='found' if i==0 else 'missing'))
    m=dict(schema_version='qualification-dataset-1',organization='fixture-org-a',data_class='synthetic',protocol_hash=PROTOCOL_HASH,training_overlap='not_applicable_weight_free',test_used_for_tuning=False,age_progression=False,records=rows)
    g=dict(data_class='synthetic',purpose='synthetic-qualification',dataset_hash=digest(m),protocol_hash=PROTOCOL_HASH,organization='fixture-org-a',principal='fixture-operator',issuer='fixture-issuer',reviewer='fixture-reviewer',issued_at='2026-10-25T00:00:00+00:00',expires_at='2026-10-27T00:00:00+00:00',revoked=False)
    return m,g


def authorize(m,g,**kwargs):
    return authorize_synthetic_dataset(m,g,organization='fixture-org-a',principal='fixture-operator',now=NOW,**kwargs)


def test_registry_has_eight_blocked_profiles_and_no_verified_binary():
    r=load_registry();assert {x['id'] for x in r['models']}==MODEL_IDS
    assert r['real_models_qualified']==0
    assert all(x['decision']=='blocked' and x['artifact']['bytes_verified'] is False for x in r['models'])


@pytest.mark.parametrize('change',['missing','duplicate','unknown','extra','download','execute','operate','verified','mutable','provenance','evidence','identity'])
def test_model_manifest_rejects_incomplete_or_activation_claims(change):
    r=load_registry();m=r['models'][0];e={x for row in r['models'] for x in row['evidence']}
    if change=='missing':r['models'].pop()
    elif change=='duplicate':r['models'][-1]=copy.deepcopy(m)
    elif change=='unknown':m['id']='unknown'
    elif change=='extra':m['accept_license']=True
    elif change=='download':m['download_allowed']=True
    elif change=='execute':m['execution_allowed']=True
    elif change=='operate':m['operational_allowed']=True
    elif change=='verified':m['artifact']['bytes_verified']=True
    elif change=='mutable':m['source_revision']='main'
    elif change=='provenance':m['training_provenance']=''
    elif change=='evidence':m['evidence']=['https://untrusted.invalid/terms']
    else:m['artifact']['identity_status']='verified'
    with pytest.raises(QualificationError):verify_registry(r,e)


@pytest.mark.parametrize('change',['source','escape','digest'])
def test_publisher_evidence_integrity_and_identity_binding(tmp_path,change):
    for phase in ['phase2a','phase2b']:
        shutil.copytree(ROOT/f'docs/{phase}/research',tmp_path/f'docs/{phase}/research')
    (tmp_path/'config').mkdir();shutil.copyfile(ROOT/'config/qualification-models.json',tmp_path/'config/qualification-models.json')
    p=tmp_path/'docs/phase2b/research/source-lock.json';lock=json.loads(p.read_text())
    if change=='source':(tmp_path/'docs/phase2b/research'/lock['sources'][0]['local']).write_text('tampered')
    elif change=='escape':lock['sources'][0]['local']='../../../../outside';p.write_text(json.dumps(lock))
    else:
        q=tmp_path/'config/qualification-models.json';r=json.loads(q.read_text());r['models'][2]['artifact']['publisher_sha256']='0'*64;q.write_text(json.dumps(r))
    with pytest.raises(QualificationError):load_registry(tmp_path)


@pytest.mark.parametrize('model',sorted(MODEL_IDS))
def test_restricted_download_cannot_be_enabled_by_flags_or_urls(model):
    with pytest.raises(QualificationError):request_model_download(model,url='https://example.invalid/model',accept_license=True,legal_approved=True,offline=False)


def test_known_synthetic_artifact_integrity_only():
    assert verify_synthetic_artifact(ARTIFACT,ARTIFACT_SHA256)==ARTIFACT_SHA256


@pytest.mark.parametrize('data,sha',[(b'child photograph','0'*64),(ARTIFACT+b'x',ARTIFACT_SHA256),(ARTIFACT,'0'*64),(ARTIFACT.decode(),ARTIFACT_SHA256),(b'pickle','1'*64)])
def test_unknown_corrupted_or_self_hashed_artifacts_rejected(data,sha):
    with pytest.raises(QualificationError):verify_synthetic_artifact(data,sha)


def test_synthetic_dataset_requires_bound_independent_permission():
    m,g=dataset();r=authorize(m,g);assert r['real_data_authorized'] is False and r['records']==2


@pytest.mark.parametrize('change',['real','self-claimed-approved-real','protocol','tuning','training-overlap','age-progression','duplicate','subject-split','nonfixture','capture-relabel','extra-field','revoked','expired','future','naive-time','retention','self-review','operator-review','tenant','principal','dataset-swap','purpose','missing-context','withdrawal'])
def test_dataset_authorization_revocation_and_leakage_fail_closed(change):
    m,g=dataset();options={}
    if change=='real':m['data_class']='child-photographs'
    elif change=='self-claimed-approved-real':m['data_class']='authorized-child';g['data_class']='authorized-child'
    elif change=='protocol':m['protocol_hash']='0'*64
    elif change=='tuning':m['test_used_for_tuning']=True
    elif change=='training-overlap':m['training_overlap']='unknown'
    elif change=='age-progression':m['age_progression']=True
    elif change=='duplicate':m['records'].append(copy.deepcopy(m['records'][0]))
    elif change=='subject-split':m['records'][1]['partition']='calibration'
    elif change=='nonfixture':m['records'][0]['image_hash']=hashlib.sha256(b'not an allowlisted fixture').hexdigest()
    elif change=='capture-relabel':m['records'][1]['capture_event']=m['records'][0]['capture_event']
    elif change=='extra-field':m['records'][0]['location']='forbidden'
    elif change=='revoked':g['revoked']=True
    elif change=='expired':g['expires_at']='2026-10-26T00:00:00+00:00'
    elif change=='future':g['issued_at']='2026-10-27T00:00:00+00:00'
    elif change=='naive-time':g['issued_at']='2026-10-25T00:00:00'
    elif change=='retention':g['expires_at']='2028-10-26T00:00:00+00:00'
    elif change=='self-review':g['reviewer']=g['issuer']
    elif change=='operator-review':g['reviewer']=g['principal']
    elif change=='tenant':g['organization']='fixture-org-b'
    elif change=='principal':g['principal']='fixture-other'
    elif change=='dataset-swap':g['dataset_hash']='0'*64
    elif change=='purpose':g['purpose']='operational-identification'
    elif change=='missing-context':
        with pytest.raises(QualificationError):authorize_synthetic_dataset(m,g,now=NOW)
        return
    else:options['revoked_subjects']=['fixture-subject-0']
    if change!='dataset-swap':g['dataset_hash']=digest(m)
    with pytest.raises(QualificationError):authorize(m,g,**options)


@pytest.mark.parametrize('rank',[1,10,50,51])
def test_recall_and_fnir_at_fixed_case_ranks(rank):
    rows=[]
    for i in range(60):
        score=1-i/100;v=(score,math.sqrt(1-score*score))+(0.,)*126
        rows.append(Record(hashlib.sha256(f'gallery{i}'.encode()).hexdigest(),f's{i}',f'f{i}',f'c{i}','found','gallery','test',v))
    rows.append(Record(hashlib.sha256(b'probe').hexdigest(),f's{rank-1}',f'f{rank-1}','query','missing','probe','test',(1.,)+(0.,)*127))
    r=evaluate(rows,threshold=0.0,bootstrap_samples=100)
    assert r['recall']=={str(k):float(rank<=k) for k in [1,10,50]}
    assert r['fnir']==float(rank>50) and r['fpir'] is None and r['recognition_accuracy_claim'] is False


@pytest.mark.parametrize('age,bucket',[(0,'0-2y'),(6,'0-2y'),(24,'0-2y'),(36,'3-5y'),(72,'6-9y'),(120,'10-13y'),(168,'14-17y')])
def test_invented_capture_age_strata_do_not_claim_longitudinal_accuracy(age,bucket):
    v=(1.,)+(0.,)*127
    rows=[Record(hashlib.sha256(b'gallery').hexdigest(),'s','f','c','found','gallery','test',v),Record(hashlib.sha256(b'probe').hexdigest(),'s','f','q','missing','probe','test',v,age_min_months=age,age_max_months=age)]
    r=evaluate(rows,threshold=.5,bootstrap_samples=100)
    assert r['strata']['capture_age'][bucket]['mate_present']==1 and r['recognition_accuracy_claim'] is False


def test_rare_event_budget_is_independent_subjects_not_image_pairs():
    assert absent_subject_budget(.001)==2995 and absent_subject_budget(.0001)==29956
    assert zero_event_upper(2995)<=.001<zero_event_upper(2994)
    assert zero_event_upper(1)==pytest.approx(.95)
    assert wilson_interval(0,0) is None
    assert wilson_interval(0,10)==pytest.approx([0,.2775327999])
    assert wilson_interval(10,10)==pytest.approx([.7224672001,1])


@pytest.mark.parametrize('n',[-1,0,True,1.5,10**10])
def test_invalid_independent_trial_denominators_rejected(n):
    with pytest.raises(QualificationError):zero_event_upper(n)


@pytest.mark.parametrize('target',[0,1,-1,float('nan'),True,None])
def test_invalid_statistical_targets_rejected(target):
    with pytest.raises(QualificationError):absent_subject_budget(target)


def test_multi_photo_case_aggregation_is_bounded_and_order_independent():
    from foc_api.research.qualification import multi_photo_candidates
    from dataclasses import replace
    v=(1.,)+(0.,)*127
    p=Record('0'*64,'s','f','q','missing','probe','test',v)
    probes=[replace(p,image_hash=str(i)*64) for i in range(4)]
    gallery=[Record('a'*64,'s','f','c','found','gallery','test',v),Record('b'*64,'x','y','d','found','gallery','test',(0.,1.)+(0.,)*126)]
    result=multi_photo_candidates(probes,gallery)
    assert [r['case'] for r in result]==['c','d']
    assert result==multi_photo_candidates(list(reversed(probes)),list(reversed(gallery)))
    assert result==multi_photo_candidates(probes[:3],gallery)


@pytest.mark.parametrize('change',['duplicate','subject','partition','space','query-gallery','budget'])
def test_multi_photo_query_leakage_and_context_fail_closed(change):
    from foc_api.research.qualification import multi_photo_candidates
    from dataclasses import replace
    v=(1.,)+(0.,)*127
    p=Record('0'*64,'s','f','q','missing','probe','test',v)
    q=replace(p,image_hash='1'*64)
    gallery=[Record('a'*64,'s','f','c','found','gallery','test',v)]
    if change=='duplicate':q=p
    elif change=='subject':q=replace(q,subject='other')
    elif change=='partition':q=replace(q,partition='calibration')
    elif change=='space':q=replace(q,space_id='unqualified')
    elif change=='query-gallery':gallery=[replace(gallery[0],image_hash=p.image_hash)]
    with pytest.raises(QualificationError):multi_photo_candidates([p,q],gallery,k=51 if change=='budget' else 50)
