"""Importe les réponses de la Google Sheet dans donnees/reponses.csv.

Usage (la clé ne doit jamais être écrite dans un fichier du dépôt) :
    COLLECTE_URL="https://script.google.com/macros/s/.../exec" EXPORT_KEY="..." python3 collecte/importer.py

COLLECTE_URL est facultatif : par défaut, l'URL de collecte écrite dans index.html.
"""
import collections
import csv
import io
import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "donnees" / "reponses.csv"
EXPECTED = ["id", "recu_le", "version", "statut", "debut", "fin", "consentement", "F1", "F2", "F3",
            "C1", "controle_ok", "groupe_controle", "P1", "P2", "P3", "P4",
            "G_3.50", "G_2.90", "G_2.40", "G_1.90", "G_1.50", "GG_prix_accepte",
            "bien_etre", "routine", "valeurs", "innovation", "confiance", "qualite", "rse",
            "genre", "regime", "depense_50cl"]


def collecte_url():
    url = os.environ.get("COLLECTE_URL")
    if url:
        return url
    m = re.search(r'const COLLECTE_URL = "([^"]+)"', (ROOT / "index.html").read_text(encoding="utf-8"))
    if not m:
        sys.exit("COLLECTE_URL introuvable (variable d'environnement ou index.html).")
    return m.group(1)


def main():
    key = os.environ.get("EXPORT_KEY")
    if not key:
        sys.exit("Variable d'environnement EXPORT_KEY manquante.")
    url = collecte_url() + "?" + urllib.parse.urlencode({"export": "csv", "key": key})
    with urllib.request.urlopen(url, timeout=60) as res:  # suit la redirection Google en GET
        text = res.read().decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text), delimiter=";"))
    if not rows or rows[0] != EXPECTED:
        sys.exit("Réponse inattendue (clé incorrecte ou script non redéployé ?) : " + text[:200])
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f, delimiter=";").writerows(rows)
    data = [dict(zip(rows[0], r)) for r in rows[1:]]
    print(f"{len(data)} réponse(s) importée(s) dans {OUT.relative_to(ROOT)}")
    print("Par statut :", dict(collections.Counter(d["statut"] for d in data)))
    print("Par version (complets) :", dict(collections.Counter(d["version"] for d in data if d["statut"] == "complet")))


if __name__ == "__main__":
    main()
