#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIGINEX · Orquestador (Agent Runtime) — implementación de referencia
Versión: 1.0.0

Ejecuta el pipeline de diagnóstico de punta a punta:
  perfil + respuestas  ->  [resolver de aplicabilidad]  ->  [scoring]  ->
  [recomendaciones]  ->  [plan de mejora]  ->  [adopción]  ->  [benchmark]  ->
  contrato de salida consolidado.

Uso:
    python3 siginex_orchestrator.py [ruta_al_artefacto.html]

El KB (banco de 500 preguntas) se toma del artefacto (const BANK) para
garantizar que el runtime evalúa exactamente lo mismo que la interfaz.
Resultado orientativo: no sustituye auditoría formal ni concepto legal.
"""
import json, sys, re, datetime, hashlib

KB_VERSION = "3.0.0"

# ----------------------- Resolver de aplicabilidad -----------------------
def applicable(q, profile):
    """Devuelve False si la pregunta no aplica según el perfil de la empresa."""
    s = " ".join([q.get("norma",""), q.get("articulo",""),
                  q.get("requisito",""), q.get("pregunta","")]).lower()
    if not profile.get("permAmbiental") and ("631" in s or "vertimiento" in s):
        return False
    if not profile.get("saglaft") and any(t in s for t in
            ["saglaft","sarlaft","supersociedades","la/ft","lavado"]):
        return False
    if not profile.get("ptee") and "ptee" in s:
        return False
    if not profile.get("rnbd") and "rnbd" in s:
        return False
    return True

# ----------------------- Motores -----------------------
RESP = {"sst":"Responsable del SG-SST","ambiental":"Coordinador Ambiental / HSEQ",
        "calidad":"Líder de Calidad","riesgos":"Oficial de Riesgos / Continuidad",
        "cumplimiento":"Oficial de Cumplimiento",
        "datos":"Oficial de Protección de Datos / Seguridad de la Información",
        "gobierno":"Secretaría General / Gobierno Corporativo",
        "esg":"Líder de Sostenibilidad / ESG","gobernanza_ia":"Responsable de Gobernanza de IA"}

ADOPT = {
 "sst":[("Fundamentos del SG-SST",[]),("Identificación de peligros y valoración de riesgos (IPER)",["peligro","iper","riesgo"]),("Investigación de incidentes e indicadores de SST",["incidente","accidente","indicador"])],
 "ambiental":[("Gestión ambiental ISO 14001",[]),("Cumplimiento legal ambiental y permisos",["permiso","licencia","legal","631","vertimiento"]),("Gestión de residuos y uso eficiente de recursos",["residuo","respel","agua","energía"])],
 "calidad":[("Sistema de gestión de calidad ISO 9001",[]),("Enfoque a procesos e indicadores",["proceso","indicador","satisfacción"]),("Auditoría interna y mejora continua",["auditoría","no conformidad","mejora","revisión"])],
 "riesgos":[("Gestión de riesgos ISO 31000",[]),("Continuidad del negocio ISO 22301",["continuidad","22301","bia"]),("Prevención LA/FT (SAGRLAFT/SARLAFT)",["saglaft","sarlaft","la/ft","lavado","supersociedades"])],
 "cumplimiento":[("Cumplimiento legal y matriz de requisitos",[]),("Programa de Transparencia y Ética Empresarial (PTEE)",["ptee","transparencia","2195"]),("Anticorrupción y debida diligencia",["anticorrup","1474","debida diligencia"])],
 "datos":[("Protección de datos personales (Ley 1581)",["1581","dato","rnbd","titular","autoriz"]),("Seguridad de la información ISO 27001",["27001","seguridad","control","acceso"]),("Gestión de incidentes de seguridad",["incidente"])],
 "gobierno":[("Gobierno corporativo y ética",[]),("Antisoborno ISO 37001",["soborno","37001","regalo","conflicto"]),("Control interno y rendición de cuentas",["control interno","coso","transparencia","rendición","1712"])],
 "esg":[("Fundamentos de sostenibilidad y ESG",[]),("Reporte de sostenibilidad (NIIF S1/S2, GRI)",["reporte","divulga","niif","gri","emisor","031"]),("Gestión de riesgos ASG y clima",["riesgo","clima","emisi","material","escenario"])],
 "gobernanza_ia":[("Fundamentos de gobernanza de IA (ISO 42001)",[]),("Evaluación de impacto y riesgos de IA",["impacto","aia","riesgo","ciclo"]),("Datos, sesgos y transparencia en IA",["dato","sesgo","transparen","explica","supervis","seguridad"])],
}

# Mercado (Benchmark_SGI_Tools): niveles de las 9 herramientas
BENCH_NIVELES = [3,3,2,2,4,4,5,4,5]
BENCH_RECO = {
 1:"Digitalice el SGI: pase de papel/Excel a una plataforma integrada.",
 2:"Consolide en una sola plataforma integrada (nivel 3) y elimine silos.",
 3:"Automatice flujos, alertas e indicadores (nivel 4) e incorpore analítica.",
 4:"Incorpore inteligencia (nivel 5): IA para vigilancia, priorización y recomendaciones.",
 5:"Manténgase a la vanguardia: orqueste IA sobre los datos del SGI (predicción y benchmarking)."}

def level_for(pct):
    if pct is None: return None
    if pct < 21:  return {"n":1,"name":"Inicial"}
    if pct < 41:  return {"n":2,"name":"Básico"}
    if pct < 61:  return {"n":3,"name":"En desarrollo"}
    if pct < 81:  return {"n":4,"name":"Optimizado"}
    return {"n":5,"name":"Excelencia"}

def es_legal(norma):
    n = (norma or "").lower()
    return any(k in n for k in ["ley","decreto","resolución","resolucion","circular"])

def ruta_for(mid, q):
    cat = ADOPT.get(mid)
    if not cat: return None
    s = " ".join([q.get("requisito",""), q.get("pregunta",""), q.get("norma","")]).lower()
    route = cat[0][0]
    for comp, trig in cat:
        if trig and any(t in s for t in trig):
            route = comp; break
    return route

# ----------------------- Pipeline -----------------------
def run(kb, company, answers, options=None):
    options = options or {}
    profile = company.get("aplicabilidad", {})
    mods = kb["modulos"]

    per_modulo, brechas, plan, alertas = [], [], [], []
    aprend = {}
    answered_tot = aplic_tot = 0

    for m in mods:
        apq = [q for q in m["preguntas"] if applicable(q, profile)]
        aplic_tot += len(apq)
        num = den = 0.0
        answered = 0
        for q in apq:
            v = answers.get(q["id"])
            if v is None:
                continue
            answered += 1
            if v == "na":
                continue
            num += (int(v)/2.0) * q["peso"]
            den += q["peso"]
            if int(v) < 2:
                prioridad = "alta" if (int(v)==0 or es_legal(q.get("norma"))) else "media"
                if int(v)==1 and not es_legal(q.get("norma")): prioridad="media"
                brechas.append({"modulo":m["id"],"pregunta_id":q["id"],
                                "brecha":q["pregunta"],"norma":q.get("norma"),
                                "evaluacion":int(v),"prioridad":prioridad})
                # plan de mejora
                dias = 30 if prioridad=="alta" else 90
                plan.append({"modulo":m["id"],"pregunta_id":q["id"],
                             "accion":q["recomendacion"][str(v)],
                             "responsable":RESP.get(m["id"]),
                             "prioridad":prioridad,"plazo_dias":dias,
                             "fase":1 if prioridad=="alta" else 2,
                             "norma":q.get("norma"),
                             "criterio_cierre":"Evidencia verificable del requisito, vigente y trazable."})
                # adopción
                comp = ruta_for(m["id"], q)
                if comp:
                    key = comp
                    if key not in aprend:
                        aprend[key] = {"competencia":comp,"modulo":m["id"],"brechas":0,"prioridad":1}
                    aprend[key]["brechas"] += 1
                    if int(v)==0: aprend[key]["prioridad"]=0
        answered_tot += answered
        comp_pct = (num/den*100) if den>0 else None
        per_modulo.append({"modulo":m["id"],"nombre":m.get("name",m.get("short",m["id"])),
                           "cumplimiento": round(comp_pct,2) if comp_pct is not None else None,
                           "nivel": level_for(comp_pct),
                           "respondidas":answered,"aplicables":len(apq)})

    # global ponderado por peso de módulo
    ev = [p for p in per_modulo if p["cumplimiento"] is not None]
    gw = sum(next(mm["weight"] for mm in mods if mm["id"]==p["modulo"]) for p in ev)
    gs = sum(p["cumplimiento"]*next(mm["weight"] for mm in mods if mm["id"]==p["modulo"]) for p in ev)
    score = round(gs/gw, 2) if gw>0 else 0.0
    nivel_sgi = level_for(score)

    # ordenar plan por prioridad y adopción por prioridad/brechas
    plan.sort(key=lambda t: (0 if t["prioridad"]=="alta" else 1))
    plan_aprendizaje = sorted(aprend.values(), key=lambda r:(r["prioridad"], -r["brechas"]))
    for r in plan_aprendizaje:
        r["nivel"] = "Básico" if r["prioridad"]==0 else "Intermedio"
        r["origen"] = "interno"

    # benchmark (opcional)
    benchmark = None
    nt = company.get("nivel_tecnologico")
    if nt:
        prom = sum(BENCH_NIVELES)/len(BENCH_NIVELES)
        benchmark = {"nivel_empresa":nt,"promedio_mercado":round(prom,1),
                     "rango_mercado":[min(BENCH_NIVELES),max(BENCH_NIVELES)],
                     "herramientas_por_encima":len([x for x in BENCH_NIVELES if x>nt]),
                     "brecha_al_lider":max(BENCH_NIVELES)-nt,
                     "recomendacion":BENCH_RECO.get(nt)}

    # alertas (motor de alertas: brechas críticas)
    criticas = [b for b in brechas if b["prioridad"]=="alta"]
    if criticas:
        alertas.append({"tipo":"plan","severidad":"alta",
                        "titulo":"Brechas de alta prioridad detectadas",
                        "detalle":{"cantidad":len(criticas)}})

    return {
        "kb_version": KB_VERSION,
        "organizacion": {"nombre":company.get("nombre"),"sector":company.get("sector"),
                          "tamano":company.get("tamano")},
        "aplicabilidad": profile,
        "resultado": {"score_sgi":score,"nivel_sgi":nivel_sgi,
                      "cumplimiento_global":score,"por_modulo":per_modulo},
        "brechas": brechas,
        "plan_mejora": plan,
        "plan_aprendizaje": plan_aprendizaje,
        "benchmark": benchmark,
        "alertas": alertas,
        "meta": {"preguntas_aplicables":aplic_tot,"respondidas":answered_tot,
                 "generado_en": datetime.datetime.now().isoformat(timespec="seconds")}
    }

# ----------------------- Utilidades -----------------------
def load_bank_from_html(path):
    html = open(path, encoding="utf-8").read()
    raw = html.split("const BANK = ",1)[1].split("</script>",1)[0].rstrip().rstrip(";")
    return json.loads(raw)

def _demo(kb):
    """Genera respuestas sintéticas deterministas para demostrar el pipeline."""
    company = {"nombre":"Manufacturas del Valle S.A.S.","sector":"Manufactura / Industria",
               "tamano":"mediana","nivel_tecnologico":2,
               "aplicabilidad":{"permAmbiental":True,"saglaft":False,"ptee":True,"rnbd":False}}
    answers = {}
    for m in kb["modulos"]:
        for q in m["preguntas"]:
            if not applicable(q, company["aplicabilidad"]):
                continue
            hv = int(hashlib.md5(q["id"].encode()).hexdigest(), 16) % 10
            answers[q["id"]] = 2 if hv >= 6 else (1 if hv >= 3 else 0)  # ~mezcla realista
    return company, answers

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/siginex-autodiagnostico-500.html"
    kb = load_bank_from_html(path)
    company, answers = _demo(kb)
    out = run(kb, company, answers)
    r = out["resultado"]
    print("=== SIGINEX · Orquestador (demo) ===")
    print("Empresa:", out["organizacion"]["nombre"])
    print("Aplicabilidad:", out["aplicabilidad"])
    print("Preguntas aplicables:", out["meta"]["preguntas_aplicables"],
          "· respondidas:", out["meta"]["respondidas"])
    print("Score SGI:", r["score_sgi"], "· Nivel:", r["nivel_sgi"])
    print("Cumplimiento por módulo:")
    for p in r["por_modulo"]:
        print(f"   - {p['modulo']:<12} {p['cumplimiento']}%  (nivel {p['nivel']['n'] if p['nivel'] else '-'})  "
              f"[{p['respondidas']}/{p['aplicables']}]")
    print("Brechas:", len(out["brechas"]),
          "· Tareas de plan:", len(out["plan_mejora"]),
          "· Rutas de aprendizaje:", len(out["plan_aprendizaje"]))
    if out["benchmark"]:
        b = out["benchmark"]
        print(f"Benchmark: nivel {b['nivel_empresa']} vs mercado (prom {b['promedio_mercado']}, "
              f"rango {b['rango_mercado']}) · brecha al líder {b['brecha_al_lider']}")
    print("Alertas:", out["alertas"])
    # guardar salida de muestra
    sample = "/mnt/user-data/outputs/siginex-orchestrator-sample.json"
    json.dump(out, open(sample,"w"), ensure_ascii=False, indent=1)
    print("Salida consolidada guardada en:", sample)
