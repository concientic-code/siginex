# SIGINEX · Skill ESG + Gobernanza de IA

**Versión del documento:** 1.0.0 · **Fecha:** 2026-07-04
**Incremento de plataforma:** SIGINEX 3.6.0 → **3.7.0**
**Entregable:** `ESG_AI_Governance_Skills.json` (skill v1.0.0)

> Amplía el SGI hacia dos frentes emergentes de alto crecimiento: sostenibilidad/ESG y gobernanza de la propia inteligencia artificial.

---

## 1. Por qué ahora

La caja "ESG / IA" estaba en ámbar (parcial): ISO 22301 de continuidad ya vivía en Riesgos, pero ESG y gobernanza de IA no tenían contenido evaluable. Además, la vigilancia de mercado había señalado a **ISO 42001 como la certificación de mayor crecimiento en 2026**. Para un sistema que es, él mismo, una capa de IA, gobernar la IA no es accesorio: es parte del producto.

## 2. Dominio 1 — Sostenibilidad / ESG

Diez preguntas organizadas en los cuatro pilares del ISSB/TCFD (Gobernanza, Estrategia, Gestión de riesgos, Métricas y objetivos), más dimensión social y cumplimiento. Anclado a **NIIF S1/S2 del ISSB** (junio 2023, vigentes internacionalmente desde ene-2024, de aplicación **voluntaria** en Colombia), GRI, SASB, ISO 26000, y al contexto colombiano: **Circular Externa 031/2021 de la SFC** (vigente desde 2024 para emisores del RNVE, alineada a TCFD y SASB), el **Informe 08 de Sostenibilidad** de la Superintendencia de Sociedades (voluntario, vía XBRL Express) y la **Circular Externa 015/2025 de la SFC** sobre riesgos ambientales, sociales y climáticos en vigiladas. Incluye la medición de emisiones GEI (alcances 1, 2 y 3 material).

## 3. Dominio 2 — Gobernanza de IA (ISO/IEC 42001)

Once preguntas que recorren las cláusulas y el Anexo A de **ISO/IEC 42001:2023** (primera norma certificable de gestión de IA): política de IA, roles y rendición de cuentas, evaluación de impacto (AIA), gestión de riesgos del ciclo de vida, gobernanza de datos y sesgos, transparencia y explicabilidad, supervisión humana, seguridad específica de IA (OWASP Top 10 LLM, MITRE ATLAS), competencias, auditoría/mejora y cumplimiento regulatorio (EU AI Act). Se apoya en NIST AI RMF (Govern, Map, Measure, Manage).

## 4. Honestidad metodológica

Las 21 preguntas se derivan de la **estructura de los marcos** citados; son una base representativa (no exhaustiva) para autodiagnóstico y deben validarse con un experto. Las NIIF S1/S2 aún no son de adopción obligatoria en Colombia. Resultado orientativo; no sustituye auditoría, aseguramiento ni concepto legal.

## 5. Integración

Ambos dominios se modelan como módulos evaluables del SGI con la misma escala 0/1/2, consumibles por el orquestador. ISO 42001 y las NIIF S1/S2 quedan bajo la capa de vigilancia normativa. **Pendiente:** integrar los dos módulos al banco del artefacto reponderando los pesos por módulo.

## 6. Estado tras esta entrega

| Componente | Antes | Ahora |
|---|---|---|
| Skill ESG / Sostenibilidad | 🟡 parcial | ✅ construida |
| Skill Gobernanza de IA (ISO 42001) | 🔴 | ✅ construida |

## 7. Próximos pendientes (mapa v8)

1. **Desplegar la vigilancia** (normativa + mercado) sobre el scheduler.
2. **Guías técnicas** (GTC 45, PTEE, MIPG).
3. Integrar ESG y Gobernanza de IA al **banco del artefacto** (reponderación).
4. **Benchmarking sectorial**, **observabilidad/evals** y **despliegue real de API + base de datos**.
