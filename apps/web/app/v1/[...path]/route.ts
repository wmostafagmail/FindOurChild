// Fixed application gateway. No arbitrary upstream URL, bearer forwarding, or privileged environment.
const allowed=/^(public\/(intake-challenges|reports\/(missing|found)|access-requests|access-exchanges|abuse-reports|safety|drafts)|reporter\/(submission|supplements|contact|logout|upload-intents(\/[a-f0-9-]{36}\/(content|complete))?)|staff\/(cases(\/[a-f0-9-]{36}(\/(transitions|assignments|assertions|notes|moderation))?)?|media\/[a-f0-9-]{36}\/content))$/;
async function proxy(request:Request,context:{params:Promise<{path:string[]}>}){
  const path=(await context.params).path.join('/');
  const workflow=/^staff\/synthetic-workflow\/(status|cases\/[a-f0-9-]{36}\/(runs|leads)|runs\/[a-f0-9-]{36}(\/cancellations)?|leads\/[a-f0-9-]{36}\/(comparison|investigation|audit|reviews|assignments|notes|peer-review-requests|independent-reviews|photos\/[a-f0-9-]{36}\/content))$/;
  if(!allowed.test(path)&&!workflow.test(path))return Response.json({code:'NOT_FOUND'},{status:404});
  if(workflow.test(path)){
    const reads=path.endsWith('/status')||path.endsWith('/leads')||/\/runs\/[a-f0-9-]{36}$/.test(path)||/\/(comparison|investigation|audit|content)$/.test(path);
    if(request.method!==(reads?'GET':'POST'))return Response.json({code:'NOT_FOUND'},{status:404});
  }
  const headers=new Headers();
  for(const key of ['cookie','origin','sec-fetch-site','content-type','x-csrf-token','x-intake-challenge','idempotency-key','if-match']){
    const value=request.headers.get(key);if(value)headers.set(key,value);
  }
  const maximum=path.endsWith('/content')?5242880:65536;
  if(Number(request.headers.get('content-length')??'0')>maximum)return Response.json({code:'TOO_LARGE'},{status:413});
  let body:Uint8Array<ArrayBuffer>|undefined;
  if(request.method==='POST'||request.method==='PUT'){
    const reader=request.body?.getReader();const chunks:Uint8Array[]=[];let size=0;
    if(reader){while(true){const part=await reader.read();if(part.done)break;size+=part.value.length;if(size>maximum){await reader.cancel();return Response.json({code:'TOO_LARGE'},{status:413});}chunks.push(part.value);}}
    body=new Uint8Array(size);let offset=0;for(const chunk of chunks){body.set(chunk,offset);offset+=chunk.length;}
  }
  const query=new URL(request.url).searchParams;
  if([...query.keys()].some(k=>!['organization_id','limit','cursor','locale',...(workflow.test(path)?['review_state','assigned_to_me']:[])].includes(k)))return Response.json({code:'INVALID_QUERY'},{status:422});
  try{
    const response=await fetch(`${process.env.FOC_API_URL??'http://127.0.0.1:8000'}/v1/${path}?${query}`,{method:request.method,headers,body,redirect:'manual',cache:'no-store',signal:AbortSignal.timeout(20000)});
    const output=new Headers({'Cache-Control':'no-store','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff'});
    for(const key of ['content-type','content-disposition','etag','retry-after']){const value=response.headers.get(key);if(value)output.set(key,value);}
    for(const cookie of response.headers.getSetCookie())output.append('set-cookie',cookie);
    return new Response(await response.arrayBuffer(),{status:response.status,headers:output});
  }catch{return Response.json({code:'SERVICE_UNAVAILABLE'},{status:503});}
}
export const GET=proxy;export const POST=proxy;export const PUT=proxy;
