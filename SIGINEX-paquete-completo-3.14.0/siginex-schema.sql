-- =====================================================================
-- SIGINEX · Capa de persistencia (PostgreSQL)
-- Versión: 1.1.1  ·  Fecha: 2026-07-04
-- Alineado con: siginex-openapi.yaml (v1.0.0) y el ERD de la sesión.
-- Multi-tenant por tenant_id con Row-Level Security (RLS).
-- Resultado orientativo: no sustituye auditoría formal ni concepto legal.
-- =====================================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";      -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";       -- búsqueda por texto

CREATE SCHEMA IF NOT EXISTS siginex;
SET search_path TO siginex, public;

-- ---------------------------------------------------------------------
-- Enumeraciones
-- ---------------------------------------------------------------------
CREATE TYPE tamano_empresa   AS ENUM ('micro','pequena','mediana','grande');
CREATE TYPE modo_diagnostico AS ENUM ('completo','rapido');
CREATE TYPE estado_diag      AS ENUM ('en_progreso','calculado','archivado');
CREATE TYPE tipo_pregunta    AS ENUM ('si_no','escala','cero_uno_dos');
CREATE TYPE valor_respuesta  AS ENUM ('0','1','2','si','no','na','sin_dato');
CREATE TYPE prioridad_reco   AS ENUM ('alta','media','baja');
CREATE TYPE origen_ruta      AS ENUM ('interno','externo');
CREATE TYPE nivel_tecnologico AS ENUM ('1','2','3','4','5'); -- benchmark Manual..IA
CREATE TYPE estado_tarea     AS ENUM ('pendiente','en_progreso','cerrada','vencida');

-- =====================================================================
-- 0. TENANTS  (cuentas consumidoras: DQnexus, Comfama, clientes)
-- =====================================================================
CREATE TABLE tenant (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre       text NOT NULL,
  slug         text UNIQUE NOT NULL,
  activo       boolean NOT NULL DEFAULT true,
  creado_en    timestamptz NOT NULL DEFAULT now()
);

-- =====================================================================
-- 1. KB_VERSION  (versión de la base de conocimiento por diagnóstico)
-- =====================================================================
CREATE TABLE kb_version (
  version      text PRIMARY KEY,          -- p. ej. '3.0.0'
  publicado_en timestamptz NOT NULL DEFAULT now(),
  checksum     text,
  total_preguntas integer,
  notas        text
);

-- =====================================================================
-- 2. ORGANIZACION  (empresa diagnosticada)
-- =====================================================================
CREATE TABLE organizacion (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  nombre        text NOT NULL,
  nit           text,
  sector        text,
  tamano        tamano_empresa,
  aplicabilidad jsonb NOT NULL DEFAULT '{}'::jsonb,  -- permisos_ambientales, saglaft, ptee, rnbd...
  creado_en     timestamptz NOT NULL DEFAULT now(),
  actualizado_en timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_org_tenant  ON organizacion(tenant_id);
CREATE INDEX ix_org_sector  ON organizacion(sector);
CREATE INDEX ix_org_nombre_trgm ON organizacion USING gin (nombre gin_trgm_ops);

-- =====================================================================
-- 3. DIAGNOSTICO
-- =====================================================================
CREATE TABLE diagnostico (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        uuid NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  organizacion_id  uuid NOT NULL REFERENCES organizacion(id) ON DELETE CASCADE,
  kb_version       text NOT NULL REFERENCES kb_version(version),
  estado           estado_diag NOT NULL DEFAULT 'en_progreso',
  modo             modo_diagnostico NOT NULL DEFAULT 'completo',
  exigir_completitud boolean NOT NULL DEFAULT false,
  score_sgi        numeric(5,2),
  nivel_sgi        smallint CHECK (nivel_sgi BETWEEN 1 AND 5),
  cumplimiento_global numeric(5,2),
  madurez_global   numeric(4,2),
  nivel_tecnologico nivel_tecnologico,      -- benchmark declarado
  creado_en        timestamptz NOT NULL DEFAULT now(),
  completado_en    timestamptz,
  idempotency_key  text
);
CREATE INDEX ix_diag_tenant ON diagnostico(tenant_id);
CREATE INDEX ix_diag_org    ON diagnostico(organizacion_id, creado_en DESC);
CREATE UNIQUE INDEX ux_diag_idem ON diagnostico(tenant_id, idempotency_key)
  WHERE idempotency_key IS NOT NULL;

-- =====================================================================
-- 4. RESPUESTA  (idempotente por (diagnostico, pregunta))
-- =====================================================================
CREATE TABLE respuesta (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       uuid NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  diagnostico_id  uuid NOT NULL REFERENCES diagnostico(id) ON DELETE CASCADE,
  pregunta_id     text NOT NULL,           -- p. ej. 'sst-1.1.1'
  skill_id        text NOT NULL,           -- módulo: sst, ambiental...
  tipo            tipo_pregunta NOT NULL,
  valor           valor_respuesta,
  peso            numeric(8,5),            -- copia del peso vigente (auditable)
  evidencia_ref   uuid,                    -- -> evidencia.id
  actualizado_en  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (diagnostico_id, pregunta_id)
);
CREATE INDEX ix_resp_diag  ON respuesta(diagnostico_id);
CREATE INDEX ix_resp_skill ON respuesta(diagnostico_id, skill_id);

-- =====================================================================
-- 5. EVIDENCIA  (trazabilidad; hash de integridad)
-- =====================================================================
CREATE TABLE evidencia (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      uuid NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  respuesta_id   uuid NOT NULL REFERENCES respuesta(id) ON DELETE CASCADE,
  tipo           text NOT NULL CHECK (tipo IN ('url','archivo','nota')),
  uri            text,
  hash           text,
  creado_en      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_evid_resp ON evidencia(respuesta_id);
ALTER TABLE respuesta
  ADD CONSTRAINT fk_resp_evid FOREIGN KEY (evidencia_ref)
  REFERENCES evidencia(id) ON DELETE SET NULL;

-- =====================================================================
-- 6. RESULTADO_PILAR  (materializado por el motor de scoring)
-- =====================================================================
CREATE TABLE resultado_pilar (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        uuid NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  diagnostico_id   uuid NOT NULL REFERENCES diagnostico(id) ON DELETE CASCADE,
  skill_id         text NOT NULL,
  score            numeric(5,2),
  nivel            smallint CHECK (nivel BETWEEN 1 AND 5),
  cumplimiento_pct numeric(5,2),
  madurez_promedio numeric(4,2),
  banda            text,                   -- Crítico / Moderadamente aceptable / Aceptable...
  hallazgos        jsonb NOT NULL DEFAULT '[]'::jsonb,
  UNIQUE (diagnostico_id, skill_id)
);
CREATE INDEX ix_respil_diag ON resultado_pilar(diagnostico_id);

-- =====================================================================
-- 7. RECOMENDACION
-- =====================================================================
CREATE TABLE recomendacion (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       uuid NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  diagnostico_id  uuid NOT NULL REFERENCES diagnostico(id) ON DELETE CASCADE,
  skill_id        text NOT NULL,
  pregunta_id     text,
  prioridad       prioridad_reco NOT NULL,
  score           numeric(5,2),
  texto           text NOT NULL,
  acciones        jsonb NOT NULL DEFAULT '[]'::jsonb,
  norma_refs      jsonb NOT NULL DEFAULT '[]'::jsonb,
  creado_en       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_reco_diag ON recomendacion(diagnostico_id, prioridad);

-- =====================================================================
-- 8. RUTA_APRENDIZAJE  (puente a la capa de aprendizaje de DQnexus · origen interno)
-- =====================================================================
CREATE TABLE ruta_aprendizaje (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        uuid NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  recomendacion_id uuid REFERENCES recomendacion(id) ON DELETE CASCADE,
  diagnostico_id   uuid NOT NULL REFERENCES diagnostico(id) ON DELETE CASCADE,
  skill_id         text NOT NULL,
  brecha           text NOT NULL,
  recurso_url      text,
  origen           origen_ruta NOT NULL DEFAULT 'interno',
  creado_en        timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_ruta_diag ON ruta_aprendizaje(diagnostico_id);

-- =====================================================================
-- 9. Vigilancia (feed normativo y de mercado) — consultable vía API
-- =====================================================================
CREATE TABLE normativa_entry (
  id          text PRIMARY KEY,
  modulo_sgi  text,
  fuente      text,
  tipo        text,
  titulo      text NOT NULL,
  fecha       date,
  url         text,
  estado      text,                        -- vigente/nuevo/modifica/derogado
  relevancia  text,                        -- alta/media/baja
  resumen     text,
  ingerido_en timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_norm_modulo ON normativa_entry(modulo_sgi, estado);

CREATE TABLE market_signal (
  id          text PRIMARY KEY,
  tipo        text,
  titulo      text NOT NULL,
  fecha       date,
  impacto     text,                        -- alto/medio/bajo
  fuente      text,
  resumen     text,
  ingerido_en timestamptz NOT NULL DEFAULT now()
);

-- =====================================================================
-- 10. Auditoría de eventos (observabilidad mínima)
-- =====================================================================
CREATE TABLE evento_auditoria (
  id          bigserial PRIMARY KEY,
  tenant_id   uuid,
  actor       text,                        -- api-key / usuario / agente
  accion      text NOT NULL,               -- diagnostico.creado, respuestas.actualizadas...
  entidad     text,
  entidad_id  text,
  payload     jsonb,
  creado_en   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_evt_tenant ON evento_auditoria(tenant_id, creado_en DESC);

-- =====================================================================
-- 10b. TAREA_MEJORA  (plan de mejoramiento generado desde recomendacion)
-- =====================================================================
CREATE TABLE tarea_mejora (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        uuid NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  diagnostico_id   uuid NOT NULL REFERENCES diagnostico(id) ON DELETE CASCADE,
  recomendacion_id uuid REFERENCES recomendacion(id) ON DELETE SET NULL,
  skill_id         text NOT NULL,
  pregunta_id      text,
  brecha           text NOT NULL,
  accion           text NOT NULL,
  norma_ref        text,
  prioridad        prioridad_reco NOT NULL,
  responsable      text,                    -- rol sugerido
  plazo_dias       integer,
  fecha_limite     date,
  esfuerzo         text CHECK (esfuerzo IN ('Alto','Medio','Bajo')),
  fase             smallint CHECK (fase BETWEEN 1 AND 3),
  criterio_cierre  text,
  estado           estado_tarea NOT NULL DEFAULT 'pendiente',
  ruta_aprendizaje_id uuid REFERENCES ruta_aprendizaje(id) ON DELETE SET NULL,
  creado_en        timestamptz NOT NULL DEFAULT now(),
  cerrado_en       timestamptz
);
CREATE INDEX ix_tarea_diag  ON tarea_mejora(diagnostico_id, prioridad);
CREATE INDEX ix_tarea_estado ON tarea_mejora(estado, fecha_limite);

-- =====================================================================
-- 10c. ALERTA  (emitidas por el motor de alertas: normativa/mercado/plan)
-- =====================================================================
CREATE TABLE alerta (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    uuid REFERENCES tenant(id) ON DELETE CASCADE,  -- NULL = global (mercado)
  tipo         text NOT NULL CHECK (tipo IN ('normativa','mercado','plan')),
  severidad    text NOT NULL CHECK (severidad IN ('critica','alta','media','informativa')),
  titulo       text NOT NULL,
  detalle      jsonb NOT NULL DEFAULT '{}'::jsonb,
  origen_id    text,                          -- id de normativa_entry / market_signal / tarea
  estado       text NOT NULL DEFAULT 'nueva' CHECK (estado IN ('nueva','despachada','resuelta')),
  creado_en    timestamptz NOT NULL DEFAULT now(),
  despachada_en timestamptz
);
CREATE INDEX ix_alerta_estado ON alerta(estado, severidad, creado_en DESC);

-- =====================================================================
-- 11. Row-Level Security (aislamiento por tenant)
--     La app fija:  SET app.tenant_id = '<uuid>'  por sesión/conexión.
-- =====================================================================
CREATE OR REPLACE FUNCTION current_tenant() RETURNS uuid
LANGUAGE sql STABLE AS $$
  SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid
$$;

DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY[
    'organizacion','diagnostico','respuesta','evidencia',
    'resultado_pilar','recomendacion','ruta_aprendizaje','tarea_mejora'
  ] LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', t);
    EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', t);
    EXECUTE format($f$
      CREATE POLICY tenant_isolation ON %I
      USING (tenant_id = current_tenant())
      WITH CHECK (tenant_id = current_tenant());
    $f$, t);
  END LOOP;
END $$;

-- =====================================================================
-- 12. Vista de conveniencia: última foto por organización
-- =====================================================================
CREATE VIEW v_ultimo_diagnostico AS
SELECT DISTINCT ON (organizacion_id)
       organizacion_id, id AS diagnostico_id, score_sgi, nivel_sgi,
       cumplimiento_global, kb_version, completado_en
FROM   diagnostico
WHERE  estado = 'calculado'
ORDER  BY organizacion_id, completado_en DESC NULLS LAST;

COMMIT;

-- Semilla mínima de versión de KB (ajustar checksum real en despliegue)
INSERT INTO kb_version(version, total_preguntas, notas)
VALUES ('3.0.0', 500, 'Banco de 500 preguntas; SST=60 oficiales Res. 0312')
ON CONFLICT (version) DO NOTHING;
