'use strict';
const status=document.getElementById('status'),code=document.getElementById('code');
const ar=document.documentElement.lang==='ar';
const words=ar?{ok:'جلسة المالك موثقة؛ لا يوجد تفويض حملة.',denied:'يلزم تسجيل دخول حديث بخطوتين.',local:'انسخ الرمز إلى أمر التهيئة المحلي فقط. ينتهي خلال خمس دقائق.'}:{ok:'Owner session verified; no campaign authorization.',denied:'Fresh owner MFA is required.',local:'Enter this code only in the local setup terminal. It expires in five minutes.'};
async function call(path,mutation=false){
 const csrf=document.cookie.split('; ').find(v=>v.startsWith('__Host-foc-demo-csrf='))?.split('=')[1]??'';
 const r=await fetch('/owner/'+path,{method:mutation?'POST':'GET',credentials:'same-origin',cache:'no-store',redirect:'error',headers:mutation?{'Content-Type':'application/json','X-CSRF-Token':csrf}:{},body:mutation?'{}':undefined});
 if(!r.ok)throw Error('denied');return r.json();
}
const proof=document.getElementById('proof'),logout=document.getElementById('logout');
async function check(){try{await call('session');status.textContent=words.ok;proof.disabled=false;logout.disabled=false;}catch{code.textContent='';status.textContent=words.denied;proof.disabled=true;logout.disabled=true;}}
proof.addEventListener('click',async()=>{proof.disabled=true;try{const r=await call('enrollment-proof',true);code.textContent=r.local_setup_code;status.textContent=words.local;}catch{code.textContent='';status.textContent=words.denied;}finally{proof.disabled=false;}});
logout.addEventListener('click',async()=>{code.textContent='';try{await call('logout',true);}finally{await check();}});
window.addEventListener('pagehide',()=>{code.textContent='';});window.addEventListener('pageshow',()=>{void check();});void check();
