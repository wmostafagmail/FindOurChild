"""Private synthetic delivery-sink reader for the deterministic test secret provider.
This operator-side fixture utility is never exposed as an application route or shipped to browsers.
"""
import hashlib
import json
import subprocess

from scripts.dev import ROOT, environment


def main():
    receipt=json.loads((ROOT/'.runtime/e2e-receipt.json').read_text())['receipt']
    name=hashlib.sha256(receipt.encode()).hexdigest()+'.json'
    program="import os,json;from pathlib import Path;from cryptography.fernet import Fernet;print(json.loads(Fernet(os.environ['FOC_CONTACT_KEY'].encode()).decrypt(Path('/delivery/'+"+repr(name)+").read_bytes()))['code'])"
    result=subprocess.run(['docker','compose','-f',str(ROOT/'compose.yaml'),'run','--rm','--no-deps','--user','0:0','api','python','-c',program],env=environment(),cwd=ROOT,capture_output=True,text=True,timeout=30,check=True)
    code=result.stdout.strip()
    if not 16<=len(code)<=64 or not code.replace('-','').replace('_','').isalnum():raise RuntimeError('Invalid isolated verification fixture')
    print(code)


if __name__=='__main__':main()
