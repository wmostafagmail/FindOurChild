import './style.css';
import { headers } from 'next/headers';
export const metadata = { title: 'Find Our Child', description: 'Synthetic engineering environment' };
export default async function Layout({children}: {children: React.ReactNode}) {
  const locale = (await headers()).get('x-foc-locale') === 'en' ? 'en' : 'ar';
  return <html lang={locale} dir={locale==='ar'?'rtl':'ltr'}><body>{children}</body></html>;
}
