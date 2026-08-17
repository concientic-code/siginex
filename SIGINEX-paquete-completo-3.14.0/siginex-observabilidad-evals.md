# SIGINEX · Observabilidad y evals del agente

**Versión del documento:** 1.0.0 · **Fecha:** 2026-07-04
**Incremento de plataforma:** SIGINEX 3.8.0 → **3.9.0**
**Entregables:** `siginex_evals.py` (arnés ejecutable v1.0.0) · `siginex-evals-report.json` (reporte)

> Aplica sobre la propia SIGINEX los principios de ISO/IEC 42001 (medir, gestionar y gobernar la IA). El sistema empieza a gobernar su propia inteligencia.

---

## 1. Evals del agente

`siginex_evals.py` ejecuta una batería determinista contra el orquestador y el banco real (9 módulos, 521 preguntas). Resultado de la última corrida: **8/8 superadas**, latencia de diagnóstico ≈ 4,3 ms.

| Eval | Qué verifica | Resultado |
|---|---|---|
| Determinismo | Mismo input → mismo output (reproducibilidad) | PASS |
| Fronteras del scoring | all-0 = 0, all-1 = 50, all-2 = 100 | PASS |
| Monotonicidad | Mejorar respuestas nunca baja el score | PASS |
| Aplicabilidad | Los toggles condicionan la cobertura (521 → 487; 34 condicionadas: 8/11/12/3) | PASS |
| Cobertura de plan | Una tarea por brecha, con responsable, prioridad, plazo, fase y criterio | PASS |
| Adopción | Rutas de aprendizaje internas y bien formadas (origen `interno`) | PASS |
| Coherencia de niveles | Mapeo score→nivel monotónico (1→5) | PASS |
| Integridad del contrato | Salida completa y `por_modulo` cubre los 9 módulos | PASS |

Las evals son deterministas y reproducibles: forman parte de la evidencia de gobernanza (cláusulas 9 y 10 de ISO 42001) y se deberían correr en cada cambio del banco, del scoring o del orquestador.

## 2. Observabilidad (producción)

Métricas y señales que el runtime debe emitir cuando se despliegue detrás de la API:

- **Latencia** por diagnóstico y por paso del pipeline (hoy ≈ 4,3 ms en referencia).
- **Tasa de error** y reintentos del orquestador y de los agentes de vigilancia.
- **Distribución de score** y de niveles por sector/tenant (para detectar sesgos o anomalías).
- **Deriva (drift)**: cambios en la distribución de resultados entre versiones de KB.
- **Cobertura**: preguntas aplicables vs respondidas por diagnóstico.
- **Trazabilidad**: cada resultado guarda `kb_version` y queda en `evento_auditoria` (DDL 1.1.1).
- **Salud de vigilancia**: número de señales por corrida, alertas emitidas, antigüedad de la última ejecución.

Estas señales alimentan el motor de alertas ya construido y cierran el lazo de mejora continua.

## 3. Estado tras esta entrega

| Componente | Antes | Ahora |
|---|---|---|
| Evals del agente | 🔴 | ✅ 8 evals ejecutables (8/8) |
| Observabilidad | 🔴 | 🟡 métricas definidas + latencia medida (falta instrumentación en despliegue) |
| Gobernanza de IA operativa | 🔴 | 🟡 dogfooding de ISO 42001 sobre SIGINEX |

## 4. Próximos pendientes

1. **Guías técnicas** (GTC 45, PTEE, MIPG) — se complementan a continuación.
2. **Benchmarking sectorial** (requiere datos persistidos).
3. **Despliegue real** de API + base de datos e **instrumentación** de observabilidad.
