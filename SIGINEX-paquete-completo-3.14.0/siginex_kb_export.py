#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIGINEX · Hidratación de la base de conocimiento (GET /kb)
Versión: 1.0.0

Extrae el banco (const BANK) del artefacto y produce:
  - kb.json          : payload que sirve GET /kb (KbBundle)
  - kb-version.json  : versión, checksum y conteos (GET /kb/version)

Uso:
    python3 siginex_kb_export.py [ruta_al_artefacto.html]
"""
import sys, json, hashlib, datetime

KB_VERSION = "3.1.0"  # banco de 521 preguntas · 9 módulos

MODELO_MADUREZ = {
    "escala_respuesta": "0/1/2 (No cumple · Parcial · Cumple)",
    "niveles": [
        {"n": 1, "nombre": "Inicial",       "rango": "0-20%"},
        {"n": 2, "nombre": "Básico",        "rango": "21-40%"},
        {"n": 3, "nombre": "En desarrollo", "rango": "41-60%"},
        {"n": 4, "nombre": "Optimizado",    "rango": "61-80%"},
        {"n": 5, "nombre": "Excelencia",    "rango": "81-100%"}
    ]
}

def load_bank_from_html(path):
    html = open(path, encoding="utf-8").read()
    raw = html.split("const BANK = ", 1)[1].split("</script>", 1)[0].rstrip().rstrip(";")
    return json.loads(raw)

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/siginex-autodiagnostico-500.html"
    bank = load_bank_from_html(path)
    modulos = [{"id": m["id"], "nombre": m.get("name", m["id"]),
                "short": m.get("short"), "weight": m["weight"],
                "norms": m.get("norms", []),
                "preguntas": m["preguntas"]} for m in bank["modulos"]]
    total = sum(len(m["preguntas"]) for m in modulos)

    payload = {
        "kb_version": KB_VERSION,
        "total_preguntas": total,
        "modelo_madurez": MODELO_MADUREZ,
        "modulos": modulos
    }
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    checksum = "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()
    payload["checksum"] = checksum

    json.dump(payload, open("/mnt/user-data/outputs/kb.json", "w"),
              ensure_ascii=False, indent=1)
    version = {"kb_version": KB_VERSION, "checksum": checksum,
               "total_preguntas": total, "modulos": len(modulos),
               "generado_en": datetime.datetime.now().isoformat(timespec="seconds")}
    json.dump(version, open("/mnt/user-data/outputs/kb-version.json", "w"),
              ensure_ascii=False, indent=1)

    print("kb.json y kb-version.json generados.")
    print("  versión:", KB_VERSION, "· módulos:", len(modulos), "· preguntas:", total)
    print("  checksum:", checksum)

if __name__ == "__main__":
    main()
