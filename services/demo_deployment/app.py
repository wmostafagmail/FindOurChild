"""Private deployment readiness UI/API. Has no campaign or asset execution endpoint."""
import base64
import hashlib
import hmac
import html
import json
import secrets
import time
from pathlib import Path
from urllib.parse import urlencode

import httpx
import jwt
import psycopg
from cryptography.fernet import InvalidToken
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from tools.phase2e.owner_only_v3.records import Denied, canonical, require, sha

SESSION = '__Host-foc-demo-session'
FLOW = '__Host-foc-demo-flow'
CSRF = '__Host-foc-demo-csrf'


def build(state):
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware('http')
    async def security(request, call_next):
        try:
            # Fixed bounded public surface; no arbitrary asset or sensitive API path.
            if request.method == 'POST':
                raw = bytearray()
                async for part in request.stream():
                    require(len(raw) + len(part) <= 4096, 'request_bound')
                    raw.extend(part)
                request._body = bytes(raw)
            response = await call_next(request)
        except (Denied, InvalidToken, jwt.PyJWTError, httpx.HTTPError, ValueError, KeyError):
            response = JSONResponse({'code': 'DEPLOYMENT_DENIED'}, status_code=403)
        except (psycopg.Error, OSError):
            response = JSONResponse({'code': 'DEPLOYMENT_UNAVAILABLE'}, status_code=503)
        response.headers.update({'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer',
            'X-Content-Type-Options': 'nosniff', 'Content-Security-Policy': "default-src 'none'; script-src 'self'; style-src 'self'; form-action 'self'; frame-ancestors 'none'",
            'Strict-Transport-Security': 'max-age=31536000', 'X-Frame-Options': 'DENY'})
        return response

    def owner(request, mutation=False):
        require(not request.query_params and not request.headers.get('authorization'), 'no_browser_authority_claim')
        session = request.cookies.get(SESSION, '')
        actor, csrf = state.session(session)
        if mutation:
            require(request.headers.get('origin') == state.config['origin']
                    and request.headers.get('sec-fetch-site') in (None, 'same-origin'), 'csrf_origin')
            supplied = request.headers.get('x-csrf-token', '')
            # HTML form fallback is bounded and handled by the endpoint; never accepts a query credential.
            require(hmac.compare_digest(sha(supplied.encode()), csrf), 'csrf_token')
        return session, actor

    @app.get('/health')
    def health():
        return {'service': 'private_demo_readiness', 'campaign_authorization_available': False,
                'acquisition': False, 'model_parsing': False, 'inference': False}

    @app.get('/owner/login')
    def login():
        require(state.config['owner_subject'] is not None and state.identity.pin is not None, 'owner_unbound')
        now = int(time.time())
        flow = {'state': secrets.token_urlsafe(32), 'nonce': secrets.token_urlsafe(32),
                'verifier': secrets.token_urlsafe(48), 'created': now}
        challenge = base64.urlsafe_b64encode(hashlib.sha256(flow['verifier'].encode()).digest()).rstrip(b'=').decode()
        args = {'client_id': state.config['client'], 'redirect_uri': state.config['origin'] + '/owner/callback',
                'response_type': 'code', 'scope': 'openid', 'state': flow['state'], 'nonce': flow['nonce'],
                'code_challenge': challenge, 'code_challenge_method': 'S256', 'prompt': 'login', 'max_age': '0'}
        r = RedirectResponse(state.config['issuer'] + '/protocol/openid-connect/auth?' + urlencode(args), status_code=302)
        r.set_cookie(FLOW, state.cipher.encrypt(canonical(flow)).decode(), max_age=300,
                     secure=True, httponly=True, samesite='lax')
        return r

    @app.get('/owner/callback')
    def callback(request: Request):
        require(set(request.query_params) == {'state', 'session_state', 'iss', 'code'}
                or set(request.query_params) == {'state', 'iss', 'code'}, 'callback_closed')
        require(request.query_params.get('iss') == state.config['issuer'], 'callback_issuer')
        flow = json.loads(state.cipher.decrypt(request.cookies.get(FLOW, '').encode(), ttl=300))
        require(hmac.compare_digest(request.query_params.get('state', ''), flow['state'])
                and 0 <= time.time() - flow['created'] < 300, 'oidc_state')
        tokens = state.identity.request('/protocol/openid-connect/token', {'grant_type': 'authorization_code',
            'code': request.query_params['code'], 'redirect_uri': state.config['origin'] + '/owner/callback',
            'code_verifier': flow['verifier']})
        state.identity.id_token(tokens['id_token'], flow['nonce'])
        session, csrf = state.new_session(tokens['access_token'])
        r = RedirectResponse('/owner/en', status_code=302)
        r.set_cookie(SESSION, session, max_age=1800, secure=True, httponly=True, samesite='lax')
        r.set_cookie(CSRF, csrf, max_age=1800, secure=True, httponly=False, samesite='strict')
        r.delete_cookie(FLOW, secure=True, httponly=True, samesite='lax')
        return r

    @app.get('/owner.js')
    def script():
        return Response(Path(__file__).with_name('owner.js').read_bytes(), media_type='text/javascript')

    @app.get('/owner.css')
    def stylesheet():
        return Response(Path(__file__).with_name('owner.css').read_bytes(), media_type='text/css')

    @app.get('/owner/session')
    def session_status(request: Request):
        owner(request)
        return {'mfa_verified': True, 'campaign_authorization': False}

    @app.get('/owner/status')
    def status(request: Request):
        session, _ = owner(request)
        return state.readiness(session)

    @app.post('/owner/enrollment-proof')
    async def proof(request: Request):
        session, _ = owner(request, True)
        require(await request.body() == b'{}', 'proof_closed')
        return {'local_setup_code': state.proof(session), 'expires_in': 300,
                'purpose': 'terminal_readiness_enrollment_only_not_campaign_authority'}

    @app.post('/owner/logout')
    async def logout(request: Request):
        session, _ = owner(request, True)
        require(await request.body() == b'{}', 'logout_closed')
        with state.connect() as conn:
            conn.execute('UPDATE owner_deployment.sessions SET revoked=true WHERE key=%s', (sha(session.encode()),))
        r = JSONResponse({'signed_out': True, 'idp_session_also_requires_explicit_sign_out': True})
        for cookie in [SESSION, FLOW, CSRF]:
            r.delete_cookie(cookie, secure=True, path='/')
        return r

    @app.get('/owner/{locale}')
    def page(locale: str):
        require(locale in ('ar', 'en'), 'locale')
        ar = locale == 'ar'
        heading = 'تهيئة العرض الخاص فقط' if ar else 'Private demonstration readiness only'
        explanation = ('لا يوجد تفويض حملة أو تنزيل أو تحليل نماذج أو استدلال. يلزم تسجيل المالك الحقيقي بخطوتين.'
                       if ar else 'No campaign authorization, acquisition, model parsing or inference. Real owner MFA is required.')
        # No inline script, token, owner identifier, technical receipt or scope rendered.
        return HTMLResponse(f'<!doctype html><html lang="{locale}" dir="{"rtl" if ar else "ltr"}"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><title>' + html.escape(heading) + '</title>'
            '<link rel="stylesheet" href="/owner.css"><main><h1>' + html.escape(heading) + '</h1><p>' + html.escape(explanation) + '</p>'
            '<p><a href="/owner/login">' + ('تسجيل الدخول بخطوتين' if ar else 'Sign in with fresh MFA') + '</a></p>'
            '<p>' + ('رمز التهيئة محلي فقط؛ لا ترسله في الدردشة أو Git.' if ar else
            'Enrollment codes are for local terminal setup only; never post them in chat or Git.') + '</p>'
            '<p id="status" role="status"></p><button id="proof" disabled>' + ('إنشاء رمز التهيئة المحلي' if ar else 'Generate local setup code') + '</button>'
            '<output id="code" aria-live="polite" dir="ltr"></output><button id="logout" disabled>' + ('تسجيل الخروج' if ar else 'Sign out') + '</button>'
            '<script src="/owner.js" defer></script></main></html>')

    return app


def app():
    from .runtime import load

    return build(load())
