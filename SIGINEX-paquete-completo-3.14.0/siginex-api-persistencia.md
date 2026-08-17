# Persistencia e integración de SIGINEX con DQnexus

Diseño de la capa de datos y del contrato de API que conecta la inteligencia ya construida (skills, motores, base de conocimiento, vigilancia) con DQnexus. El contrato ejecutable está en `siginex-openapi.yaml`; el modelo de datos, en el ERD de esta sesión.

> Resultado orientativo: SIGINEX no sustituye una auditoría formal ni un concepto legal. Este descargo viaja como campo en cada respuesta de resultados.

---

## 1. Decisiones de arquitectura (supuestos)

Tomé estos defaults por ser los más universalmente consumibles; todos son puntos que puedes recalibrar.

- **Estilo API:** REST + OpenAPI 3.1. Es lo más simple de consumir desde DQnexus y terceros, y se documenta solo. (Alternativa: GraphQL si prevés clientes que compongan consultas muy variables.)
- **Persistencia:** relacional (PostgreSQL) con columnas `JSONB` para los campos flexibles (aplicabilidad, acciones, norma_refs). Da integridad referencial para diagnósticos y trazabilidad, y flexibilidad para el contenido normativo.
- **Multi-tenant:** aislamiento por `tenant_id` en cada organización (row-level security). Un tenant = una cuenta consumidora (p. ej. Comfama); las empresas diagnosticadas cuelgan del tenant.
- **Autenticación:** OAuth2 client-credentials (servicio-a-servicio) + API Key para integraciones simples, con scopes `diagnosticos:read/write` y `normativa:read`.
- **Idempotencia:** `Idempotency-Key` en creaciones y `PUT` de respuestas por `pregunta_id` (reenviar sobrescribe). Reintentos seguros.
- **Versionado de conocimiento:** cada diagnóstico guarda la `kb_version` con la que se calculó, para poder auditar por qué obtuvo su score aunque la base cambie después.

---

## 2. Modelo de datos (persistencia)

Entidades núcleo (ver ERD):

- `organizacion` — empresa diagnosticada. Incluye `aplicabilidad` (JSONB) que resuelve qué skills/preguntas se activan (permisos ambientales, SAGRLAFT/SARLAFT, emisor de valores).
- `diagnostico` — una evaluación. Guarda estado (`en_progreso | calculado | archivado`), `modo`, `kb_version`, y los consolidados (`score_sgi`, `nivel_sgi`, cumplimiento y madurez globales).
- `respuesta` — respuesta a una pregunta del banco (`si_no` o `escala`), con estado (`respondida | no_aplica | sin_dato`).
- `resultado_pilar` — score, nivel (1–5), cumplimiento y madurez por skill; materializa la salida del motor de scoring.
- `recomendacion` — por skill: prioridad, acciones (JSONB) y `norma_refs` (JSONB).
- `evidencia` — soporte de una respuesta (URL, archivo o nota) con `hash` para trazabilidad e integridad.
- `kb_version` — versión de la base de conocimiento (versión, fecha, checksum).
- `ruta_aprendizaje` — puente a la capa de aprendizaje de DQnexus: deriva de una recomendación una ruta de capacitación (`brecha`, `recurso_url`, `origen`).

Notas de diseño:

- **Trazabilidad primero:** conservar `respuesta.valor` + `evidencia.hash` + `diagnostico.kb_version` hace el scoring explicable y auditable (por qué cada pilar quedó en su nivel).
- **Resultados materializados:** `resultado_pilar` y `recomendacion` se persisten (no solo se calculan al vuelo) para servir históricos y benchmarking sin recomputar.
- **Privacidad (Ley 1581):** la Ley de protección de datos también te aplica a ti como responsable del tratamiento. Clasificar `organizacion`/`evidencia` como datos de terceros, definir retención, cifrar en reposo y registrar el consentimiento del tenant.

---

## 3. Contrato de API (resumen)

Recursos y endpoints (detalle y esquemas en `siginex-openapi.yaml`):

| Recurso | Método · ruta | Propósito |
|---|---|---|
| Organizaciones | `POST /organizaciones` · `GET /organizaciones/{id}` | Alta y consulta de la empresa y su aplicabilidad |
| Diagnósticos | `POST /diagnosticos` · `GET /diagnosticos` · `GET /diagnosticos/{id}` | Iniciar, listar y consultar diagnósticos |
| Respuestas | `PUT /diagnosticos/{id}/respuestas` | Registrar respuestas en lote (idempotente) |
| Cálculo | `POST /diagnosticos/{id}/calcular` | Ejecuta scoring + recomendaciones y cierra el diagnóstico |
| Resultados | `GET .../resultados` · `.../recomendaciones` · `.../rutas-aprendizaje` | Consolidados, recomendaciones y rutas de aprendizaje |
| Vigilancia | `GET /normativa` | Feed normativo por módulo/estado/fecha |
| Meta | `GET /meta/kb-version` | Versión vigente de la base de conocimiento |

Transversales: paginación por cursor, modelo de error uniforme (`code`, `message`, `details`), y webhooks `diagnostico.calculado` y `normativa.nueva` para arquitecturas orientadas a eventos.

---

## 4. Flujo de integración con DQnexus

```
DQnexus                                       SIGINEX API
      │  POST /organizaciones (perfil + aplicabilidad)   │
      │ ───────────────────────────────────────────────►│
      │  POST /diagnosticos                              │
      │ ───────────────────────────────────────────────►│  resuelve skills aplicables
      │  PUT  /diagnosticos/{id}/respuestas (lotes)      │
      │ ───────────────────────────────────────────────►│  persiste + progreso
      │  POST /diagnosticos/{id}/calcular                │
      │ ───────────────────────────────────────────────►│  scoring + recomendaciones
      │ ◄─────────────────── ResultadoDiagnostico ───────│
      │  GET  /diagnosticos/{id}/rutas-aprendizaje       │
      │ ───────────────────────────────────────────────►│  brecha → recurso de aprendizaje
      │ ◄──────────────── webhook normativa.nueva ───────│  (vigilancia continua)
```

El puente estratégico es `rutas-aprendizaje`: cada brecha del diagnóstico se traduce en una ruta de capacitación en la capa de aprendizaje de DQnexus (origen `interno`). Ahí es donde SIGINEX deja de ser diagnóstico y se vuelve la tesis de DQnexus: articular aprendizaje, producto y decisión en un mismo ecosistema.

---

## 5. Gobernanza, seguridad y calidad

- **Descargo** embebido en cada `ResultadoDiagnostico`.
- **Versionado + auditoría:** `kb_version` por diagnóstico e histórico inmutable de resultados.
- **Seguridad:** OAuth2/scopes, API keys por tenant, cifrado en reposo/tránsito, rate limiting.
- **Privacidad:** política de tratamiento de datos (Ley 1581), retención y minimización de evidencias.
- **Calidad del agente:** registrar entradas/salidas de los motores para evals (consistencia del scoring, calidad de recomendaciones) antes de escalar.

---

## 6. Puntos que conviene que decidas

1. **REST vs GraphQL** (asumí REST).
2. **Motor de persistencia** (asumí PostgreSQL + JSONB; alternativa documental si prefieres esquema flexible puro).
3. **Modelo de tenant:** ¿el consumidor es siempre Comfama/DQnexus, o habrá múltiples clientes externos con aislamiento fuerte?
4. **Completitud:** ¿se permite calcular diagnósticos parciales (preliminar) o se exige 100% (`exigir_completitud`)?
5. **Origen de rutas de aprendizaje:** mapa brecha → recurso (¿catálogo curado en la capa de aprendizaje de DQnexus o recomendación dinámica?).
