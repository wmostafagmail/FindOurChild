// Loopback TLS termination for the synthetic BFF and IdP; no external requests or access logs.
import https from 'node:https';
import http from 'node:http';
import {readFileSync} from 'node:fs';
const options={key:readFileSync('.runtime/tls/key.pem'),cert:readFileSync('.runtime/tls/cert.pem'),minVersion:'TLSv1.2'};
for(const [port,upstream] of [[3443,3000],[8443,8080]]){
  https.createServer(options,(request,response)=>{
    const headers={...request.headers,'x-forwarded-proto':'https','x-forwarded-host':`127.0.0.1:${port}`};
    const proxy=http.request({hostname:'127.0.0.1',port:upstream,path:request.url,method:request.method,headers},(result)=>{
      response.writeHead(result.statusCode??503,result.headers);result.pipe(response);
    });
    proxy.on('error',()=>{response.writeHead(503,{'content-type':'application/json'});response.end('{"code":"SERVICE_UNAVAILABLE"}');});
    request.pipe(proxy);
  }).listen(port,'127.0.0.1');
}
