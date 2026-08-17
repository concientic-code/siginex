# SIGINEX · Runbook de despliegue (puesta en producción)

**Versión del documento:** 1.0.0 · **Fecha:** 2026-07-04
**Incremento de plataforma:** SIGINEX 3.10.0 → **3.11.0**
**Entregables:** `siginex_kb_export.py` · `kb.json` · `kb-version.json` · `siginex_api.py` (servidor de referencia) · `docker-compose.yml` · `.env.example`

> El salto de "sistema construido" a "sistema operando". Todo lo anterior (skills, motores, orquestador) se expone detrás de una API sobre una base de datos multi-tenant.

---

## 1. Arquitectura de despliegue

Base de datos **PostgreSQL** (esquema `siginex`, RLS por tenant) + servicio **API** (FastAPI de referencia) que ejecuta el **orquestador** sobre el **kb.json**. La vigilancia (scheduler + agentes) corre como jobs programados que escriben en `normativa_entry`, `market_signal` y `alerta`.

## 2. Prerrequisitos

- Docker / Docker Compose (o Postgres 16 + Python 3.11 gestionados).
- Un `Dockerfile` para el servicio `api` (Python 3.11-slim + `pip install fastapi uvicorn psycopg[binary]`).
- Variables de entorno (ver `.env.example`): `DB_PASSWORD`, `SIGINEX_API_KEYS`.

## 3. Migraciones (base de datos)

El DDL es la migración inicial. Con Compose se aplica solo al crear el contenedor (`docker-entrypoint-initdb.d`). Manualmente:

```
psql "$DATABASE_URL" -f siginex-schema.sql
```

Cada cambio de esquema futuro se versiona como una migración incremental (p. ej. con Alembic o archivos `NNN_*.sql`) y se registra en el CHANGELOG.

## 4. Hidratación de la base de conocimiento (GET /kb)

El banco deja de vivir embebido en el artefacto: se exporta y se sirve por API.

```
python3 siginex_kb_export.py siginex-autodiagnostico-500.html   # genera kb.json y kb-version.json
```

El artefacto y cualquier cliente consumen `GET /kb` (con `ETag` = checksum) y cachean por versión. Al publicar un nuevo banco se regenera `kb.json`, cambia el checksum y se incrementa `kb_version`.

## 5. Autenticación y multi-tenant

- Cada petición envía `X-Api-Key` (validada por tenant) y `X-Tenant-Id`.
- Al abrir la conexión a la base, la app ejecuta `SET app.tenant_id = '<uuid>'`; la **RLS FORCE** del DDL garantiza el aislamiento aunque la app tenga un error de filtrado.
- En producción, gestionar las llaves con un secreto (no en texto plano) y usar OAuth2 client-credentials para integraciones (scopes `kb:read`, `diagnosticos:read/write`, `market:read`).

## 6. Ciclo de un diagnóstico

1. `POST /diagnosticos` crea el diagnóstico (idempotente por `Idempotency-Key`).
2. `PUT /diagnosticos/{id}/respuestas` registra respuestas.
3. `POST /diagnosticos/{id}/calcular` ejecuta el **orquestador** y persiste `resultado_pilar`, `recomendacion`, `tarea_mejora` y `ruta_aprendizaje`; registra `evento_auditoria`.
4. `GET /diagnosticos/{id}/resultados` devuelve el consolidado.

El servidor de referencia (`siginex_api.py`) implementa `GET /kb`, `GET /kb/version`, `GET /market-signals`, `POST /diagnosticos/{id}/calcular` y `GET /health`.

## 7. Observabilidad

Instrumentar según `siginex-observabilidad-evals.md`: latencia por endpoint y por paso del pipeline, tasa de error, distribución de score/niveles por tenant, deriva entre versiones de KB, y salud de la vigilancia. Correr `siginex_evals.py` en el pipeline de CI ante cualquier cambio de banco, scoring u orquestador (compuerta: 8/8).

## 8. Seguridad

- TLS en tránsito; cifrado en reposo.
- Privacidad (Ley 1581): minimización de evidencias, retención y consentimiento del tenant.
- Gobernanza de IA (ISO 42001): trazabilidad de decisiones (`kb_version`), validación humana y las evals como evidencia.

## 9. Checklist go-live

- [ ] DDL aplicado y RLS verificada (probar aislamiento entre dos tenants).
- [ ] `kb.json` publicado; `GET /kb/version` responde el checksum esperado.
- [ ] API con auth por tenant y OAuth2 para integraciones.
- [ ] `siginex_evals.py` en verde (8/8) en CI.
- [ ] Scheduler de vigilancia activo (normativa diaria, mercado semanal) y alertas enrutadas.
- [ ] Observabilidad instrumentada (dashboards y alertas de salud).
- [ ] Respaldo/restore de la base probado.

## 10. Lo que habilita

Con esto operando, se acumulan diagnósticos reales y se desbloquea el **benchmarking sectorial** (agregación por sector), el último gran pendiente del mapa.
