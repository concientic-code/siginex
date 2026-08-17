# SIGINEX — Despliegue en Vercel

## Estructura del proyecto

```
siginex/
├── public/                          # Archivos estáticos (se sirven directamente)
│   ├── index.html                   # Landing page (/)
│   └── diagnostico.html             # App de autodiagnóstico (/diagnostico)
├── api/                             # Serverless Functions (Python)
│   ├── _data/                       # Datos estáticos consumidos por las functions
│   │   ├── kb.json                  # Base de conocimiento (521 preguntas)
│   │   ├── kb-version.json          # Versión y checksum de la KB
│   │   └── Benchmark_Market_Watch.json
│   ├── index.py                     # GET /api — info del servicio
│   ├── health.py                    # GET /api/health — healthcheck
│   ├── market-signals.py            # GET /api/market-signals
│   ├── kb/
│   │   ├── index.py                 # GET /api/kb — banco completo (con ETag)
│   │   └── version.py              # GET /api/kb/version
│   └── diagnosticos/
│       └── [id]/
│           └── calcular.py          # POST /api/diagnosticos/{id}/calcular
├── SIGINEX-paquete-completo-3.14.0/ # Código fuente original (orquestador, skills, docs)
├── vercel.json                      # Configuración de Vercel (routes, builds, env)
├── .vercelignore                    # Archivos excluidos del deploy
├── requirements.txt                 # Dependencias Python (vacío — stdlib pura)
└── DEPLOY-VERCEL.md                 # Este archivo
```

## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Landing page |
| GET | `/diagnostico` | App de autodiagnóstico (React SPA) |
| GET | `/api` | Información del servicio |
| GET | `/api/health` | Healthcheck |
| GET | `/api/kb` | Banco de conocimiento (ETag/304) |
| GET | `/api/kb/version` | Versión de la KB |
| GET | `/api/market-signals` | Señales de vigilancia de mercado |
| POST | `/api/diagnosticos/{id}/calcular` | Ejecutar pipeline de diagnóstico |

## Despliegue paso a paso

### 1. Instalar Vercel CLI (si no lo tienes)

```bash
npm install -g vercel
```

### 2. Configurar variables de entorno

En el dashboard de Vercel o con la CLI, configura:

```bash
vercel secrets add siginex-api-keys "tu-api-key-1,tu-api-key-2"
```

O desde el dashboard: Settings → Environment Variables → agregar `SIGINEX_API_KEYS`.

### 3. Desplegar

Desde la raíz del proyecto:

```bash
# Preview (staging)
vercel

# Producción
vercel --prod
```

### 4. Verificar

```bash
# Healthcheck
curl https://tu-dominio.vercel.app/api/health

# Versión de la KB
curl -H "X-Api-Key: tu-api-key" -H "X-Tenant-Id: test" \
  https://tu-dominio.vercel.app/api/kb/version

# Calcular diagnóstico
curl -X POST -H "Content-Type: application/json" \
  -H "X-Api-Key: tu-api-key" -H "X-Tenant-Id: test" \
  -d '{"company":{"nombre":"Test"},"answers":{"sst-1.1.1":2,"sst-1.1.2":1}}' \
  https://tu-dominio.vercel.app/api/diagnosticos/demo-1/calcular
```

## Autenticación

Las rutas `/api/kb`, `/api/kb/version`, `/api/market-signals` y `/api/diagnosticos/*/calcular` requieren:

- **`X-Api-Key`**: clave configurada en `SIGINEX_API_KEYS`
- **`X-Tenant-Id`**: identificador del tenant

El endpoint `/api/health` es público (no requiere auth).

## Notas técnicas

- **Runtime:** Python 3.9+ (runtime de Vercel para serverless functions)
- **Sin dependencias externas:** las functions usan solo la stdlib de Python
- **Orquestador:** `api/diagnosticos/[id]/calcular.py` importa `siginex_orchestrator.py` desde el paquete original
- **Cold start:** los datos (kb.json) se cargan en memoria al primer request
- **Límites Vercel (plan free):** 10s timeout, 50MB deploy size, 100 deploys/día

## Dominio personalizado

En Vercel dashboard → Settings → Domains → Agregar tu dominio (ej: `siginex.dqnexus.io`).

## Diferencias con el despliegue Docker

| Aspecto | Docker (original) | Vercel |
|---------|-------------------|--------|
| Runtime | FastAPI + uvicorn | Serverless functions |
| DB | PostgreSQL (RLS) | No incluida* |
| Persistencia | Sí (multi-tenant) | Sin estado (stateless) |
| Escalado | Manual | Automático |
| Cold start | No | Sí (~1-2s primer request) |

*Para persistencia completa, conectar una base de datos externa (Vercel Postgres, Supabase, Neon) y adaptar las functions.
