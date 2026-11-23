"""Produit dossier/index.html (le dossier Prix en site web) à partir de dossier/analyse.py.

Lancer : python3 dossier/build.py
"""
import html, math, pathlib, re
import analyse as an
import theme as th

OUT = pathlib.Path(__file__).resolve().parent / "index.html"
esc = html.escape
A, B, S = an.A, an.B, an.S
nA, nB, nS = len(A(S)), len(B(S)), len(S)

# ---------- formatting ----------
def fr(x, n=2):
    return f"{x:,.{n}f}".replace(",", " ").replace(".", ",").replace("-", "−")
def eur(x, n=2): return fr(x, n) + " €"
def pct(x, n=0): return fr(100 * x, n) + " %"
def fp(p): return "p < 0,001" if p < 0.001 else f"p = {fr(p, 3)}"
def L(text, key): return f'<a href="{SRC[key]}" target="_blank" rel="noopener">{text}</a>'

GH = "https://github.com/H-Wen-LIN/Prix-budget-marketing-volvic-enquete/blob/claude/adoring-brahmagupta-ec1uhd/"
SRC = {
    "danone": "https://www.danone.com/fr/newsroom/communiques-de-presse/full-year-results-2025.html",
    "sev_jde": "https://www.lejournaldesentreprises.com/entreprise/societe-des-eaux-de-volvic",
    "sev_xerfi": "https://www.xerfi.com/etudes-par-entreprise/ste-des-eaux-de-volvic_395780059",
    "agra": "https://www.agra.fr/agra-innovation/volvic-et-son-marche",
    "lsa": "https://www.lsa-conso.fr/canicule-les-ventes-d-eaux-doublent-les-premiers-jours-laurent-guivarch-danone-eaux-france,214428",
    "volvic": "https://www.danone.com/fr/marques/eaux/volvic.html",
    "bcorp": "https://www.danone.com/fr/brands/Volvic-certifiee-BCorp.html",
    "volvic_prix": "https://www.houra.fr/marque/volvic-4000005-1000955-1",
    "essentiel": "https://www.bonial.fr/Caen/Promos/Volvic",
    "vitwell": "https://www.fitadium.com/en/2318-vitamin-well-antioxidant-500ml.html",
    "humble_prix": "https://www.jevaismieuxmerci.com/fr_FR/humble-canette-menthe-citron-330-ml-1",
    "humble_dose": "https://www.atida.fr/humble-collagen-water-mangue-passion-canette-330-ml.html",
    "collagene": "https://total-ingredients.com/products/bovine-collagen-peptide-100-grass-fed",
    "bambou": "https://total-ingredients.com/products/organic-bamboo-extract-70-silica-by-uv",
    "vitc": "https://www.expertmarketresearch.com/price-forecast/ascorbic-acid-price-trends",
    "swanson": "https://www.vitacost.com/products/swanson-vitamins-vegan-collagen-builder-60-veggie-capsules-119463",
    "preforme": "https://m.indiamart.com/impcat/pet-preform.html",
    "tva": "https://bofip.impots.gouv.fr/bofip/2033-PGP.html/identifiant=BOI-TVA-LIQ-30-10-10-20160302",
    "tva20": "https://www.publicsenat.fr/actualites/environnement/scandale-des-eaux-minerales-le-senat-augmente-le-taux-de-tva-de-55-a-20-sur-leau-en-bouteille-plastique",
    "vegan": "https://www.darwin-nutrition.fr/conseils/collagene-vegan",
    "allegation": "https://eur-lex.europa.eu/eli/reg/2012/432/oj/fra",
    "hauser": "https://doi.org/10.3389/fpsyg.2018.00998",
    "questionnaire": "https://h-wen-lin.github.io/Prix-budget-marketing-volvic-enquete/",
    "donnees": GH + "donnees/reponses.csv",
    "code": GH + "dossier/analyse.py",
    "sources_echelles": GH + "SOURCES.md",
    "elhedhli": "https://doi.org/10.1016/j.jbusres.2011.06.011", "moore": "https://doi.org/10.1287/isre.2.3.192",
    "karahanna": "https://doi.org/10.2307/25148754", "netemeyer": "https://doi.org/10.1016/S0148-2963(01)00303-4",
    "chaudhuri": "https://doi.org/10.1509/jmkg.65.2.81.18255", "dodds": "https://doi.org/10.1177/002224379102800305",
    "becker": "https://doi.org/10.1016/j.jbusres.2005.01.001",
}

# ---------- SVG helpers ----------
W = 640
def svg(h, body, label, minw=560):
    return (f'<div class="cw"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{esc(label)}" class="chart" '
            f'style="min-width:{minw}px">{body}</svg></div>')
def txt(x, y, s, cls="m", anchor="start"):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{esc(s)}</text>'
def rect(x, y, w, h, cls, tip=None, r=3):
    t = f"<title>{esc(tip)}</title>" if tip else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" rx="{r}" class="{cls}">{t}</rect>'
def line(x1, y1, x2, y2, cls): return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}"/>'
def legend_ab(y=14, x=0):
    return (rect(x, y - 9, 12, 12, "fa", r=3) + txt(x + 18, y + 1, "Version A · collagène végétal", "t") +
            rect(x + 230, y - 9, 12, 12, "fb", r=3) + txt(x + 248, y + 1, "Version B · collagène animal", "t"))

def funnel_svg():
    rowh, top, x0, x1 = 36, 6, 300, W - 70
    mx = len(an.funnel[0][1]); out = []; prev = None
    for i, (lab, Lst) in enumerate(an.funnel):
        n = len(Lst); y = top + i * rowh; w = (x1 - x0) * n / mx; last = i == len(an.funnel) - 1
        out.append(txt(x0 - 12, y + 19, lab, "t" if last else "m", "end"))
        out.append(rect(x0, y + 6, w, 20, "fk" if last else "fn", f"{lab} : {n}"))
        out.append(txt(x0 + w + 8, y + 21, str(n), "t b"))
        if prev is not None and prev - n: out.append(txt(x0 + w + 38, y + 21, f"−{prev - n}", "m"))
        prev = n
    y = top + len(an.funnel) * rowh
    out.append(txt(x0, y + 14, f"dont {nA} en version A et {nB} en version B", "m"))
    return svg(y + 24, "".join(out), "Entonnoir de nettoyage des réponses")

MARKET = [("Volvic nature, 50 cl (pack de 6 à 2,99 €)", 2.99 / 6, "volvic_prix", "n"),
          ("Volvic Essentiel Bio, 75 cl (prix promo)", 1.75, "essentiel", "n"),
          ("Vitamin Well, 50 cl (eau vitaminée)", 2.55, "vitwell", "n"),
          ("Humble+ Collagen Water, 33 cl", 2.99, "humble_prix", "k")]
def market_svg():
    x0, x1, top, rowh = 270, W - 70, 10, 34
    sx = lambda v: x0 + (x1 - x0) * v / 3.5; out = []
    zl, zh = an.vw["all"]["PMC"], an.vw["all"]["PME"]
    yb = top + rowh * len(MARKET) + 6
    out.append(rect(sx(zl), top - 4, sx(zh) - sx(zl), yb - top + 4, "zone", f"Zone de prix acceptable des répondants : {eur(zl)} à {eur(zh)}", r=0))
    for t_ in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5):
        out.append(line(sx(t_), top - 4, sx(t_), yb, "grid")); out.append(txt(sx(t_), yb + 14, eur(t_), "m s", "middle"))
    for i, (lab, p, _, c) in enumerate(MARKET):
        y = top + i * rowh
        out.append(txt(x0 - 10, y + 17, lab, "t", "end"))
        out.append(rect(x0, y + 4, sx(p) - x0, 18, "fk" if c == "k" else "fn", f"{lab} : {eur(p)}"))
        out.append(txt(sx(p) + 6, y + 18, eur(p), "t b s"))
    out.append(txt(sx((zl + zh) / 2), yb + 32, f"zone grisée : prix acceptable selon nos répondants ({eur(zl)} à {eur(zh)})", "m s", "middle"))
    return svg(yb + 40, "".join(out), "Prix des produits concurrents en rayon")

def vw_svg():
    x0, x1, top, bot = 50, W - 20, 16, 250
    hi = 4.0; sx = lambda v: x0 + (x1 - x0) * v / hi; sy = lambda f: bot - (bot - top) * f
    v = an.vw["all"]; cv = v["curves"]; out = []
    for f in (0, 0.25, 0.5, 0.75, 1):
        out.append(line(x0, sy(f), x1, sy(f), "grid")); out.append(txt(x0 - 6, sy(f) + 4, pct(f), "m s", "end"))
    for t_ in range(0, 5):
        out.append(txt(sx(t_), bot + 16, eur(t_, 0), "m s", "middle"))
    zl, zh = v["PMC"], v["PME"]
    out.insert(0, rect(sx(zl), top, sx(zh) - sx(zl), bot - top, "zone", r=0))
    specs = [("tbm", "trop bon marché", "c-ch dashc"), ("bm", "bon marché", "c-ch"), ("ch", "cher", "c-ex"), ("tc", "trop cher", "c-ex dashc")]
    idx = [i for i, g in enumerate(an.GRID) if g <= hi]
    for key, lab, cls in specs:
        pts = " ".join(f"{sx(an.GRID[i]):.1f},{sy(cv[key][i]):.1f}" for i in idx[::5])
        out.append(f'<polyline points="{pts}" class="curve {cls}"/>')
    lx = x0
    for key, lab, cls in specs:
        out.append(f'<line x1="{lx}" y1="{bot + 40}" x2="{lx + 26}" y2="{bot + 40}" class="curve {cls}"/>')
        out.append(txt(lx + 32, bot + 44, lab, "m s")); lx += 32 + 6.4 * len(lab) + 22
    for k, lab in (("PMC", "PMC"), ("OPP", "OPP"), ("IPP", "IPP"), ("PME", "PME")):
        x = sx(v[k]); out.append(line(x, top, x, bot, "pt"))
    out.append(txt(sx(zh) + 6, top + 14, f"zone acceptable {eur(zl)} → {eur(zh)}", "t b s"))
    return svg(bot + 54, "".join(out), "Courbes de Van Westendorp, tous répondants")

def vwzone_svg():
    x0, x1, top, rowh = 140, W - 20, 30, 46
    lo, hi = 0.8, 2.0; sx = lambda v: x0 + (x1 - x0) * (v - lo) / (hi - lo); out = []
    rows = [("Version A · végétal", an.vw["A"], "fa"), ("Version B · animal", an.vw["B"], "fb"), ("Ensemble", an.vw["all"], "fk")]
    yb = top + rowh * len(rows)
    for t_ in (0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0):
        out.append(line(sx(t_), top - 10, sx(t_), yb - 10, "grid")); out.append(txt(sx(t_), yb + 4, eur(t_), "m s", "middle"))
    for i, (lab, v, cls) in enumerate(rows):
        y = top + i * rowh
        out.append(txt(x0 - 10, y + 12, lab, "t", "end"))
        out.append(rect(sx(v["PMC"]), y, sx(v["PME"]) - sx(v["PMC"]), 16, cls, f"{lab} : {eur(v['PMC'])} à {eur(v['PME'])}", r=8))
        out.append(f'<circle cx="{sx(v["OPP"]):.1f}" cy="{y + 8}" r="5" class="dot"><title>OPP {eur(v["OPP"])}</title></circle>')
        out.append(txt(sx(v["PMC"]) - 4, y + 30, eur(v["PMC"]), "m s", "end") + txt(sx(v["PME"]) + 4, y + 30, eur(v["PME"]), "m s"))
        out.append(txt(sx(v["OPP"]), y - 4, f"OPP {eur(v['OPP'])}", "m s", "middle"))
    return svg(yb + 12, "".join(out), "Zone de prix acceptable par version")

def gg_svg():
    x0, x1, top, bot = 50, W - 20, 30, 230
    sx = lambda p: x0 + (x1 - x0) * (p - 1.3) / (3.7 - 1.3); sy = lambda f: bot - (bot - top) * f
    out = [legend_ab()]
    for f in (0, 0.25, 0.5, 0.75, 1):
        out.append(line(x0, sy(f), x1, sy(f), "grid")); out.append(txt(x0 - 6, sy(f) + 4, pct(f), "m s", "end"))
    for p in an.GGP:
        out.append(txt(sx(p), bot + 16, eur(p), "m s", "middle"))
    for v, cls in (("A", "sa"), ("B", "sb")):
        pts = " ".join(f"{sx(r['price']):.1f},{sy(r['part']):.1f}" for r in an.ggt[v])
        out.append(f'<polyline points="{pts}" class="curve {cls}"/>')
        for r in an.ggt[v]:
            out.append(f'<circle cx="{sx(r["price"]):.1f}" cy="{sy(r["part"]):.1f}" r="4.5" class="{"fa" if v == "A" else "fb"} ring">'
                       f'<title>Version {v} à {eur(r["price"])} : {pct(r["part"])} achèteraient</title></circle>')
            out.append(txt(sx(r["price"]) + (7 if v == "A" else -7), sy(r["part"]) + (-7 if v == "A" else 14), pct(r["part"]), "m s", "start" if v == "A" else "end"))
    return svg(bot + 26, "".join(out), "Part des répondants qui achèteraient, à chaque prix")

def cost_svg(price):
    top, base_y, x0 = 34, 300, 64
    mx = 3.5; sy = lambda v: base_y - (base_y - top) * v / mx; out = []
    for t_ in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5):
        out.append(line(x0, sy(t_), W - 10, sy(t_), "grid")); out.append(txt(x0 - 8, sy(t_) + 4, eur(t_), "m s", "end"))
    out.append(line(x0, sy(an.CONC), W - 10, sy(an.CONC), "dash"))
    out.append(txt(W - 12, sy(an.CONC) - 7, f"plafond des concurrents : {eur(an.CONC)} (Humble+)", "t b s", "end"))
    bw = 120
    for i, v in enumerate("AB"):
        cx = x0 + 110 + i * 250; x = cx - bw / 2
        ttc = price; ht = ttc / (1 + an.TVA); net = ht * (1 - an.MARGE_DISTRIB); var = an.var_A if v == "A" else an.var_B
        cm = net - an.CVU[v]
        segs = [("produit de base", an.base_cost, "seg-base"), ("actif", var, "fa" if v == "A" else "fb"),
                ("marge producteur", cm, "seg-marge"), ("distributeur", ht - net, "seg-dist"), ("TVA", ttc - ht, "seg-tva")]
        acc = 0
        for lab, val, cls in segs:
            y1, y2 = sy(acc + val), sy(acc)
            out.append(rect(x, y1, bw, y2 - y1, cls, f"{lab} : {fr(val, 3)} €", r=0))
            if y2 - y1 > 15: out.append(txt(cx, (y1 + y2) / 2 + 4, f"{lab} {eur(val)}", "t s", "middle"))
            acc += val
        out.append(line(x - 8, sy(ttc), x + bw + 8, sy(ttc), ("sa" if v == "A" else "sb") + " pl"))
        out.append(txt(x + bw + 12, sy(ttc) + 4, f"prix {eur(ttc)}", "t b s"))
        out.append(txt(cx, base_y + 18, "Version " + v, "t b", "middle"))
        out.append(txt(cx, base_y + 34, "collagène végétal" if v == "A" else "collagène animal", "m s", "middle"))
    lx = x0
    for lab, cls in [("produit de base", "seg-base"), ("actif", "fa"), ("marge producteur", "seg-marge"), ("distributeur", "seg-dist"), ("TVA", "seg-tva")]:
        out.append(rect(lx, base_y + 48, 12, 12, cls, r=2)); out.append(txt(lx + 17, base_y + 58, lab, "m s")); lx += 17 + 6.6 * len(lab) + 14
    return svg(base_y + 68, "".join(out), "Ce que devient le prix d'une bouteille, par version")

def grouped_svg(cats, counts, label):
    top, base, x0 = 34, 190, 10
    n = len(cats); slot = (W - 2 * x0) / n; bw = min(34, slot * 0.3); out = [legend_ab()]
    out.append(line(x0, base, W - x0, base, "ax"))
    for i, c in enumerate(cats):
        cx = x0 + slot * (i + 0.5)
        for j, v in enumerate("AB"):
            N = nA if v == "A" else nB; p = counts[v][i] / N; h = (base - top - 18) * p; x = cx - bw - 1 + j * (bw + 2)
            out.append(rect(x, base - h, bw, h, "fa" if v == "A" else "fb", f"{c} · version {v} : {counts[v][i]} sur {N}"))
            out.append(txt(x + bw / 2, base - h - 6, pct(p), "m s", "middle"))
        out.append(txt(cx, base + 20, c, "t", "middle"))
    return svg(base + 30, "".join(out), label)

def pvalue_svg(rows):
    x0, x1, top, rowh = 300, W - 20, 26, 32
    sx = lambda p: x0 + (x1 - x0) * p; out = [rect(sx(0), top - 8, sx(0.05) - sx(0), rowh * len(rows) + 2, "zone", r=0)]
    out.append(txt(sx(0.05) + 5, top - 12, "seuil 0,05", "m s"))
    out.append(line(sx(0.05), top - 8, sx(0.05), top + rowh * len(rows) - 6, "thr"))
    for i, (lab, _, p, _) in enumerate(rows):
        y = top + i * rowh + 8
        out.append(txt(x0 - 12, y + 4, lab, "t", "end")); out.append(line(x0, y, x1, y, "grid"))
        out.append(f'<circle cx="{sx(p):.1f}" cy="{y}" r="6" class="dot"><title>{esc(lab)} : {fp(p)}</title></circle>')
        out.append(txt(sx(p) + (10 if p < 0.85 else -10), y - 8, fr(p, 3), "m s", "start" if p < 0.85 else "end"))
    yb = top + rowh * len(rows) + 4
    for v in (0, 0.25, 0.5, 0.75, 1): out.append(txt(sx(v), yb + 12, fr(v, 2), "m s", "middle"))
    out.append(txt(x0, yb + 28, "valeur de p (au-dessus de 0,05 : écart dû au hasard)", "m s"))
    return svg(yb + 36, "".join(out), "Comparabilité des deux groupes")

EXPL = {"bien_etre": "E1", "routine": "E2", "innovation": "E3"}
ALLW = ([dict(r, code=r["h"], lab=f"Seuil « {r['lab'].lower()} »") for r in an.prix] +
        [dict(r, code=r["h"] or EXPL[r["k"]]) for r in an.perc] +
        [dict(an.gg_first, code="E4", lab="Premier prix accepté (Q10)")])
def forest_svg():
    x0, x1, top, rowh = 300, W - 20, 30, 25
    lo, hi = -1.2, 1.4; sx = lambda v: x0 + (x1 - x0) * (v - lo) / (hi - lo); mde = an.prix[0]["mde"]
    yb = top + rowh * len(ALLW); out = [rect(sx(-mde), top - 10, sx(mde) - sx(-mde), yb - top + 2, "zone", r=0)]
    out.append(txt(sx(0), top - 14, f"zone trop petite pour être détectée (|d| < {fr(mde)})", "m s", "middle"))
    for t_ in (-1, -0.5, 0, 0.5, 1):
        out.append(line(sx(t_), top - 8, sx(t_), yb - 6, "ax" if t_ == 0 else "grid")); out.append(txt(sx(t_), yb + 8, fr(t_, 1), "m s", "middle"))
    for i, it in enumerate(ALLW):
        y = top + i * rowh + 6; sig = it["p2"] < 0.05 or it["p"] < 0.05
        out.append(txt(x0 - 12, y + 4, it["lab"], "t" if sig else "m", "end"))
        out.append(txt(4, y + 4, it["code"], "b " + ("t" if sig else "m")))
        out.append(line(sx(it["dlo"]), y, sx(it["dhi"]), y, "sk w"))
        out.append(f'<circle cx="{sx(it["d"]):.1f}" cy="{y}" r="5" class="{"dot" if sig else "hollow"}"><title>d = {fr(it["d"])}, {fp(it["p"])}</title></circle>')
    out.append(txt(sx(lo), yb + 26, "← plus haut en B (animal)", "m s"))
    out.append(txt(sx(hi), yb + 26, "plus haut en A (végétal) →", "m s", "end"))
    return svg(yb + 34, "".join(out), "Taille de tous les effets testés")

# ---------- numbers used in the text ----------
P_REC = 1.50
vA, vB = an.vw["A"], an.vw["B"]; vAll = an.vw["all"]
netA = an.net_producteur(P_REC); cmA = netA - an.CVU["A"]; cmB = netA - an.CVU["B"]
gA = {r["price"]: r for r in an.ggt["A"]}; gB = {r["price"]: r for r in an.ggt["B"]}
v7, v8, v9, v10, v11, v12, v14 = an.perc
dep = [r for r in an.rand if r[0].startswith("Dépense")][0]
RAND = [r for r in an.rand if r[0] != "Genre"]          # le genre ne fait pas l'objet du contrôle du tirage au sort
rand_other = min(r[2] for r in RAND if not r[0].startswith("Dépense"))
ages = [float(d["F3"]) for d in S]; age_m = sum(ages) / len(ages)
import collections
cnt = lambda k: collections.Counter(d[k] for d in S)
genre, regime, f1 = cnt("genre"), cnt("regime"), cnt("F1")

# Stress test (price 1,50 €, version A unless said)
def cm_A(tva=an.TVA, m=an.MARGE_DISTRIB, base_mult=1.0, var=None):
    var = an.var_A if var is None else var
    return an.net_producteur(P_REC, tva, m) - (an.base_cost * base_mult + var)
stress = [
    ("Scénario de base", cm_A(), "TVA 5,5 %, distributeur 30 %, coûts du tableau"),
    ("TVA à 20 % au lieu de 5,5 %", cm_A(tva=0.20), "hausse débattue au Parlement pour les bouteilles en plastique"),
    ("Distributeur à 40 % au lieu de 30 %", cm_A(m=0.40), "négociation commerciale moins favorable"),
    ("Coûts du produit de base doublés", cm_A(base_mult=2), "nos hypothèses sur l'embouteillage sont fausses du simple au double"),
    ("Les trois à la fois", cm_A(tva=0.20, m=0.40, base_mult=2), "cumul des trois chocs"),
]
m_break = 1 - an.CVU["A"] * (1 + an.TVA) / P_REC          # part distributeur qui annule la contribution
var_break = an.var_B                                        # coût des actifs végétaux à partir duquel A n'a plus d'avantage

def stress_svg():
    x0, x1, top, rowh = 250, W - 70, 8, 32
    sx = lambda v: x0 + (x1 - x0) * v / 1.0; out = []
    yb = top + rowh * len(stress)
    for t_ in (0, 0.25, 0.5, 0.75, 1.0):
        out.append(line(sx(t_), top - 4, sx(t_), yb, "ax" if t_ == 0 else "grid")); out.append(txt(sx(t_), yb + 14, eur(t_), "m s", "middle"))
    for i, (lab, v, _) in enumerate(stress):
        y = top + i * rowh
        out.append(txt(x0 - 10, y + 17, lab, "t", "end"))
        out.append(rect(x0, y + 4, sx(v) - x0, 18, "fk" if i == 0 else "fn", f"{lab} : {eur(v)} par bouteille"))
        out.append(txt(sx(v) + 6, y + 18, eur(v), "t b s"))
    out.append(txt(x0, yb + 32, "contribution par bouteille pour le producteur, version végétale vendue 1,50 €", "m s"))
    return svg(yb + 40, "".join(out), "Contribution par bouteille selon les scénarios")

# ---------- page blocks ----------
def verdict(it):
    if it["code"].startswith("E"):
        return "écart significatif" if it["p2"] < 0.05 else "pas d'écart"
    if it["p"] < 0.05: return "<strong>validée</strong>"
    if it["alt"] and it["p2"] < 0.05: return "<strong>rejetée : effet inverse</strong>"
    return "non validée"
HYP_TXT = {"H2": "L'origine végétale fait monter le seuil « trop cher »", "H3": "… le seuil « cher »", "H4": "… le seuil « bonne affaire »",
           "H5": "… le seuil « trop bon marché »", "H7": "L'origine végétale rend le produit plus conforme aux valeurs",
           "H8": "… plus cohérent avec l'image naturelle de l'eau", "H9": "L'origine animale inspire plus confiance dans l'efficacité",
           "H10": "L'origine animale donne une impression de qualité supérieure", "E1": "Bien-être (exploratoire)",
           "E2": "Consommation quotidienne (exploratoire)", "E3": "L'innovation justifie un prix plus élevé (exploratoire)", "E4": "Premier prix accepté (exploratoire)"}
REF = {"H7": "karahanna", "H8": "becker", "H9": "chaudhuri", "H10": "dodds"}
def hyp_table():
    rows = []
    for it in ALLW:
        unit = " €" if it["k"].startswith("P") or it["k"] == "GG_prix_accepte" else ""
        h = it["code"] + (f" · {L('source', REF[it['code']])}" if it["code"] in REF else "")
        pv = fp(it["p"]) + (" (unilatéral)" if it["alt"] else "")
        if it["alt"] == "B>A" and it["d"] > 0: pv = f"p bilatéral = {fr(it['p2'], 3)}"
        rows.append([f"<strong>{h}</strong>", HYP_TXT[it["code"]], fr(it["ma"]) + unit, fr(it["mb"]) + unit, pv, fr(it["d"]), verdict(it)])
    b6 = an.buy[0]
    rows.insert(4, ["<strong>H6</strong>", "L'origine végétale fait acheter plus à 3,50 € (chi², hors graphique)", pct(b6["na"] / nA), pct(b6["nb"] / nB),
                    fp(b6["p"]), f"V = {fr(b6['v'])}", "non validée"])
    return table(["Code", "Hypothèse", "A", "B", "p", "d", "Résultat"], rows, "hyp")

def calc_dec():
    ht = P_REC / (1 + an.TVA); net = an.net_producteur(P_REC)
    defs = ("<ul class='terms'>"
            f"<li><strong>TVA</strong> : taxe reversée à l'État, {L('5,5 % sur l\'eau', 'tva')}. Elle est comprise dans le prix en rayon.</li>"
            "<li><strong>Part du distributeur</strong> : ce que garde le supermarché qui revend la bouteille. Hypothèse : 30 % du prix hors taxe.</li>"
            "<li><strong>Prix net producteur</strong> : ce qui arrive réellement chez Volvic pour une bouteille.</li>"
            "<li><strong>Coût variable</strong> : ce que coûte la fabrication d'une bouteille (bouteille, bouchon, eau, transport et actif). Il diffère entre A et B à cause de l'actif.</li>"
            "<li><strong>Contribution</strong> : ce qui reste à Volvic une fois la bouteille payée. Elle sert d'abord à couvrir les coûts fixes (publicité, usine), puis devient du bénéfice.</li></ul>")
    rows = [("Prix en rayon", eur(P_REC), eur(P_REC)),
            ("− TVA (5,5 %)", "− " + eur(P_REC - ht), "− " + eur(P_REC - ht)),
            ("= Prix hors taxe", eur(ht), eur(ht)),
            ("− Part du distributeur (30 %)", "− " + eur(ht - net), "− " + eur(ht - net)),
            ("<strong>= Prix net producteur</strong>", f"<strong>{eur(net)}</strong>", f"<strong>{eur(net)}</strong>"),
            ("− Coût variable", f"− {fr(an.CVU['A'], 3)} €", f"− {fr(an.CVU['B'], 3)} €"),
            ("<strong>= Contribution par bouteille</strong>", f"<strong>{eur(cmA)}</strong>", f"<strong>{eur(cmB)}</strong>"),
            ("Taux de contribution (contribution ÷ prix net)", pct(cmA / net), pct(cmB / net)),
            ("Bouteilles pour couvrir 100 000 € de coûts fixes", fr(100000 / cmA, 0), fr(100000 / cmB, 0))]
    tr = "".join(f"<tr><td>{a}</td><td class='num ca'>{b}</td><td class='num cb'>{c}</td></tr>" for a, b, c in rows)
    return (f"<details class='calc'><summary>Construction du calcul · contribution par bouteille vendue 1,50 €</summary>{defs}"
            f"<div class='tw'><table class='wf'><thead><tr><th></th><th class='ca'>A · végétal</th><th class='cb'>B · animal</th></tr></thead><tbody>{tr}</tbody></table></div>"
            f"<p class='cnote'>Les deux versions se vendent au même prix ; seule la ligne « coût variable » diffère. A garde donc {fr(cmA - cmB, 3)} € de plus par bouteille. Les coûts fixes de Danone ne sont pas publics : le seuil est donné pour 100 000 €.</p></details>")

def calc(title, rows, note="", head=("Terme", "D'où il vient", "Valeur")):
    tr = "".join(f"<tr><td>{a}</td><td>{b}</td><td class='num'>{c}</td></tr>" for a, b, c in rows)
    n = f"<p class='cnote'>{note}</p>" if note else ""
    th = "".join(f"<th>{h}</th>" for h in head)
    return f"<details class='calc'><summary>Construction du calcul · {title}</summary><div class='tw'><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>{n}</details>"

def calc_ab(title, rows_a, rows_b, total_rows, note=""):
    def t(rows): return "".join(f"<tr><td>{a}</td><td>{b}</td><td class='num'>{c}</td></tr>" for a, b, c in rows)
    tot = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in total_rows)
    n = f"<p class='cnote'>{note}</p>" if note else ""
    return (f"<details class='calc'><summary>Construction du calcul · {title}</summary><div class='ab'>"
            f"<div class='colA'><h5>Version A · collagène végétal</h5><div class='tw'><table><tbody>{t(rows_a)}</tbody></table></div></div>"
            f"<div class='colB'><h5>Version B · collagène animal</h5><div class='tw'><table><tbody>{t(rows_b)}</tbody></table></div></div></div>"
            f"<div class='tw'><table class='tot'><thead><tr><th></th><th>A · végétal</th><th>B · animal</th></tr></thead><tbody>{tot}</tbody></table></div>{n}</details>")

def table(head, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<div class='tw'><table class='{cls}'><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>"

def fig(chart, caption, cls=""): return f"<figure class='reveal {cls}'>{chart}<figcaption>{caption}</figcaption></figure>"

def answer(text): return f"<p class='answer reveal'><span>En bref</span>{text}</p>"

sec = {}

sec["entreprise"] = f"""
{answer(f"Volvic est une marque d'eau minérale de Danone, exploitée par la Société des Eaux de Volvic. Elle vit de la vente d'eau embouteillée, et ses comptes sont solides : {L('547 M€ de chiffre d\'affaires en 2024', 'sev_jde')} et {L('45 M€ de bénéfice', 'sev_jde')}.")}
<h3>Qui est-elle ?</h3>
<p>Volvic est une eau minérale naturelle puisée dans le massif volcanique d'Auvergne ({L('présentation de la marque par Danone', 'volvic')}). La marque appartient au groupe Danone, qui a réalisé {L('27,28 milliards d\'euros de chiffre d\'affaires en 2025', 'danone')} dans les produits laitiers, la nutrition spécialisée et les eaux. En France, Danone détient {L('plus de 30 % du marché de l\'eau en bouteille', 'lsa')} avec Evian, Volvic, Badoit et La Salvetat. Volvic pèse environ {L('10 % du marché en valeur, derrière Evian (17 %)', 'agra')} ; ce chiffre de part de marché n'est pas daté par sa source. Volvic est {L('certifiée B Corp', 'bcorp')}, un label qui récompense les engagements sociaux et environnementaux.</p>
<h3>De quoi vit-elle ?</h3>
<p>De la vente de bouteilles d'eau, nature ou aromatisée, en grande surface et en magasin de proximité. C'est une activité de volume et de saison : pour Danone Eaux France, {L('juin à septembre représentent 40 % des volumes annuels', 'lsa')}. Le prix unitaire est bas : une bouteille de Volvic nature de 50 cl se vend environ {L(eur(2.99 / 6) + " (pack de 6 à 2,99 €)", 'volvic_prix')}.</p>
<h3>Que disent ses comptes ?</h3>
{table(["Société des Eaux de Volvic", "2023", "2024", "Source"], [
    ["Chiffre d'affaires", "515,5 M€", "547,0 M€", L("Le Journal des Entreprises", "sev_jde")],
    ["Résultat net", "23,0 M€", "45,0 M€", L("Le Journal des Entreprises", "sev_jde")],
    ["Résultat d'exploitation", "", "69 M€", L("Xerfi", "sev_xerfi")]])}
{calc("ce que disent ces chiffres", [
    ["Croissance du chiffre d'affaires", "(547,0 − 515,5) ÷ 515,5", "+6,1 %"],
    ["Marge nette 2024", "45,0 ÷ 547,0", "8,2 %"],
    ["Marge d'exploitation 2024", "69 ÷ 547,0", "12,6 %"],
    ["Repère groupe : marge opérationnelle courante de Danone 2025", L("communiqué de résultats Danone", "danone"), "13,4 %"]],
    "La filiale grandit et gagne de l'argent : sa rentabilité d'exploitation est proche de celle du groupe. Elle a les moyens de lancer une nouvelle référence.")}
"""

sec["marche"] = f"""
{answer(f"Une eau au collagène n'a qu'un concurrent direct en France dans nos recherches : Humble+, vendue {L('2,99 € la canette de 33 cl', 'humble_prix')}. C'est notre plafond. Autour, les eaux aromatisées et vitaminées se vendent entre 1 et 2,50 €.")}
<h3>Les concurrents et leurs prix</h3>
<p>Une eau Volvic au collagène se situerait entre l'eau nature et les boissons « santé ». Nous avons relevé les prix des produits les plus proches :</p>
{table(["Produit", "Format", "Prix", "Prix pour 50 cl", "Source"], [
    ["Volvic nature", "50 cl (pack de 6)", "2,99 € le pack", eur(2.99 / 6), L("houra.fr", "volvic_prix")],
    ["Volvic Essentiel Bio (eau aromatisée)", "75 cl", "1,75 € (prix promo)", eur(1.75 / 1.5), L("Bonial, Carrefour", "essentiel")],
    ["Vitamin Well (eau vitaminée)", "50 cl", "2,55 €", eur(2.55), L("Fitadium", "vitwell")],
    ["Humble+ Collagen Water (5 g de collagène marin)", "33 cl", "2,99 €", eur(2.99 / 0.66), L("Je vais mieux merci", "humble_prix") + ", " + L("Atida", "humble_dose")]])}
{fig(market_svg(), cls="key", caption="Prix en rayon d'une unité. La bande grisée est la zone de prix que nos répondants jugent acceptable (Van Westendorp, voir « Le client »).")}
<h3>Quel plafond en tirer ?</h3>
<p>Le plafond est le prix du concurrent le plus proche et le plus cher : <strong>{eur(an.CONC)} pour Humble+</strong>, la seule eau au collagène trouvée en vente en France. Au-dessus, le consommateur trouve une offre comparable moins chère.</p>
"""

sec["proposition"] = f"""
{answer(f"Nous testons l'origine du collagène : <strong>végétale</strong> (version A, la variation) contre <strong>animale</strong> (version B, la formule standard du marché). La variation ne coûte pas plus cher, elle coûte moins : environ {fr(an.var_A, 3)} € d'actifs végétaux par bouteille, contre {fr(an.var_B, 3)} € de collagène bovin.")}
<h3>Quelle variation, et pourquoi celle-là ?</h3>
<p>Les eaux au collagène du marché utilisent du collagène animal, comme Humble+ et ses {L('5 g de collagène marin', 'humble_dose')}. Notre variation est un collagène <strong>d'origine végétale</strong>. {L('Il n\'existe pas à proprement parler', 'vegan')} : ce sont des nutriments végétaux, comme la vitamine C, qui aident le corps à fabriquer son propre collagène.</p>
{fig(th.collagen_svg(), f"Le collagène est une protéine en triple hélice, présente seulement chez les animaux. La version B en apporte directement ; la version A apporte des nutriments végétaux, comme la vitamine C, qui {L('contribue à la formation normale de collagène', 'allegation')}.", "paint")}
<p>Pourquoi celle-là : elle oppose l'éthique et le naturel au « vrai » collagène, réputé plus efficace, et elle colle à l'image naturelle de Volvic. Seule l'origine change entre les deux versions.</p>
{fig(th.mindmap_svg([
    ("Éthique et valeurs", "aucun ingrédient animal", f"valeurs : {fr(v7['ma'])} contre {fr(v7['mb'])} sur 7", "→ confirmé (H7)"),
    ("Image naturelle", "une eau de volcan, B Corp", f"cohérence : {fr(v8['ma'])} contre {fr(v8['mb'])} sur 7", "→ confirmé (H8)"),
    ("Coût", f"actifs végétaux : {fr(an.var_A, 3)} €", f"collagène bovin : {fr(an.var_B, 3)} €", f"→ {fr(an.var_B / an.var_A, 0)} fois moins cher"),
    ("Le risque", "le « vrai » collagène", "jugé plus efficace ?", "→ non : plus de confiance (H9)")]),
    "Pourquoi le collagène végétal : les quatre arguments du choix, et ce que l'étude en a dit (détail dans « Qui a répondu »).", "paint key")}
<figure class="duo"><img src="../img/bouteille_vegetal.jpg" alt="Bouteille version A, collagène 100 % végétal"><img src="../img/bouteille_animal.jpg" alt="Bouteille version B, collagène d'origine animale"><figcaption>Les deux visuels montrés aux répondants. Version A : « Eau minérale naturelle enrichie en collagène d'origine végétale. 50 cl. » Version B : « … d'origine animale. » Les étiquettes diffèrent aussi par leur couleur, une limite à garder en tête.</figcaption></figure>
<h3>Combien coûte-t-elle ?</h3>
<p>Danone ne publie pas ses coûts. Nous avons chiffré chaque poste avec un prix de gros public quand il existe, et une hypothèse signalée sinon.</p>
{calc("produit de base, commun aux deux versions", [
    ["Bouteille en plastique 50 cl", f"{L('préforme à 2,5 à 4 cents de dollar', 'preforme')}, arrondi pour du plastique recyclé", "0,04 €"],
    ["Bouchon et étiquette", "hypothèse", "0,02 €"],
    ["Eau, mise en bouteille, énergie", "hypothèse", "0,03 €"],
    ["Transport jusqu'au magasin", "hypothèse", "0,05 €"],
    ["<strong>Total</strong>", "", f"<strong>{eur(an.base_cost)}</strong>"]], head=("Poste", "D'où vient le chiffre", "Coût"))}
{calc_ab("l'actif, différent pour A et pour B",
    [["Vitamine C", f"{fr(an.vitc_kg)} €/kg ({L('3,03 $/kg', 'vitc')}) × 80 mg", fr(an.vitc_kg * 0.080 / 1000, 4) + " €"],
     ["Extrait de bambou", f"{fr(an.bamb_kg)} €/kg ({L('42 à 48 $/kg', 'bambou')}) × 100 mg", fr(an.bamb_kg * 0.100 / 1000, 4) + " €"],
     ["<strong>Actif A</strong>", "", f"<strong>{fr(an.var_A, 3)} €</strong>"]],
    [["Collagène bovin", f"{fr(an.coll_kg)} €/kg ({L('20,5 à 26,5 $/kg', 'collagene')}) × 5 g", fr(an.var_B, 3) + " €"],
     ["<strong>Actif B</strong>", "", f"<strong>{fr(an.var_B, 3)} €</strong>"]],
    [["Coût variable par bouteille", f"{eur(an.base_cost)} + {fr(an.var_A, 3)} € = <strong>{fr(an.CVU['A'], 3)} €</strong>", f"{eur(an.base_cost)} + {fr(an.var_B, 3)} € = <strong>{fr(an.CVU['B'], 3)} €</strong>"]],
    f"Doses : 80 mg de vitamine C et 100 mg de bambou comme {L('un complément « vegan collagen »', 'swanson')} ; 5 g de collagène comme {L('Humble+', 'humble_dose')}. Dollars convertis à 0,90 €. Le collagène coûte cher au poids ; les nutriments qui aident à le fabriquer, presque rien.")}
"""

sec["client"] = f"""
{answer(f"Le client accepte environ <strong>1,50 €</strong> la bouteille, quelle que soit l'origine du collagène. Zone acceptable de {eur(vA['PMC'])} à {eur(vA['PME'])} avec la variation végétale, de {eur(vB['PMC'])} à {eur(vB['PME'])} sans. La variation ne change pas le prix accepté.")}
<p>Nous avons mesuré le prix accepté de deux façons, sur les {nS} répondants (voir « Qui a répondu » plus haut) :</p>
<ul class="def"><li><strong>Van Westendorp</strong> : chacun indique, sur un curseur, à partir de quel prix il trouve le produit trop bon marché, bon marché, cher, puis trop cher (Q6 à Q9). En croisant les réponses de tous, on obtient une zone de prix acceptable.</li>
<li><strong>Gabor-Granger</strong> : on propose des prix du plus cher (3,50 €) au moins cher (1,50 €), et chacun dit s'il achèterait (Q10). On obtient la part d'acheteurs à chaque prix.</li></ul>
<h3>Van Westendorp</h3>
{fig(vw_svg(), f"Part des répondants ({nS}) qui jugent chaque prix trop bon marché, bon marché, cher ou trop cher. Les croisements de courbes donnent quatre points ; la zone grisée va du PMC au PME.")}
{table(["Point", "Croisement", "Ce qu'il signifie", "Ensemble", "A · végétal", "B · animal"], [
    ["PMC", "trop bon marché × cher", "bas de la zone", eur(vAll["PMC"]), eur(vA["PMC"]), eur(vB["PMC"])],
    ["OPP", "trop bon marché × trop cher", "prix qui fait le moins de rejets", eur(vAll["OPP"]), eur(vA["OPP"]), eur(vB["OPP"])],
    ["IPP", "bon marché × cher", "prix perçu comme normal", eur(vAll["IPP"]), eur(vA["IPP"]), eur(vB["IPP"])],
    ["PME", "bon marché × trop cher", "haut de la zone", eur(vAll["PME"]), eur(vA["PME"]), eur(vB["PME"])]])}
{fig(vwzone_svg(), cls="key", caption="Zone de prix acceptable (du PMC au PME) et prix optimal (OPP) pour chaque version. Les zones se recouvrent presque entièrement.")}
<p>Les courbes se comparent à l'œil ; la différence entre versions se teste sur les réponses de chaque répondant (voir « Ce que permettent de conclure les réponses »). Aucun des quatre seuils ne diffère significativement entre A et B.</p>
<h3>Gabor-Granger</h3>
{fig(gg_svg(), "Part des répondants de chaque version qui achèteraient au prix indiqué. Un répondant achète à un prix s'il a dit oui à ce prix ou à un prix plus élevé.")}
"""

c1 = an.c1
rand_rows = [[r[0], r[1], fp(r[2])] for r in an.rand]
sec["repondants"] = f"""
{answer(f"{nS} vraies réponses complètes ({nA} en version végétale, {nB} en version animale), surtout de jeunes adultes ({fr(age_m, 1)} ans en moyenne). Les répondants ont bien vu la différence, et elle change leurs <strong>perceptions</strong> (valeurs, image naturelle, confiance), pas leurs <strong>prix</strong>.")}
<h3>Qui a répondu ?</h3>
<p>Le {L('questionnaire en ligne', 'questionnaire')} a été diffusé du 20 octobre au 12 novembre 2026. Chaque répondant voyait une seule version, tirée au sort. Les réponses brutes sont publiées dans {L('le fichier de données', 'donnees')} et tous les calculs dans {L('le script d\'analyse', 'code')}.</p>
{fig(th.ab_svg(nA, nB), "Le principe du test A/B : le hasard décide de la version vue. Les deux groupes ne diffèrent que par l'origine du collagène, donc un écart entre eux vient de là.", "paint key")}
<figure>{funnel_svg()}</figure>
{table(["Profil", "Répartition"], [
    ["Âge moyen", f"{fr(age_m, 1)} ans (de {int(min(ages))} à {int(max(ages))} ans)"],
    ["Genre", ", ".join(f"{k} : {v}" for k, v in genre.most_common())],
    ["Régime alimentaire", ", ".join(f"{k} : {v}" for k, v in regime.most_common())],
    ["A acheté de l'eau en bouteille ces 3 derniers mois", f"{f1['Oui']} sur {nS}"]])}
<p>Un échantillon jeune et surtout omnivore : il ne représente pas tous les acheteurs d'eau, et il ne permet pas de comparer les régimes (trop peu de végétariens et de végans).</p>
<h3>Que permettent de conclure les réponses ?</h3>
<h4>1. Les répondants ont-ils vu la différence ? Oui.</h4>
{fig(grouped_svg(an.C1CATS, c1, "Origine du collagène retenue par version"), "Q5 : « D'après la description, quelle est l'origine du collagène ? » en % de chaque version.")}
<p><strong>La manipulation a fonctionné :</strong> {pct(c1['A'][0] / nA)} des répondants de la version végétale retiennent une origine végétale, et {pct(c1['B'][1] / nB)} de ceux de la version animale une origine animale (chi² = {fr(an.manip['chi'])}, {an.manip['dof']} ddl, {fp(an.manip['p'])}, V de Cramer = {fr(an.manip['v'])}). Un test A/B sans effet peut donc être lu comme un vrai résultat, et non comme un test raté.</p>
<h4>2. Le tirage au sort a-t-il donné deux groupes comparables ? Oui, sauf sur un point.</h4>
{fig(pvalue_svg(RAND), "Comparaison des profils des deux groupes. Un point à droite du seuil : pas de différence.")}
<p>Âge, régime et habitudes d'achat sont comparables (toutes les valeurs de p sont au moins de {fr(rand_other, 3)}). <strong>Exception : la dépense habituelle pour une bouteille</strong> ({fp(dep[2])}). {an.dep3['tab'][1][0]} répondants de la version animale dépensent moins de 0,50 €, contre {an.dep3['tab'][0][0]} en version végétale. Cette différence se signale et se garde en tête : un groupe qui dépense moins pourrait déclarer des prix plus bas.</p>
<h4>3. La version change-t-elle les réponses ?</h4>
{fig(forest_svg(), cls="key", caption="Chaque ligne est un test de Welch, repérée par le même code que dans le tableau dessous. Le point est la taille de l'écart entre A et B (d de Cohen), le trait son intervalle de confiance. Point plein : écart significatif. E = question exploratoire, sans hypothèse.")}
{hyp_table()}
<p class="note">Perceptions notées de 1 à 7, sur l'échelle de l'article de référence de chaque concept ({L('détail des échelles', 'sources_echelles')}). Pour les seuils de prix, l'étude ne pouvait détecter qu'un écart d'au moins d ≈ {fr(an.prix[0]['mde'])} : un effet plus petit reste possible.</p>
<p><strong>Ce que nous concluons :</strong> l'origine végétale est un argument d'image. Elle rend le produit plus conforme aux valeurs, plus cohérent avec une eau naturelle, et, contre notre attente, plus digne de confiance. Elle ne fait pas payer plus cher.</p>
"""

sec["decision"] = f"""
{answer(f"Nous recommandons la <strong>version végétale à 1,50 €</strong> la bouteille de 50 cl. La variation se paie, par le coût et non par le prix. Le scénario lâche si le prix dépasse environ {eur(vA['PME'])}, ou si la recette végétale coûtait plus de {fr(var_break, 3)} € par bouteille.")}
<h3>Quel prix recommandons-nous ? 1,50 €</h3>
<ul class="def">
<li>C'est le <strong>prix perçu comme normal</strong> par nos répondants (IPP de Van Westendorp : {eur(vAll['IPP'])}).</li>
<li>Il est <strong>dans la zone acceptable</strong> de la version végétale ({eur(vA['PMC'])} à {eur(vA['PME'])}).</li>
<li>Il donne la <strong>marge par répondant la plus forte</strong> de Gabor-Granger : {eur(gA[P_REC]['marge'])} en version végétale.</li>
<li>Il reste <strong>deux fois sous le plafond</strong> des concurrents ({eur(an.CONC)}) et trois fois au-dessus de Volvic nature ({eur(2.99 / 6)}).</li></ul>
<p class="note">Limite : 1,50 € est le prix le plus bas proposé en Q10. Le vrai optimum pourrait être un peu plus bas ; le prix optimal de Van Westendorp, {eur(vA['OPP'])} en version végétale, le suggère.</p>
<h3>La variation se paie-t-elle ? Oui, par le coût.</h3>
{fig(cost_svg(P_REC), cls="key", caption="Ce que devient 1,50 € payé en rayon, pour chaque version. L'actif végétal est presque invisible : il coûte moins d'un demi-centime.")}
{calc_dec()}
<p>La version végétale ne se vend pas plus cher, mais elle coûte environ {fr(an.var_B - an.var_A, 2)} € de moins à produire, et elle améliore l'image du produit. Elle rapporte donc plus par bouteille, à prix égal.</p>
<h3>À quel moment le scénario lâche-t-il ?</h3>
{fig(stress_svg(), "Contribution par bouteille de la version végétale vendue 1,50 €, quand on dégrade nos hypothèses.")}
<p>La rentabilité unitaire résiste à tous les chocs testés : même en cumulant une TVA à 20 % ({L('hausse débattue au Parlement', 'tva20')}), un distributeur plus gourmand et des coûts doublés, il reste {eur(stress[-1][1])} par bouteille. Le scénario lâche ailleurs :</p>
<ul class="def">
<li><strong>Si le prix dépasse environ {eur(vA['PME'])}</strong> : au-delà du PME, les répondants jugeant le produit trop cher deviennent plus nombreux que ceux qui le trouvent bon marché. À 1,90 €, la part d'acheteurs tombe de {pct(gA[1.5]['part'])} à {pct(gA[1.9]['part'])}.</li>
<li><strong>Si la recette végétale coûtait plus de {fr(var_break, 3)} € par bouteille</strong>, soit environ {fr(var_break / an.var_A, 0)} fois notre estimation : l'avantage de coût sur le collagène animal disparaîtrait, et rien ne compense, puisque le prix accepté est le même.</li>
<li><strong>Si le distributeur prenait plus de {pct(m_break)} du prix hors taxe</strong> : la contribution deviendrait nulle. C'est très improbable.</li>
<li><strong>Si les intentions d'achat sont surestimées</strong>, ce qui est le cas de toute intention déclarée : la marge par répondant baisse d'autant, mais la comparaison entre les versions ne change pas.</li>
<li><strong>Si l'allégation ne tenait pas</strong> : le produit ne contient pas de collagène, il ne peut pas l'afficher comme tel. Il devra s'appuyer sur l'{L('allégation autorisée pour la vitamine C', 'allegation')}, ce qui affaiblit le nom « collagène végétal » testé ici.</li></ul>
"""

sec["methode"] = f"""
<p>Les termes utilisés dans ce dossier, pour qui n'a pas suivi le cours :</p>
<dl class="gloss">
<dt>Test A/B</dt><dd>Deux groupes tirés au sort voient chacun une version ; seule l'origine du collagène change. Un écart entre groupes vient donc de cette différence.</dd>
<dt>Valeur de p</dt><dd>Probabilité d'observer un écart au moins aussi grand si, en réalité, il n'y avait aucune différence. Sous 0,05, on parle d'écart « significatif ».</dd>
<dt>Test de Welch</dt><dd>Compare deux moyennes (un prix, une note). Unilatéral quand l'hypothèse annonce un sens.</dd>
<dt>Chi²</dt><dd>Compare deux répartitions (oui/non, choix multiples).</dd>
<dt>d de Cohen, V de Cramer</dt><dd>Tailles d'effet : disent si un écart est petit ou grand. d : 0,2 petit, 0,5 moyen, 0,8 grand. V : de 0 à 1.</dd>
<dt>Contrôle de manipulation</dt><dd>Vérifie que les répondants ont bien perçu la différence entre les versions.</dd>
<dt>Contribution marginale</dt><dd>Ce qui reste par bouteille une fois payés les coûts de fabrication ; elle couvre les coûts fixes puis fait le bénéfice.</dd>
</dl>
<h3>Limites</h3>
<ul class="def">
<li>Échantillon de {nS} répondants, jeune, recruté par le réseau du groupe : pas représentatif des acheteurs d'eau.</li>
<li>Les deux bouteilles diffèrent aussi par la couleur de leur étiquette (vert contre rose).</li>
<li>Question de contrôle à choix, posée avant les prix ; pas de contrôle d'attention ; membres du M1 non identifiables.</li>
<li>Prix déclarés, pas observés en magasin ; 1,50 € est le prix le plus bas testé en Gabor-Granger.</li>
<li>Coûts : prix de gros affichés par des fournisseurs, pas des devis ; plusieurs postes sont des hypothèses signalées.</li>
</ul>
"""

NAV = [("entreprise", "L'entreprise"), ("marche", "Le marché"), ("proposition", "La proposition"),
       ("repondants", "Qui a répondu"), ("client", "Le client"), ("decision", "La décision")]
QUESTIONS = {"entreprise": "Qui est-elle, de quoi vit-elle, et que disent ses comptes ?",
             "marche": "Qui sont ses concurrents, à quels prix, et quel plafond en tirer ?",
             "proposition": "Quelle variation du mix, pourquoi celle-là, et combien coûte-t-elle ?",
             "client": "Quel prix accepte-t-il, avec et sans la variation ?",
             "repondants": "Qui a répondu, et que permettent de conclure les réponses ?",
             "decision": "Quel prix recommandons-nous, la variation se paie-t-elle, et à quel moment le scénario lâche-t-il ?",
             "methode": "Comment lire ce dossier"}

def read_min(h):
    words = len(re.sub(r"<[^>]+>", " ", h).split())
    return max(1, round(words / 180))

def next_link(i):
    if i + 1 < len(NAV):
        k, t = NAV[i + 1]
        return f"<p class='next'><a href='#{k}'>Suite : {i + 2:02d} · {t} <span aria-hidden='true'>↓</span></a></p>"
    return "<p class='next'><a href='#carte'>Revenir au plan <span aria-hidden='true'>↑</span></a></p>"

sections_html = "".join(
    f"<section id='{k}'><header class='sh'><span class='kicker'>{i + 1:02d} · {t}</span><h2>{QUESTIONS[k]}</h2>"
    f"<span class='rt'>Lecture : environ {read_min(sec[k])} min · l'essentiel en 30 secondes dans « En bref »</span></header>{sec[k]}"
    f"<p class='ess-note'>Mode « l'essentiel » : les détails et les calculs de cette partie sont masqués.</p>{next_link(i)}</section>"
    for i, (k, t) in enumerate(NAV))

carte = f"""<div class="carte reveal" id="carte"><p class="eyebrow">Le dossier en un coup d'œil</p>
<h2>Six questions, six réponses courtes</h2>
<p class="rt">Cliquez sur une bulle pour aller à la partie. Elles se lisent dans l'ordre, de 01 à 06.</p>
{th.sitemap_svg(("Quel prix pour", "Volvic Boost ?"), [
    ("entreprise", "01", "L'entreprise", "Volvic, filiale de Danone", "45 M€ de bénéfice en 2024"),
    ("marche", "02", "Le marché", "un seul concurrent direct", f"Humble+ à {eur(an.CONC)}"),
    ("proposition", "03", "La proposition", "collagène végétal (A)", "contre animal (B)"),
    ("repondants", "04", "Qui a répondu", f"{nS} répondants", "le végétal change l'image"),
    ("client", "05", "Le client", "accepte environ 1,50 €", f"zone {fr(vA['PMC'])} – {eur(vA['PME'])}"),
    ("decision", "06", "La décision", "végétal à 1,50 €", f"+{fr(cmA - cmB, 2)} € par bouteille")])}
</div>"""

comfort = """<div class="comfort"><div class="panel" id="comfort-panel" hidden role="group" aria-label="Confort de lecture">
<label><input type="checkbox" data-mode="dys"> Police adaptée dys<small>Police plus lisible, lettres et lignes plus espacées, sans italique ni majuscules.</small></label>
<label><input type="checkbox" data-mode="calm"> Sans animations<small>Tout s'arrête : rien ne bouge ni ne clignote.</small></label>
<label><input type="checkbox" data-mode="essentiel"> L'essentiel seulement<small>Garde la réponse « En bref » et un schéma par partie ; masque les détails.</small></label>
</div><button type="button" id="comfort-btn" aria-expanded="false" aria-controls="comfort-panel" aria-label="Confort de lecture">Aa<span class="cf-l"> · Confort de lecture</span></button></div>"""

head_js = """<script>(function(){var r=document.documentElement;['dys','calm','essentiel'].forEach(function(m){try{var x=localStorage.getItem('cf-'+m);if(x==='1'||(x===null&&m==='calm'&&matchMedia('(prefers-reduced-motion: reduce)').matches))r.classList.add(m);}catch(e){}});})();</script>"""
nav_html = "".join(f"<a href='#{k}'>{t}</a>" for k, t in NAV)

hero = th.hero(
    "Dossier Prix · M1 Marketing · IAE Clermont Auvergne",
    "Volvic Boost, <em>soutien collagène</em>",
    "Végétal ou animal : lequel le consommateur paie-t-il plus cher ?",
    f"Nous avons imaginé une eau Volvic enrichie en collagène, testé deux versions auprès de {nS} répondants, puis confronté le prix accepté aux coûts et aux concurrents. Suivez l'eau : elle descend de la source jusqu'à la décision.",
    [("Prix recommandé", "1,50 €", "la bouteille de 50 cl, version végétale", "1.50"),
     ("Zone acceptable", f"{fr(vA['PMC'])} – {eur(vA['PME'])}", "Van Westendorp, version végétale", ""),
     ("Effet du végétal sur le prix", "aucun", "seuils identiques entre A et B", ""),
     ("Gain par bouteille", f"+{fr(cmA - cmB, 2)} €", "l'actif végétal coûte moins cher", f"{cmA - cmB:.2f}")],
    "Étude universitaire, non affiliée à la marque Volvic ni au groupe Danone. Le film et les bouteilles sont des maquettes réalisées pour l'étude.")

finale = f"""<div class="finale reveal"><div class="fr">{th.mountains(1600, 300, "range")}</div>
<p>De la source à la bouteille : la version végétale, à 1,50 €, plaît pour ses valeurs et coûte moins cher à produire.</p></div>"""



page = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Volvic Boost · Dossier Prix</title>
<meta name="description" content="Dossier Prix, M1 Marketing IAE Clermont Auvergne : prix accepté d'une eau Volvic au collagène végétal contre animal.">
<meta name="theme-color" content="#0f5a36">
{th.FONTS}
<style>{th.CSS}</style>{head_js}</head>
<body>
{th.SVG_DEFS}
<nav class="topnav" aria-label="Sections"><div class="in"><strong>Volvic Boost · Dossier Prix</strong>{nav_html}</div><div class="progress"></div></nav>
{hero}
<div class="flowwrap"><svg class="river" aria-hidden="true"></svg>
<main>
{carte}
{sections_html}
{finale}
<p class="foot">Étude universitaire, M1 Marketing, IAE Clermont Auvergne. Non affiliée à la marque Volvic ni au groupe Danone. Le film publicitaire et les visuels de bouteille sont des maquettes réalisées pour l'étude. Données : {L('réponses au questionnaire', 'donnees')}, export du 23 novembre 2026. Calculs : {L('script d\'analyse', 'code')}.</p>
</main></div>
{comfort}
<script>{th.JS}</script>
</body></html>"""
OUT.write_text(page, encoding="utf-8")
print("ok", OUT, len(page) // 1024, "Ko")
