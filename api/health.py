"""SIGINEX · GET /api/health"""
from http.server import BaseHTTPRequestHandler
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '_data')


def _load_json(name):
    with open(os.path.join(DATA_DIR, name), encoding='utf-8') as f:
        return json.load(f)


KB_VER = _load_json('kb-version.json')


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        body = json.dumps({
            'status': 'ok',
            'kb_version': KB_VER.get('kb_version'),
            'modulos': KB_VER.get('modulos'),
            'preguntas': KB_VER.get('total_preguntas'),
        })
        self.wfile.write(body.encode())
