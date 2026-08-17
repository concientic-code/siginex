# SIGINEX — Sistema Inteligente para el Sistema de Gestión Integral (SGI)

Capa de inteligencia de **DQnexus** para el autodiagnóstico del SGI en Colombia: evalúa cumplimiento normativo y madurez organizacional con IA, sobre **9 módulos** y **521 preguntas**, y convierte cada brecha en un plan de acción y en rutas de aprendizaje.

> Resultado orientativo. SIGINEX no sustituye una auditoría formal ni un concepto legal.

**Estado:** Plataforma SIGINEX 3.14.0 · KB 3.1.0 · OpenAPI 1.1.2 · DDL 1.1.1

---

## Arquitectura (6 planos)

1. **Experiencia y adopción** — artefacto interactivo, reporte ejecutivo, histórico, rutas de aprendizaje.
2. **Agente** — orquestador (runtime), resolver de aplicabilidad, skills de evaluación (7 + ESG + Gobernanza de IA).
3. **Motores** — scoring 0/1/2, recomendaciones, benchmark, plan de mejora + adopción.
4. **Conocimiento** — normativo, diagnóstico (521), benchmark de herramientas, ESG/IA, guías técnicas.
5. **Vigilancia** — scheduler + motor de alertas (normativa + mercado).
6. **Plataforma** — persistencia PostgreSQL (multi-tenant, RLS), API, despliegue.

## Componentes

| Área | Archivos |
|---|---|
| Artefacto | `siginex-autodiagnostico-500.html` · `siginex-landing.html` |
| Orquestador y evals | `siginex_orchestrator.py` · `siginex_evals.py` · `Agent_Orchestrator.json` |
| Skills | `Normative_Knowledge_SGI.json` · `SGI_Diagnostic_Skills.json` · `Benchmark_SGI_Tools.json` · `Benchmark_Market_Watch.json` · `Improvement_Plan_Generator.json` · `Adoption_Layer.json` · `ESG_AI_Governance_Skills.json` |
| Plataforma | `siginex-schema.sql` · `siginex-openapi.yaml` · `siginex_api.py` · `siginex_kb_export.py` · `kb.json` |
| Despliegue | `Dockerfile` · `docker-compose.yml` · `requirements.txt` · `.env.example` · `.github/workflows/ci.yml` |
| Docs | `siginex-*.md` · `siginex-construccion-producto.pdf` · `CHANGELOG.md` |

## Quickstart

```bash
# 1) Hidratar la base de conocimiento (genera kb.json + kb-version.json)
make kb

# 2) Correr la batería de evals del agente (compuerta 8/8)
make evals

# 3) Levantar base de datos + API (aplica el DDL como migración inicial)
cp .env.example .env      # ajustar secretos
make up                   # http://localhost:8080/health
```

## API (referencia)

`GET /kb` · `GET /kb/version` · `GET /market-signals` · `POST /diagnosticos/{id}/calcular` · `GET /health`. Autenticación por `X-Api-Key` + `X-Tenant-Id`; la RLS del DDL aísla por tenant (`SET app.tenant_id`).

## Principios

Trazabilidad a la norma · validación humana (contenido generado etiquetado) · versionado continuo (SemVer + `CHANGELOG.md`) · desacoplar conocimiento, lógica e interfaz · gobernanza de la propia IA (evals como evidencia, ISO 42001).
