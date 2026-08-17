# SIGINEX · Histórico y reporte ejecutivo

**Versión del documento:** 1.0.0 · **Fecha:** 2026-07-04
**Incremento de plataforma:** SIGINEX 3.4.0 → **3.5.0**
**Entregable:** artefacto `siginex-autodiagnostico-500.html` (**Artefacto 3.3.0**)

> Cierra el plano de experiencia: el diagnóstico deja de ser una foto y pasa a leerse como evolución, con una narrativa lista para dirección.

---

## 1. Reporte ejecutivo (narrativa automática)

En la parte superior de los resultados aparece una tarjeta **"Reporte ejecutivo · Resumen para dirección"** que genera, de forma automática, un párrafo redactado para un comité o gerencia a partir del diagnóstico:

- Índice global de cumplimiento (0–100) y nivel de madurez (1–5).
- Fortalezas (los dos módulos con mayor cumplimiento) y oportunidades (los dos más bajos).
- Número de brechas detectadas.
- Una recomendación de foco según el tramo del score (estabilizar lo legal, formalizar lo parcial, consolidar hacia certificación, o sostener e innovar).

La narrativa se recalcula al vuelo y viaja dentro del área exportada a PDF, de modo que el informe descargable ya abre con el resumen ejecutivo.

## 2. Histórico y evolución

Una tarjeta al final de los resultados permite **guardar una "foto"** del diagnóstico actual y **comparar la evolución** en el tiempo:

- **Guardar foto:** almacena fecha, empresa, score global, completitud y el cumplimiento por módulo.
- **Tabla de fotos:** cada registro muestra su score y el delta (▲/▼) frente a la foto anterior.
- **Cambio por módulo:** compara la última foto contra la anterior, módulo por módulo, con su variación en puntos.
- **Exportar / Importar:** las fotos se descargan como `siginex-historico.json` y se vuelven a cargar en otra sesión, de modo que la comparación temporal persiste sin depender del navegador.

## 3. Relación con la plataforma

En el artefacto, el histórico vive en memoria de sesión y se persiste por exportación. En la plataforma, la fuente de verdad es la base de datos: cada diagnóstico calculado queda en `diagnostico` + `resultado_pilar` (DDL 1.1.1), lo que habilita el histórico real por organización (vista `v_ultimo_diagnostico` y consultas por fecha) y el futuro **benchmarking sectorial** con datos acumulados. El reporte ejecutivo se generará también del lado servidor a partir de `resultado_pilar`.

## 4. Estado tras esta entrega

| Componente | Antes | Ahora |
|---|---|---|
| Reporte ejecutivo (narrativa) | 🔴 | ✅ en artefacto |
| Histórico y comparación temporal | 🔴 | ✅ en artefacto (memoria + export/import) |
| Histórico persistido (servidor) | 🔴 | 🟡 modelado en DDL, pendiente de despliegue |

Con esto, el **plano de experiencia y adopción queda completo** en el artefacto (diagnóstico, aplicabilidad, benchmark, vigilancia de mercado, plan de mejora, adopción, reporte ejecutivo e histórico).

## 5. Próximos pendientes (mapa v7)

1. **Orquestador (runtime)** y **resolver de aplicabilidad** al backend → cerrar el plano del agente.
2. **Skill ESG + gobernanza de IA (ISO 42001)**.
3. **Desplegar la vigilancia** (normativa + mercado) sobre el scheduler.
4. **Benchmarking sectorial**, **observabilidad/evals** y **despliegue real de API + base de datos**.
