import {notFound} from 'next/navigation';
import Reporting from './reporting';
export const dynamic='force-dynamic';
export default async function Page({params}:{params:Promise<{locale:string}>}){
 const {locale}=await params;if(!['ar','en'].includes(locale))notFound();
 return <Reporting initialLocale={locale as 'ar'|'en'}/>;
}
