"""SIGINEX · GET /api/market-signals — Feed de vigilancia de mercado"""
from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs

DATA_DIR = os.path.join(os.path.dirname(__file__), '_data')

API_KEYS = {k.strip() for k in os.environ.get('SIGINEX_API_KEYS', 'demo-key').split(',') if k.strip()}

MARKET = []
try:
    with open(os.path.join(DATA_DIR, 'Benchmark_Market_Watch.json'), encoding='utf-8') as f:
        mw = json.load(f)
    MARKET = mw.get('registro_senales', mw.get('signals', []))
except Exception:
    pass


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Api-Key, X-Tenant-Id')
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

        # Filtros opcionales
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        impacto = params.get('impacto', [None])[0]
        desde = params.get('desde', [None])[0]

        data = MARKET
        if impacto:
            data = [s for s in data if str(s.get('impacto', '')).startswith(impacto)]
        if desde:
            data = [s for s in data if str(s.get('fecha', '')) >= desde]

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'data': data, 'next_cursor': None}).encode())
