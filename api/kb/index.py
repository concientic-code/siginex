"""SIGINEX · GET /api/kb — Devuelve el banco de conocimiento completo (con ETag)"""
from http.server import BaseHTTPRequestHandler
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '_data')

API_KEYS = {k.strip() for k in os.environ.get('SIGINEX_API_KEYS', 'demo-key').split(',') if k.strip()}


def _load_json(name):
    with open(os.path.join(DATA_DIR, name), encoding='utf-8') as f:
        return json.load(f)


KB = _load_json('kb.json')
KB_ETAG = KB.get('checksum', '')


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers',
                         'Content-Type, X-Api-Key, X-Tenant-Id, If-None-Match')
        self.end_headers()

    def do_GET(self):
        api_key = self.headers.get('X-Api-Key', '')
        tenant_id = self.headers.get('X-Tenant-Id', '')

        if api_key not in API_KEYS:
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'API key inválida'}).encode())
            return

        if not tenant_id:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Falta X-Tenant-Id'}).encode())
            return

        # ETag / 304
        if_none_match = self.headers.get('If-None-Match', '')
        if if_none_match and if_none_match == KB_ETAG:
            self.send_response(304)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('ETag', KB_ETAG)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(KB).encode())
