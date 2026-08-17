# SIGINEX · Generador de plan de mejoramiento

**Versión del documento:** 1.0.1 · **Fecha:** 2026-07-04
**Incremento de plataforma:** SIGINEX 3.2.1 → **3.3.0**
**Entregables:** `Improvement_Plan_Generator.json` (skill v1.0.0) · `siginex-schema.sql` (**DDL 1.1.0**) · artefacto `siginex-autodiagnostico-500.html` (plan enriquecido)

> Plan orientativo. Responsables y plazos son sugerencias; ajustar a la estructura real de cada organización.

---

## 1. Qué resuelve

Cierra el pendiente del plano de motores: el diagnóstico ya detectaba brechas y recomendaba acciones, pero no las convertía en un **plan ejecutable**. Este generador transforma cada brecha en una **tarea con responsable, prioridad, plazo, esfuerzo, evidencia esperada y criterio de cierre**, organizada por fases.

## 2. Lógica del generador

Genera una tarea por cada pregunta con evaluación menor a 2 (0 = No cumple, 1 = Parcial), priorizando por brecha ponderada `(2 - evaluación) × peso × peso_módulo`. La acción base es la recomendación correspondiente al puntaje.

- **Prioridad:** evaluación 0 → Alta; evaluación 1 → Media; se eleva a Alta si la norma es de obligación legal (Ley/Decreto/Resolución).
- **Plazo sugerido:** Alta 30 días · Media 90 días · Baja 180 días.
- **Responsable sugerido por módulo:** SG-SST → Responsable del SG-SST; Ambiental → Coordinador Ambiental/HSEQ; Calidad → Líder de Calidad; Riesgos → Oficial de Riesgos/Continuidad; Cumplimiento → Oficial de Cumplimiento; Datos → Oficial de Protección de Datos/Seguridad; Gobierno → Secretaría General/Gobierno Corporativo.
- **Esfuerzo (heurística):** tramitar permiso/implementar sistema → Alto; documentar política/procedimiento → Medio; medir/evidenciar/actualizar → Bajo.
- **Criterio de cierre:** evidencia verificable del requisito, vigente y trazable.

## 3. Fases

El plan se ordena en tres fases temporales, alineadas al ciclo PHVA: Estabilización (0–30 días, prioridad Alta, brechas legales y de mayor riesgo), Consolidación (31–90 días, formalizar lo parcial) y Optimización (91–180 días, medición y mejora continua).

## 4. Persistencia (DDL 1.1.0)

Se añaden dos tablas:

- `tarea_mejora` — una fila por tarea, derivada de `recomendacion`, con `prioridad`, `responsable`, `plazo_dias`, `fecha_limite`, `esfuerzo`, `fase`, `criterio_cierre`, `estado` (pendiente/en_progreso/cerrada/vencida) y enlace opcional a `ruta_aprendizaje`. Con RLS por tenant.
- `alerta` — emitidas por el motor de alertas (normativa/mercado/plan), que ahora puede notificar tareas próximas a vencer o vencidas. (Esta tabla saldó el pendiente que dejó la capa de vigilancia unificada.)

## 5. En el artefacto

La sección "Plan de mejora priorizado" ahora muestra, por tarea, la **prioridad, el responsable sugerido y el plazo** además de la acción y la norma. La exportación a Excel incluye las nuevas columnas Responsable y Plazo. El banco de 500 preguntas y el resto de las vistas no cambian.

## 6. KPIs del plan

Porcentaje de tareas cerradas por fase, reducción de brechas (ítems en 0) frente al diagnóstico previo, y cumplimiento de fechas límite.

## 7. Estado tras esta entrega

| Componente | Antes | Ahora |
|---|---|---|
| Generador de plan de mejoramiento | 🔴 | ✅ skill 1.0.0 + UI + persistencia |
| Tabla `tarea_mejora` | 🔴 | ✅ DDL 1.1.0 |
| Tabla `alerta` (pendiente de vigilancia) | 🔴 | ✅ DDL 1.1.0 |

## 8. Próximos pendientes (mapa v4)

1. **Capa de adopción** — vincular cada tarea con rutas de aprendizaje en la capa de aprendizaje de DQnexus. → Plataforma 3.4.0.
2. **Benchmarking sectorial** — con datos persistidos acumulados. → Motores 3.2.0.
3. **Histórico y reporte ejecutivo** — comparación temporal y narrativa automática.
4. **Gobernanza de IA (ISO 42001) y observabilidad/evals.**
