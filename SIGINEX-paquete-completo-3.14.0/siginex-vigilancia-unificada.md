# SIGINEX · Vigilancia unificada (scheduler + motor de alertas)

**Versión del documento:** 1.0.2 · **Fecha:** 2026-07-04
**Incremento de plataforma:** SIGINEX 3.1.0 → **3.2.0**
**Entregable de configuración:** `siginex-vigilancia-config.json` (v1.0.0)
**Skills que orquesta:** `agente-vigilancia-normativa` · `Benchmark_Market_Watch`

> Inteligencia orientativa. Validar en fuentes oficiales y con el proveedor.

---

## 1. Qué resuelve

Hasta ahora teníamos dos agentes de vigilancia **diseñados y sembrados** pero sin ejecución autónoma: cada uno requería dispararse a mano. Este componente cierra ese vacío del mapa (plano 5) con dos piezas que faltaban en rojo:

- **Scheduler único** — un solo orquestador corre ambos agentes según su cadencia (normativa a diario, mercado semanal) y consolida sus salidas.
- **Motor de alertas** — evalúa las señales nuevas contra reglas comunes y decide severidad, acción y canal.

El principio de diseño se mantiene: las **skills producen señales**; el **scheduler las ejecuta** y el **motor de alertas las evalúa**. Así, cambiar una fuente o una regla no toca la lógica de las skills.

---

## 2. Scheduler único

Un solo runtime (cron, n8n, Airflow o GitHub Actions) corre tres jobs encadenados, en zona horaria `America/Bogota`:

1. `vigilancia_normativa_diaria` (06:00) → produce `normativa_entry[]`.
2. `vigilancia_mercado_semanal` (lunes 07:00) → produce `market_signal[]`.
3. `consolidacion_alertas` (07:30, depende de los anteriores) → evalúa y despacha alertas.

Cada corrida es idempotente: deduplica por id de señal y solo procesa lo ingerido desde la última ejecución. Inicio, fin, conteos y errores quedan en `evento_auditoria`.

---

## 3. Motor de alertas

Evalúa cada señal nueva y decide **severidad** (crítica, alta, media, informativa), **acción** y **canal**. Reglas principales:

| Regla | Cuándo | Severidad | Acción |
|---|---|---|---|
| Norma nueva relevante | normativa nueva/modifica, relevancia alta | Alta | Alerta + marcar módulo del SGI afectado |
| Norma con plazo | fecha límite ≤ hoy+30 días | Crítica | Alerta con cuenta regresiva al responsable |
| Norma derogada | estado derogado | Media | Revisar preguntas del banco ancladas a esa norma |
| Mercado impacto alto | señal de mercado con impacto alto | Alta | Alerta a producto/estrategia (DQnexus) |
| Cambio de nivel | una herramienta del benchmark cambia de nivel | Alta | Proponer actualización de `Benchmark_SGI_Tools` (versión++) |
| Nuevo entrante | competidor emergente en nivel 4-5 | Media | Evaluar incorporación al benchmark |
| Nueva certificación | p. ej. ISO 42001 (gobernanza de IA) | Media | Evaluar nuevo módulo/skill en el SGI |

Canales: webhooks a DQnexus (`normativa.nueva`, `mercado.senal`), correo al responsable de cumplimiento para severidad crítica/alta, y registro en tabla `alerta`/`evento_auditoria`. Para evitar ruido, agrupa señales similares en 24 h y no repite alertas ya despachadas.

---

## 4. Integración y trazabilidad

- **Persistencia:** `normativa_entry` y `market_signal` ya existen en el DDL v1.0.0. Este componente requiere añadir una tabla `alerta` → **DDL 1.1.0** (pendiente).
- **API:** las señales se sirven por `GET /normativa` y `GET /market-signals` (OpenAPI 1.1.0).
- **Versionado:** un cambio de nivel o un nuevo entrante confirmado incrementa `Benchmark_SGI_Tools`; una norma nueva relevante puede incrementar la KB. Todo cambio se registra en `CHANGELOG.md`.

---

## 5. Estado del plano de vigilancia tras esta entrega

| Componente | Antes | Ahora |
|---|---|---|
| Vigilancia normativa | 🟡 diseñado + sembrado | 🟡 (sin cambio) |
| Vigilancia de mercado | 🟡 diseñado + sembrado | 🟡 (sin cambio) |
| Scheduler único | 🔴 faltante | ✅ configurado (v1.0.0) |
| Motor de alertas | 🔴 faltante | ✅ diseñado (reglas + canales) |

Pendiente de implementación (código): desplegar el runtime elegido, la tabla `alerta` (DDL 1.1.0) y los conectores de fuentes reales.

---

## 6. Próximos pendientes (mapa v3)

1. **Generador de plan de mejoramiento** — tareas con responsables y plazos sobre `recomendacion`. → KB/Motores 3.1.0.
2. **Capa de adopción** — rutas de aprendizaje por brecha hacia la capa de aprendizaje de DQnexus. → Plataforma 3.4.0.
3. **Benchmarking sectorial** — con datos persistidos acumulados. → Motores 3.2.0.
