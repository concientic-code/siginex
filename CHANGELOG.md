# CHANGELOG — SIGINEX (capa de inteligencia del SGI · DQnexus)

Formato basado en Keep a Changelog · Versionado SemVer (`MAYOR.MENOR.PARCHE`).
Cada entrada indica el artefacto afectado y su versión. La base de conocimiento se versiona aparte y cada diagnóstico guarda su `kb_version`.

---

## [Plataforma 3.14.0] — 2026-08-17
### Cambiado
- **Rebranding del proyecto: SIGIA → SIGINEX.** Cambio de nombre aplicado en todos los artefactos, skills, código, esquema de base de datos y documentación.
  - **Archivos renombrados** (prefijo `sigia-`/`sigia_` → `siginex-`/`siginex_`): el artefacto interactivo, la landing, el orquestador y su muestra, las evals y su reporte, la exportación/servidor de KB, la API, el benchmarking sectorial y su muestra, el DDL, el contrato OpenAPI, la configuración de vigilancia, el mapa de arquitectura, el pitch (`.pptx`, texto interno actualizado), el PDF de construcción del producto y toda la documentación (`siginex-*.md`).
  - **Esquema de base de datos:** `CREATE SCHEMA sigia` → `CREATE SCHEMA siginex`; `search_path` actualizado (DDL sigue en 1.1.1, sin cambios estructurales adicionales).
  - **Código:** imports y referencias cruzadas entre módulos Python actualizados (`import siginex_orchestrator as orch`); `Dockerfile`, `docker-compose.yml` (servicio, base de datos, usuario y volumen ahora `siginex`), `Makefile` y el workflow de CI actualizados a los nuevos nombres de archivo.
  - **Contenido:** todas las menciones de marca en prosa, JSON (skills) y el artefacto (título, textos) pasan de "sigIA/SIGIA" a "SIGINEX"; el dominio "SGI" (Sistema de Gestión Integral, el objeto que se diagnostica) se mantiene sin cambios por ser un concepto distinto del nombre del producto.
  - **Verificación de extremo a extremo tras el cambio:** `siginex_kb_export.py`, `siginex_orchestrator.py` (9 módulos · 521 preguntas · score 56.81), `siginex_evals.py` (8/8 superadas) y `siginex_sectorial.py` (60 empresas · 5 sectores) ejecutados sin errores sobre los archivos ya renombrados.
  - **Fuera de alcance de este cambio:** el material de Academia AI Native (`curso-*.md`, `DQnexus-AINPL-framework.md`, carpeta `academia-ai-native/`) referencia a "sigIA" como caso de estudio y no fue modificado por ser un producto/track independiente; se recomienda actualizarlo en un cambio aparte si se desea consistencia de marca.

## [Plataforma 3.13.0] — 2026-07-04
### Añadido
- **Benchmarking sectorial (v1.0.0):** `siginex_sectorial.py` agrega los diagnósticos por sector (media, mediana, p25/p75, rango; global y por módulo) y posiciona a cada empresa frente a su industria (percentil y delta vs. media sectorial). Demostrado con 60 empresas sintéticas / 5 sectores → `siginex-sectorial-sample.json`. `siginex-benchmarking-sectorial.md` (v1.0.0).
- **Cierra el mapa:** todas las capacidades quedan construidas; lo restante es operación (desplegar y acumular datos).

## [Plataforma 3.12.0] — 2026-07-04
### Añadido
- **Despliegue 100% ejecutable:** `Dockerfile` (API), `requirements.txt`, `.dockerignore`, `Makefile` (targets `kb`, `evals`, `demo`, `migrate`, `up`, `down`), workflow de CI `.github/workflows/ci.yml` (corre las evals como compuerta) y `README.md` que indexa todo el sistema y su quickstart.
- El paquete queda listo para `make kb && make evals && make up` (PostgreSQL + API con el DDL como migración inicial).

## [Plataforma 3.11.0] — 2026-07-04
### Añadido
- **Paquete de puesta en producción:** convierte lo construido en un sistema operable.
  - **Hidratación de la KB:** `siginex_kb_export.py` genera `kb.json` (payload de `GET /kb`, con `ETag`=checksum) y `kb-version.json` (versión 3.1.0 · 9 módulos · 521 preguntas).
  - **Servidor API de referencia:** `siginex_api.py` (FastAPI) implementa `GET /kb`, `GET /kb/version`, `GET /market-signals`, `POST /diagnosticos/{id}/calcular` (ejecuta el orquestador) y `GET /health`, con auth por API key + `X-Tenant-Id` y nota de RLS (`SET app.tenant_id`).
  - **Infraestructura:** `docker-compose.yml` (PostgreSQL 16 + API, DDL como migración inicial) y `.env.example`.
  - **Runbook:** `siginex-despliegue.md` (v1.0.0) con migraciones, auth, hidratación, observabilidad, seguridad y checklist go-live.

## [Plataforma 3.10.0] — 2026-07-04
### Añadido
- **Guías técnicas (v1.0.0):** `siginex-guias-tecnicas.md` con GTC 45 (identificación de peligros y valoración de riesgos SST: ND·NE·NP·NC·NR y jerarquía de controles), PTEE (componentes del Programa de Transparencia y Ética Empresarial) y MIPG (7 dimensiones y FURAG). Complementan los módulos SG-SST, Cumplimiento y Gobierno.

## [Plataforma 3.9.0] — 2026-07-04
### Añadido
- **Observabilidad y evals del agente (v1.0.0):** `siginex_evals.py` — batería determinista sobre el orquestador y el banco (9 módulos, 521 preguntas). Última corrida **8/8** superadas; latencia ≈ 4,3 ms. Verifica determinismo, fronteras del scoring (0/50/100), monotonicidad, aplicabilidad (521→487; 34 condicionadas), cobertura de plan, adopción interna, coherencia de niveles e integridad del contrato.
  - `siginex-observabilidad-evals.md` (v1.0.0) + `siginex-evals-report.json`. Dogfooding de ISO 42001 sobre la propia SIGINEX.

## [Plataforma 3.8.0] — 2026-07-04
### Añadido
- **Integración de ESG y Gobernanza de IA al banco (Artefacto 3.4.0 · KB 3.1.0):** el diagnóstico pasa de 7 a **9 módulos** y de 500 a **521 preguntas** (ESG 10, Gobernanza de IA 11), con reponderación por módulo (el global se normaliza por los pesos evaluados).
  - Adopción (rutas internas de DQnexus) y responsables extendidos a los dos módulos nuevos.
  - El orquestador `siginex_orchestrator.py` evalúa los 9 módulos de punta a punta (507 preguntas aplicables en el ejemplo).

## [Plataforma 3.7.0] — 2026-07-04
### Añadido
- **Skill ESG + Gobernanza de IA (ESG_AI_Governance_Skills v1.0.0):** dos dominios evaluables (escala 0/1/2).
  - **Sostenibilidad/ESG** (10 preguntas) sobre los cuatro pilares ISSB/TCFD, anclada a NIIF S1/S2, GRI, SASB y al contexto colombiano (SFC Circular 031/2021 y 015/2025; Informe 08 de Supersociedades).
  - **Gobernanza de IA** (11 preguntas) sobre ISO/IEC 42001:2023 (política, AIA, riesgos del ciclo de vida, datos/sesgos, transparencia, supervisión humana, seguridad, auditoría), con NIST AI RMF y EU AI Act.
  - `siginex-esg-gobernanza-ia.md` (v1.0.0). Pendiente: integrar ambos módulos al banco del artefacto (reponderación).

## [Plataforma 3.6.0] — 2026-07-04
### Añadido
- **Orquestador (Agent Runtime) — Agent_Orchestrator v1.0.0:** ejecuta el diagnóstico de punta a punta (aplicabilidad → scoring → recomendaciones → plan → adopción → benchmark → consolidación → alertas) y devuelve un contrato de salida único con `kb_version`.
  - `siginex_orchestrator.py` (implementación de referencia ejecutable sobre el banco de 500) + `siginex-orchestrator-sample.json` (salida de ejemplo) + `Agent_Orchestrator.json` (contrato) + `siginex-orquestador.md` (v1.0.0).
- **Resolver de aplicabilidad** formalizado como componente del runtime (antes solo en el artefacto).

## [Plataforma 3.5.0] — 2026-07-04
### Añadido
- **Histórico y reporte ejecutivo (Artefacto 3.3.0):** cierra el plano de experiencia.
  - **Reporte ejecutivo:** narrativa automática para dirección al inicio de los resultados (score, madurez, fortalezas, oportunidades, brechas y foco), incluida en el PDF.
  - **Histórico y evolución:** guardar "fotos" del diagnóstico, comparar deltas (global y por módulo) y exportar/importar `siginex-historico.json` para conservar la comparación entre sesiones.
  - `siginex-historico-reporte.md` (v1.0.0).

## [Plataforma 3.4.0] — 2026-07-04
### Añadido
- **Capa de adopción (Adoption_Layer v1.0.0):** convierte cada brecha del diagnóstico en una ruta de aprendizaje de la capa de aprendizaje de DQnexus (origen `interno`), con competencia, nivel (básico/intermedio según la brecha), formato y duración.
  - `Adoption_Layer.json` (skill, catálogo por módulo + regla de mapeo).
  - **Artefacto 3.2.0:** nueva tarjeta "Plan de aprendizaje (adopción)" en resultados y hoja "Plan de aprendizaje" en el Excel.
- Cierra el ciclo diagnóstico → brechas → tareas (responsable/plazo) → rutas de aprendizaje internas.

## [Plataforma 3.3.2] — 2026-07-04
### Eliminado
- **Purga completa de referencias externas de e-learning** en todos los archivos del sistema. El origen de las rutas de aprendizaje queda como `interno` (capa de aprendizaje de DQnexus).
  - `siginex-schema.sql` → **DDL 1.1.1**: `origen_ruta` = `('interno','externo')`, default `interno`.
  - `siginex-openapi.yaml` → **OpenAPI 1.1.2**: enum `origen` = `[interno, externo]`.
  - Docs y skills: `siginex-plataforma.md` (1.1.2), `siginex-vigilancia-unificada.md` (1.0.2), `siginex-plan-mejoramiento.md` (1.0.1), `Improvement_Plan_Generator.json` (1.0.1), `siginex-api-persistencia.md`.

## [Plataforma 3.3.1] — 2026-07-04
### Añadido
- **Aplicabilidad en el artefacto (Artefacto 3.1.0):** la pantalla inicial recupera la tarjeta de Aplicabilidad con cuatro toggles (vertimientos/Res. 631, SAGRLAFT/SARLAFT, PTEE, RNBD). Es una primera versión del **resolver de aplicabilidad**: cada toggle condiciona sus preguntas.
- **Motor de scoring** asociado a la aplicabilidad: las preguntas no aplicables se excluyen del cálculo, del progreso y de brechas/plan (34 preguntas condicionadas; 466 siempre aplicables). El Excel las marca como "No aplica (perfil)".

## [Plataforma 3.3.0] — 2026-07-04
### Añadido
- **Generador de plan de mejoramiento**: convierte cada brecha en tareas con responsable, prioridad, plazo, esfuerzo, fase (PHVA) y criterio de cierre.
  - `Improvement_Plan_Generator.json` (skill v1.0.0) · `siginex-plan-mejoramiento.md` (v1.0.0)
- **Persistencia → DDL 1.1.0**: nuevas tablas `tarea_mejora` (con RLS por tenant) y `alerta` (motor de alertas: normativa/mercado/plan); nuevo enum `estado_tarea`. Salda el pendiente de la tabla `alerta` de la vigilancia.
- **Artefacto**: la sección "Plan de mejora" ahora muestra prioridad, responsable sugerido y plazo por tarea; el Excel incluye columnas Responsable y Plazo.

## [Plataforma 3.2.1] — 2026-07-04
### Cambiado / Eliminado
- **Se desacopló la capa de e-learning externa** de los entregables de SIGINEX/DQnexus. Las rutas de aprendizaje/adopción apuntan a la capa de aprendizaje de DQnexus (origen `interno`).
  - `siginex-schema.sql` → DDL: `origen_ruta` como `('interno','externo')`; default `interno`.
  - `siginex-openapi.yaml` → OpenAPI: enum `origen` con `interno`/`externo`; descripciones actualizadas.
  - Docs actualizadas: `siginex-plataforma.md` (1.1.1), `siginex-vigilancia-unificada.md` (1.0.1), `siginex-api-persistencia.md`.

## [Plataforma 3.2.0] — 2026-07-04
### Añadido
- **Vigilancia unificada**: scheduler único (jobs normativa diaria + mercado semanal + consolidación) y motor de alertas con reglas, severidades y canales.
  - `siginex-vigilancia-config.json` (v1.0.0) · `siginex-vigilancia-unificada.md` (v1.0.0)
- **Contrato API → OpenAPI 1.1.0**: nuevos endpoints `GET /kb`, `GET /market-signals`, `POST /diagnosticos/{id}/benchmark`; scopes `kb:read` y `market:read`; schemas `KbBundle`, `MarketSignal`, `BenchmarkInput`, `BenchmarkResult`.
- **Documentación**: `CHANGELOG.md` (este archivo).
### Pendiente
- Tabla `alerta` en el DDL (→ DDL 1.1.0) y despliegue del runtime de vigilancia.

## [Plataforma 3.1.0] — 2026-07-04
### Añadido
- **Persistencia PostgreSQL** `siginex-schema.sql` (DDL v1.0.0): 12 tablas, 8 enums, 14 índices, multi-tenant con RLS (`FORCE`), versionado de KB por diagnóstico, evidencias con hash, auditoría.
- **Cierre del plano de plataforma** `siginex-plataforma.md` (v1.1.0): esquema de versionado SemVer, diseño de persistencia, adiciones de API y gobernanza (privacidad Ley 1581, ISO 42001).

## [Artefacto 3.0.0 · KB 3.0.0] — 2026-07-04
### Añadido
- **Banco de 500 preguntas** en el artefacto (`siginex-autodiagnostico-500.html`), escala 0/1/2, con SG-SST anclado en los 60 ítems oficiales del Excel de estándares mínimos (Res. 0312/2019).
- **Skill de vigilancia de mercado** `Benchmark_Market_Watch.json` (v1.0.0) + sección "Vigilancia de mercado" en el artefacto.
- **Skill de benchmark** `Benchmark_SGI_Tools.json` (v1.0.0): 9 herramientas (Colombia + LATAM), modelo de 5 niveles, scoring competitivo, recomendaciones; vista "Benchmark" en el artefacto.
### Cambiado
- Motor de scoring migrado de Sí/No + escala 1-5 a **0/1/2** con pesos por módulo normalizados.

## [Skills de conocimiento 1.0.0] — 2026-07-03
### Añadido
- `SGI_Diagnostic_Skills.json` (v3.0): sistema de skills con scoring 0/1/2, niveles de cumplimiento y madurez, y motor de recomendaciones.
- `Normative_Knowledge_SGI.json` (v1.0): base normativa (norma → requisito → pregunta) con modelo de madurez; vista "Marco normativo" en el artefacto.

## [Diseño de plataforma 1.0.0] — 2026-07-03
### Añadido
- Contrato `siginex-openapi.yaml` (v1.0.0) y diseño de persistencia `siginex-api-persistencia.md`; ERD del modelo de datos.

## [Base del agente] — 2026-07-02
### Añadido
- Artefacto inicial de autodiagnóstico (6 módulos), base de conocimiento `base-conocimiento-sgi.json`, diseño del agente y skills ejecutables, y agentes/registros de vigilancia normativa (sembrados).

---

### Tabla de versiones vigentes
| Artefacto | Versión |
|---|---|
| Plataforma SIGINEX | 3.14.0 |
| Base de conocimiento (banco 521 · 9 módulos) | 3.1.0 |
| Contrato API (OpenAPI) | 1.1.2 |
| DDL de persistencia | 1.1.1 |
| Orquestador (Agent_Orchestrator) | 1.0.0 |
| Benchmarking sectorial | 1.0.0 |
| Observabilidad y evals | 1.0.0 |
| Guías técnicas (GTC 45 · PTEE · MIPG) | 1.0.0 |
| Skill ESG + Gobernanza de IA | 1.0.0 |
| Capa de adopción (Adoption_Layer) | 1.0.0 |
| Motor de plan de mejoramiento | 1.0.1 |
| Artefacto interactivo | 3.4.0 |
| Vigilancia unificada (config) | 1.0.0 |
| Skill Normative_Knowledge_SGI | 1.0.0 |
| Skill Benchmark_SGI_Tools | 1.0.0 |
| Skill Benchmark_Market_Watch | 1.0.0 |
