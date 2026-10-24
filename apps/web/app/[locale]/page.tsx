import { notFound } from 'next/navigation';
export const dynamic = 'force-dynamic';
export default async function Home({params}: {params: Promise<{locale:string}>}) {
  const {locale} = await params;
  if (!['ar','en'].includes(locale)) notFound();
  const ar = locale === 'ar';
  let ready = false;
  try {
    const response = await fetch(`${process.env.FOC_API_URL ?? 'http://127.0.0.1:8000'}/health/ready`, {cache:'no-store', signal:AbortSignal.timeout(2000)});
    ready = response.ok && (await response.json()).status === 'ready';
  } catch { /* Dependency failure must never be presented as ready. */ }
  return <>
    <a className="skip" href="#main">{ar?'انتقل إلى المحتوى':'Skip to content'}</a>
    <header><span className="brand" lang="en" dir="ltr">Find Our Child</span>
      <nav aria-label={ar?'اللغة':'Language'}><a href={ar?'/en':'/ar'} lang={ar?'en':'ar'}>{ar?'English':'العربية'}</a></nav>
    </header>
    <main id="main" tabIndex={-1}><p className="eyebrow">{ar?'بيئة هندسية تجريبية':'ENGINEERING ENVIRONMENT'}</p>
      <h1>{ar?'معًا من أجل سلامة كل طفل':'Together for every child’s safety'}</h1>
      <p>{ar?'يجري إعداد المنصة. الإبلاغ والوصول إلى القضايا غير متاحين بعد.':'The platform is being prepared. Reporting and case access are not yet available.'}</p>
      <p className="notice">{ar?'بيانات اصطناعية فقط. لا تُدخل معلومات أو صور أطفال حقيقيين.':'Synthetic data only. Do not enter information or photographs of real children.'}</p>
      <section aria-label={ar?'حالة الخدمات':'Service status'}><h2>{ar?'حالة الخدمات':'Service status'}</h2>
        <p role="status" data-testid="readiness" data-ready={String(ready)}>{ready ? (ar?'الخدمات الأساسية جاهزة':'Foundation services ready') : (ar?'الخدمات الأساسية غير متاحة':'Foundation services unavailable')}</p>
      </section>
    </main><footer>{ar?'المرحلة 1A · مراجعة الأساس الهندسي':'Phase 1A · Engineering foundation review'}</footer>
  </>;
}
