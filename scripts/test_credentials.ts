import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {createHmac} from 'node:crypto';
function totp(secret:string){
  const alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'; let bits='';
  for(const c of secret.replace(/=+$/,'')) bits+=alphabet.indexOf(c).toString(2).padStart(5,'0');
  const bytes=Buffer.from(bits.match(/.{8}/g)!.map(v=>parseInt(v,2)));
  const counter=Buffer.alloc(8);counter.writeBigUInt64BE(BigInt(Math.floor(Date.now()/30000)));
  const hash=createHmac('sha1',bytes).update(counter).digest();const offset=hash[19]&15;
  return String((hash.readUInt32BE(offset)&0x7fffffff)%1000000).padStart(6,'0');
}

export function privateFixture(){return JSON.parse(readFileSync('.runtime/identity.json','utf8')) as {password:string,otp:string};}
export function password(){return privateFixture().password;}
export function otp(){return totp(privateFixture().otp);}

// Resolved by the official runner only at secret fill time. Never logged or sent to a model.
export function reporterCode(){
  return execFileSync('.venv/bin/python',['-m','scripts.reporting_code'],{encoding:'utf8',stdio:['ignore','pipe','pipe']}).trim();
}
