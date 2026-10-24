// Fixed upstream BFF. No browser-controlled URL, bearer token, or forwarded identity headers.
const paths = /^(login|callback|me|logout|organizations\/[a-f0-9-]{36}\/(memberships|audit|cases\/[a-f0-9-]{36}\/permission))$/;
async function proxy(request: Request, context: {params: Promise<{path:string[]}>}) {
  const path = (await context.params).path.join('/');
  if (!paths.test(path)) return Response.json({code:'NOT_FOUND'}, {status:404});
  const headers = new Headers();
  for (const name of ['cookie','origin','content-type','x-csrf-token','sec-fetch-site']) {
    const value = request.headers.get(name);
    if (value) headers.set(name,value);
  }
  if (request.method === 'POST' && Number(request.headers.get('content-length') ?? '0') > 4096) {
    return Response.json({code:'TOO_LARGE'}, {status:413});
  }
  try {
    const body = request.method === 'POST' ? await request.text() : undefined;
    if (body && body.length>4096) return Response.json({code:'TOO_LARGE'}, {status:413});
    const response = await fetch(`${process.env.FOC_API_URL ?? 'http://127.0.0.1:8000'}/identity/${path}${new URL(request.url).search}`, {
      method:request.method,headers,body,redirect:'manual',cache:'no-store',signal:AbortSignal.timeout(15000),
    });
    const output = new Headers({'Cache-Control':'no-store','Referrer-Policy':'no-referrer'});
    for (const key of ['content-type','location']) {
      const value = response.headers.get(key); if (value) output.set(key,value);
    }
    for (const cookie of response.headers.getSetCookie()) output.append('set-cookie',cookie);
    return new Response(await response.arrayBuffer(),{status:response.status,headers:output});
  } catch { return Response.json({code:'IDENTITY_UNAVAILABLE'},{status:503}); }
}
export const GET = proxy;
export const POST = proxy;
