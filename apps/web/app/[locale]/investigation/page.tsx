import {notFound} from 'next/navigation';
import Investigation from './workspace';
export const dynamic='force-dynamic';
export default async function Page({params}:{params:Promise<{locale:string}>}){
 const {locale}=await params;if(!['ar','en'].includes(locale))notFound();
 return <Investigation initialLocale={locale as 'ar'|'en'}/>;
}
