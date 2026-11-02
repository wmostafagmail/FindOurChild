import {notFound} from 'next/navigation';
import OwnerPanel from './panel';

export default async function Page({params}:{params:Promise<{locale:string}>}) {
  const {locale}=await params;
  if(!['ar','en'].includes(locale))notFound();
  const ar=locale==='ar';
  return <><a className="skip" href="#main">{ar?'انتقل إلى المحتوى':'Skip to content'}</a>
    <header><span className="brand">Find Our Child</span>
      <a href={ar?'/en/demo-authorization':'/ar/demo-authorization'}>{ar?'English':'العربية'}</a></header>
    <main id="main" className="workflow-panel" tabIndex={-1}>
      <h1>{ar?'تفويض العرض التجريبي للمالك':'Owner demonstration authorization'}</h1>
      <p className="notice" data-testid="source-only">{ar?
        'هندسة مصدرية فقط — بيانات خيالية. اقتناء الصور والنماذج والاستدلال معطلة. لا تثبت النتائج دقة تحديد هوية الأطفال.':
        'Source-only engineering — fictional data. Image/model acquisition and inference are disabled. Results do not establish child-identification accuracy.'}</p>
      <OwnerPanel ar={ar}/>
    </main></>;
}
