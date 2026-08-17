# SIGINEX · Benchmarking sectorial

**Versión del documento:** 1.0.0 · **Fecha:** 2026-07-04
**Incremento de plataforma:** SIGINEX 3.12.0 → **3.13.0**
**Entregables:** `siginex_sectorial.py` (motor v1.0.0) · `siginex-sectorial-sample.json` (demo)

> El último componente del mapa. Compara a cada empresa no solo contra la norma, sino contra su propia industria.

---

## 1. Qué resuelve

El diagnóstico dice qué tan bien cumple una empresa; el benchmarking sectorial dice **qué tan bien lo hace frente a su sector**. Era el único pendiente en rojo, y no por falta de capacidad sino porque requiere **datos acumulados**. El motor ya está construido y listo; su valor real crece con cada diagnóstico que entra en producción.

## 2. Cómo funciona

- **Agregación por sector:** agrupa los diagnósticos por `organizacion.sector` y calcula, para el score global y por módulo, la media, la mediana, los percentiles 25/75 y el rango.
- **Posicionamiento:** para una empresa, calcula su **percentil dentro del sector**, su **delta frente a la media sectorial** y una comparación **módulo por módulo** contra el promedio del sector.

En la demo (60 empresas sintéticas, 5 sectores) los promedios de score fueron: Tecnología 75,4 · Servicios financieros 72,6 · Salud 68,4 · Manufactura 65,5 · Construcción 55,2; y la empresa de ejemplo quedó en el percentil 66,7 de su sector (+4,9 sobre la media).

## 3. Fuente de datos en producción

Los datos salen de lo ya persistido (DDL 1.1.1). Bosquejo de consulta:

```sql
SELECT o.sector, d.score_sgi, rp.skill_id, rp.cumplimiento_pct
FROM   diagnostico d
JOIN   organizacion o    ON o.id = d.organizacion_id
JOIN   resultado_pilar rp ON rp.diagnostico_id = d.id
WHERE  d.estado = 'calculado';
```

Se recomienda un **umbral mínimo de muestra por sector** (p. ej. n ≥ 5) antes de exponer comparaciones, y anonimización (solo agregados) para no revelar datos de empresas individuales.

## 4. Integración

- **API:** se expone como `GET /benchmark/sectorial?sector=...` (agregados) y se incorpora al resultado del diagnóstico como una sección de posicionamiento.
- **Artefacto:** el benchmark actual (madurez tecnológica vs. herramientas) se complementa con el benchmark sectorial (cumplimiento vs. industria) cuando haya datos.

## 5. Estado tras esta entrega

| Componente | Antes | Ahora |
|---|---|---|
| Benchmarking sectorial | 🔴 (dependía de datos) | ✅ motor construido (listo para datos) |

Con esto, **todas las capacidades del mapa quedan construidas**. Lo que resta es operación: desplegar, acumular diagnósticos reales e instrumentar la observabilidad.
