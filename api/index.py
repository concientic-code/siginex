"""
SIGINEX · Vercel Serverless API (Python Runtime)
Expone los endpoints principales como serverless functions.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Agregar la carpeta del paquete completo al path para importar el orquestador
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'SIGINEX-paquete-completo-3.14.0'))

DATA_DIR = os.path.join(os.path.dirname(__file__), '_data')


def _load_json(name):
    with open(os.path.join(DATA_DIR, name), encoding='utf-8') as f:
        return json.load(f)


# Pre-cargar datos en memoria (cold start)
KB = _load_json('kb.json')
KB_VERSION = KB.get('kb_version')
KB_ETAG = KB.get('checksum', '')
MARKET = []
try:
    mw = _load_json('Benchmark_Market_Watch.json')
    MARKET = mw.get('registro_senales', mw.get('signals', []))
except Exception:
    pass

API_KEYS = {k.strip() for k in os.environ.get('SIGINEX_API_KEYS', 'demo-key').split(',') if k.strip()}


def _cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-Api-Key, X-Tenant-Id, Idempotency-Key, If-None-Match',
        'Content-Type': 'application/json',
    }


def _error(status, msg):
    return {
        'statusCode': status,
        'headers': _cors_headers(),
        'body': json.dumps({'error': msg}),
    }


def _auth(headers):
    api_key = headers.get('x-api-key', '')
    tenant_id = headers.get('x-tenant-id', '')
    if api_key not in API_KEYS:
        return None, _error(401, 'API key inválida')
    if not tenant_id:
        return None, _error(400, 'Falta X-Tenant-Id')
    return tenant_id, None


class handler(BaseHTTPRequestHandler):
    def _set_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers',
                         'Content-Type, X-Api-Key, X-Tenant-Id, Idempotency-Key, If-None-Match')

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._set_cors()
        self.end_headers()
        body = json.dumps({
            'service': 'SIGINEX API',
            'version': '1.1.2',
            'status': 'ok',
            'endpoints': [
                'GET /api/health',
                'GET /api/kb',
                'GET /api/kb/version',
                'GET /api/market-signals',
                'POST /api/diagnosticos/{id}/calcular',
            ]
        })
        self.wfile.write(body.encode())
