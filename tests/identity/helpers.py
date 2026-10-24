"""Synthetic real-Keycloak browser flow helper. Never emit cookies, codes or credentials."""

import base64
import hashlib
import hmac
import html
import json
import re
import ssl
import struct
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx


def otp(secret):
    counter = struct.pack(">Q", int(time.time()) // 30)
    mac = hmac.new(base64.b32decode(secret), counter, hashlib.sha1).digest()
    offset = mac[-1] & 15
    return str((int.from_bytes(mac[offset : offset + 4], "big") & 0x7FFFFFFF) % 1000000).zfill(6)


def real_login(username="synthetic-reviewer-a"):
    """Running Next BFF -> running Keycloak -> running API/private DB. Secure cookies forwarded explicitly by this non-browser HTTP harness."""
    private = json.loads((Path(__file__).resolve().parents[2] / ".runtime/identity.json").read_text())
    client = httpx.Client(
        follow_redirects=False,
        timeout=20,
        trust_env=False,
        verify=ssl.create_default_context(
            cafile=str(Path(__file__).resolve().parents[2] / ".runtime/tls/cert.pem")
        ),
    )
    start = client.get("https://127.0.0.1:3443/identity/login")
    assert start.status_code == 302
    flow = start.cookies["__Host-foc-flow"]
    page = client.get(start.headers["location"])

    def action(response):
        return html.unescape(re.search(r'<form[^>]*action="([^"]+)"', response.text).group(1))

    page = client.post(action(page), data={"username": username, "password": private["password"]})
    assert "otp" in page.text
    page = client.post(action(page), data={"otp": otp(private["otp"])})
    assert page.status_code == 302, "Synthetic MFA did not complete"
    target = page.headers["location"]
    assert urlparse(target).path == "/identity/callback"
    response = client.get(target, headers={"cookie": "__Host-foc-flow=" + flow})
    assert response.status_code == 302, "Synthetic OIDC callback did not complete"
    client._synthetic_callback = (target, flow)
    session = response.cookies["__Host-foc-session"]
    csrf = response.cookies["__Host-foc-csrf"]
    headers = {
        "cookie": "__Host-foc-session=" + session,
        "origin": "https://127.0.0.1:3443",
        "x-csrf-token": csrf,
    }
    return client, headers
