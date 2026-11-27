"""Render the profile graphics into assets/ (light) and assets/dark/ (dark).

Minimal black and white. Effects: liquid fill of the name over a drifting cloud
photo, line drawing, soft shadows, paper grain, a scrolling stack marquee and a
footer where the same cloud is rebuilt from dithered pixels. The README picks the
light or dark file with <picture> and prefers-color-scheme.

Animations use SMIL (GitHub does not run CSS animations in README images).
Run: python scripts/make_assets.py   (standard library only)
"""
import base64
import os
import random
from xml.sax.saxutils import escape

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

THEMES = {
    "light": dict(dir="assets", clouds="clouds-light.jpg", bg=255, ink="#0f0f0f", ink2="#3a3a3a", muted="#8a8a8a", faint="#c9c9c9",
                  paper="#ffffff", line="#ebebeb", shadow=0.06, grain="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.022 0",
                  pixels=["#7d7d7d", "#a3a3a3", "#c6c6c6", "#e0e0e0"]),
    "dark": dict(dir="assets/dark", clouds="clouds-dark.jpg", bg=14, ink="#f2f2f2", ink2="#cfcfcf", muted="#8a8a8a", faint="#4a4a4a",
                 paper="#0e0e0e", line="#232323", shadow=0.5, grain="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.035 0",
                 pixels=["#4d4d4d", "#7c7c7c", "#b3b3b3", "#ededed"]),
}
T = THEMES["light"]  # current theme, switched in main()


# ---------------------------------------------------------------- helpers
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
    """Card with soft shadow and a border that draws itself."""
    return f'''<rect x="{x}" y="{y + 8}" width="{w}" height="{h}" rx="{r}" fill="#000" opacity="{T['shadow']}" filter="url(#shadow)"/>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{T['paper']}"/>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{T['line']}"/>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{T['faint']}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">{draw(delay, 1.6)}
<animate attributeName="stroke-opacity" values="1;1;0" keyTimes="0;0.6;1" begin="{delay + 1.6:.2f}s" dur="1.2s" fill="freeze"/></rect>'''


def grain(x, y, w, h, r):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="#fff" filter="url(#grain)"/>'


def svg(w, h, label, body, defs=""):
    common = (f'<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" '
              f'baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="{T["grain"]}"/></filter>'
              f'<filter id="shadow" x="-10%" y="-20%" width="120%" height="150%"><feGaussianBlur stdDeviation="10"/></filter>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(label)}"><defs>{common}{defs}</defs>{body}</svg>')


def write(name, content):
    path = os.path.join(ROOT, T["dir"], name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"wrote {T['dir']}/{name} ({len(content) // 1024} KB)")


def data_uri(name):
    with open(os.path.join(ROOT, "assets", name), "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


# ---------------------------------------------------------------- pixel cloud
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


# ---------------------------------------------------------------- name decode (text scramble)
NOISE = "!<>-_/[]{}=+*^?#01アカサ"


def decode_name(name, x, y, size, style, width, start, dur):
    """The name is revealed left to right in letter-sized steps; just ahead of the edge a few
    cells of random glyphs flicker, so it reads as text being decoded. Works with any font,
    because the final name is a single normal text element."""
    steps = len(name)
    step_w = width / steps
    keys = ";".join(f"{i / steps:.4f}" for i in range(steps + 1))
    widths = ";".join(f"{i * step_w:.1f}" for i in range(steps + 1))
    shifts = ";".join(f"{i * step_w:.1f} 0" for i in range(steps + 1))
    timing = f'begin="{start}s" dur="{dur}s" calcMode="discrete" keyTimes="{keys}" fill="freeze"'
    rnd = random.Random(8)
    noise = []
    for slot in range(3):
        cx = x + step_w * (slot + 0.5)
        glyphs = []
        for k in range(3):
            vals = ";".join("1" if j == k else "0" for j in range(3))
            glyphs.append(f'<text x="{cx:.1f}" y="{y - size * 0.06:.1f}" text-anchor="middle" fill="{T["muted"]}" opacity="{1 if k == 0 else 0}" '
                          f'style="font:400 {size * 0.62:.0f}px {MONO}">{escape(rnd.choice(NOISE))}'
                          f'<animate attributeName="opacity" values="{vals}" dur="{0.18 + slot * 0.05:.2f}s" calcMode="discrete" repeatCount="indefinite"/></text>')
        noise.append(f'<g opacity="{1 - slot * 0.3:.1f}">{"".join(glyphs)}</g>')
    return f'''<clipPath id="reveal"><rect x="{x - 6}" y="{y - size}" height="{size * 1.35:.0f}" width="0">
  <animate attributeName="width" values="{widths}" {timing}/></rect></clipPath>
<text x="{x}" y="{y}" fill="{T["ink"]}" clip-path="url(#reveal)" style="{style}">{escape(name)}</text>
<g opacity="0">
  <set attributeName="opacity" to="1" begin="{start}s"/>
  <animate attributeName="opacity" values="1;0" begin="{start + dur:.2f}s" dur="0.3s" fill="freeze"/>
  <animateTransform attributeName="transform" type="translate" values="{shifts}" {timing}/>
  {"".join(noise)}
</g>'''


# ---------------------------------------------------------------- header
def header():
    W, H, M = 1280, 440, 16
    CW, CH = W - 2 * M, H - 2 * M - 8
    NX, NY, NS = M + 72, M + 188, 92
    ink, muted, faint = T["ink"], T["muted"], T["faint"]

    name = "Tlektes Bekzhan"
    name_style = f"font:300 {NS}px {SANS};letter-spacing:-3px"
    fill = decode_name(name, NX, NY, NS, name_style, width=680, start=0.4, dur=2.2)

    body = f'''{card_shell(M, M, CW, CH, 22)}
<clipPath id="card"><rect x="{M}" y="{M}" width="{CW}" height="{CH}" rx="22"/></clipPath>
<g clip-path="url(#card)">
  <image x="{M - 40}" y="{M}" width="{CW + 80}" height="{CH}" preserveAspectRatio="xMidYMid slice" href="{data_uri(T['clouds'])}">
    <animateTransform attributeName="transform" type="translate" values="0 0;-40 0;0 0" dur="40s" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;1" dur="1.6s" fill="freeze"/>
  </image>
</g>
<g>{appear(0.1)}{text(NX + 4, M + 70, "FRONT-END DEVELOPER  /  WEB DESIGNER", 13, muted, 600, spacing=3)}</g>
{fill}
<path d="M{NX + 4} {NY + 46} H{NX + 700}" stroke="{ink}" stroke-width="1" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">{draw(1.6, 1.4)}</path>
<g>{appear(2.4)}
  <circle cx="{NX + 9}" cy="{NY + 84}" r="4" fill="{ink}"><animate attributeName="opacity" values="1;0.25;1" dur="2.4s" repeatCount="indefinite"/></circle>
  {text(NX + 24, NY + 89, "Open to work", 15, ink, 500)}
  {text(NX + 140, NY + 89, "Aktobe, Kazakhstan", 15, muted)}
  {text(NX + 300, NY + 89, "K. Zhubanov Aktobe Regional University", 15, muted)}
</g>
<g>{appear(2.8)}{text(W - M - 40, H - M - 38, "2026", 13, faint, 500, "end", MONO, 2)}</g>
{grain(M, M, CW, CH, 22)}'''
    write("header.svg", svg(W, H, "Tlektes Bekzhan, Front-End Developer and Web Designer, Aktobe, Kazakhstan", body))


# ---------------------------------------------------------------- section titles: "01  About  ————"
def title(n, slug, label):
    W, H = 1280, 60
    lx = 54 + len(label) * 11.5 + 24
    c = T["muted"]
    body = f'''<g>{appear(0, 0.6, 6)}
{text(0, 38, f"{n:02d}", 13, c, 500, family=MONO, spacing=1)}
{text(40, 38, label, 22, T["ink"], 600, spacing=-0.3)}</g>
<path d="M{lx:.0f} 32 H{W}" stroke="{c}" stroke-opacity="0.45" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">{draw(0.2, 1.6)}</path>'''
    write(f"title-{slug}.svg", svg(W, H, label, body))


# ---------------------------------------------------------------- stack marquee
ROWS = [
    (["TypeScript", "JavaScript", "React", "Next.js", "Tailwind CSS", "Framer Motion", "HTML", "CSS"], 1, 34),
    (["Python", "FastAPI", "Node.js", "Docker", "Vite", "Vitest", "Git", "Figma", "Photoshop"], -1, 40),
]


def marquee():
    W, H = 1280, 112
    size, spacing = 15, 2
    adv = size * 0.6 + spacing           # monospace advance including letter-spacing
    rows = []
    for i, (items, direction, dur) in enumerate(ROWS):
        unit = "  ·  ".join(i.upper() for i in items) + "  ·  "
        width = len(unit) * adv
        reps = int(W / width) + 2
        y = 42 + i * 44
        frm, to = (0, -width) if direction > 0 else (-width, 0)
        rows.append(
            f'<g>{appear(0.2 + i * 0.2, 0.8, 0)}<text x="0" y="{y}" xml:space="preserve" fill="{T["ink"] if i == 0 else T["muted"]}" '
            f'style="font:500 {size}px {MONO};letter-spacing:{spacing}px">{escape(unit * reps)}'
            f'<animateTransform attributeName="transform" type="translate" values="{frm:.1f} 0;{to:.1f} 0" dur="{dur}s" repeatCount="indefinite"/>'
            f'</text></g>')
    defs = ('<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset="0.12" stop-color="#fff"/><stop offset="0.88" stop-color="#fff"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>')
    body = (f'<path d="M0 0.5 H{W}" stroke="{T["line"]}"/><path d="M0 {H - 0.5} H{W}" stroke="{T["line"]}"/>'
            f'<g mask="url(#m)">{"".join(rows)}</g>')
    label = "Stack: " + ", ".join(i for items, _, _ in ROWS for i in items)
    write("stack.svg", svg(W, H, label, body, defs))


# ---------------------------------------------------------------- skills orbit
ORBITS = [
    (70, ["React", "TypeScript", "Tailwind CSS"], 26),
    (118, ["Next.js", "JavaScript", "Framer Motion", "Figma"], 38),
    (162, ["Python", "FastAPI", "Node.js", "Docker", "Vite", "Git"], 54),
]


def orbit():
    W, H, M = 1280, 420, 16
    CW, CH = W - 2 * M, H - 2 * M - 8
    cx, cy = W / 2, M + CH / 2
    out = [card_shell(M, M, CW, CH, 22)]
    for i, (r, items, dur) in enumerate(ORBITS):
        rx, ry = r * 2.6, r * 0.78
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.0f}" ry="{ry:.0f}" fill="none" stroke="{T["line"]}" '
                   f'pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">{draw(0.2 + i * 0.2, 1.6)}</ellipse>')
        path = f"M{cx + rx:.0f} {cy} A{rx:.0f} {ry:.0f} 0 1 1 {cx - rx:.0f} {cy} A{rx:.0f} {ry:.0f} 0 1 1 {cx + rx:.0f} {cy}"
        for k, it in enumerate(items):
            w = len(it) * 8 + 26
            out.append(f'<g><g>{appear(0.8 + i * 0.25 + k * 0.06, 0.6, 0)}'
                       f'<rect x="{-w / 2:.0f}" y="-15" width="{w:.0f}" height="30" rx="15" fill="{T["paper"]}" stroke="{T["faint"]}"/>'
                       f'{text(0, 5, it, 13, T["ink2"], 500, "middle", MONO)}</g>'
                       f'<animateMotion dur="{dur}s" begin="-{dur * k / len(items):.2f}s" repeatCount="indefinite" path="{path}"/></g>')
    out.append(f'<g>{appear(0.2, 0.8, 0)}<circle cx="{cx}" cy="{cy}" r="36" fill="{T["ink"]}"/>'
               f'{text(cx, cy + 6, "TB", 17, T["paper"], 600, "middle")}</g>')
    out.append(grain(M, M, CW, CH, 22))
    label = "Core stack: " + ", ".join(i for _, items, _ in ORBITS for i in items)
    write("orbit.svg", svg(W, H, label, "".join(out)))


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
    ink, muted, faint = T["ink"], T["muted"], T["faint"]
    lines = "".join(text(x0, y0 + 84 + n * 24, l, 15.5, T["ink2"]) for n, l in enumerate(desc))
    arrow = "" if link.startswith("private") else (
        f'<path d="M{W - M - 44} {y0 + 6} l10 -10 M{W - M - 43} {y0 - 4} h9 v9" fill="none" stroke="{ink}" stroke-width="1.3"/>')
    body = f'''{card_shell(M, M, W - 2 * M, H - 2 * M - 8, 18, 0.1 + i * 0.15)}
<g>{appear(0.3 + i * 0.15)}
{text(x0, y0 + 6, f"{i + 1:02d}", 12.5, muted, 500, family=MONO, spacing=1)}
{text(x0, y0 + 48, name, 26, ink, 700, spacing=-0.5)}
{arrow}
{lines}
{text(x0, H - M - 42, "  /  ".join(tags), 12.5, muted, 500, family=MONO, extra='xml:space="preserve" ')}
{text(W - M - (52 if arrow else 32), y0 + 6, link, 12.5, muted if arrow else faint, 400, "end", MONO)}
</g>
{grain(M, M, W - 2 * M, H - 2 * M - 8, 18)}'''
    write(f"card-{slug}.svg", svg(W, H, f"{name}: {' '.join(desc)}", body))


# ---------------------------------------------------------------- footer: the header cloud, rebuilt from pixels
def tone(v):
    """Map photo brightness (0-255) to the same washed-out grey the header photo uses."""
    if T["bg"] > 128:
        return 255 - (255 - v) * 0.42
    return 14 + (v / 255) ** 1.6 * 150


def footer_cloud(x0, y0, cell):
    with open(os.path.join(ROOT, "scripts", "footer_map.txt")) as f:
        rows = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    gh, gw = len(rows), len(rows[0])
    s = cell - 1
    chunk = 25                                   # columns per reveal step
    buckets = {}                                 # (chunk, grey) -> path parts
    bright = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            v = int(ch, 32) * 8 + 4
            t = min(1, max(0, (x / gw - 0.28) / 0.47))
            t = t * t * (3 - 2 * t)              # same left-to-right fade as the header photo
            if BAYER[y % 4][x % 4] / 16 >= t:
                continue
            g = tone(v)
            g = T["bg"] + (g - T["bg"]) * (0.35 + 0.65 * t)
            if abs(g - T["bg"]) < 7:
                continue
            g = int(round(g / 12) * 12)
            g = max(0, min(255, g))
            buckets.setdefault((x // chunk, g), []).append(f"M{x0 + x * cell} {y0 + y * cell}h{s}v{s}h-{s}z")
            if v > 150 and t > 0.6:
                bright.append((x, y))
    n_chunks = gw // chunk + 1
    groups = []
    for c in range(n_chunks):
        parts = "".join(f'<path d="{"".join(p)}" fill="#{g:02x}{g:02x}{g:02x}"/>'
                        for (cc, g), p in sorted(buckets.items()) if cc == c)
        if parts:
            delay = 0.2 + (n_chunks - 1 - c) * 0.12   # pixels arrive from the right
            groups.append(f'<g>{appear(delay, 0.6, 0)}{parts}</g>')
    rnd = random.Random(11)
    twinkle = []
    for k in range(4):
        pick = rnd.sample(bright, min(len(bright), 60))
        d = "".join(f"M{x0 + x * cell} {y0 + y * cell}h{s}v{s}h-{s}z" for x, y in pick)
        twinkle.append(f'<path d="{d}" fill="{T["ink"]}" opacity="0"><animate attributeName="opacity" values="0;0.35;0" '
                       f'dur="{rnd.uniform(2, 3.6):.2f}s" begin="{1.5 + k * 0.6:.1f}s" repeatCount="indefinite"/></path>')
    return (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;30 0;0 0" dur="40s" '
            f'calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" repeatCount="indefinite"/>'
            + "".join(groups) + "".join(twinkle) + "</g>")


def footer():
    W, H, M = 1280, 240, 16
    CW, CH = W - 2 * M, H - 2 * M - 8
    body = f'''{card_shell(M, M, CW, CH, 22)}
<clipPath id="card"><rect x="{M}" y="{M}" width="{CW}" height="{CH}" rx="22"/></clipPath>
<g clip-path="url(#card)">{footer_cloud(M, M, 5)}</g>
<g>{appear(0.2)}
{text(M + 64, M + 96, "Thanks for stopping by.", 30, T["ink"], 300, spacing=-0.5)}
{text(M + 64, M + 130, "Open to full-time roles, internships and freelance projects.", 15, T["muted"])}
</g>
{grain(M, M, CW, CH, 22)}'''
    write("footer.svg", svg(W, H, "Thanks for stopping by. Open to full-time roles, internships and freelance projects.", body))


def main():
    global T
    for theme in THEMES.values():
        T = theme
        header()
        for n, (slug, label) in enumerate([("about", "About"), ("stack", "Stack"), ("projects", "Selected work"),
                                           ("achievements", "Recognition"), ("activity", "Activity"), ("contact", "Contact")], 1):
            title(n, slug, label)
        orbit()
        marquee()
        for i, p in enumerate(PROJECTS):
            card(i, *p)
        footer()


if __name__ == "__main__":
    main()
