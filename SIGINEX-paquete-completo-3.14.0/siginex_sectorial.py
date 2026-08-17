#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIGINEX · Benchmarking sectorial
Versión: 1.0.0

Agrega los diagnósticos persistidos por sector y posiciona a una empresa
frente a su industria (percentil, delta vs. media del sector, por módulo).

En producción, la entrada son los resultados persistidos (diagnostico +
resultado_pilar + organizacion.sector). Aquí se demuestra con un conjunto
sintético de empresas generado con el orquestador sobre el banco real.

Uso:
    python3 siginex_sectorial.py [ruta_kb.json]
"""
import sys, json, random, statistics, datetime
import siginex_orchestrator as orch

def load_kb(path):
    kb = json.load(open(path, encoding="utf-8"))
    return {"modulos": kb["modulos"]}

# ---------------- Agregación ----------------
def aggregate(results):
    por_sector = {}
    for r in results:
        sec = r["organizacion"]["sector"]
        d = por_sector.setdefault(sec, {"scores": [], "modulos": {}})
        d["scores"].append(r["resultado"]["score_sgi"])
        for p in r["resultado"]["por_modulo"]:
            if p["cumplimiento"] is not None:
                d["modulos"].setdefault(p["modulo"], []).append(p["cumplimiento"])

    def stats(v):
        v = sorted(v)
        q = statistics.quantiles(v, n=4) if len(v) >= 4 else [v[0], statistics.median(v), v[-1]]
        return {"n": len(v), "media": round(statistics.mean(v), 2),
                "mediana": round(statistics.median(v), 2),
                "p25": round(q[0], 2), "p75": round(q[2], 2),
                "min": round(min(v), 2), "max": round(max(v), 2)}

    out = {}
    for sec, d in por_sector.items():
        out[sec] = {"score": stats(d["scores"]),
                    "por_modulo": {m: round(statistics.mean(v), 2) for m, v in d["modulos"].items()}}
    return out

def percentile(value, data):
    data = sorted(data)
    return round(sum(1 for x in data if x <= value) / len(data) * 100, 1)

def position(result, results, agg):
    sec = result["organizacion"]["sector"]
    peers = [r["resultado"]["score_sgi"] for r in results if r["organizacion"]["sector"] == sec]
    sec_stats = agg[sec]
    comp = {}
    for p in result["resultado"]["por_modulo"]:
        if p["cumplimiento"] is None:
            continue
        media = sec_stats["por_modulo"].get(p["modulo"])
        if media is not None:
            comp[p["modulo"]] = {"empresa": p["cumplimiento"], "media_sector": media,
                                 "delta": round(p["cumplimiento"] - media, 2)}
    return {"empresa": result["organizacion"]["nombre"], "sector": sec,
            "score": result["resultado"]["score_sgi"],
            "percentil_en_sector": percentile(result["resultado"]["score_sgi"], peers),
            "media_sector": sec_stats["score"]["media"],
            "delta_vs_media_sector": round(result["resultado"]["score_sgi"] - sec_stats["score"]["media"], 2),
            "por_modulo": comp}

# ---------------- Demo sintética ----------------
SECTORES = {
    "Servicios financieros": 0.70, "Tecnología / Software": 0.68,
    "Salud": 0.58, "Manufactura / Industria": 0.55, "Construcción": 0.47,
}

def synth_company(kb, sector, mu, rng):
    m = min(0.95, max(0.10, rng.gauss(mu, 0.12)))
    prof = {"permAmbiental": rng.random() < 0.5,
            "saglaft": sector == "Servicios financieros" or rng.random() < 0.3,
            "ptee": rng.random() < 0.5, "rnbd": rng.random() < 0.5}
    answers = {}
    for mod in kb["modulos"]:
        for q in mod["preguntas"]:
            if not orch.applicable(q, prof):
                continue
            x = rng.random()
            answers[q["id"]] = 2 if x < m else (0 if x > 1 - (1 - m) * 0.6 else 1)
    company = {"nombre": f"{sector[:12]}-{rng.randint(100,999)}", "sector": sector,
               "aplicabilidad": prof, "nivel_tecnologico": rng.randint(2, 4)}
    return orch.run(kb, company, answers)

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/kb.json"
    kb = load_kb(path)
    rng = random.Random(42)
    results = []
    for sector, mu in SECTORES.items():
        for _ in range(12):
            results.append(synth_company(kb, sector, mu, rng))

    agg = aggregate(results)
    ejemplo = position(results[0], results, agg)

    print("=== SIGINEX · Benchmarking sectorial (demo sintética) ===")
    print(f"Muestra: {len(results)} empresas · {len(agg)} sectores\n")
    print(f"{'Sector':<26} {'n':>3} {'media':>7} {'p25':>6} {'p75':>6}")
    for sec, d in sorted(agg.items(), key=lambda kv: -kv[1]["score"]["media"]):
        s = d["score"]
        print(f"{sec:<26} {s['n']:>3} {s['media']:>7} {s['p25']:>6} {s['p75']:>6}")

    print(f"\nPosicionamiento de {ejemplo['empresa']} ({ejemplo['sector']}):")
    print(f"  score {ejemplo['score']} · percentil {ejemplo['percentil_en_sector']} · "
          f"media sector {ejemplo['media_sector']} · delta {ejemplo['delta_vs_media_sector']:+}")

    report = {"componente": "SIGINEX · Benchmarking sectorial", "version": "1.0.0",
              "generado_en": datetime.datetime.now().isoformat(timespec="seconds"),
              "nota": "Demostración con datos sintéticos; en producción usa diagnósticos persistidos.",
              "muestra": {"empresas": len(results), "sectores": list(agg.keys())},
              "por_sector": agg, "posicionamiento_ejemplo": ejemplo}
    out = "/mnt/user-data/outputs/siginex-sectorial-sample.json"
    json.dump(report, open(out, "w"), ensure_ascii=False, indent=1)
    print("\nReporte guardado en:", out)

if __name__ == "__main__":
    main()
