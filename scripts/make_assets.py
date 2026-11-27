"""Render the profile graphics into assets/.

Black-and-white, minimal. Effects: liquid fill of the name, line drawing, soft
shadows, paper grain and a drifting ASCII/Unicode cloud with Matrix-style
flicker and rain. Animations use SMIL (GitHub does not run CSS animations in
README images). Run: python scripts/make_assets.py
"""
import base64
import math
import os
import random
from xml.sax.saxutils import escape

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

INK, INK_2, MUTED, FAINT = "#0f0f0f", "#3a3a3a", "#8a8a8a", "#c9c9c9"
PAPER, LINE = "#ffffff", "#ebebeb"
NEUTRAL = "#8a8a8a"  # readable on both GitHub light and dark backgrounds
SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
GLYPHS = "01:+*·°%#@=アカサタナハマヤラワ"

COMMON_DEFS = f'''
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/>
  <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.022 0"/>
</filter>
<filter id="shadow" x="-10%" y="-20%" width="120%" height="150%"><feGaussianBlur stdDeviation="10"/></filter>'''


def text(x, y, s, size, fill, weight=400, anchor="start", family=SANS, spacing=0, extra=""):
    ls = f";letter-spacing:{spacing}px" if spacing else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{fill}" {extra}'
            f'style="font:{weight} {size}px {family}{ls}">{escape(s)}</text>')


def appear(delay=0.0, dur=0.7, dy=10):
    total = delay + dur
    k = delay / total
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" dur="{total:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 {dy};0 {dy};0 0" '
            f'keyTimes="0;{k:.3f};1" calcMode="spline" keySplines="0 0 1 1;0.2 0.8 0.2 1" dur="{total:.2f}s" fill="freeze"/>')


def draw(delay=0.0, dur=1.4):
    """Stroke draw-on for shapes with pathLength="1"."""
    return (f'<animate attributeName="stroke-dashoffset" values="1;1;0" keyTimes="0;{delay / (delay + dur):.3f};1" '
            f'dur="{delay + dur:.2f}s" calcMode="spline" keySplines="0 0 1 1;0.4 0 0.2 1" fill="freeze"/>')


def card_shell(x, y, w, h, r=18, delay=0.0):
    """White card with soft shadow, grain and a border that draws itself."""
    return f'''<rect x="{x}" y="{y + 8}" width="{w}" height="{h}" rx="{r}" fill="#000" opacity="0.06" filter="url(#shadow)"/>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{PAPER}"/>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{LINE}"/>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{FAINT}" stroke-width="1"
 pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">{draw(delay, 1.6)}
<animate attributeName="stroke-opacity" values="1;1;0" keyTimes="0;0.6;1" begin="{delay + 1.6:.2f}s" dur="1.2s" fill="freeze"/></rect>'''


def grain(x, y, w, h, r):
    """Paper grain laid over the whole card, including photos."""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="#fff" filter="url(#grain)"/>'


def svg(w, h, label, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(label)}"><defs>{COMMON_DEFS}{defs}</defs>{body}</svg>')


def write(name, content):
    with open(os.path.join(ASSETS, name), "w") as f:
        f.write(content)
    print(f"wrote {name} ({len(content) // 1024} KB)")


def data_uri(name):
    with open(os.path.join(ASSETS, name), "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


# ---------------------------------------------------------------- ASCII cloud
def ascii_cloud(cx, cy, seed=3):
    """A cloud made of flickering glyphs, drifting sideways, with glyph rain underneath."""
    rnd = random.Random(seed)
    puffs = [(-110, 10, 70, 38), (-40, -18, 82, 52), (45, -8, 74, 46), (120, 12, 60, 34), (0, 22, 150, 30)]
    cw, ch = 10, 13
    cells = []
    for gy in range(-78, 56, ch):
        for gx in range(-200, 200, cw):
            d = min(((gx - px) / rx) ** 2 + ((gy - py) / ry) ** 2 for px, py, rx, ry in puffs)
            if d < 1:
                cells.append((gx, gy, d))
    out = []
    for gx, gy, d in cells:
        shade = INK_2 if d < 0.3 else (MUTED if d < 0.65 else FAINT)
        g1, g2, g3 = rnd.sample(GLYPHS, 3)
        dur = rnd.uniform(1.6, 4.2)
        off = rnd.uniform(0, dur)
        x, y = cx + gx, cy + gy
        out.append(
            f'<g fill="{shade}">'
            f'<text x="{x}" y="{y}">{escape(g1)}<animate attributeName="opacity" values="1;0;0;1" keyTimes="0;0.33;0.99;1" '
            f'calcMode="discrete" dur="{dur:.2f}s" begin="-{off:.2f}s" repeatCount="indefinite"/></text>'
            f'<text x="{x}" y="{y}" opacity="0">{escape(g2)}<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;0.33;0.66;1" '
            f'calcMode="discrete" dur="{dur:.2f}s" begin="-{off:.2f}s" repeatCount="indefinite"/></text>'
            f'<text x="{x}" y="{y}" opacity="0">{escape(g3)}<animate attributeName="opacity" values="0;0;1;0" keyTimes="0;0.66;0.99;1" '
            f'calcMode="discrete" dur="{dur:.2f}s" begin="-{off:.2f}s" repeatCount="indefinite"/></text></g>')
    # glyph rain
    for i in range(14):
        x = cx + rnd.randrange(-130, 130, cw)
        dur = rnd.uniform(1.8, 3.2)
        begin = rnd.uniform(0, 3)
        col = "".join(f'<tspan x="{x}" dy="{ch if k else 0}">{escape(rnd.choice(GLYPHS))}</tspan>' for k in range(3))
        out.append(
            f'<text y="{cy + 40}" fill="{MUTED}" opacity="0">{col}'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 120" dur="{dur:.2f}s" '
            f'begin="{begin:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.8;0" dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/></text>')
    return (f'<g style="font:500 12px {MONO}">'
            f'<animateTransform attributeName="transform" type="translate" values="-60 0;60 -6;-60 0" dur="18s" '
            f'calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" repeatCount="indefinite"/>'
            + "".join(out) + "</g>")


# ---------------------------------------------------------------- header
def header():
    W, H, M = 1280, 440, 16
    CW, CH = W - 2 * M, H - 2 * M - 8
    NX, NY, NS = M + 72, M + 196, 112

    # liquid fill: a wave that rises behind the name, clipped to the letters
    wave_w = 240
    wave = "M0 0 " + " ".join(
        f"Q{x + wave_w / 4:.0f} {-12 if (x // (wave_w // 2)) % 2 == 0 else 12} {x + wave_w / 2:.0f} 0"
        for x in range(0, 2400, wave_w // 2)) + " V300 H0 Z"
    fill = f'''<clipPath id="name"><text x="{NX}" y="{NY}" style="font:800 {NS}px {SANS};letter-spacing:-4px">Bekzhan</text></clipPath>
<g clip-path="url(#name)">
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 {NY + 20};0 {NY + 20};0 {NY - NS - 30}"
      keyTimes="0;0.25;1" dur="3.4s" calcMode="spline" keySplines="0 0 1 1;0.45 0 0.25 1" fill="freeze"/>
    <path d="{wave}" fill="{INK}">
      <animateTransform attributeName="transform" type="translate" values="0 0;-{wave_w} 0" dur="1.6s" repeatCount="indefinite"/>
    </path>
  </g>
</g>
<text x="{NX}" y="{NY}" fill="none" stroke="{INK}" stroke-width="1.2" style="font:800 {NS}px {SANS};letter-spacing:-4px">Bekzhan</text>'''

    body = f'''{card_shell(M, M, CW, CH, 22)}
<clipPath id="card"><rect x="{M}" y="{M}" width="{CW}" height="{CH}" rx="22"/></clipPath>
<g clip-path="url(#card)">
  <image x="{W - 900}" y="{M}" width="900" height="165" preserveAspectRatio="xMaxYMin slice" href="{data_uri('clouds.jpg')}">
    <animateTransform attributeName="transform" type="translate" values="0 0;-24 0;0 0" dur="30s" repeatCount="indefinite"/>
  </image>
  {ascii_cloud(W - 300, M + 150)}
</g>
<g>{appear(0.1)}{text(NX + 4, M + 70, "FRONT-END DEVELOPER  /  WEB DESIGNER", 13, MUTED, 600, spacing=3)}</g>
{fill}
<path d="M{NX + 4} {NY + 46} H{NX + 560}" stroke="{INK}" stroke-width="1" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">{draw(1.6, 1.4)}</path>
<g>{appear(2.4)}
  <circle cx="{NX + 9}" cy="{NY + 84}" r="4" fill="{INK}"><animate attributeName="opacity" values="1;0.25;1" dur="2.4s" repeatCount="indefinite"/></circle>
  {text(NX + 24, NY + 89, "Open to work", 15, INK, 500)}
  {text(NX + 140, NY + 89, "Aktobe, Kazakhstan", 15, MUTED)}
  {text(NX + 300, NY + 89, "K. Zhubanov Aktobe Regional University", 15, MUTED)}
</g>
<g>{appear(2.8)}{text(W - M - 40, H - M - 38, "2026", 13, FAINT, 500, "end", MONO, 2)}</g>
{grain(M, M, CW, CH, 22)}'''
    write("header.svg", svg(W, H, "Bekzhan, Front-End Developer and Web Designer, Aktobe, Kazakhstan", body))


# ---------------------------------------------------------------- section titles: "01  About  ————"
def title(n, slug, label):
    W, H = 1280, 60
    lx = 54 + len(label) * 11.5 + 24
    body = f'''<g>{appear(0, 0.6, 6)}
{text(0, 38, f"{n:02d}", 13, NEUTRAL, 500, family=MONO, spacing=1)}
{text(40, 38, label, 22, NEUTRAL, 600, spacing=-0.3)}</g>
<path d="M{lx:.0f} 32 H{W}" stroke="{NEUTRAL}" stroke-opacity="0.45" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">{draw(0.2, 1.6)}</path>'''
    write(f"title-{slug}.svg", svg(W, H, label, body))


# ---------------------------------------------------------------- project cards
PROJECTS = [
    ("fill-ai", "Fill AI", ["Real-time AI copilot for online lectures. Turns a live",
                            "lesson into a structured summary, quizzes and flashcards."],
     ["React", "TypeScript", "Tailwind CSS", "FastAPI"], "github.com/b-beka/fill-ai"),
    ("kaytadan", "Kaytadan", ["Offline-first flashcard app with spaced repetition.",
                              "Installable as a PWA, data stays on the device."],
     ["React", "TypeScript", "Vite", "IndexedDB"], "github.com/b-beka/Kaytadan"),
    ("homeprise", "HomePrise", ["Web application that estimates house prices",
                                "from property parameters."],
     ["HTML", "CSS", "JavaScript"], "github.com/b-beka/HomePrise"),
    ("qazaq-loc-qa", "Qazaq Loc QA", ["Quality checks for the Kazakh localization of",
                                      "Flutter ARB files. Built for Decentrathon 6.0."],
     ["Python", "CLI", "i18n"], "private repository"),
]


def card(i, slug, name, desc, tags, link):
    W, H, M = 640, 236, 12
    x0, y0 = M + 32, M + 30
    lines = "".join(text(x0, y0 + 84 + n * 24, l, 15.5, INK_2) for n, l in enumerate(desc))
    arrow = "" if link.startswith("private") else (
        f'<path d="M{W - M - 44} {y0 + 6} l10 -10 M{W - M - 43} {y0 - 4} h9 v9" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    body = f'''{card_shell(M, M, W - 2 * M, H - 2 * M - 8, 18, 0.1 + i * 0.15)}
<g>{appear(0.3 + i * 0.15)}
{text(x0, y0 + 6, f"{i + 1:02d}", 12.5, MUTED, 500, family=MONO, spacing=1)}
{text(x0, y0 + 48, name, 26, INK, 700, spacing=-0.5)}
{arrow}
{lines}
{text(x0, H - M - 42, "  /  ".join(tags), 12.5, MUTED, 500, family=MONO, extra='xml:space="preserve" ')}
{text(W - M - (52 if arrow else 32), y0 + 6, link, 12.5, MUTED if arrow else FAINT, 400, "end", MONO)}
</g>
{grain(M, M, W - 2 * M, H - 2 * M - 8, 18)}'''
    write(f"card-{slug}.svg", svg(W, H, f"{name}: {' '.join(desc)}", body))


# ---------------------------------------------------------------- footer
def footer():
    W, H, M = 1280, 230, 16
    CW, CH = W - 2 * M, H - 2 * M - 8
    body = f'''{card_shell(M, M, CW, CH, 22)}
<clipPath id="card"><rect x="{M}" y="{M}" width="{CW}" height="{CH}" rx="22"/></clipPath>
<g clip-path="url(#card)">{ascii_cloud(280, M + 96, seed=9)}</g>
<g>{appear(0.2)}
{text(W - M - 64, M + 90, "Thanks for stopping by.", 28, INK, 700, "end", spacing=-0.5)}
{text(W - M - 64, M + 122, "Open to full-time roles, internships and freelance projects.", 15, MUTED, 400, "end")}
</g>
{grain(M, M, CW, CH, 22)}'''
    write("footer.svg", svg(W, H, "Thanks for stopping by. Open to full-time roles, internships and freelance projects.", body))


if __name__ == "__main__":
    header()
    for n, (slug, label) in enumerate([("about", "About"), ("stack", "Stack"), ("projects", "Selected work"),
                                       ("achievements", "Recognition"), ("activity", "Activity"), ("contact", "Contact")], 1):
        title(n, slug, label)
    for i, p in enumerate(PROJECTS):
        card(i, *p)
    footer()
