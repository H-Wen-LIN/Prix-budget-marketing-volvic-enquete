"""Produit le site du dossier Prix en récit (dossier/index.html) et, hors site, l'annexe détaillée (dossier/hors-site/annexe.html).

Lancer : python3 dossier/build.py        puis, pour le PDF : node dossier/pdf.mjs
Principes du récit : une idée par scène (titre = l'affirmation, visuel = la preuve, deux phrases),
3 ou 4 scènes par chapitre (environ 3 minutes à l'oral), une question au début, « Ce qu'on retient » à la fin.
Tout ce qui est retiré du récit (tableaux, calculs, tests, sources) est dans l'annexe, qui n'est pas publiée sur le site
(dossier/hors-site/ est ignoré par Git).
"""
import pathlib
import re
import contenu as c
import analyse as an
import theme as th

HERE = pathlib.Path(__file__).resolve().parent
fr, eur, pct, L, esc = c.fr, c.eur, c.pct, c.L, c.esc
nA, nB, nS = c.nA, c.nB, c.nS
vA, vB, vAll = c.vA, c.vB, c.vAll
gA, gB = c.gA, c.gB
v7, v8, v9, v10 = c.v7, c.v8, c.v9, c.v10
P = c.P_REC
ratio = an.var_B / an.var_A
c1 = an.c1


# ---------- briques du récit ----------
def scene(n, total, claim, evidence, say, src=""):
    s = f"<p class='src'>Sources : {src}</p>" if src else ""
    return (f"<article class='scene'><h3 class='claim'>{claim}</h3>"
            f"<div class='evidence'>{evidence}</div><p class='say'>{say}</p>{s}</article>")


def chapter(i, key, title, stage, promise, scenes, recap, bridge):
    total = len(scenes)
    body = "".join(scene(j + 1, total, *sc) for j, sc in enumerate(scenes))
    br = f"<p class='bridge'>{bridge}</p>" if bridge else ""
    return (f"<section id='{key}' class='chapter'><header class='opener'><div class='ot'><span class='kicker'>{i:02d} · {title}</span>"
            f"<p class='stage'>{stage}</p><h2>{c.QUESTIONS[key]}</h2><p class='promise'>{promise}</p></div>"
            f"<div class='ill'>{th.vignette(VIG[key])}</div></header>"
            f"{body}<aside class='recap'>{th.ripple()}<span>Ce qu'on retient</span><p>{recap}</p>{br}</aside></section>")


VIG = {"entreprise": "source", "marche": "vallee", "proposition": "idee", "repondants": "test", "client": "verdict", "decision": "bouteille"}


def tiles(items, cls=""):
    return f"<div class='tiles {cls}'>" + "".join(
        f"<div class='tile {k}'><span class='tk'>{a}</span><span class='tv'>{b}</span><span class='ts'>{d}</span></div>"
        for a, b, d, k in items) + "</div>"


# ---------- visuels propres au récit ----------
def dumbbell(rows, lo, hi, ticks, unit, label, title):
    W = c.W; x0, x1, top, rowh = 270, W - 30, 38, 50
    sx = lambda v: x0 + (x1 - x0) * (v - lo) / (hi - lo)
    out = [c.txt(0, 14, title, "t b")]
    yb = top + rowh * len(rows)
    for t_ in ticks:
        out.append(c.line(sx(t_), top - 8, sx(t_), yb - 14, "grid"))
        out.append(c.txt(sx(t_), yb, (eur(t_, 0) if unit == "€" else fr(t_, 0)), "m s", "middle"))
    for i, (lab, verdict, a, b, strong) in enumerate(rows):
        y = top + i * rowh + 8
        out.append(c.txt(x0 - 14, y + 1, lab, "t" + (" b" if strong else ""), "end"))
        out.append(c.txt(x0 - 14, y + 17, verdict, "m s", "end"))
        ya, yb_ = y - 8, y + 8
        out.append(c.line(sx(a), ya, sx(b), yb_, "sk w"))
        fmt = (lambda v: eur(v)) if unit == "€" else (lambda v: fr(v))
        a_right = a >= b
        for v, yy, cls, tcls, right in ((a, ya, "fa", "ta s b", a_right), (b, yb_, "fb", "tb s", not a_right)):
            out.append(f'<circle cx="{sx(v):.1f}" cy="{yy}" r="6.5" class="{cls} ring"><title>{fmt(v)}</title></circle>')
            out.append(c.txt(sx(v) + (11 if right else -11), yy + 4, fmt(v), tcls, "start" if right else "end"))
    return c.svg(yb + 8, "".join(out), label)


perc_rows = [("Conforme à mes valeurs", "écart réel ✓", v7["ma"], v7["mb"], True),
             ("Cohérent avec une eau naturelle", "écart réel ✓", v8["ma"], v8["mb"], True),
             ("Confiance dans l'efficacité", "écart réel ✓ (inverse de l'attendu)", v9["ma"], v9["mb"], True),
             ("Qualité perçue", "pas d'écart", v10["ma"], v10["mb"], False)]
price_rows = [(f"Trop cher (on n'achète pas)", "pas d'écart", an.prix[0]["ma"], an.prix[0]["mb"], False),
              ("Cher", "pas d'écart", an.prix[1]["ma"], an.prix[1]["mb"], False),
              ("Bonne affaire", "pas d'écart", an.prix[2]["ma"], an.prix[2]["mb"], False),
              ("Trop bon marché (on doute)", "pas d'écart", an.prix[3]["ma"], an.prix[3]["mb"], False)]
legend = "<p class='lg'><span class='dot a'></span>Version A · végétal <span class='dot b'></span>Version B · animal</p>"
image_vs_prix = (legend +
                 dumbbell(perc_rows, 1, 7, range(1, 8), "", "Perceptions moyennes par version, de 1 à 7", "Ce que les répondants pensent (note moyenne de 1 à 7)") +
                 dumbbell(price_rows, 0, 3.5, (0, 1, 2, 3), "€", "Seuils de prix moyens par version", "Les prix qu'ils donnent (moyenne, en €)"))

chain = """<div class="chain">
<div class="node"><b>Danone</b><span>{d}</span><span>plus de 30 % de l'eau en bouteille en France (Evian, Volvic, Badoit, La Salvetat)</span></div>
<span class="arr" aria-hidden="true">→</span>
<div class="node"><b>Société des Eaux de Volvic</b><span>la filiale qui exploite la source, en Auvergne</span></div>
<span class="arr" aria-hidden="true">→</span>
<div class="node hl"><b>Volvic</b><span>environ 10 % du marché en valeur, derrière Evian (17 %)</span><span>certifiée B Corp</span></div>
</div>""".format(d="27,28 milliards d'euros de chiffre d'affaires en 2025")

season = f"""<div class="pair">
<div class="big"><span class="bn">≈ {eur(2.99 / 6)}</span><span>la bouteille de Volvic nature (50 cl, pack de 6 à 2,99 €)</span></div>
<div class="splitw"><p class="lbl">Part des volumes annuels de Danone Eaux France</p>
<div class="split"><span class="hot" style="width:40%">juin → septembre<br><b>40 %</b></span><span style="width:60%">les 8 autres mois<br><b>60 %</b></span></div>
<p class="lbl">4 mois d'été font 40 % des ventes.</p></div></div>"""

accounts = tiles([("Chiffre d'affaires", "+6,1 %", "515,5 → 547,0 M€ (2023 → 2024)", ""),
                  ("Bénéfice", "45 M€", "deux fois plus qu'en 2023 (23 M€)", ""),
                  ("Marge d'exploitation", "12,6 %", "Danone : 13,4 %", "hl")]) + \
    "<p class='calcline'>Calculs : (547,0 − 515,5) ÷ 515,5 = +6,1 % · 45 ÷ 547 = 8,2 % de marge nette · 69 ÷ 547 = 12,6 % de marge d'exploitation</p>"

humble = f"""<div class="card-k"><p class="ck-t">Humble+ Collagen Water</p>
<p class="ck-p">{eur(an.CONC)}</p><ul><li>canette de 33 cl, soit {eur(2.99 / 0.66)} pour 50 cl</li><li>5 g de collagène <b>marin</b> (animal)</li>
<li>la seule eau au collagène trouvée en vente en France</li></ul></div>"""

ladder = f"""<div class="ladder">
<div class="rung top"><b>{eur(an.CONC)}</b><span>Humble+ · <strong>notre plafond</strong></span></div>
<div class="rung mid"><b>?</b><span>notre bouteille, quelque part entre les deux</span></div>
<div class="rung low"><b>{eur(2.99 / 6)}</b><span>Volvic nature · le bas du rayon</span></div></div>"""

bottles = """<figure class="duo"><div><img src="../img/bouteille_vegetal.jpg" alt="Bouteille version A, collagène d'origine végétale"><p class="tag a">Version A · végétal<br><small>notre variation</small></p></div>
<div><img src="../img/bouteille_animal.jpg" alt="Bouteille version B, collagène d'origine animale"><p class="tag b">Version B · animal<br><small>le standard du marché</small></p></div></figure>"""

mind = th.mindmap_svg([
    ("Éthique", "aucun ingrédient animal", "plus proche des valeurs ?", "→ à vérifier (H7)"),
    ("Image naturelle", "une eau de volcan, B Corp", "plus cohérent ?", "→ à vérifier (H8)"),
    ("Coût", f"actifs végétaux : {fr(an.var_A, 3)} €", f"collagène bovin : {fr(an.var_B, 3)} €", f"→ {fr(ratio, 0)} fois moins cher"),
    ("Le risque", "le « vrai » collagène", "jugé plus efficace ?", "→ à vérifier (H9)")])

wA = 100 * an.var_A / an.var_B
costs = f"""<div class="cost2">
<div class="cc a"><p class="ch">Version A · végétal</p><p>Actif : <b>{fr(an.var_A, 3)} €</b><br><small>80 mg de vitamine C + 100 mg d'extrait de bambou</small></p>
<div class="bar"><span style="width:{wA:.1f}%"></span></div><p class="tot">Coût d'une bouteille : <b>{fr(an.CVU['A'], 3)} €</b></p></div>
<div class="cc b"><p class="ch">Version B · animal</p><p>Actif : <b>{fr(an.var_B, 3)} €</b><br><small>5 g de collagène bovin, la dose d'Humble+</small></p>
<div class="bar"><span style="width:100%"></span></div><p class="tot">Coût d'une bouteille : <b>{fr(an.CVU['B'], 3)} €</b></p></div>
</div><p class="calcline">Commun aux deux : bouteille, bouchon, eau, transport = {eur(an.base_cost)} · Coût d'une bouteille = {eur(an.base_cost)} + actif</p>"""

f = an.funnel
equation = f"""<div class="eq"><span>{len(f[0][1])} lignes reçues</span><span class="op">− 5</span><span>tests de mise en ligne</span>
<span class="op">− 50</span><span>réponses générées automatiquement</span><span class="op">− 1</span><span>refus</span><span class="op">=</span>
<span class="res">{nS} répondants<br><small>{nA} en A · {nB} en B</small></span></div>""" + tiles([
    ("Âge moyen", f"{fr(c.age_m, 1)} ans", f"de {int(min(c.ages))} à {int(max(c.ages))} ans", ""),
    ("Genre", f"{c.genre['Une femme']} · {c.genre['Un homme']}", "femmes · hommes", ""),
    ("Régime", f"{c.regime['Omnivore']} sur {nS}", "omnivores", ""),
    ("Acheteurs d'eau", f"{c.f1['Oui']} sur {nS}", "en bouteille, ces 3 derniers mois", "")], "four")

manip = c.grouped_svg(an.C1CATS, c1, "Origine du collagène retenue par version")

methods = """<div class="m2">
<div class="mc"><p class="ch">Van Westendorp</p><p>Quatre curseurs : à partir de quel prix ce produit est-il…</p>
<ol><li><b>trop bon marché</b> (on doute de la qualité)</li><li>une <b>bonne affaire</b></li><li><b>cher</b> (mais on l'achète)</li><li><b>trop cher</b> (on ne l'achète pas)</li></ol>
<p class="out">→ une <b>zone de prix acceptable</b></p></div>
<div class="mc"><p class="ch">Gabor-Granger</p><p>Des prix proposés du plus cher au moins cher. À chaque prix : « l'achèteriez-vous ? »</p>
<p class="prices"><span>3,50 €</span><span>2,90 €</span><span>2,40 €</span><span>1,90 €</span><span>1,50 €</span></p>
<p class="out">→ la <b>part d'acheteurs</b> à chaque prix</p></div></div>"""

vwcurves = (f"<figure class='vwc'>{c.vw_svg()}<figcaption>Part des répondants ({nS}) qui jugent chaque prix trop bon marché, bon marché, cher ou trop cher. "
            "Les croisements de courbes donnent quatre points ; la zone grisée va du PMC au PME.</figcaption></figure>" +
            c.table(["Point", "Croisement", "Ce qu'il signifie", "Ensemble", "A · végétal", "B · animal"], [
                ["PMC", "trop bon marché × cher", "bas de la zone", eur(vAll["PMC"]), eur(vA["PMC"]), eur(vB["PMC"])],
                ["OPP", "trop bon marché × trop cher", "prix qui fait le moins de rejets", eur(vAll["OPP"]), eur(vA["OPP"]), eur(vB["OPP"])],
                ["IPP", "bon marché × cher", "prix perçu comme normal", eur(vAll["IPP"]), eur(vA["IPP"]), eur(vB["IPP"])],
                ["PME", "bon marché × trop cher", "haut de la zone", eur(vAll["PME"]), eur(vA["PME"]), eur(vB["PME"])]]))

vwlegend = f"""<ul class="keys"><li><b>Début de la zone</b> (PMC) : en dessous, on doute de la qualité.</li>
<li><b>Fin de la zone</b> (PME) : au-dessus, c'est trop cher.</li>
<li><b>Point noir</b> (OPP) : le prix qui fait le moins de rejets.</li>
<li><b>Prix jugé normal</b> (IPP) : {eur(vA['IPP'])} en A, {eur(vB['IPP'])} en B.</li></ul>"""

converge = f"""<div class="conv"><div class="why">
<p><b>Prix jugé normal</b>IPP = {eur(vAll['IPP'])}</p>
<p><b>Dans la zone acceptable</b>{eur(vA['PMC'])} – {eur(vA['PME'])} en végétal</p>
<p><b>Meilleure marge</b>{eur(gA[P]['marge'])} par répondant en végétal</p>
<p><b>Sous le concurrent</b>deux fois moins cher qu'Humble+ ({eur(an.CONC)})</p></div>
<span class="arr" aria-hidden="true">→</span><div class="price"><span>{eur(P)}</span>version végétale<br>50 cl</div></div>"""

breaks = f"""<div class="breaks">
<div><b>Si le prix dépasse {eur(vA['PME'])}</b><span>les clients le jugent trop cher : à 1,90 €, {pct(gA[1.9]['part'])} achètent au lieu de {pct(gA[1.5]['part'])}</span></div>
<div><b>Si l'actif végétal coûtait plus de {fr(c.var_break, 3)} €</b><span>soit {fr(c.var_break / an.var_A, 0)} fois notre estimation : l'avantage de coût disparaît</span></div>
<div><b>Si le distributeur prenait plus de {pct(c.m_break)}</b><span>du prix hors taxe : il ne resterait rien à Volvic (très improbable)</span></div></div>
<p class="worst">Pire cas testé : TVA à 20 %, distributeur à 40 % et coûts doublés <b>en même temps</b> : il reste encore <b>{eur(c.stress[-1][1])}</b> par bouteille.</p>"""

# ---------- les six chapitres ----------
CH = [
    (1, "entreprise", "L'entreprise", "La source", "Au programme : qui est Volvic, comment elle gagne sa vie, et si elle a les moyens de se lancer.", [
        ("Volvic est l'eau de volcan du groupe Danone.", chain,
         "Volvic est une eau minérale naturelle puisée dans le massif volcanique d'Auvergne. Le chiffre de 10 % de part de marché n'est pas daté par sa source : c'est un ordre de grandeur.",
         f"{L('Danone 2025', 'danone')}, {L('LSA', 'lsa')}, {L('Agra', 'agra')}, {L('B Corp', 'bcorp')}, {L('Volvic', 'volvic')}"),
        ("Elle vit du volume : des bouteilles peu chères, vendues surtout l'été.", season,
         "Une bouteille rapporte peu : c'est le nombre de bouteilles qui fait le chiffre d'affaires.",
         f"{L('houra.fr', 'volvic_prix')}, {L('LSA', 'lsa')}"),
        ("Ses comptes sont solides : elle grandit et elle est rentable.", accounts,
         "Sur 100 € vendus, Volvic garde 12,60 € grâce à son métier, presque autant que le groupe Danone. Elle a les moyens de lancer une nouvelle bouteille.",
         f"{L('Le Journal des Entreprises', 'sev_jde')}, {L('Xerfi', 'sev_xerfi')}, {L('Danone 2025', 'danone')}")],
     "Volvic est une marque solide et rentable de Danone, qui vit de gros volumes à petit prix. Elle peut se permettre d'innover.",
     "Mais sur quel marché arriverait une eau au collagène ?"),
    (2, "marche", "Le marché", "La vallée", "Au programme : les prix autour de nous, le seul concurrent direct, et le plafond qu'on en tire.", [
        ("Autour de nous, les prix vont de 0,50 € à 2,99 € la bouteille.", c.market_svg(),
         "L'eau nature est la moins chère ; les eaux vitaminées et au collagène, les plus chères. La bande grise est la zone de prix que nos répondants jugeront acceptable : nous y reviendrons au chapitre 05.",
         f"{L('houra.fr', 'volvic_prix')}, {L('Bonial (prix promo)', 'essentiel')}, {L('Fitadium', 'vitwell')}, {L('Je vais mieux merci', 'humble_prix')}"),
        ("Un seul concurrent direct : Humble+, une eau au collagène.", humble,
         "Son collagène est d'origine animale, comme presque tout le marché. C'est le produit le plus proche du nôtre.",
         f"{L('Je vais mieux merci', 'humble_prix')}, {L('Atida', 'humble_dose')}"),
        (f"Son prix devient notre plafond : {eur(an.CONC)}.", ladder,
         "Au-dessus, le client trouve une offre comparable moins chère. Nous retenons le prix à l'unité en rayon, plus prudent que le prix ramené à 50 cl (4,53 €).", "")],
     f"Le marché va de l'eau simple ({eur(2.99 / 6)}) à l'eau au collagène ({eur(an.CONC)}). Notre prix devra rester sous {eur(an.CONC)}.",
     "Que mettre dans notre bouteille pour se distinguer ?"),
    (3, "proposition", "La proposition", "L'idée", "Au programme : nos deux bouteilles, ce qu'est vraiment le collagène végétal, pourquoi ce choix, et ce qu'il coûte.", [
        ("Deux bouteilles, une seule différence : l'origine du collagène.", bottles,
         "Chaque répondant n'a vu qu'une des deux. Limite à garder en tête : les étiquettes diffèrent aussi par leur couleur.", ""),
        ("Le « collagène végétal » n'existe pas : les plantes aident le corps à fabriquer le sien.", th.collagen_svg(),
         "Le collagène est une protéine animale. La version A apporte de la vitamine C et du bambou ; la loi autorise seulement à dire que la vitamine C « contribue à la formation normale de collagène ».",
         f"{L('Darwin Nutrition', 'vegan')}, {L('règlement européen 432/2012', 'allegation')}"),
        ("Pourquoi le végétal ? Trois atouts et un risque.", mind,
         "Le végétal colle à l'image naturelle de Volvic et coûte moins cher. Le risque : que le client juge le collagène animal plus efficace. Le chapitre 04 vérifie chaque point.", ""),
        (f"Et l'actif végétal coûte {fr(ratio, 0)} fois moins cher.", costs,
         "Le collagène coûte cher au kilo ; les nutriments qui aident à le fabriquer, presque rien. Danone ne publiant pas ses coûts, nous les avons estimés avec des prix de gros publics et des hypothèses signalées.",
         f"{L('vitamine C', 'vitc')}, {L('bambou', 'bambou')}, {L('collagène bovin', 'collagene')}, {L('doses Swanson', 'swanson')}, {L('dose Humble+', 'humble_dose')}, {L('bouteille plastique (préforme)', 'preforme')}")],
     f"Notre variation : un collagène d'origine végétale, plus éthique, plus naturel, et {eur(an.var_B - an.var_A)} moins cher par bouteille.",
     "Reste la vraie question : le client le paiera-t-il autant ?"),
    (4, "repondants", "Qui a répondu", "L'expérience", "Au programme : comment nous avons testé, qui a répondu, s'ils ont vu la différence, et ce qu'elle change.", [
        ("Pour comparer, nous avons laissé le hasard choisir.", th.ab_svg(nA, nB),
         "Du 20 octobre au 12 novembre 2026, chaque personne a reçu au hasard la version A ou B, puis a répondu aux mêmes questions. Seule l'origine change : un écart entre les groupes vient donc de l'origine.",
         L("notre questionnaire", "questionnaire")),
        (f"{nS} vraies réponses, surtout de jeunes adultes.", equation,
         "Les deux groupes se ressemblent (âge, genre, régime, habitudes), sauf sur un point : il y a plus de petits budgets en version B. L'échantillon est jeune : il sert à comparer A et B, pas à représenter tous les acheteurs d'eau.",
         L("nos données brutes", "donnees")),
        (f"Ils ont vu la différence : 9 sur 10 retiennent la bonne origine.", manip,
         f"{pct(c1['A'][0] / nA)} des répondants A retiennent « végétal », {pct(c1['B'][1] / nB)} des B « animal ». Un test du chi² confirme un lien très fort (V de Cramer = {fr(an.manip['v'])} sur 1) : notre test a bien testé quelque chose.", ""),
        ("Le végétal change l'image… mais pas le prix.", image_vs_prix,
         "Le végétal paraît plus conforme aux valeurs, plus cohérent avec une eau naturelle et, contre notre attente, plus digne de confiance. Les quatre seuils de prix, eux, sont presque identiques (tests de Welch).",
         f"échelles de mesure : {L('valeurs, Karahanna et al.', 'karahanna')}, {L('image naturelle, Becker-Olsen et al.', 'becker')}, {L('confiance, Chaudhuri et Holbrook', 'chaudhuri')}, {L('qualité, Dodds et al.', 'dodds')} ({L('détail des échelles', 'sources_echelles')})")],
     "Les répondants ont bien vu la différence. Le végétal est un argument d'image, pas un argument de prix.",
     "Alors, quel prix le client accepte-t-il ?"),
    (5, "client", "Le client", "Le verdict", "Au programme : nos deux méthodes, les courbes de Van Westendorp, la zone de prix acceptable, et combien achèteraient.", [
        ("Nous avons mesuré le prix accepté de deux façons.", methods,
         "La première dit quels prix sont acceptables. La seconde dit combien de personnes achèteraient, ce qui permet de calculer une marge.", ""),
        ("Quatre courbes, quatre croisements : les points de prix du client.", vwcurves,
         f"Quand le prix monte, ceux qui le trouvent bon marché diminuent et ceux qui le trouvent cher augmentent. Chaque croisement de deux courbes donne un point de prix ; la zone grisée va du PMC ({eur(vAll['PMC'])}) au PME ({eur(vAll['PME'])}) pour l'ensemble des {nS} répondants.", ""),
        (f"Prix acceptable : de {eur(vA['PMC'])} à {eur(vA['PME'])} pour le végétal.", c.vwzone_svg() + vwlegend,
         "Les zones des deux versions se recouvrent presque entièrement. Comparés personne par personne, les seuils ne diffèrent pas entre A et B.", ""),
        (f"À {eur(P)}, près de 9 personnes sur 10 achèteraient.", c.gg_svg(),
         f"{pct(gA[P]['part'])} en version végétale, {pct(gB[P]['part'])} en animale : l'écart n'est pas significatif. À 1,90 €, on tombe à {pct(gA[1.9]['part'])} et {pct(gB[1.9]['part'])}. 1,50 € est le prix le plus bas que nous avons proposé.", "")],
     f"Le client accepte environ {eur(P)}, que le collagène soit végétal ou animal.",
     "À ce prix, que gagne Volvic, et quelle version choisir ?"),
    (6, "decision", "La décision", "La bouteille", "Au programme : notre prix, ce qu'il rapporte, et quand le plan ne tient plus.", [
        (f"Notre prix : {eur(P)}, version végétale.", converge,
         f"Quatre indicateurs différents pointent vers le même prix. Limite : le prix qui fait le moins de rejets ({eur(vA['OPP'])}) suggère que le meilleur prix pourrait être un peu plus bas.", ""),
        (f"Sur {eur(P)}, il reste {eur(c.cmA)} à Volvic en végétal, {eur(c.cmB)} en animal.", c.cost_svg(P) + re.sub(r"<ul class='terms'>.*?</ul>", "", c.calc_dec(), flags=re.S),
         f"On retire la TVA (5,5 %), la part du distributeur (30 %, notre hypothèse) et le coût de la bouteille. À prix égal, le végétal rapporte {eur(c.cmA - c.cmB)} de plus : la variation se paie par le coût, pas par le prix.",
         f"{L('TVA, BOFiP', 'tva')}"),
        ("Le plan tient… sauf dans trois cas.", breaks,
         "Deux autres réserves : les intentions d'achat déclarées sont toujours trop optimistes, et sans collagène dans la bouteille, l'étiquette devra s'appuyer sur la vitamine C.",
         f"{L('TVA à 20 % en débat', 'tva20')}")],
     f"Nous recommandons la version végétale à {eur(P)} : même prix accepté, meilleure image, et {eur(c.cmA - c.cmB)} de plus par bouteille.",
     ""),
]
chapters_html = "".join(chapter(*ch) for ch in CH)

SHORT = [("entreprise", "01", "L'entreprise", "Qui est Volvic ?"), ("marche", "02", "Le marché", "Face à qui ?"),
         ("proposition", "03", "La proposition", "Quelle bouteille ?"), ("repondants", "04", "Qui a répondu", "Comment tester ?"),
         ("client", "05", "Le client", "Quel prix accepte-t-il ?"), ("decision", "06", "La décision", "Quel prix choisir ?")]
route = "".join(f"<a href='#{k}'><span class='n'>{n}</span><b>{t}</b><span>{q}</span></a>" for k, n, t, q in SHORT)
nav_html = "".join(f"<a href='#{k}'>{t}</a>" for k, n, t, q in SHORT)

hero = f"""
<header class="hero" id="top">
  <div class="hero-media">
    <video id="pub" autoplay muted playsinline preload="auto" poster="media/volvic-boost-poster.jpg" aria-label="Notre film publicitaire Volvic Boost">
      <source src="media/volvic-boost-pub.mp4" type="video/mp4">
    </video>
    <button class="sound" id="sound" type="button" aria-pressed="false">Activer le son</button>
    <p class="hero-tag">Notre film publicitaire · 10 secondes</p>
  </div>
  <div class="hero-range">{th.mountains()}</div>
  <div class="hero-text">
    <p class="eyebrow">Dossier Prix · M1 Marketing · IAE Clermont Auvergne</p>
    <h1>Volvic Boost, <em>soutien collagène</em></h1>
    <p class="sub">Végétal ou animal : lequel le consommateur paie-t-il plus cher ?</p>
    <p class="lede">Nous avons imaginé une eau Volvic enrichie en collagène, en deux versions, et interrogé {nS} consommateurs. Suivez l'eau, de la source jusqu'à la bouteille, en six étapes.</p>
    <nav class="route" aria-label="Les six étapes">{route}</nav>
    <p class="disclaimer">Étude universitaire, non affiliée à la marque Volvic ni au groupe Danone. Le film et les bouteilles sont des maquettes réalisées pour l'étude.</p>
  </div>
</header>"""

voyage = f"""<div class="carte voyage" id="voyage"><p class="eyebrow">Tout le voyage en une image</p>
<h2>Six questions, six réponses</h2>
{th.sitemap_svg(("Quel prix pour", "Volvic Boost ?"), [
    ("entreprise", "01", "L'entreprise", "solide et rentable", "45 M€ de bénéfice en 2024"),
    ("marche", "02", "Le marché", "un seul concurrent direct", f"plafond : {eur(an.CONC)}"),
    ("proposition", "03", "La proposition", "collagène végétal (A)", f"{fr(ratio, 0)} fois moins cher"),
    ("repondants", "04", "Qui a répondu", f"{nS} répondants", "change l'image, pas le prix"),
    ("client", "05", "Le client", f"accepte environ {eur(P)}", f"zone {fr(vA['PMC'])} – {eur(vA['PME'])}"),
    ("decision", "06", "La décision", f"végétal à {eur(P)}", f"+{eur(c.cmA - c.cmB)} par bouteille")])}
</div>
<aside class="limits"><p class="lt">Ce que notre étude ne dit pas</p><ul>
<li>{nS} répondants jeunes, issus de notre réseau : on compare A et B, on n'estime pas tout le marché.</li>
<li>Les étiquettes diffèrent aussi par leur couleur (vert pour A, rose pour B).</li>
<li>Prix et achats déclarés, pas observés en magasin ; 1,50 € est le prix le plus bas testé.</li>
<li>Coûts estimés à partir de prix de gros publics et d'hypothèses : Danone ne publie pas les siens.</li>
<li>Question de contrôle posée avant les prix, et pas de question de contrôle d'attention.</li></ul></aside>"""

finale = f"""<div class="finale"><div class="fr">{th.mountains(1600, 300, "range")}</div>
<p>De la source à la bouteille : la version végétale, à {eur(P)}, plaît pour ses valeurs et coûte moins cher à produire.</p></div>"""

comfort = """<div class="comfort"><div class="panel" id="comfort-panel" hidden role="group" aria-label="Confort de lecture">
<label><input type="checkbox" data-mode="dys"> Police adaptée dys<small>Police plus lisible, lettres et lignes plus espacées, sans italique ni majuscules.</small></label>
<label><input type="checkbox" data-mode="calm"> Sans animations<small>Tout s'arrête : rien ne bouge ni ne clignote.</small></label>
<label><input type="checkbox" data-mode="essentiel"> L'essentiel seulement<small>Garde le titre de chaque scène et « Ce qu'on retient » : l'histoire se lit en deux minutes.</small></label>
<p class="kbd">Pour présenter : touches <kbd>→</kbd> et <kbd>←</kbd> pour passer d'une scène à l'autre.</p>
</div><button type="button" id="comfort-btn" aria-expanded="false" aria-controls="comfort-panel" aria-label="Confort de lecture">Aa<span class="cf-l"> · Confort de lecture</span></button></div>"""

head_js = """<script>(function(){var r=document.documentElement;['dys','calm','essentiel'].forEach(function(m){try{var x=localStorage.getItem('cf-'+m);if(x==='1'||(x===null&&m==='calm'&&matchMedia('(prefers-reduced-motion: reduce)').matches))r.classList.add(m);}catch(e){}});if(!r.classList.contains('calm')&&('IntersectionObserver' in window))r.classList.add('anim');})();</script>"""

STORY_CSS = """
/* ===== Récit : une idée par scène ===== */
.topnav a.pdf{margin-left:auto;color:var(--accent);font-weight:600}
.route{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin-top:14px}
.route a{display:grid;gap:2px;text-decoration:none;color:var(--ink);background:color-mix(in srgb,var(--surface) 92%,transparent);border:1px solid var(--line);border-radius:16px 12px 18px 12px;padding:12px 12px 14px}
.route a:hover{border-color:var(--water)}
.route .n{width:28px;height:28px;border-radius:50%;background:var(--accent);color:#fff;display:grid;place-items:center;font:600 13px var(--body);margin-bottom:4px}
.route b{font:600 16px/1.2 var(--display)}.route span:last-child{color:var(--muted);font-size:14px}
.chapter{padding:0;border-bottom:0}
.opener{min-height:72vh;display:grid;align-content:center;gap:12px;padding:60px 0 30px}
.opener .stage{font:600 30px/1 var(--hand);color:var(--water);margin:0}
.opener h2{font-size:clamp(30px,4.4vw,52px);max-width:22ch}
.promise{font-size:19px;color:var(--muted);margin:0}
.scene{min-height:90vh;display:grid;align-content:center;gap:14px;padding:56px 0;border-top:1px dashed var(--line)}
.sn{margin:0;font:500 12.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--water)}
.claim{font:600 clamp(26px,3.5vw,40px)/1.15 var(--display);font-variation-settings:"SOFT" 100;margin:0;max-width:26ch;text-wrap:balance}
.evidence{margin:6px 0;min-width:0}.scene>*,.opener>*,.recap>*{min-width:0}
.evidence>figure,.evidence>.cw{margin:0}
.evidence .cw{background:var(--surface);border:1px solid var(--line);border-radius:22px 18px 24px 16px;padding:16px}
.say{font-size:19px;line-height:1.6;margin:0;max-width:64ch}
.src{font-size:13.5px;color:var(--muted);margin:0}
.recap{margin:20px 0 40px;padding:28px 30px;border-radius:26px 20px 28px 18px;background:linear-gradient(135deg,color-mix(in srgb,var(--water-2) 45%,var(--surface)),color-mix(in srgb,var(--leaf) 22%,var(--surface)));border:1px solid var(--line)}
.recap span{font:500 12.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
.recap>p{font:600 clamp(21px,2.4vw,28px)/1.3 var(--display);font-variation-settings:"SOFT" 100;margin:6px 0 0;max-width:none}
.recap .bridge{font:600 26px/1.2 var(--hand);color:var(--water);margin-top:14px}
.recap .bridge::after{content:" ↓"}
/* composants */
.chain{display:flex;flex-wrap:wrap;align-items:stretch;gap:10px}
.chain .node{flex:1 1 200px;display:grid;gap:4px;align-content:start;background:var(--surface);border:1px solid var(--line);border-radius:18px 14px 20px 12px;padding:14px 16px}
.chain .node b{font:600 19px var(--display)}.chain .node span{color:var(--muted);font-size:15px}
.chain .node.hl{border:2px solid var(--water)}
.arr{align-self:center;font-size:28px;color:var(--water)}
.pair{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);gap:18px;align-items:center}
.big{display:grid;gap:4px}.bn{font:600 clamp(54px,8vw,92px)/1 var(--display);color:var(--accent)}
.big span:last-child{color:var(--muted)}
.split{display:flex;border-radius:14px;overflow:hidden;border:1px solid var(--line);font-size:15px}
.split span{padding:12px 14px;background:var(--surface);line-height:1.3}.split .hot{background:var(--water);color:#fff}
.lbl{color:var(--muted);font-size:14.5px;margin:6px 0}
.tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.tiles.four{grid-template-columns:repeat(4,minmax(0,1fr));margin-top:12px}
.tile{display:grid;gap:2px;background:var(--surface);border:1px solid var(--line);border-radius:18px 14px 20px 12px;padding:14px 16px}
.tile.hl{border:2px solid var(--water)}
.tk{font:500 11.5px var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.tv{font:600 34px/1.1 var(--display);color:var(--accent)}.ts{font-size:14.5px;color:var(--muted)}
.calcline{font:500 13.5px var(--mono);color:var(--muted);margin:10px 0 0}
.card-k{background:var(--surface);border:2px solid var(--b);border-radius:24px 18px 26px 16px;padding:20px 24px;max-width:520px}
.ck-t{font:600 22px var(--display);margin:0}.ck-p{font:600 64px/1 var(--display);color:var(--ink);margin:6px 0 8px}
.card-k ul{margin:0;padding-left:20px}
.ladder{display:grid;gap:0;max-width:560px;border-left:6px solid;border-image:linear-gradient(var(--b),var(--water-2),var(--leaf)) 1;padding-left:18px}
.rung{display:flex;gap:14px;align-items:baseline;padding:14px 0}
.rung b{font:600 34px var(--display);min-width:120px}.rung.mid b{color:var(--water)}
.rung span{color:var(--muted)}.rung.top{border-bottom:2px dashed var(--b)}
figure.duo{grid-template-columns:repeat(2,minmax(0,1fr));justify-items:center;align-items:end;background:#fff}
figure.duo>div{display:grid;justify-items:center;gap:8px}
.tag{margin:0;font-weight:600;text-align:center;padding:6px 14px;border-radius:999px;line-height:1.25}
.tag.a{background:color-mix(in srgb,var(--a) 14%,#fff);color:var(--a)}.tag.b{background:color-mix(in srgb,var(--b) 20%,#fff);color:#11281c}
.tag small{font-weight:400}
.cost2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.cc{background:var(--surface);border:1px solid var(--line);border-top:5px solid;border-radius:14px;padding:14px 16px}
.cc.a{border-top-color:var(--a)}.cc.b{border-top-color:var(--b)}
.cc .ch{font:600 18px var(--display);margin:0 0 6px}.cc p{margin:4px 0}.cc small{color:var(--muted)}
.cc .bar{height:16px;border-radius:8px;background:var(--mist);overflow:hidden;margin:8px 0}
.cc .bar span{display:block;height:100%;min-width:3px}.cc.a .bar span{background:var(--a)}.cc.b .bar span{background:var(--b)}
.eq{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:15px}
.eq span{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:8px 12px}
.eq .op{background:none;border:0;font:600 20px var(--display);color:var(--water);padding:0 2px}
.eq .res{border:2px solid var(--water);font-weight:600;font-size:17px}
.lg{display:flex;gap:6px 14px;align-items:center;flex-wrap:wrap;margin:0 0 8px;font-size:15px}
.lg .dot{width:13px;height:13px;border-radius:50%;display:inline-block}.lg .dot.a{background:var(--a)}.lg .dot.b{background:var(--b)}
.evidence .cw+.cw{margin-top:12px}
.m2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.mc{background:var(--surface);border:1px solid var(--line);border-radius:20px 16px 22px 14px;padding:16px 18px}
.mc .ch{font:600 21px var(--display);margin:0 0 6px;color:var(--accent)}.mc ol{margin:6px 0;padding-left:22px}
.mc .out{margin:10px 0 0;color:var(--water)}
.prices{display:flex;flex-wrap:wrap;gap:6px}.prices span{border:1px solid var(--line);border-radius:999px;padding:4px 10px;font-weight:600}
.keys{margin:12px 0 0;padding-left:20px;font-size:16px}.keys li{margin:3px 0}
.conv{display:grid;grid-template-columns:minmax(0,1.6fr) auto minmax(0,1fr);gap:14px;align-items:center}
.why{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.why p{margin:0;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:10px 14px;display:grid;font-size:14.5px;color:var(--muted)}
.why b{color:var(--ink);font-size:16px}
.price{text-align:center;background:var(--surface);border:2px solid var(--a);border-radius:26px;padding:18px;color:var(--muted)}
.price span{display:block;font:600 64px/1 var(--display);color:var(--a)}
.breaks{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.breaks div{background:var(--surface);border:1px solid var(--line);border-left:5px solid var(--b);border-radius:14px;padding:12px 14px;display:grid;gap:4px}
.breaks b{font:600 17px/1.25 var(--display)}.breaks span{color:var(--muted);font-size:15px}
.worst{margin:12px 0 0;padding:12px 16px;border-radius:14px;background:color-mix(in srgb,var(--leaf) 18%,var(--surface));border:1px solid var(--line)}
.voyage{padding-top:70px}
.limits{margin:30px 0 0;background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:20px 24px}
.limits .lt{font:600 21px var(--display);margin:0 0 6px}.limits ul{margin:0;padding-left:20px}.limits li{margin:4px 0}
.more{margin:12px 0 0;font-weight:600}
.kbd{margin:0;font-size:13.5px;color:var(--muted)}
kbd{font:600 12px var(--mono);border:1px solid var(--line);border-bottom-width:2px;border-radius:5px;padding:1px 6px;background:var(--paper)}
/* l'essentiel : les titres de scène + les résumés */
html.essentiel .scene .evidence,html.essentiel .scene .say,html.essentiel .scene .src{display:none}
html.essentiel .scene{min-height:0;padding:16px 0}html.essentiel .opener{min-height:0;padding:40px 0 10px}
html.essentiel .claim{font-size:clamp(21px,2.6vw,28px)}
@media (max-width:900px){.route{grid-template-columns:repeat(3,minmax(0,1fr))}.tiles.four{grid-template-columns:repeat(2,minmax(0,1fr))}.conv{grid-template-columns:1fr}.conv .arr{transform:rotate(90deg);justify-self:center}.breaks{grid-template-columns:1fr}}
@media (max-width:640px){.route{grid-template-columns:repeat(2,minmax(0,1fr))}.scene{min-height:0;padding:40px 0}.opener{min-height:0;padding:50px 0 20px}
 .pair,.tiles,.cost2,.m2,.why{grid-template-columns:1fr}.chain .arr{transform:rotate(90deg);width:100%;text-align:center}.say{font-size:17px}.ck-p{font-size:52px}.rung b{min-width:90px;font-size:28px}}
@media print{.comfort,.topnav,.hero-media,.river{display:none}}

.evidence figure.vwc{margin:0 0 10px}.evidence .calc{margin:14px 0 0}.evidence figure.vwc .cw{border:0;padding:0}
/* ===== Illustrations des chapitres ===== */
.opener{grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);align-items:center;column-gap:36px}
.ot{display:grid;gap:12px}
.ill{max-width:460px;width:100%;justify-self:end}
.vg{width:100%;height:auto;display:block;overflow:visible}
.vg .v-sky{fill:var(--mist);opacity:.75}.vg .v-sun{fill:#f3d98b;opacity:.85}
.vg .v-line{fill:none;stroke:var(--ink);stroke-opacity:.25;stroke-width:2}
.vg .v-river{fill:none;stroke:var(--water-2);stroke-width:11;stroke-linecap:round}
.vg .v-flow{fill:none;stroke:var(--water);stroke-width:4;stroke-linecap:round;stroke-dasharray:12 14}
.vg .drop{fill:var(--water)}
.vg .glass{fill:color-mix(in srgb,var(--water-2) 38%,#fff);stroke:var(--water);stroke-width:2}
.vg .glass2{fill:none;stroke:var(--water);stroke-width:2.5}
.vg .v-cap{fill:var(--accent)}.vg .v-glassA{fill:var(--water-2)}
.vg .fa{fill:var(--a)}.vg .fb{fill:var(--b)}
.vg .v-t{font:600 13px var(--body);fill:var(--ink)}.vg .v-t.s{font-size:11px;fill:var(--muted)}
.vg .v-ceil{stroke:var(--b);stroke-width:2;stroke-dasharray:5 4}
.vg .v-leafc{fill:var(--leaf)}.vg .v-vein{fill:none;stroke:var(--a);stroke-width:1.5}
.vg .v-hx{fill:none;stroke-width:3.5;stroke-linecap:round}.vg .h0{stroke:var(--b)}.vg .h1{stroke:var(--water)}.vg .h2{stroke:var(--accent-2)}
.vg .v-p0{fill:var(--muted)}.vg .v-pa{fill:var(--a)}.vg .v-pb{fill:var(--b)}
.vg .v-arrow{fill:none;stroke:var(--water);stroke-width:2.5;stroke-dasharray:5 6;stroke-linecap:round}
.vg .v-dicer{fill:#fff;stroke:var(--ink);stroke-width:2}.vg .v-pip{fill:var(--ink)}
.vg .v-scale{fill:var(--line)}.vg .v-zone{fill:var(--a);opacity:.75}
.vg .v-string{stroke:var(--muted);stroke-width:1.5}
.vg .v-tagb{fill:#fff;stroke:var(--a);stroke-width:3}.vg .v-hole{fill:var(--mist);stroke:var(--muted)}
.vg .v-price{font:600 30px var(--display);fill:var(--a)}
.vg .v-water{fill:var(--water-2);opacity:.8}.vg .v-wave{fill:var(--water);opacity:.55}
.vg .v-lab{font:600 22px var(--display);fill:#fff}
.vg .v-bub{fill:#fff;opacity:.85}
.recap{position:relative;overflow:hidden}
.ripple{position:absolute;right:-10px;bottom:-14px;width:230px;opacity:.55;pointer-events:none}
.ripple .rp{fill:none;stroke:var(--water);stroke-width:2}.ripple .drop{fill:var(--water)}
.recap>*:not(.ripple){position:relative}
@media (max-width:900px){.opener{grid-template-columns:1fr}.ill{justify-self:start;max-width:380px;order:-1}}

/* ===== Animations au défilement (seulement si html.anim : JS actif et pas « sans animations ») ===== */
html.anim .opener .ot>*,html.anim .scene .sn,html.anim .scene .claim,html.anim .scene .say,html.anim .scene .src,
html.anim .recap>*:not(.ripple),html.anim .voyage>*,html.anim .limits{opacity:0;transform:translateY(22px);
 transition:opacity .8s ease,transform .9s cubic-bezier(.2,.75,.2,1)}
html.anim .in .ot>*,html.anim .in.scene .sn,html.anim .in.scene .claim,html.anim .in.scene .say,html.anim .in.scene .src,
html.anim .in.recap>*:not(.ripple),html.anim .in.voyage>*,html.anim .limits.in{opacity:1;transform:none}
html.anim .ot>:nth-child(2){transition-delay:.08s}html.anim .ot>:nth-child(3){transition-delay:.16s}html.anim .ot>:nth-child(4){transition-delay:.28s}
html.anim .scene .claim{transition-delay:.06s}html.anim .scene .say{transition-delay:.55s}html.anim .scene .src{transition-delay:.7s}
html.anim .recap>p{transition-delay:.15s}html.anim .recap .bridge{transition-delay:.5s}
/* le titre de scène reçoit un coup de pinceau */
.claim::after{content:"";display:block;width:92px;height:7px;margin-top:12px;border-radius:7px 3px 6px 4px;background:linear-gradient(90deg,var(--water-2),var(--water));transform-origin:left}
html.anim .scene .claim::after{transform:scaleX(0);transition:transform .9s cubic-bezier(.2,.75,.2,1) .45s}
html.anim .scene.in .claim::after{transform:none}
/* l'illustration du chapitre */
html.anim .opener .ill{opacity:0;transform:translateY(26px) scale(.96);transition:opacity 1s ease .15s,transform 1.1s cubic-bezier(.2,.75,.2,1) .15s}
html.anim .opener.in .ill{opacity:1;transform:none}
html.anim .vg .grow{transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0);transition:transform 1s cubic-bezier(.2,.8,.2,1) calc(.5s + var(--dl))}
html.anim .in .vg .grow{transform:none}
html.anim .in .vg .v-flow{animation:vflow 2.6s linear 4}
html.anim .vg .v-drip{opacity:0}
html.anim .in .vg .v-drip{animation:drip 2.2s ease-in 3 both}.vg .d2{animation-delay:.6s!important}.vg .d3{animation-delay:1.2s!important}
html.anim .in .vg .v-leaf{transform-box:fill-box;transform-origin:85% 95%;animation:sway 2.4s ease-in-out 3}
html.anim .in .vg .v-helix{animation:hxs 2.6s linear 3}
html.anim .vg .tilt-l,html.anim .vg .tilt-r{transform-box:fill-box;transform-origin:50% 100%;transition:transform 1.1s cubic-bezier(.2,.8,.2,1) .4s}
html.anim .vg .tilt-l{transform:translateX(-30px) rotate(-8deg)}html.anim .vg .tilt-r{transform:translateX(30px) rotate(8deg)}
html.anim .in .vg .tilt-l,html.anim .in .vg .tilt-r{transform:none}
html.anim .in .vg .v-arrow{animation:vflow 1.6s linear 4}
html.anim .in .vg .v-dice{transform-box:fill-box;transform-origin:center;animation:roll 1.3s cubic-bezier(.3,.7,.3,1) .4s 2}
html.anim .vg .v-pa,html.anim .vg .v-pb{opacity:0;transition:opacity .7s ease 1.2s}
html.anim .in .vg .v-pa,html.anim .in .vg .v-pb{opacity:1}
html.anim .in .vg .v-tag{transform-box:view-box;transform-origin:180px 22px;animation:swing 2.2s ease-in-out .3s 3}
html.anim .vg .v-water,html.anim .vg .v-wave{transform:translateY(160px);transition:transform 2.4s cubic-bezier(.25,.7,.2,1) .5s}
html.anim .in .vg .v-water,html.anim .in .vg .v-wave{transform:translateY(0)}
html.anim .in .vg .v-bub{animation:bub 2.4s ease-in 2.4s 3 both}.vg .b1{animation-delay:3s!important}.vg .b2{animation-delay:3.5s!important}
/* les preuves : graphiques qui se dessinent, cartes qui arrivent une à une */
html.anim .scene .evidence{opacity:0;transform:translateY(16px);transition:opacity .9s ease .2s,transform .9s cubic-bezier(.2,.75,.2,1) .2s}
html.anim .scene.in .evidence{opacity:1;transform:none}
html.anim .scene .evidence svg.chart{clip-path:inset(0 100% 0 0);transition:clip-path 1.7s cubic-bezier(.35,.6,.2,1) .45s}
html.anim .scene.in .evidence svg.chart{clip-path:inset(0 0 0 0)}
html.anim .stg>*{opacity:0;transform:translateY(16px);transition:opacity .6s ease,transform .7s cubic-bezier(.2,.75,.2,1);transition-delay:calc(.35s + var(--i,0) * .11s)}
html.anim .in .stg>*{opacity:1;transform:none}
html.anim .split span,html.anim .cc .bar span{transform:scaleX(0);transform-origin:left;transition:transform 1.2s cubic-bezier(.2,.75,.2,1) .6s}
html.anim .in .split span,html.anim .in .cc .bar span{transform:none}
html.anim .price{transform:scale(.85);opacity:0;transition:transform .8s cubic-bezier(.3,1.6,.4,1) 1s,opacity .5s ease 1s}
html.anim .in .price{transform:none;opacity:1}
html.anim .in .conv>.arr,html.anim .in .chain .arr{animation:nudge 1.2s ease-in-out 1s 3}
html.anim .scene figure.duo>div{opacity:0;transform:translateY(30px);transition:opacity .9s ease,transform 1s cubic-bezier(.2,.75,.2,1)}
html.anim .scene figure.duo>div:nth-child(2){transition-delay:.25s}
html.anim .scene.in figure.duo>div{opacity:1;transform:none}
/* « Ce qu'on retient » : des ronds dans l'eau */
html.anim .ripple .rp{transform-box:fill-box;transform-origin:center}
html.anim .in .ripple .rp{animation:ring 2.4s ease-out 3 backwards}.ripple .r1{animation-delay:.5s!important}.ripple .r2{animation-delay:1s!important}
html.anim .in .ripple .rpd{animation:fall 1.1s cubic-bezier(.5,0,1,1) backwards}
@keyframes vflow{to{stroke-dashoffset:-52}}
@keyframes drip{0%{opacity:0;transform:translateY(-8px)}25%{opacity:1}100%{opacity:0;transform:translateY(30px)}}
@keyframes sway{50%{transform:rotate(9deg)}}
@keyframes hxs{50%{transform:translateX(-10px)}}
@keyframes swing{0%,100%{transform:rotate(0)}25%{transform:rotate(5deg)}75%{transform:rotate(-5deg)}}
@keyframes bub{0%{opacity:0;transform:translateY(0)}20%{opacity:.9}100%{opacity:0;transform:translateY(-120px)}}
@keyframes nudge{50%{transform:translateX(6px)}}
@keyframes ring{0%{opacity:0;transform:scale(.4)}30%{opacity:.9}100%{opacity:1;transform:scale(1)}}
@keyframes fall{0%{opacity:0;transform:translate(100px,-10px) scale(1.3)}40%{opacity:1}100%{opacity:1;transform:translate(100px,44px) scale(1.3)}}
"""

STORY_JS = r"""
(() => {
  // Apparitions au défilement, chiffres qui défilent, cartes une à une
  const root = document.documentElement;
  document.querySelectorAll('.chain, .tiles, .eq, .why, .breaks, .ladder, .m2, .cost2, .keys, .route, .limits ul').forEach(g => {
    g.classList.add('stg'); [...g.children].forEach((ch, i) => ch.style.setProperty('--i', i));
  });
  const count = el => {
    const txt = el.textContent, m = txt.match(/\d+(?:,\d+)?/); if (!m) return;
    const target = parseFloat(m[0].replace(',', '.')), dec = (m[0].split(',')[1] || '').length, t0 = performance.now(), dur = 1300;
    const step = now => { const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = txt.replace(m[0], (target * e).toFixed(dec).replace('.', ','));
      if (k < 1) requestAnimationFrame(step); else el.textContent = txt; };
    requestAnimationFrame(step);
  };
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in'); io.unobserve(e.target);
      if (root.classList.contains('anim')) e.target.querySelectorAll('.bn, .tv, .ck-p, .price>span, .rung b').forEach(count);
    }), {threshold: 0.15, rootMargin: '0px 0px -6% 0px'});
    document.querySelectorAll('.hero-text, .opener, .scene, .recap, .voyage, .limits, .finale').forEach(el => io.observe(el));
  }
  document.querySelectorAll('.comfort input[data-mode="calm"]').forEach(inp => inp.addEventListener('change', () => {
    root.classList.toggle('anim', !inp.checked);
    if (inp.checked) document.querySelectorAll('.opener, .scene, .recap, .voyage, .limits, .finale').forEach(el => el.classList.add('in'));
  }));

  // Présentation : → et ← passent d'une scène à l'autre
  const stops = () => [...document.querySelectorAll('.hero, .opener, .scene, .recap, .voyage, .limits')]
    .filter(el => el.offsetParent !== null).map(el => el.getBoundingClientRect().top + scrollY - 64);
  addEventListener('keydown', e => {
    const dir = {ArrowRight: 1, PageDown: 1, ArrowLeft: -1, PageUp: -1}[e.key];
    if (!dir || e.altKey || e.ctrlKey || e.metaKey || (e.target.matches && e.target.matches('input, textarea, select'))) return;
    const list = stops(), y = scrollY;
    const t = dir > 0 ? list.find(v => v > y + 8) : [...list].reverse().find(v => v < y - 8);
    if (t === undefined) return;
    e.preventDefault();
    scrollTo({top: t, behavior: document.documentElement.classList.contains('calm') ? 'auto' : 'smooth'});
  });
})();
"""

page = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Volvic Boost · Dossier Prix</title>
<meta name="description" content="Dossier Prix, M1 Marketing IAE Clermont Auvergne : le prix accepté d'une eau Volvic au collagène végétal ou animal, raconté en six étapes.">
<meta name="theme-color" content="#0f5a36">
{th.FONTS}
<style>{th.CSS}{STORY_CSS}</style>{head_js}</head>
<body>
{th.SVG_DEFS}
<nav class="topnav" aria-label="Chapitres"><div class="in"><strong>Volvic Boost · Dossier Prix</strong>{nav_html}</div><div class="progress"></div></nav>
{hero}
<div class="flowwrap"><svg class="river" aria-hidden="true"></svg>
<main>
{chapters_html}
{voyage}
{finale}
<p class="foot">Étude universitaire, M1 Marketing, IAE Clermont Auvergne. Non affiliée à la marque Volvic ni au groupe Danone. Le film publicitaire et les visuels de bouteille sont des maquettes réalisées pour l'étude. Données : {L('réponses au questionnaire', 'donnees')}, export du 23 novembre 2026. Calculs : {L("script d'analyse", 'code')}.</p>
</main></div>
{comfort}
<script>{th.JS}{STORY_JS}</script>
</body></html>"""

(HERE / "index.html").write_text(page, encoding="utf-8")
(HERE / "hors-site").mkdir(exist_ok=True)
(HERE / "hors-site" / "annexe.html").write_text(c.annexe_html().replace('href="../img/', 'href="../../img/').replace('src="../img/', 'src="../../img/'), encoding="utf-8")
print("ok index.html", len(page) // 1024, "Ko · hors-site/annexe.html")
