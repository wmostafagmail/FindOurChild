'use client';
import {useEffect,useState} from 'react';
type Session={principal_id:string,organizations:{id:string,role:string}[]};
export default function Identity({ar}:{ar:boolean}) {
  const [session,setSession]=useState<Session|null>(null);
  const [state,setState]=useState('loading');
  useEffect(()=>{fetch('/identity/me',{cache:'no-store'}).then(async r=>{
    if(r.ok){setSession(await r.json());setState('authenticated');}else{setState(r.status===401?'signed_out':'unavailable');}
  }).catch(()=>setState('unavailable'));},[]);
  async function logout(){
    const csrf=document.cookie.split('; ').find(v=>v.startsWith('__Host-foc-csrf='))?.split('=')[1] ?? '';
    const r=await fetch('/identity/logout',{method:'POST',headers:{'X-CSRF-Token':csrf}});
    if(r.ok){setSession(null);setState('signed_out');}else{setState('unavailable');}
  }
  return <section className="identity-panel" aria-label={ar?'الجلسة':'Session'}><p role="status" data-testid="identity-state" data-state={state}>
    {state==='authenticated'?(ar?'تم التحقق بخطوتين':'MFA verified'):state==='loading'?(ar?'جارٍ التحقق':'Checking session'):state==='unavailable'?(ar?'التحقق غير متاح. الوصول مرفوض.':'Verification unavailable. Access denied.'):(ar?'يلزم تسجيل الدخول':'Sign in required')}</p>
    {!session&&<a href="/identity/login">{ar?'تسجيل الدخول بخطوتين':'Sign in with MFA'}</a>}
    {session&&<><p data-testid="principal">{session.principal_id}</p><ul>{session.organizations.map((o)=><li key={o.id+o.role}>{o.id} · {o.role}</li>)}</ul><button onClick={logout}>{ar?'تسجيل الخروج':'Sign out'}</button></>}
  </section>;
}
