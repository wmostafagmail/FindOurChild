// Separate fixed V3 BFF. Browser cannot select a policy, upstream, owner, path or trust root.
async function proxy(request: Request, context: {params: Promise<{path:string[]}>}) {
  const path=(await context.params).path.join('/');
  if (!['status','prepare','confirm','revoke'].includes(path) || new URL(request.url).search) {
    return Response.json({code:'NOT_FOUND'},{status:404});
  }
  if ((path==='status') !== (request.method==='GET')) return Response.json({code:'METHOD_DENIED'},{status:405});
  const headers=new Headers();
  for (const key of ['cookie','origin','content-type','x-csrf-token','sec-fetch-site']) {
    const value=request.headers.get(key); if(value)headers.set(key,value);
  }
  if(Number(request.headers.get('content-length')??0)>16384)return Response.json({code:'TOO_LARGE'},{status:413});
  try {
    const body=request.method==='POST'?await request.text():undefined;
    if(body && new TextEncoder().encode(body).length>16384)return Response.json({code:'TOO_LARGE'},{status:413});
    // Host-only synthetic harness uses port 8001 in CI; ordinary app remains unprovisioned at 8000.
    const upstream=process.env.FOC_OWNER_ONLY_API_URL??'http://127.0.0.1:8000';
    if(!['http://127.0.0.1:8000','http://127.0.0.1:8001'].includes(upstream))throw new Error('Fixed upstream required');
    const response=await fetch(`${upstream}/demo-authorization/${path}`,{
      method:request.method,headers,body,cache:'no-store',redirect:'error',signal:AbortSignal.timeout(15000),
    });
    return new Response(await response.arrayBuffer(),{status:response.status,
      headers:{'Content-Type':'application/json','Cache-Control':'no-store','Referrer-Policy':'no-referrer'}});
  } catch {return Response.json({code:'OWNER_SERVICE_UNAVAILABLE'},{status:503,headers:{'Cache-Control':'no-store'}});}
}
export const GET=proxy;
export const POST=proxy;
