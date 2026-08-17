# SIGINEX · Cierre del plano de plataforma

**Versión del documento:** 1.1.2 · **Fecha:** 2026-07-04
**Alcance:** persistencia, API, gobernanza/seguridad y esquema de versionado.
**Entregables asociados:** `siginex-schema.sql` (DDL v1.0.0) · `siginex-openapi.yaml` (contrato) · `siginex-api-persistencia.md` (diseño previo).

> Resultado orientativo. SIGINEX no sustituye una auditoría formal ni un concepto legal.

---

## 1. Esquema de versionado (nuevo — aplica a todo el sistema)

Adoptamos **SemVer** (`MAYOR.MENOR.PARCHE`) por artefacto, más una **versión de plataforma** que los agrupa.

- **MAYOR**: cambios incompatibles (rompe API, contrato de datos o scoring).
- **MENOR**: nuevas capacidades compatibles (nueva skill, nuevos endpoints, nuevas preguntas).
- **PARCHE**: correcciones sin cambio de contrato.

Cada actualización registra: versión, fecha, cambios y artefacto afectado (ver `CHANGELOG.md`). La **base de conocimiento** también se versiona y cada diagnóstico guarda su `kb_version`, de modo que un resultado siempre es reproducible y auditable.

| Artefacto | Versión actual |
|---|---|
| Plataforma SIGINEX | 3.1.0 |
| Base de conocimiento (banco 500) | 3.0.0 |
| Contrato API (OpenAPI) | 1.1.0 |
| DDL de persistencia | 1.0.0 |
| Skill Normative_Knowledge_SGI | 1.0.0 |
| Skill Benchmark_SGI_Tools | 1.0.0 |
| Skill Benchmark_Market_Watch | 1.0.0 |
| Artefacto interactivo | 3.0.0 |

---

## 2. Persistencia (PostgreSQL)

El DDL (`siginex-schema.sql`) materializa el ERD con doce tablas: `tenant`, `kb_version`, `organizacion`, `diagnostico`, `respuesta`, `evidencia`, `resultado_pilar`, `recomendacion`, `ruta_aprendizaje`, más `normativa_entry` y `market_signal` (feeds de vigilancia) y `evento_auditoria` (observabilidad).

Decisiones clave:

- **Multi-tenant con RLS.** Cada tabla con datos de cliente lleva `tenant_id` y una política `tenant_isolation` con `FORCE ROW LEVEL SECURITY`. La aplicación fija `SET app.tenant_id = '<uuid>'` por conexión; PostgreSQL garantiza el aislamiento aunque la app tenga un bug de filtrado.
- **Trazabilidad y reproducibilidad.** `respuesta.peso` guarda el peso vigente al momento de responder y `diagnostico.kb_version` fija la versión del banco: el scoring es explicable aunque la KB cambie después. `evidencia.hash` da integridad.
- **Resultados materializados.** `resultado_pilar` y `recomendacion` se persisten (no solo se calculan al vuelo) para servir históricos y el benchmarking sectorial sin recomputar.
- **Idempotencia.** `diagnostico` tiene índice único por `(tenant_id, idempotency_key)`; `respuesta` es única por `(diagnostico_id, pregunta_id)` — reenviar sobrescribe.
- **Escala 0/1/2.** El enum `valor_respuesta` cubre `0/1/2` y también `si/no/na/sin_dato` para compatibilidad con el módulo SG-SST oficial (binario).

---

## 3. API — cambios de esta versión (OpenAPI 1.1.0)

Se añaden al contrato ya existente:

- `GET /kb` — sirve el banco de conocimiento vigente (banco de 500 + pesos + modelo de madurez), para que el artefacto **deje de llevar las preguntas embebidas** y las consuma por API. Devuelve `kb_version` y `ETag` para caché.
- `GET /kb/version` — versión y checksum vigentes (ya existía como `meta/kb-version`; se normaliza la ruta).
- `GET /market-signals` — feed de vigilancia de mercado (Benchmark_Market_Watch), con filtros por `impacto` y `fecha`.
- `POST /diagnosticos/{id}/benchmark` — registra el `nivel_tecnologico` (1–5) y devuelve el scoring competitivo frente al mercado.

El resto del ciclo (crear organización → diagnóstico → respuestas → calcular → resultados/recomendaciones/rutas) permanece **sin cambios de contrato** (compatibilidad hacia atrás → incremento MENOR, no MAYOR).

---

## 4. Gobernanza, seguridad y calidad

- **Autenticación:** OAuth2 client-credentials + API Key por tenant, con scopes `diagnosticos:read/write`, `kb:read`, `market:read`.
- **Privacidad (Ley 1581).** SIGINEX es responsable del tratamiento de datos de las empresas diagnosticadas: cifrado en reposo/tránsito, minimización de evidencias, política de retención y registro del consentimiento del tenant. RLS refuerza el aislamiento.
- **Observabilidad.** `evento_auditoria` traza acciones clave; se recomienda además métricas de latencia y una batería de **evals del agente** (consistencia del scoring, calidad de recomendaciones) antes de escalar.
- **Gobernanza de IA (ISO 42001).** Señal de mercado 2026: incorporar controles de gobernanza sobre la propia IA de SIGINEX (trazabilidad de decisiones, sesgos, validación humana) como parte del producto, no como accesorio.
- **Descargo + validación humana.** El campo de descargo viaja en cada resultado; las decisiones de cumplimiento requieren validación jurídica.

---

## 5. Estado del plano de plataforma tras esta entrega

| Componente | Antes | Ahora |
|---|---|---|
| Persistencia (multi-tenant, evidencias, versionado KB) | 🔴 | ✅ DDL v1.0.0 |
| API de diagnóstico (contrato) | 🟡 | 🟡→✅ contrato 1.1.0 (falta despliegue) |
| Servir banco desde `GET /kb` | 🔴 | 🟡 diseñado en contrato |
| Gobernanza/seguridad/privacidad | 🔴 | 🟡 diseñada |
| Observabilidad / evals | 🔴 | 🟡 base (evento_auditoria) |

Pendiente de implementación (código): desplegar la API sobre el DDL, migraciones, y el job de carga de la KB. Con esto el artefacto podrá hidratarse desde `GET /kb` y cada diagnóstico quedará persistido y disponible para DQnexus.

---

## 6. Próximos pendientes (según el mapa v3)

En orden sugerido, cada uno con su incremento de versión:
1. **Unificar vigilancia** — scheduler único + motor de alertas (normativa + mercado). → Plataforma 3.2.0.
2. **Generador de plan de mejoramiento** — tareas con responsables y plazos, sobre `recomendacion`. → KB/Motores 3.1.0.
3. **Capa de adopción** — rutas de aprendizaje por brecha hacia la capa de aprendizaje de DQnexus (`ruta_aprendizaje` ya modelada). → Plataforma 3.4.0.
4. **Benchmarking sectorial** — una vez acumulados datos persistidos. → Motores 3.2.0.
