#!/usr/bin/env python3
"""Create a Gmail refresh token locally; never paste credentials into chat."""

from __future__ import annotations

import argparse
import getpass
import json
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Optional, Sequence
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


SCOPE = "https://www.googleapis.com/auth/gmail.send"
REDIRECT_URI = "http://127.0.0.1:8765/callback"


class CallbackHandler(BaseHTTPRequestHandler):
    code: Optional[str] = None
    error: Optional[str] = None
    state: Optional[str] = None

    def do_GET(self) -> None:  # noqa: N802
        query = parse_qs(urlparse(self.path).query)
        CallbackHandler.code = query.get("code", [None])[0]
        CallbackHandler.error = query.get("error", [None])[0]
        CallbackHandler.state = query.get("state", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Kind of News Gmail authorization received. You can close this tab.")

    def log_message(self, format: str, *args: object) -> None:
        return


def exchange_code(client_id: str, client_secret: str, code: str) -> Dict[str, object]:
    values = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }
    request = Request(
        "https://oauth2.googleapis.com/token",
        data=urlencode(values).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Create a Gmail OAuth refresh token locally")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--client-secret")
    args = parser.parse_args(argv)
    client_secret = args.client_secret or getpass.getpass("Google OAuth client secret: ")

    state = secrets.token_urlsafe(16)
    query = urlencode(
        {
            "client_id": args.client_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
    )
    CallbackHandler.code = None
    CallbackHandler.error = None
    CallbackHandler.state = None
    server = HTTPServer(("127.0.0.1", 8765), CallbackHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + query
    print("Opening the Google authorization page in your browser...")
    webbrowser.open(url)
    thread.join(timeout=180)
    server.server_close()
    if CallbackHandler.error:
        raise SystemExit("Google authorization failed: %s" % CallbackHandler.error)
    if CallbackHandler.state != state:
        raise SystemExit("Google authorization state did not match")
    if not CallbackHandler.code:
        raise SystemExit("Timed out waiting for the Google authorization callback")
    response = exchange_code(args.client_id, client_secret, CallbackHandler.code)
    refresh_token = response.get("refresh_token")
    if not refresh_token:
        raise SystemExit("Google did not return a refresh token; retry with consent prompt")
    print("GMAIL_REFRESH_TOKEN=%s" % refresh_token)
    print("Store this value only in GitHub Secrets, never in config.yml or source control.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
