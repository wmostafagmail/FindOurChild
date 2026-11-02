'use client';

import {useEffect,useRef,useState} from 'react';

type RecordValue={record_id:string;confirmation:{reviewed_draft_sha256:string};time:{expires_at:string}} & Record<string,unknown>;
type Draft={record:RecordValue;nonce:string;challenge_expires_at:string};
type Status={permanent_fixture_history:boolean;record_template:Record<string,unknown>;fixture_plan:{images:Record<string,unknown>[];pairings:Record<string,unknown>[]}};
const canonical=(value:unknown):string=>{
  if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
  if(value!==null && typeof value==='object')return '{'+Object.entries(value).sort(([a],[b])=>a<b?-1:a>b?1:0)
    .map(([key,item])=>JSON.stringify(key)+':'+canonical(item)).join(',')+'}';
  return JSON.stringify(value);
};

export default function OwnerPanel({ar}:{ar:boolean}) {
  const [status,setStatus]=useState<Status|null>(null);
  const [draft,setDraft]=useState<Draft|null>(null);
  const [result,setResult]=useState<{record_id:string;expires_at:string}|null>(null);
  const [state,setState]=useState('loading');
  const [checked,setChecked]=useState(false);
  const [busy,setBusy]=useState(false);
  const summary=useRef<HTMLHeadingElement>(null);
  const words=ar?{
    loading:'جار التحقق',ready:'تم التحقق من جلسة الاختبار الخيالية',denied:'الوصول مرفوض أو غير متاح. يلزم مالك معين ومصادقة حديثة متعددة العوامل.',
    prepared:'راجع النطاق الكامل ثم أكد صراحة',confirmed:'تم حفظ تفويض الاختبار. التنفيذ الفعلي معطل.',revoked:'ألغي التفويض. تمنع النتائج المتأخرة.',
    prepare:'إعداد نطاق ثابت للمراجعة',confirm:'تأكيد هذه البصمة والنطاق فقط',revoke:'إلغاء التفويض',refresh:'إعادة التحقق',
    login:'تسجيل الدخول بمصادقة حديثة متعددة العوامل',scope:'السجل الكامل للنطاق الثابت',digest:'بصمة المسودة المعروضة',
    check:'راجعت النطاق والبصمة وجميع القيود. أؤكد هذا الاختبار الخيالي فقط.',fixtures:'خطة الصور الخيالية الثابتة',
    warning:'لا يوجد فحص بشري مستقل. تتركز الثقة في المالك ومزود الهوية والمضيف. مصدر الصور ومعرفة النتائج السابقة لا يمكن إثباتهما بشكل مستقل. استثناء زمن قاعدة البيانات مستمر؛ الهدف الأصلي ١٠٠٠ مللي ثانية.',
    times:'ينتهي التحدي خلال خمس دقائق؛ التفويض بحد أقصى أربع ساعات؛ إذن العامل الداخلي بحد أقصى ثلاثين ثانية.',
    unknown:'تواريخ الالتقاط والأعمار غير المعروفة تبقى مجهولة. تحفظ جميع الصور الثماني والأربعين وروابطها الأربع والعشرون والأخطاء دون استبدال.',
  }:{loading:'Checking session',ready:'Synthetic engineering session verified',denied:'Denied or unavailable. A designated owner and fresh MFA are required.',
    prepared:'Review the entire scope, then explicitly confirm',confirmed:'Test authorization saved. Actual execution remains disabled.',revoked:'Authorization revoked. Late results are fenced.',
    prepare:'Prepare immutable scope for review',confirm:'Confirm only this digest and scope',revoke:'Revoke authorization',refresh:'Check again',
    login:'Sign in with fresh MFA',scope:'Complete immutable scope record',digest:'Reviewed draft digest',
    check:'I reviewed the scope, digest and all restrictions. I confirm only this fictional engineering test.',fixtures:'Immutable fictional image plan',
    warning:'There is no independent human review. Trust is concentrated in the owner, IdP and host. Image provenance and prior score knowledge cannot be independently proven. The database latency exception remains; the original target is 1,000 ms.',
    times:'The challenge expires in five minutes; authorization lasts at most four hours; an internal worker lease lasts at most thirty seconds.',
    unknown:'Unknown capture dates and ages remain unknown. All 48 images, 24 links and failures are retained without replacement.',
  };
  async function request(path:string,body?:unknown) {
    const csrf=document.cookie.split('; ').find(v=>v.startsWith('__Host-foc-csrf='))?.split('=')[1]??'';
    const response=await fetch('/demo-authorization/'+path,{method:body===undefined?'GET':'POST',cache:'no-store',
      headers:body===undefined?{}:{'Content-Type':'application/json','X-CSRF-Token':csrf},
      body:body===undefined?undefined:canonical(body)});
    if(!response.ok)throw new Error('denied');
    return response.json();
  }
  async function load(){setBusy(true);try{setStatus(await request('status'));setState('ready');}
    catch{setStatus(null);setDraft(null);setResult(null);setState('denied');}finally{setBusy(false);}}
  useEffect(()=>{void load();},[]); // No credentials/records in persistent browser storage.
  async function act(action:'prepare'|'confirm'|'revoke') {
    if(busy)return;setBusy(true);
    try {
      if(action==='prepare'){setDraft(await request('prepare',{}));setResult(null);setChecked(false);setState('prepared');}
      if(action==='confirm' && draft && checked){setResult(await request('confirm',{record_id:draft.record.record_id,
        nonce:draft.nonce,reviewed_draft_sha256:draft.record.confirmation.reviewed_draft_sha256}));setState('confirmed');}
      if(action==='revoke' && result){await request('revoke',{record_id:result.record_id});setState('revoked');setDraft(null);setResult(null);}
      summary.current?.focus();
    }catch{setState('denied');setDraft(null);setResult(null);setStatus(null);}finally{setBusy(false);}
  }
  return <div data-testid="owner-panel" data-state={state}>
    <p role="status" aria-live="polite">{words[state as keyof typeof words]??words.denied}</p>
    <a href="/identity/login">{words.login}</a>
    <p>{words.warning}</p><p>{words.times}</p><p>{words.unknown}</p>
    <div className="actions"><button onClick={()=>void load()} disabled={busy}>{words.refresh}</button>
      {status && <button data-testid="prepare" disabled={busy} onClick={()=>void act('prepare')}>{words.prepare}</button>}</div>
    {status && <section aria-labelledby="fixture-title"><h2 id="fixture-title">{words.fixtures}</h2>
      <p data-testid="fixture-count">48 / 24</p>
      <p data-testid="freeze-history" data-frozen={String(status.permanent_fixture_history)}>{ar?
        'سجل التعرض الأول دائم عبر الحملات وعمليات الاستعادة؛ لا يسمح بتغيير الروابط بناء على النتائج.':
        'First-run history is permanent across campaigns and restores; score-informed pairing changes are prohibited.'}</p>
      <details><summary>{words.fixtures}</summary><pre className="owner-record" dir="ltr" data-testid="fixture-json">
        {JSON.stringify(status.fixture_plan,null,2)}</pre></details></section>}
    {draft && <section aria-labelledby="scope-title"><h2 id="scope-title" tabIndex={-1} ref={summary}>{words.scope}</h2>
      <p>{words.digest}: <bdi data-testid="draft-digest" dir="ltr">{draft.record.confirmation.reviewed_draft_sha256}</bdi></p>
      <pre dir="ltr" className="owner-record" data-testid="scope-record">{JSON.stringify(draft.record,null,2)}</pre>
      <p><time dateTime={draft.challenge_expires_at}>{draft.challenge_expires_at}</time></p>
      <label className="workflow-check"><input type="checkbox" checked={checked} onChange={e=>setChecked(e.target.checked)}
        data-testid="confirm-check"/>{words.check}</label>
      <button data-testid="confirm" disabled={busy||!checked||Boolean(result)} onClick={()=>void act('confirm')}>{words.confirm}</button>
    </section>}
    {result && <section><h2>{words.confirmed}</h2><p><time dateTime={result.expires_at}>{result.expires_at}</time></p>
      <button data-testid="revoke" disabled={busy} onClick={()=>void act('revoke')}>{words.revoke}</button></section>}
  </div>;
}
