# SIGINEX · Orquestador (Agent Runtime)

**Versión del documento:** 1.0.0 · **Fecha:** 2026-07-04
**Incremento de plataforma:** SIGINEX 3.5.0 → **3.6.0**
**Entregables:** `Agent_Orchestrator.json` (contrato v1.0.0) · `siginex_orchestrator.py` (implementación de referencia v1.0.0) · `siginex-orchestrator-sample.json` (salida de ejemplo)

> Cierra el núcleo del plano del agente y formaliza el resolver de aplicabilidad como componente del runtime.

---

## 1. Qué resuelve

Hasta ahora las capacidades (skills, motores) existían como piezas separadas y el artefacto las coordinaba en el navegador. El orquestador es el **runtime** que las ejecuta de punta a punta desde un único punto de entrada: recibe el perfil de la empresa y las respuestas, y devuelve un **contrato de salida consolidado** (score, brechas, plan, adopción, benchmark y alertas). Es lo que permite que el mismo diagnóstico se ejecute igual desde la API, un lote o un agente.

## 2. Pipeline

1. **Resolver de aplicabilidad** — según el perfil (vertimientos/631, SAGRLAFT, PTEE, RNBD) determina qué preguntas aplican.
2. **Scoring** — cumplimiento 0/1/2 ponderado por pregunta y módulo; nivel de madurez 1–5; global ponderado por peso de módulo.
3. **Recomendaciones** — una por cada brecha (evaluación < 2), con prioridad y norma.
4. **Plan de mejora** — brechas → tareas con responsable, prioridad, plazo, fase (PHVA) y criterio de cierre.
5. **Adopción** — cada brecha se asocia a una ruta de aprendizaje interna (capa de aprendizaje de DQnexus, origen `interno`).
6. **Benchmark** (opcional) — si se declara el nivel tecnológico (1–5), calcula el scoring competitivo frente al mercado.
7. **Consolidar** — ensambla el contrato de salida único.
8. **Alertas** (opcional) — emite alertas (p. ej. brechas de alta prioridad) para el motor de alertas y la vigilancia.

## 3. Resolver de aplicabilidad (formalizado)

Antes vivía sólo en el artefacto; ahora es una función del runtime con reglas declarativas: cada flag del perfil, si está apagado, excluye las preguntas cuyo texto (norma + artículo + requisito + pregunta) contiene ciertas palabras clave. Las no aplicables quedan fuera del scoring, del progreso y de brechas/plan/adopción. En el ejemplo de referencia, con `permAmbiental` y `ptee` activos y `saglaft`/`rnbd` inactivos, el runtime evalúa **486 de 500** preguntas.

## 4. Contrato de salida

El runtime devuelve un objeto único con: `kb_version`, `organizacion`, `aplicabilidad`, `resultado` (score y por módulo), `brechas`, `plan_mejora`, `plan_aprendizaje`, `benchmark`, `alertas` y `meta`. Incluir `kb_version` hace el resultado **reproducible y auditable**.

## 5. Implementación de referencia

`siginex_orchestrator.py` ejecuta el pipeline sobre el banco real de 500 preguntas (lo toma del artefacto para garantizar paridad con la interfaz). Es determinista para un mismo `(kb_version, answers, aplicabilidad)`. Se ejecuta con:

```
python3 siginex_orchestrator.py [ruta_al_artefacto.html]
```

y produce un resumen por consola más `siginex-orchestrator-sample.json`.

## 6. Integración con la plataforma

`POST /diagnosticos/{id}/calcular` (OpenAPI) invoca este pipeline; los resultados se persisten en `resultado_pilar`, `recomendacion`, `tarea_mejora` y `ruta_aprendizaje` (DDL 1.1.1). El siguiente paso de despliegue es exponer el runtime detrás de ese endpoint con autenticación y migraciones.

## 7. Estado tras esta entrega

| Componente | Antes | Ahora |
|---|---|---|
| Orquestador (runtime) | 🟡 diseñado | ✅ implementación de referencia |
| Resolver de aplicabilidad | 🟡 parcial (artefacto) | ✅ formalizado en el runtime |

## 8. Próximos pendientes (mapa v8)

1. **Skill ESG + gobernanza de IA (ISO 42001)**.
2. **Desplegar la vigilancia** (normativa + mercado) sobre el scheduler.
3. **Guías técnicas** (GTC 45, PTEE, MIPG).
4. **Benchmarking sectorial**, **observabilidad/evals** y **despliegue real de API + base de datos** (auth, migraciones, `GET /kb`).
