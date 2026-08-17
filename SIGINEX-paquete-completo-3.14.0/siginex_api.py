#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIGINEX · Servidor API de referencia
Versión: 1.0.0  ·  Contrato: OpenAPI 1.1.2

Implementa los endpoints principales sobre el orquestador y el kb.json:
  GET  /kb                              -> banco de conocimiento (ETag = checksum)
  GET  /kb/version                      -> versión y checksum
  GET  /market-signals                  -> feed de vigilancia de mercado
  POST /diagnosticos/{id}/calcular      -> ejecuta el pipeline y devuelve el consolidado

Autenticación: API Key por tenant (cabecera X-Api-Key) + X-Tenant-Id.
Persistencia: al conectar PostgreSQL, fijar por sesión  SET app.tenant_id = '<uuid>'
para que la RLS del DDL 1.1.1 aísle los datos por tenant.

Requiere:  pip install fastapi uvicorn
Ejecutar:  uvicorn siginex_api:app --host 0.0.0.0 --port 8080
"""
import os, json
from fastapi import FastAPI, Header, HTTPException, Response, Request
from fastapi.responses import JSONResponse

import siginex_orchestrator as orch

BASE = os.path.dirname(os.path.abspath(__file__))

def _load(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as f:
        return json.load(f)

KB = _load("kb.json")
KB_VERSION = KB.get("kb_version")
KB_ETAG = KB.get("checksum", "")
# banco en el formato que espera el orquestador
KB_FOR_ORCH = {"modulos": KB["modulos"]}

# API keys por tenant (en producción: secreto gestionado / base de datos)
API_KEYS = {k.strip() for k in os.environ.get("SIGINEX_API_KEYS", "demo-key").split(",") if k.strip()}

try:
    MARKET = _load("Benchmark_Market_Watch.json").get("registro_senales", [])
except Exception:
    MARKET = []

app = FastAPI(title="SIGINEX API", version="1.1.2",
              description="API de diagnóstico del SGI. Resultado orientativo; no sustituye auditoría ni concepto legal.")

def _auth(x_api_key, x_tenant_id):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="API key inválida")
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Falta X-Tenant-Id")
    # En producción: abrir conexión y ejecutar  SET app.tenant_id = x_tenant_id  (RLS)
    return x_tenant_id


@app.get("/kb")
def get_kb(response: Response,
           x_api_key: str = Header(None), x_tenant_id: str = Header(None),
           if_none_match: str = Header(None)):
    _auth(x_api_key, x_tenant_id)
    if if_none_match and if_none_match == KB_ETAG:
        return Response(status_code=304)
    response.headers["ETag"] = KB_ETAG
    return KB


@app.get("/kb/version")
def get_kb_version(x_api_key: str = Header(None), x_tenant_id: str = Header(None)):
    _auth(x_api_key, x_tenant_id)
    return {"kb_version": KB_VERSION, "checksum": KB_ETAG,
            "total_preguntas": KB.get("total_preguntas")}


@app.get("/market-signals")
def get_market_signals(impacto: str = None, desde: str = None,
                       x_api_key: str = Header(None), x_tenant_id: str = Header(None)):
    _auth(x_api_key, x_tenant_id)
    data = MARKET
    if impacto:
        data = [s for s in data if str(s.get("impacto", "")).startswith(impacto)]
    if desde:
        data = [s for s in data if str(s.get("fecha", "")) >= desde]
    return {"data": data, "next_cursor": None}


@app.post("/diagnosticos/{diagnostico_id}/calcular")
async def calcular(diagnostico_id: str, request: Request,
                   x_api_key: str = Header(None), x_tenant_id: str = Header(None),
                   idempotency_key: str = Header(None)):
    tenant = _auth(x_api_key, x_tenant_id)
    body = await request.json()
    company = body.get("company", {})
    answers = body.get("answers", {})
    if not isinstance(answers, dict):
        raise HTTPException(status_code=422, detail="answers debe ser un objeto pregunta_id->valor")
    # normalizar valores numéricos que llegan como texto
    norm = {}
    for k, v in answers.items():
        norm[k] = int(v) if str(v) in ("0", "1", "2") else v
    result = orch.run(KB_FOR_ORCH, company, norm)
    result["diagnostico_id"] = diagnostico_id
    result["tenant_id"] = tenant
    # En producción: persistir en diagnostico/resultado_pilar/recomendacion/
    #                 tarea_mejora/ruta_aprendizaje y registrar evento_auditoria.
    return JSONResponse(result)


@app.get("/health")
def health():
    return {"status": "ok", "kb_version": KB_VERSION,
            "modulos": len(KB["modulos"]), "preguntas": KB.get("total_preguntas")}
