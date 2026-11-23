"""Toutes les analyses du dossier Prix, à partir de donnees/reponses.csv.

Lancer : python3 dossier/analyse.py   (affiche les résultats)
Le site (dossier/index.html) est produit par dossier/build.py, qui importe ce module.
"""
import csv, math, collections, pathlib
from scipy import stats, optimize
from scipy.stats import chi2_contingency

ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = list(csv.reader(open(ROOT / "donnees" / "reponses.csv", encoding="utf-8-sig"), delimiter=";"))
H = rows[0]
D = [dict(zip(H, r)) for r in rows[1:]]

# ---------- Nettoyage ----------
TESTS = {"testcurl0001", "mvgp6qe2f5hy", "mvgp6vewxb83", "mvgp6z4bgky5", "mvgp714k5mga"}   # tests de mise en service
R1 = [d for d in D if d["id"] not in TESTS]
R = [d for d in R1 if not d["id"].startswith("test")]        # sans les 50 réponses générées test0000xx
C = [d for d in R if d["statut"] == "complet"]               # échantillon d'analyse : personne n'est retiré sur Q5
A = lambda L: [d for d in L if d["version"] == "A"]          # A = collagène d'origine végétale (la variation)
B = lambda L: [d for d in L if d["version"] == "B"]          # B = collagène d'origine animale (le produit standard)

def vw_ok(d): return float(d["P1"]) >= float(d["P2"]) >= float(d["P3"]) >= float(d["P4"])
GGP = [3.5, 2.9, 2.4, 1.9, 1.5]
def gg_ok(d):
    v = [d["G_" + f"{p:.2f}"] for p in GGP]; seen = False
    for x in v:
        if seen and x: return False
        if x == "Oui": seen = True
    return not any(v[i] == "" and v[i + 1] for i in range(4))

funnel = [("Lignes reçues dans la feuille", D), ("Sans les 5 tests de mise en service", R1),
          ("Sans les 50 réponses générées (test0000xx)", R),
          ("Sans les refus de participer", [d for d in R if d["statut"] != "refus"]),
          ("Sans les moins de 18 ans", [d for d in R if d["statut"] not in ("refus", "mineur")]),
          ("Sans les doublons", C), ("Van Westendorp cohérent", [d for d in C if vw_ok(d)]),
          ("Gabor-Granger cohérent", [d for d in C if vw_ok(d) and gg_ok(d)])]
S = [d for d in C if vw_ok(d) and gg_ok(d)]
assert len(S) == len(C)

# ---------- Outils statistiques ----------
def welch(k, alt=None, L=None):
    L = L or S
    a = [float(d[k]) for d in A(L) if d[k] != ""]; b = [float(d[k]) for d in B(L) if d[k] != ""]
    na, nb = len(a), len(b); ma, mb = sum(a) / na, sum(b) / nb; va, vb = stats.tvar(a), stats.tvar(b)
    t, p2 = stats.ttest_ind(a, b, equal_var=False)
    df = (va / na + vb / nb) ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    p = stats.t.sf(t, df) if alt == "A>B" else stats.t.cdf(t, df) if alt == "B>A" else p2
    sp = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2)); d = (ma - mb) / sp
    sed = math.sqrt((na + nb) / (na * nb) + d * d / (2 * (na + nb)))
    ci = lambda v, n: stats.t.ppf(0.975, n - 1) * math.sqrt(v / n)
    dfp = na + nb - 2; tc = stats.t.ppf(1 - 0.05 / (1 if alt else 2), dfp)
    mde = optimize.brentq(lambda x: stats.nct.sf(tc, dfp, x * math.sqrt(na * nb / (na + nb))) - 0.8, 0.01, 3)
    return dict(k=k, a=a, b=b, na=na, nb=nb, ma=ma, mb=mb, ea=ci(va, na), eb=ci(vb, nb), t=t, df=df, p=p, p2=p2,
                d=d, dlo=d - 1.96 * sed, dhi=d + 1.96 * sed, alt=alt, mde=mde)

def chi2(key, L=None, cats=None):
    L = L or S
    get = key if callable(key) else (lambda d: d[key])
    cats = cats or sorted({get(d) for d in L})
    tab = [[sum(get(d) == c for d in A(L)) for c in cats], [sum(get(d) == c for d in B(L)) for c in cats]]
    keep = [j for j in range(len(cats)) if tab[0][j] + tab[1][j] > 0]
    t2 = [[r[j] for j in keep] for r in tab]
    c, p, dof, e = chi2_contingency(t2, correction=False); n = sum(map(sum, t2))
    return dict(chi=c, p=p, dof=dof, v=math.sqrt(c / n), low=sum(x < 5 for r in e for x in r), cells=2 * len(keep),
                cats=[cats[j] for j in keep], tab=t2)

# ---------- 1. Contrôle de manipulation (chi², Q5 à choix) ----------
C1CATS = ["Origine végétale", "Origine animale", "Origine marine", "Je ne sais pas"]
manip = chi2("C1", cats=C1CATS)
c1 = {v: [sum(d["C1"] == c for d in L) for c in C1CATS] for v, L in (("A", A(S)), ("B", B(S)))}

# ---------- 2. Tirage au sort ----------
age = welch("F3")
rand = [("Âge", "Welch", age["p"], age)]
for k, lab in [("genre", "Genre"), ("regime", "Régime alimentaire"), ("depense_50cl", "Dépense habituelle pour 50 cl"),
               ("F1", "Achat d'eau en bouteille (3 derniers mois)"), ("F2", "Achat d'une boisson enrichie (3 derniers mois)")]:
    rand.append((lab, "chi²", chi2(k)["p"], chi2(k)))
DEP3 = {"Moins de 0,30 €": "moins de 0,50 €", "De 0,30 € à 0,49 €": "moins de 0,50 €", "De 0,50 € à 0,79 €": "0,50 à 0,99 €",
        "De 0,80 € à 0,99 €": "0,50 à 0,99 €", "De 1,00 € à 1,49 €": "1 € ou plus", "De 1,50 € à 1,99 €": "1 € ou plus", "2,00 € ou plus": "1 € ou plus"}
dep3 = chi2(lambda d: DEP3[d["depense_50cl"]], cats=["moins de 0,50 €", "0,50 à 0,99 €", "1 € ou plus"])

# ---------- 3. Tests A/B ----------
PRIX = [("P1", "Trop cher", "H2"), ("P2", "Cher", "H3"), ("P3", "Bonne affaire", "H4"), ("P4", "Trop bon marché", "H5")]
prix = [dict(welch(k, "A>B"), lab=l, h=h) for k, l, h in PRIX]
PERC = [("valeurs", "Valeurs (Q13)", "H7", "A>B"), ("rse", "Cohérence avec l'image naturelle (Q17)", "H8", "A>B"),
        ("confiance", "Confiance dans l'efficacité (Q15)", "H9", "B>A"), ("qualite", "Qualité perçue (Q16)", "H10", "B>A"),
        ("bien_etre", "Bien-être (Q11)", "", None), ("routine", "Consommation quotidienne (Q12)", "", None),
        ("innovation", "L'innovation justifie un prix plus élevé (Q14)", "", None)]
perc = [dict(welch(k, alt), lab=l, h=h) for k, l, h, alt in PERC]
gg_first = welch("GG_prix_accepte")
def buys(d, p): return d["GG_prix_accepte"] != "" and float(d["GG_prix_accepte"]) >= p - 1e-9
buy = []
for p in GGP:
    c = chi2(lambda d, p=p: "oui" if buys(d, p) else "non", cats=["oui", "non"])
    buy.append(dict(price=p, na=c["tab"][0][0], Na=len(A(S)), nb=c["tab"][1][0], Nb=len(B(S)), **c))

# ---------- 4. Van Westendorp : courbes et points ----------
GRID = [i / 100 for i in range(0, 1001)]
def vw_points(L):
    n = len(L)
    tbm = [sum(float(d["P4"]) >= x for d in L) / n for x in GRID]   # trop bon marché (descend)
    bm = [sum(float(d["P3"]) >= x for d in L) / n for x in GRID]    # bon marché (descend)
    ch = [sum(float(d["P2"]) <= x for d in L) / n for x in GRID]    # cher (monte)
    tc = [sum(float(d["P1"]) <= x for d in L) / n for x in GRID]    # trop cher (monte)
    def cross(down, up):
        for i in range(1, len(GRID)):
            if down[i] - up[i] <= 0 < down[i - 1] - up[i - 1] or down[i] - up[i] == 0:
                d0, d1 = down[i - 1] - up[i - 1], down[i] - up[i]
                return GRID[i - 1] + (GRID[i] - GRID[i - 1]) * d0 / (d0 - d1) if d0 != d1 else GRID[i]
        return None
    return dict(curves=dict(tbm=tbm, bm=bm, ch=ch, tc=tc), PMC=cross(tbm, ch), OPP=cross(tbm, tc), IPP=cross(bm, ch), PME=cross(bm, tc), n=n)
vw = {"A": vw_points(A(S)), "B": vw_points(B(S)), "all": vw_points(S)}

# ---------- 5. Coûts (chaque montant : source ou hypothèse) ----------
USD = 0.90                    # hypothèse : 1 $ = 0,90 €
TVA = 0.055                   # taux réduit eau et boissons non alcooliques (BOFiP)
MARGE_DISTRIB = 0.30          # hypothèse : part du distributeur, en % du prix hors taxe
BASE = [("Bouteille PET 50 cl (préforme)", 0.04, "source + hypothèse"), ("Bouchon et étiquette", 0.02, "hypothèse"),
        ("Eau, embouteillage, énergie", 0.03, "hypothèse"), ("Transport jusqu'au distributeur", 0.05, "hypothèse")]
base_cost = sum(x[1] for x in BASE)
coll_kg = (20.5 + 26.5) / 2 * USD          # collagène bovin hydrolysé, 20,5 à 26,5 $/kg
DOSE_COLL = 5                              # g par bouteille, comme Humble+ (5 g par canette de 33 cl)
var_B = coll_kg * DOSE_COLL / 1000
vitc_kg = 3.03 * USD                       # vitamine C, 3,03 $/kg (4e trimestre 2025)
bamb_kg = (42 + 48) / 2 * USD              # extrait de bambou 70 % silice, 42 à 48 $/kg
var_A = vitc_kg * 0.080 / 1000 + bamb_kg * 0.100 / 1000   # 80 mg de vitamine C + 100 mg d'extrait de bambou
CVU = {"A": base_cost + var_A, "B": base_cost + var_B}
CONC = 2.99                                # Humble+ Collagen Water, 33 cl
def net_producteur(ttc, tva=TVA, m=MARGE_DISTRIB): return ttc / (1 + tva) * (1 - m)

# Gabor-Granger : part qui achète, chiffre d'affaires et marge par répondant (formule du cours, prix net producteur)
def gg_table(L, v):
    n = len(L); out = []
    for p in GGP:
        part = sum(buys(d, p) for d in L) / n
        out.append(dict(price=p, part=part, ca=p * part, net=net_producteur(p), marge=(net_producteur(p) - CVU[v]) * part))
    return out
ggt = {"A": gg_table(A(S), "A"), "B": gg_table(B(S), "B")}
best = {v: max(ggt[v], key=lambda r: r["marge"]) for v in "AB"}

# ---------- 6. Stress test ----------
def marge_at(v, p, tva=TVA, m=MARGE_DISTRIB, reel=1.0, cvu=None):
    part = sum(buys(d, p) for d in (A(S) if v == "A" else B(S))) / len(A(S) if v == "A" else B(S)) * reel
    return (net_producteur(p, tva, m) - (cvu if cvu is not None else CVU[v])) * part

if __name__ == "__main__":
    print("entonnoir", [(l, len(L), len(A(L)), len(B(L))) for l, L in funnel])
    print("manip", {k: manip[k] for k in ("chi", "dof", "p", "v", "low", "cells")}, c1)
    for lab, t, p, _ in rand: print("tirage", lab, t, round(p, 3))
    print("dep3", round(dep3["p"], 3), dep3["tab"])
    for r in prix + perc + [gg_first]: print(r["k"], round(r["ma"], 2), round(r["mb"], 2), "p", round(r["p"], 3), "p2", round(r["p2"], 3), "d", round(r["d"], 2), "mde", round(r["mde"], 2))
    for b in buy: print("achat", b["price"], b["na"], b["Na"], b["nb"], b["Nb"], round(b["p"], 3), round(b["v"], 2), b["low"])
    for v in ("A", "B", "all"): print("VW", v, {k: round(vw[v][k], 2) if vw[v][k] else None for k in ("PMC", "OPP", "IPP", "PME")})
    print("couts", round(base_cost, 3), round(var_A, 4), round(var_B, 4))
    for v in "AB":
        for r in ggt[v]: print("GG", v, r["price"], round(r["part"], 3), round(r["ca"], 3), round(r["marge"], 3))
    print("best", {v: best[v]["price"] for v in "AB"})
