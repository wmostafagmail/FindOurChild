import {notFound} from 'next/navigation';
import Identity from './session';
export default async function Page({params}: {params:Promise<{locale:string}>}) {
  const {locale}=await params;
  if (!['ar','en'].includes(locale)) notFound();
  return <><a className="skip" href="#main">{locale==='ar'?'انتقل إلى المحتوى':'Skip to content'}</a>
    <header><span className="brand">Find Our Child</span><a href={locale==='ar'?'/en/identity':'/ar/identity'}>{locale==='ar'?'English':'العربية'}</a></header>
    <main id="main" tabIndex={-1}><h1>{locale==='ar'?'هوية الموظف وصلاحياته':'Staff identity and permissions'}</h1>
    <p className="notice">{locale==='ar'?'عرض توضيحي خيالي فقط. يلزم وصول موظف مصرح له.':'Fictional demonstration only. Authorized staff access is required.'}</p>
    <Identity ar={locale==='ar'}/></main></>;
}
