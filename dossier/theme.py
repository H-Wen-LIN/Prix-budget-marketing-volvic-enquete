"""Identité visuelle du dossier : aquarelle, montagnes d'Auvergne, rivière qui suit la lecture.

Importé par build.py. Tout est généré ici (pas d'image externe) sauf la vidéo et les visuels de bouteille.
"""
import math, html

esc = html.escape

# ---------- Peinture : filtres SVG partagés ----------
SVG_DEFS = """
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
 <defs>
  <filter id="wc" x="-8%" y="-8%" width="116%" height="116%">
   <feTurbulence type="fractalNoise" baseFrequency="0.011" numOctaves="3" seed="4" result="n"/>
   <feDisplacementMap in="SourceGraphic" in2="n" scale="16" xChannelSelector="R" yChannelSelector="G" result="d"/>
   <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="9" result="g"/>
   <feColorMatrix in="g" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -0.9 1.15" result="ga"/>
   <feComposite in="d" in2="ga" operator="in" result="t"/>
   <feGaussianBlur in="t" stdDeviation="0.5"/>
  </filter>
  <filter id="wc-soft" x="-10%" y="-10%" width="120%" height="120%">
   <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="2" result="n"/>
   <feDisplacementMap in="SourceGraphic" in2="n" scale="6" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="wc-blob" x="-20%" y="-20%" width="140%" height="140%">
   <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="3" seed="7" result="n"/>
   <feDisplacementMap in="SourceGraphic" in2="n" scale="18" xChannelSelector="R" yChannelSelector="G" result="d"/>
   <feGaussianBlur in="d" stdDeviation="1.2"/>
  </filter>
  <linearGradient id="water-grad" x1="0" y1="0" x2="0" y2="1">
   <stop offset="0" stop-color="var(--water-2)"/><stop offset="1" stop-color="var(--water)"/>
  </linearGradient>
 </defs>
</svg>"""

PAPER = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'>"
         "<filter id='p'><feTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='3' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 0.35 0 0 0 0 0.42 0 0 0 0 0.38 0 0 0 0.09 0'/></filter>"
         "<rect width='100%25' height='100%25' filter='url(%23p)'/></svg>\")")


# ---------- La chaîne des volcans, peinte ----------
def _ridge(width, base, peaks, step=6):
    """Profil de crête : somme de dômes gaussiens (les puys), avec un cratère éventuel."""
    pts = []
    for x in range(0, width + step, step):
        y = base
        for cx, h, w, crater in peaks:
            g = math.exp(-((x - cx) / w) ** 2)
            y -= h * g
            if crater:
                y += h * 0.18 * math.exp(-((x - cx) / (w * 0.22)) ** 2)
        pts.append((x, y))
    return pts

def mountains(width=1600, height=320, cls="range"):
    layers = [
        ("far", 0.55, 210, [(120, 70, 120, 0), (420, 95, 140, 1), (760, 80, 130, 0), (1080, 120, 150, 1), (1420, 85, 140, 0)]),
        ("mid", 0.85, 250, [(260, 110, 130, 1), (620, 150, 150, 1), (980, 95, 120, 0), (1300, 135, 140, 1), (1560, 70, 110, 0)]),
        ("near", 1.0, 300, [(60, 90, 160, 0), (480, 120, 190, 0), (860, 170, 170, 1), (1240, 100, 180, 0), (1600, 140, 170, 0)]),
    ]
    out = []
    for name, op, base, peaks in layers:
        pts = _ridge(width, base, peaks)
        d = f"M0,{height} " + " ".join(f"L{x},{y:.1f}" for x, y in pts) + f" L{width},{height} Z"
        out.append(f'<g class="ridge ridge-{name}" data-depth="{ {"far": 0.06, "mid": 0.12, "near": 0.2}[name] }">'
                   f'<path d="{d}" class="m-{name}" filter="url(#wc)" opacity="{op}"/>'
                   f'<path d="{d}" class="m-edge" filter="url(#wc-soft)"/></g>')
    return (f'<svg class="{cls}" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMax slice" aria-hidden="true">'
            + "".join(out) + "</svg>")


# ---------- Animation : qu'est-ce que le collagène ? ----------
def _helix(x0, x1, yc, amp, wl, phase, step=4):
    pts = [(x, yc + amp * math.sin(2 * math.pi * (x - x0) / wl + phase)) for x in range(int(x0), int(x1) + 1, step)]
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)

def collagen_svg():
    W, H = 640, 380
    strands = "".join(
        f'<path d="{_helix(40 - 92, 600 + 92, 62, 15, 92, ph)}" class="strand s{i}"/>' for i, ph in enumerate((0, 2.094, 4.189)))
    def mini(x, y, cls):
        return "".join(f'<path d="{_helix(x, x + 70, y, 7, 34, ph, 2)}" class="strand mini {cls}" pathLength="1"/>' for ph in (0, 2.094, 4.189))
    leaf = ('<path d="M52,186 C52,156 84,144 104,148 C104,176 84,196 52,194 Z" class="leaf" filter="url(#wc-soft)"/>'
            '<path d="M56,190 C70,176 84,164 100,152" class="leaf-vein"/>')
    beads = "".join(f'<circle cx="{58 + 13 * i}" cy="{292 + (5 if i % 2 else -5)}" r="7" class="bead" filter="url(#wc-soft)"/>' for i in range(4))
    body = lambda y: (f'<circle cx="330" cy="{y - 16}" r="11" class="body"/>'
                      f'<path d="M306,{y + 22} C306,{y - 2} 354,{y - 2} 354,{y + 22} Z" class="body"/>')
    pathA = "M128,158 C200,128 250,150 300,158"; pathA2 = "M362,158 C410,150 440,148 500,158"
    pathB = "M128,292 C200,322 250,300 300,292"; pathB2 = "M362,292 C410,300 440,302 500,292"
    dots = "".join(
        f'<circle r="4" class="{c}"><animateMotion dur="{d}s" begin="{b}s" repeatCount="indefinite" path="{p}"/></circle>'
        for p, c, d, b in ((pathA, "fa", 2.6, 0), (pathA, "fa", 2.6, 1.3), (pathA2, "fa", 2.2, 0.6),
                           (pathB, "fb", 2.6, 0.4), (pathB, "fb", 2.6, 1.7), (pathB2, "fb", 2.2, 1.0)))
    t = lambda x, y, s, c="t", a="start": f'<text x="{x}" y="{y}" class="{c}" text-anchor="{a}">{esc(s)}</text>'
    body_txt = (
        t(320, 24, "le collagène : trois chaînes de protéines enroulées en hélice", "hand", "middle") +
        t(320, 104, "on n'en trouve que chez les animaux", "m s", "middle") +
        t(30, 136, "Version A · végétal", "ta b") + t(30, 216, "vitamine C + silice de bambou", "m s") +
        t(30, 268, "Version B · animal", "tb b") + t(30, 322, "5 g de peptides de collagène bovin", "m s") +
        t(330, 206, "le corps", "m s", "middle") + t(330, 340, "le corps", "m s", "middle") +
        t(540, 190, "fabrique son", "m s", "middle") + t(540, 204, "propre collagène", "m s", "middle") +
        t(540, 324, "reçoit du collagène", "m s", "middle") + t(540, 338, "déjà formé", "m s", "middle"))
    return (f'<div class="cw"><svg class="chart collagen" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Schéma animé : le collagène est une triple hélice animale ; la version A apporte des nutriments végétaux qui aident le corps à le fabriquer, la version B apporte du collagène bovin." style="min-width:560px">'
            f'<clipPath id="hx"><rect x="40" y="30" width="560" height="70" rx="20"/></clipPath><g clip-path="url(#hx)"><g class="helix">{strands}</g></g>{leaf}{beads}'
            f'<path d="{pathA}" class="flow fa-s"/><path d="{pathA2}" class="flow fa-s"/><path d="{pathB}" class="flow fb-s"/><path d="{pathB2}" class="flow fb-s"/>'
            f'{body(170)}{body(304)}<g class="build">{mini(505, 160, "sa-h")}</g>{mini(505, 294, "sb-h")}{dots}{body_txt}</svg></div>')


# ---------- Carte mentale : pourquoi cette variation ----------
def mindmap_svg(items):
    """items : liste de 4 (titre, ligne 1, ligne 2, verdict) dans l'ordre haut-gauche, haut-droite, bas-gauche, bas-droite."""
    W, H = 640, 400; cx, cy = 320, 200
    pos = [(118, 78), (522, 78), (118, 322), (522, 322)]
    out = [f'<ellipse cx="{cx}" cy="{cy}" rx="118" ry="58" class="mm-core" filter="url(#wc-blob)"/>',
           f'<text x="{cx}" y="{cy - 6}" class="mm-title" text-anchor="middle">Collagène</text>',
           f'<text x="{cx}" y="{cy + 18}" class="mm-title" text-anchor="middle">d\'origine végétale</text>']
    for i, ((x, y), (title, l1, l2, verdict)) in enumerate(zip(pos, items)):
        sx = cx + (-90 if x < cx else 90); sy = cy + (-30 if y < cy else 30)
        c1x, c1y = sx + (x - sx) * 0.15, y; c2x, c2y = sx + (x - sx) * 0.5, sy
        ex, ey = x + (96 if x < cx else -96), y + (34 if y < cy else -34)
        out.append(f'<path d="M{sx},{sy} C{sx:.0f},{(sy + ey) / 2:.0f} {ex:.0f},{(sy + ey) / 2:.0f} {ex},{ey}" class="mm-branch b{i}" pathLength="1"/>')
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="104" ry="56" class="mm-node n{i}" filter="url(#wc-blob)"/>')
        out.append(f'<text x="{x}" y="{y - 22}" class="mm-h" text-anchor="middle">{esc(title)}</text>')
        out.append(f'<text x="{x}" y="{y - 2}" class="m s" text-anchor="middle">{esc(l1)}</text>')
        out.append(f'<text x="{x}" y="{y + 14}" class="m s" text-anchor="middle">{esc(l2)}</text>')
        out.append(f'<text x="{x}" y="{y + 36}" class="hand v" text-anchor="middle">{esc(verdict)}</text>')
    return (f'<div class="cw"><svg class="chart mindmap" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Carte mentale des raisons du choix de la variation" style="min-width:560px">{"".join(out)}</svg></div>')


# ---------- Héros : la vidéo, les volcans, le titre ----------
def hero(eyebrow, title, subtitle, lede, kpis, disclaimer):
    k = "".join(f'<div class="kpi"><span class="k">{a}</span><span class="v" data-count="{c}">{b}</span><span class="s">{d}</span></div>'
                for a, b, d, c in kpis)
    return f"""
<header class="hero" id="top">
  <div class="hero-media">
    <video id="pub" autoplay muted playsinline preload="auto" poster="media/volvic-boost-poster.jpg" aria-label="Notre film publicitaire Volvic Boost">
      <source src="media/volvic-boost-pub.mp4" type="video/mp4">
    </video>
    <button class="sound" id="sound" type="button" aria-pressed="false">Activer le son</button>
    <p class="hero-tag">Notre film publicitaire · 10 secondes</p>
  </div>
  <div class="hero-range">{mountains()}</div>
  <div class="hero-text">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{title}</h1>
    <p class="sub">{subtitle}</p>
    <p class="lede">{lede}</p>
    <div class="kpis">{k}</div>
    <p class="disclaimer">{disclaimer}</p>
  </div>
</header>"""


CSS = """
/* Concept : on suit l'eau, de la source (le volcan, en haut) jusqu'à la bouteille (la décision, en bas).
   Aquarelle sur papier frais, verts d'Auvergne, rose pour la version animale comme dans notre film. */
:root{
 --bg:#ffffff;--paper:#ffffff;--surface:#ffffff;--ink:#11281c;--muted:#506559;--line:#d5e0d8;
 --accent:#0f5a36;--accent-2:#1c7a4b;--leaf:#8cc63f;--water:#2f86c0;--water-2:#9fd0ec;--mist:#dde9ee;
 --m-far:#b9d3dd;--m-mid:#8fb98f;--m-near:#2f6b45;--zone:#e5efe7;
 --a:#2F7A44;--b:#E07BA0;--sg-base:#c7d3cb;--sg-marge:#d8eedf;--sg-dist:#ece6da;--sg-tva:#e0e2ea;
 --warn-bg:#fff4e6;--warn-ink:#7a4a00;
 color-scheme:light;
 --display:"Fraunces",Georgia,serif;--body:"Figtree",system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace;--hand:"Caveat",cursive;
}

*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:70px}
body{margin:0;color:var(--ink);font:17px/1.65 var(--body);background:var(--bg) PAPER}
a{color:var(--accent-2);text-decoration-thickness:1px;text-underline-offset:3px}a:hover{color:var(--accent)}
:focus-visible{outline:3px solid var(--leaf);outline-offset:3px}

/* Barre de navigation */
.topnav{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--paper) 86%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.topnav .in{max-width:1180px;margin:0 auto;padding:10px max(16px,env(safe-area-inset-right,0px)) 10px max(16px,env(safe-area-inset-left,0px));display:flex;gap:6px 18px;flex-wrap:wrap;align-items:center}
.topnav strong{font:600 16px var(--display);color:var(--accent);margin-right:10px}
.topnav a{font-size:14px;color:var(--muted);text-decoration:none;padding:2px 0;border-bottom:2px solid transparent}
.topnav a.on{color:var(--accent);border-bottom-color:var(--water)}
.progress{position:absolute;left:0;bottom:-1px;height:3px;width:100%;transform-origin:left;transform:scaleX(0);background:linear-gradient(90deg,var(--water-2),var(--water))}

/* Héros */
.hero{position:relative;display:grid}
.hero-media{position:relative;max-width:1180px;width:100%;margin:22px auto 0;padding:0 max(16px,env(safe-area-inset-right,0px)) 0 max(16px,env(safe-area-inset-left,0px))}
.hero-media video{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;border-radius:22px 26px 18px 24px;box-shadow:0 30px 60px -30px rgba(15,60,40,.45);background:var(--mist)}
.sound{position:absolute;z-index:4;right:calc(max(16px,env(safe-area-inset-right,0px)) + 16px);top:14px;border:0;border-radius:999px;padding:9px 16px;font:600 14px var(--body);background:rgba(255,255,255,.86);color:#11281c;cursor:pointer;backdrop-filter:blur(4px)}
.sound[aria-pressed="true"]{background:#11281c;color:#fff}
.hero-tag{position:absolute;left:calc(max(16px,env(safe-area-inset-left,0px)) + 18px);top:14px;margin:0;font:500 11.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:#fff;text-shadow:0 1px 8px rgba(0,0,0,.4)}
.hero-range{height:clamp(120px,18vw,240px);margin-top:clamp(-150px,-11vw,-60px);position:relative;z-index:2;pointer-events:none;overflow:hidden}
.hero-range svg{width:100%;height:100%;display:block}
.m-far{fill:var(--m-far)}.m-mid{fill:var(--m-mid)}.m-near{fill:var(--m-near)}
.m-edge{fill:none;stroke:var(--ink);stroke-opacity:.12;stroke-width:1.5}
.ridge{will-change:transform}
.hero-text{max-width:1180px;width:100%;margin:-6px auto 0;padding:0 max(16px,env(safe-area-inset-right,0px)) 30px max(16px,env(safe-area-inset-left,0px));display:grid;gap:12px;position:relative;z-index:3}
.eyebrow,.kicker{font:500 12.5px/1.3 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--accent-2)}
h1{font:600 clamp(40px,6.4vw,82px)/.98 var(--display);font-variation-settings:"SOFT" 100,"WONK" 1;margin:0;letter-spacing:-.015em;text-wrap:balance}
h1 em{font-style:italic;color:var(--accent-2)}
.sub{font:500 clamp(20px,2.4vw,28px)/1.25 var(--display);font-variation-settings:"SOFT" 100;margin:0;color:var(--water);max-width:34ch;text-wrap:balance}
.lede{max-width:66ch;margin:4px 0 0;font-size:19px;color:var(--muted)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:12px}
.kpi{background:color-mix(in srgb,var(--surface) 92%,transparent);border:1px solid var(--line);border-radius:18px 14px 20px 12px;padding:14px 16px;display:grid;gap:2px}
.kpi .k{font:500 11.5px var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.kpi .v{font:600 32px/1.1 var(--display);color:var(--accent);font-variant-numeric:tabular-nums}
.kpi .s{font-size:14px;color:var(--muted)}
.disclaimer{font-size:13px;color:var(--muted);margin:6px 0 0}

/* La rivière */
.flowwrap{position:relative;max-width:1180px;margin:0 auto}
.river{position:absolute;left:max(4px,env(safe-area-inset-left,0px));top:0;width:84px;pointer-events:none;z-index:1;overflow:visible}
.river .bed{fill:none;stroke:var(--mist);stroke-width:10;stroke-linecap:round}
.river .run{fill:none;stroke:url(#water-grad);stroke-width:7;stroke-linecap:round}
.river .src{fill:var(--paper);stroke:var(--water);stroke-width:2.5}
.river .src.on{fill:var(--water)}
.river .num{font:600 11px var(--mono);fill:var(--muted)}
.river .drop{fill:var(--water);filter:drop-shadow(0 2px 3px rgba(47,134,192,.5))}
main{max-width:1180px;margin:0 auto;padding:0 max(16px,env(safe-area-inset-right,0px)) 64px max(16px,env(safe-area-inset-left,0px));position:relative;z-index:2}
@media (min-width:1000px){main{padding-left:110px}}
@media (max-width:999px){.river{display:none}}

/* Sections */
section{padding:64px 0 10px;border-bottom:1px dashed var(--line)}
section:last-of-type{border-bottom:0}
.sh{display:grid;gap:6px;margin-bottom:18px}
.kicker{display:flex;align-items:center;gap:8px}
.kicker::before{content:"";width:10px;height:14px;background:var(--water);border-radius:50% 50% 50% 50% / 62% 62% 38% 38%;transform:rotate(180deg)}
h2{font:600 clamp(26px,3.4vw,40px)/1.12 var(--display);font-variation-settings:"SOFT" 100;margin:0;max-width:28ch;text-wrap:balance}
h3{font:600 23px/1.3 var(--display);font-variation-settings:"SOFT" 100;margin:38px 0 8px}
h4{font:600 17px var(--body);margin:26px 0 6px;color:var(--accent-2)}
p,li,dd{max-width:72ch}
.answer{position:relative;background:var(--surface);border:1px solid var(--line);border-radius:20px 16px 22px 14px;padding:16px 20px 16px 22px;font-size:18.5px;max-width:none;overflow:hidden}
.answer::before{content:"";position:absolute;inset:0 auto 0 0;width:7px;background:linear-gradient(var(--water-2),var(--water))}
.answer span{display:block;font:500 11.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--water);margin-bottom:3px}
.note,.cnote,figcaption{color:var(--muted);font-size:15px}
figure{margin:20px 0;background:var(--surface);border:1px solid var(--line);border-radius:22px 18px 24px 16px;padding:18px;display:grid;gap:10px}
figure.duo{grid-template-columns:repeat(2,minmax(0,1fr));justify-items:center;background:#fff}
figure.duo img{max-height:330px;width:auto;max-width:100%}
figure.duo figcaption{grid-column:1/-1;color:#506559}
figure.paint{background:linear-gradient(180deg,var(--surface),color-mix(in srgb,var(--mist) 45%,var(--surface)))}
.cw{overflow-x:auto}
.chart{width:100%;height:auto;display:block;font-family:var(--body)}
.chart .t{fill:var(--ink);font-size:13px}.chart .m{fill:var(--muted);font-size:13px}.chart .s{font-size:11.5px}.chart .b{font-weight:600}
.chart .ta{fill:var(--a);font-size:14px}.chart .tb{fill:var(--ink);font-size:14px}
.chart .hand{font:600 19px var(--hand);fill:var(--accent-2)}
.chart .fa{fill:var(--a)}.chart .fb{fill:var(--b)}.chart .fn{fill:var(--line)}.chart .fk{fill:var(--accent)}
.chart .sa{stroke:var(--a)}.chart .sb{stroke:var(--b)}.chart .sk{stroke:var(--ink)}.chart .w{stroke-width:2;stroke-linecap:round}
.chart .ring{stroke:var(--surface);stroke-width:2}.chart .ax{stroke:var(--muted)}.chart .grid{stroke:var(--line)}
.chart .zone{fill:var(--zone)}.chart .thr{stroke:var(--accent);stroke-width:2;stroke-dasharray:4 3}
.chart .dot{fill:var(--ink);stroke:var(--surface);stroke-width:2}.chart .hollow{fill:var(--surface);stroke:var(--muted);stroke-width:2}
.chart .curve{fill:none;stroke-width:2.5}.chart .c-ch{stroke:var(--accent-2)}.chart .c-ex{stroke:var(--ink)}.chart .dashc{stroke-dasharray:7 4}
.chart .pt{stroke:var(--muted);stroke-dasharray:2 3}.chart .dash{stroke:var(--ink);stroke-width:1.5;stroke-dasharray:6 4}.chart .pl{stroke-width:4}
.chart .seg-base{fill:var(--sg-base)}.chart .seg-marge{fill:var(--sg-marge)}.chart .seg-dist{fill:var(--sg-dist)}.chart .seg-tva{fill:var(--sg-tva)}

/* Schéma du collagène */
.collagen .strand{fill:none;stroke-width:5;stroke-linecap:round}
.collagen .helix{animation:slide 3.2s linear infinite}
.collagen .s0{stroke:var(--accent-2)}.collagen .s1{stroke:var(--water)}.collagen .s2{stroke:var(--b)}
.collagen .mini{stroke-width:3;stroke-dasharray:none;animation:none}.collagen .sa-h{stroke:var(--a)}.collagen .sb-h{stroke:var(--b)}
.collagen .build .mini{stroke-dasharray:1;stroke-dashoffset:1;animation:build 3.4s ease-in-out infinite}
.collagen .flow{fill:none;stroke-width:2;stroke-dasharray:3 5;opacity:.7}.collagen .fa-s{stroke:var(--a)}.collagen .fb-s{stroke:var(--b)}
.collagen .leaf{fill:var(--leaf)}.collagen .leaf-vein{fill:none;stroke:var(--a);stroke-width:1.5}
.collagen .bead{fill:var(--b);opacity:.9}.collagen .body{fill:var(--mist);stroke:var(--muted);stroke-width:1.2}
@keyframes slide{to{transform:translateX(-92px)}}
@keyframes build{0%{stroke-dashoffset:1}55%,85%{stroke-dashoffset:0}100%{stroke-dashoffset:-1}}

/* Carte mentale */
.mindmap .mm-core{fill:var(--water-2);opacity:.9}
.mindmap .mm-title{font:600 21px var(--display);fill:var(--ink)}
.mindmap .mm-node{opacity:.55}.mindmap .n0{fill:var(--leaf)}.mindmap .n1{fill:var(--m-far)}.mindmap .n2{fill:var(--sg-dist)}.mindmap .n3{fill:var(--b)}
.mindmap .mm-h{font:600 16px var(--display);fill:var(--ink)}
.mindmap .v{font-size:17px}
.mindmap .mm-branch{fill:none;stroke:var(--water);stroke-width:3;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:0}

/* Tableaux et calculs */
.tw{overflow-x:auto;margin:12px 0}
table{border-collapse:collapse;width:100%;font-size:15px;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font:500 11.5px var(--mono);letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
td.num{white-space:nowrap}
.calc{background:var(--surface);border:1.5px dashed color-mix(in srgb,var(--water) 60%,var(--line));border-radius:18px 14px 20px 12px;padding:12px 18px;margin:16px 0}
.calc summary{cursor:pointer;font:600 14px var(--mono);color:var(--accent-2);letter-spacing:.02em}
.calc .tw{margin:8px 0 4px}
ul.def{padding-left:20px}ul.def li{margin:6px 0}
.ab{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:10px}
.ab h5{margin:0 0 4px;font:600 13px var(--mono);letter-spacing:.03em}
.colA{border-top:4px solid var(--a);padding-top:6px}.colA h5{color:var(--a)}
.colB{border-top:4px solid var(--b);padding-top:6px}.colB h5{color:var(--ink)}
.ab .tw{margin:0}.ab td{font-size:14px}
table.tot td:first-child{font-weight:600}
table.wf th.ca,table.wf td.ca{border-left:4px solid var(--a)}table.wf th.cb,table.wf td.cb{border-left:4px solid var(--b)}
table.wf th.ca{color:var(--a)}
ul.terms{margin:10px 0;padding-left:18px;font-size:15px}ul.terms li{margin:3px 0}
table.hyp td:nth-child(2){min-width:220px}

/* Fin : la bouteille */
.finale{margin:40px 0 0;position:relative;border-radius:26px;overflow:hidden;background:linear-gradient(180deg,var(--mist),var(--surface));border:1px solid var(--line)}
.finale .fr{height:190px}.finale .fr svg{width:100%;height:100%;display:block}
.finale p{margin:0;padding:6px 24px 24px;font:500 clamp(20px,2.4vw,28px)/1.3 var(--display);font-variation-settings:"SOFT" 100;max-width:none}
.foot{color:var(--muted);font-size:14px;padding:28px 0}

/* Apparition au défilement (navigateurs compatibles uniquement ; sinon tout est déjà visible) */
@supports (animation-timeline: view()){
 @media (prefers-reduced-motion:no-preference){
  .reveal{animation:rise linear both;animation-timeline:view();animation-range:entry 0% entry 45%}
  .mindmap .mm-branch{stroke-dashoffset:1;animation:draw linear both;animation-timeline:view();animation-range:entry 20% cover 45%}
 }
}
@keyframes rise{from{opacity:.15;transform:translateY(28px)}to{opacity:1;transform:none}}
@keyframes draw{to{stroke-dashoffset:0}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.collagen .helix,.collagen .build .mini{animation:none;stroke-dashoffset:0}}
@media (max-width:640px){.hero-tag{display:none}.topnav .in{flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;scrollbar-width:none}.topnav strong{display:none}body{font-size:16px}.ab{grid-template-columns:1fr}figure{padding:12px}figure.duo{grid-template-columns:1fr 1fr}.hero-media video{border-radius:16px}}
""".replace("PAPER", PAPER)

JS = """
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Son de la vidéo
  const v = document.getElementById('pub'), s = document.getElementById('sound');
  if (v && s) s.addEventListener('click', () => { v.muted = !v.muted; if (!v.muted) v.play(); s.setAttribute('aria-pressed', String(!v.muted)); s.textContent = v.muted ? 'Activer le son' : 'Couper le son'; });
  if (v && reduce) { v.removeAttribute('autoplay'); v.pause(); }
  const mute = () => { if (v && !v.muted) { v.muted = true; s.setAttribute('aria-pressed', 'false'); s.textContent = 'Activer le son'; } };
  if (v && 'IntersectionObserver' in window) new IntersectionObserver(es => es.forEach(e => { if (e.intersectionRatio < 0.35) mute(); }), {threshold: [0, 0.35, 1]}).observe(v);
  if (v) v.addEventListener('ended', () => { s.textContent = 'Revoir le film'; s.setAttribute('aria-pressed', 'false'); });
  if (v && s) s.addEventListener('click', () => { if (v.ended) { v.currentTime = 0; v.play(); } });

  // Compteurs des chiffres clés
  if (!reduce) document.querySelectorAll('.kpi .v[data-count]').forEach(el => {
    const target = parseFloat(el.dataset.count); if (isNaN(target)) return;
    const fmt = el.textContent, dec = (fmt.match(/,(\\d+)/) || [,''])[1].length, t0 = performance.now(), dur = 1400;
    const step = now => { const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt.replace(/[\\d]+(,[\\d]+)?/, (target * e).toFixed(dec).replace('.', ','));
      if (k < 1) requestAnimationFrame(step); else el.textContent = fmt; };
    requestAnimationFrame(step);
  });

  // La rivière : un tracé qui relie les étapes et se remplit au fil de la lecture
  const wrap = document.querySelector('.flowwrap'), svg = document.querySelector('.river');
  const heads = [...document.querySelectorAll('main section .kicker')];
  let run, len = 0, drop, srcs = [];
  function build() {
    if (!svg || getComputedStyle(svg).display === 'none') return;
    svg.setAttribute('height', 0);
    const top = wrap.getBoundingClientRect().top + scrollY, h = wrap.offsetHeight;
    svg.setAttribute('height', h); svg.setAttribute('viewBox', `0 0 84 ${h}`);
    const pts = [[42, 0], ...heads.map((el, i) => [i % 2 ? 58 : 26, el.getBoundingClientRect().top + scrollY - top + 8]), [42, h - 40]];
    let d = `M${pts[0][0]},${pts[0][1]}`;
    for (let i = 1; i < pts.length; i++) { const [x0, y0] = pts[i - 1], [x1, y1] = pts[i], m = (y1 - y0) / 2;
      d += ` C${x0},${y0 + m} ${x1},${y1 - m} ${x1},${y1}`; }
    svg.innerHTML = `<path class="bed" d="${d}"/><path class="run" d="${d}"/>` +
      pts.slice(1, -1).map((p, i) => `<circle class="src" cx="${p[0]}" cy="${p[1]}" r="9"/><text class="num" x="${p[0] + (i % 2 ? 14 : -14)}" y="${p[1] + 4}" text-anchor="${i % 2 ? 'start' : 'end'}">0${i + 1}</text>`).join('') +
      `<path class="drop" d="M0,-10 C6,-2 8,2 8,5 A8,8 0 0 1 -8,5 C-8,2 -6,-2 0,-10 Z"/>`;
    run = svg.querySelector('.run'); drop = svg.querySelector('.drop'); srcs = [...svg.querySelectorAll('.src')];
    len = run.getTotalLength(); run.style.strokeDasharray = len; update();
  }
  const bar = document.querySelector('.progress'), links = [...document.querySelectorAll('.topnav a[href^="#"]')];
  function update() {
    const doc = document.documentElement, p = Math.min(1, Math.max(0, scrollY / (doc.scrollHeight - innerHeight)));
    if (bar) bar.style.transform = `scaleX(${p})`;
    if (run) {
      const top = wrap.getBoundingClientRect().top, h = wrap.offsetHeight;
      const q = Math.min(1, Math.max(0, (innerHeight * 0.55 - top) / (h - innerHeight * 0.45))), at = len * q;
      run.style.strokeDashoffset = len - at;
      const pt = run.getPointAtLength(at); drop.setAttribute('transform', `translate(${pt.x},${pt.y})`);
      srcs.forEach(c => c.classList.toggle('on', +c.getAttribute('cy') <= pt.y + 2));
    }
    let cur = null; heads.forEach(h => { if (h.getBoundingClientRect().top < innerHeight * 0.4) cur = h.closest('section').id; });
    links.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + cur));
    if (!reduce) document.querySelectorAll('.hero .ridge').forEach(g => g.style.transform = `translateY(${Math.min(scrollY, 900) * g.dataset.depth}px)`);
  }
  addEventListener('scroll', () => requestAnimationFrame(update), {passive: true});
  addEventListener('resize', build); addEventListener('load', build);
  if (document.fonts) document.fonts.ready.then(build);
  build();
})();
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@600&family=Figtree:wght@400;500;600&'
         'family=Fraunces:opsz,wght,SOFT,WONK@9..144,500..700,100,1&family=JetBrains+Mono:wght@500&display=swap">')
