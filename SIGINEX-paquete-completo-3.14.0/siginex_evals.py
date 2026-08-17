#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIGINEX · Evals y observabilidad del agente
Versión: 1.0.0

Batería de evaluaciones deterministas sobre el orquestador (siginex_orchestrator),
alineada con los principios de ISO/IEC 42001 (medir, gestionar y gobernar la IA):
consistencia del scoring, monotonicidad, aplicabilidad, cobertura de plan/adopción,
coherencia de niveles e integridad del contrato de salida.

Uso:
    python3 siginex_evals.py [ruta_al_artefacto.html]

Produce un reporte por consola y siginex-evals-report.json.
"""
import sys, json, time, datetime
import siginex_orchestrator as orch

TOL = 0.01
ALL_ON = {"permAmbiental": True, "saglaft": True, "ptee": True, "rnbd": True}
ALL_OFF = {"permAmbiental": False, "saglaft": False, "ptee": False, "rnbd": False}

def answers_uniform(kb, val, profile):
    return {q["id"]: val for m in kb["modulos"] for q in m["preguntas"]
            if orch.applicable(q, profile)}

def company(profile, nt=None):
    return {"nombre": "Eval Corp", "aplicabilidad": profile, "nivel_tecnologico": nt}

def applic_count(kb, profile):
    return sum(1 for m in kb["modulos"] for q in m["preguntas"] if orch.applicable(q, profile))

def run_evals(kb):
    ev = []
    def rec(id, nombre, passed, detalle):
        ev.append({"id": id, "nombre": nombre, "passed": bool(passed), "detalle": detalle})

    # 1. Determinismo / reproducibilidad
    a = answers_uniform(kb, 1, ALL_ON)
    r1 = orch.run(kb, company(ALL_ON), a); r2 = orch.run(kb, company(ALL_ON), a)
    same = (r1["resultado"]["score_sgi"] == r2["resultado"]["score_sgi"] and
            r1["resultado"]["por_modulo"] == r2["resultado"]["por_modulo"])
    rec("determinismo", "Mismo input → mismo output", same,
        f"score {r1['resultado']['score_sgi']} == {r2['resultado']['score_sgi']}")

    # 2. Fronteras del scoring (0→0, 1→50, 2→100)
    s0 = orch.run(kb, company(ALL_ON), answers_uniform(kb,0,ALL_ON))["resultado"]["score_sgi"]
    s1 = orch.run(kb, company(ALL_ON), answers_uniform(kb,1,ALL_ON))["resultado"]["score_sgi"]
    s2 = orch.run(kb, company(ALL_ON), answers_uniform(kb,2,ALL_ON))["resultado"]["score_sgi"]
    ok = abs(s0-0)<TOL and abs(s1-50)<TOL and abs(s2-100)<TOL
    rec("fronteras", "Fronteras del scoring 0/50/100", ok, f"all-0={s0} · all-1={s1} · all-2={s2}")

    # 3. Monotonicidad direccional (mejorar respuestas no baja el score)
    base = answers_uniform(kb, 0, ALL_ON)
    up = dict(base)
    ids = list(base.keys())[:120]
    for k in ids: up[k] = 2
    sb = orch.run(kb, company(ALL_ON), base)["resultado"]["score_sgi"]
    su = orch.run(kb, company(ALL_ON), up)["resultado"]["score_sgi"]
    rec("monotonicidad", "Mejorar respuestas nunca baja el score", su >= sb, f"base={sb} → mejorado={su}")

    # 4. Aplicabilidad (los toggles condicionan la cobertura)
    full = applic_count(kb, ALL_ON)
    off  = applic_count(kb, ALL_OFF)
    cond = full - off
    per_flag = {}
    for flag in ["permAmbiental","saglaft","ptee","rnbd"]:
        p = dict(ALL_OFF); p[flag] = True
        per_flag[flag] = applic_count(kb, p) - off
    ok = full > off and cond == sum(per_flag.values())
    rec("aplicabilidad", "Los toggles condicionan preguntas", ok,
        f"aplican(on)={full} · aplican(off)={off} · condicionadas={cond} · por_flag={per_flag}")

    # 5. Cobertura de plan (una tarea por brecha, con campos completos)
    mix = {}
    for i,(m,q) in enumerate([(m,q) for m in kb["modulos"] for q in m["preguntas"]]):
        if orch.applicable(q, ALL_ON): mix[q["id"]] = (i % 3)  # 0,1,2 rotando
    out = orch.run(kb, company(ALL_ON, nt=2), mix)
    nb, npl = len(out["brechas"]), len(out["plan_mejora"])
    campos_ok = all(all(t.get(k) is not None for k in
                    ["responsable","prioridad","plazo_dias","fase","criterio_cierre"])
                    for t in out["plan_mejora"])
    rec("plan_cobertura", "Una tarea por brecha, con campos completos",
        nb == npl and campos_ok, f"brechas={nb} · tareas={npl} · campos_completos={campos_ok}")

    # 6. Adopción (rutas internas, con competencia)
    rutas = out["plan_aprendizaje"]
    ok = len(rutas) > 0 and all(r.get("origen")=="interno" and r.get("competencia") for r in rutas)
    rec("adopcion", "Rutas de aprendizaje internas y bien formadas", ok,
        f"rutas={len(rutas)} · todas_internas={all(r.get('origen')=='interno' for r in rutas)}")

    # 7. Coherencia de niveles (monotonía del mapeo score→nivel)
    seq = [orch.level_for(p)["n"] for p in [10,30,50,70,95]]
    ok = seq == sorted(seq)
    rec("niveles", "Mapeo score→nivel monotónico", ok, f"niveles={seq}")

    # 8. Integridad del contrato de salida
    req = ["kb_version","organizacion","aplicabilidad","resultado","brechas",
           "plan_mejora","plan_aprendizaje","benchmark","alertas","meta"]
    faltan = [k for k in req if k not in out]
    modulos_ok = len(out["resultado"]["por_modulo"]) == len(kb["modulos"])
    rec("contrato", "Contrato de salida íntegro", not faltan and modulos_ok,
        f"faltan={faltan} · modulos={len(out['resultado']['por_modulo'])}/{len(kb['modulos'])}")

    return ev

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/siginex-autodiagnostico-500.html"
    kb = orch.load_bank_from_html(path)

    # Observabilidad: latencia de una corrida completa
    a = answers_uniform(kb, 1, ALL_ON)
    t0 = time.perf_counter(); orch.run(kb, company(ALL_ON), a); lat = (time.perf_counter()-t0)*1000

    ev = run_evals(kb)
    passed = sum(1 for e in ev if e["passed"]); total = len(ev)

    print("=== SIGINEX · Evals del agente (ISO 42001 · medir/gestionar) ===")
    for e in ev:
        print(f"  [{'PASS' if e['passed'] else 'FALLA'}] {e['id']:<16} {e['detalle']}")
    print(f"\nResultado: {passed}/{total} evals superadas · latencia diagnóstico ≈ {lat:.1f} ms")

    report = {
        "componente": "SIGINEX · Evals y observabilidad",
        "version": "1.0.0",
        "generado_en": datetime.datetime.now().isoformat(timespec="seconds"),
        "kb": {"modulos": len(kb["modulos"]),
               "preguntas": sum(len(m["preguntas"]) for m in kb["modulos"])},
        "metricas_observabilidad": {"latencia_diagnostico_ms": round(lat,1)},
        "resumen": {"superadas": passed, "total": total,
                    "tasa": round(passed/total,3)},
        "evals": ev
    }
    out = "/mnt/user-data/outputs/siginex-evals-report.json"
    json.dump(report, open(out,"w"), ensure_ascii=False, indent=1)
    print("Reporte guardado en:", out)
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
