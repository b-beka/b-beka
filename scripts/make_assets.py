"""Render the static profile graphics into assets/.

Everything shares one blue-to-violet gradient and the same dark surface.
Animations use SMIL only (GitHub does not run CSS animations in README images).
Run: python scripts/make_assets.py
"""
import os
from xml.sax.saxutils import escape

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

BLUE, VIOLET = "#58a6ff", "#a371f7"
BG, SURFACE, BORDER = "#0d1117", "#161b22", "#30363d"
TEXT, MUTED = "#e6edf3", "#8b949e"
SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, Inter, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"


def gradient(id_="g", flow=True, dur=6):
    """Horizontal blue-violet gradient; with flow=True it slowly shifts back and forth."""
    anim = (f'<animate attributeName="x1" values="0;-1;0" dur="{dur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="x2" values="1;0;1" dur="{dur}s" repeatCount="indefinite"/>') if flow else ""
    return (f'<linearGradient id="{id_}" x1="0" x2="1" y1="0" y2="0">'
            f'<stop offset="0" stop-color="{BLUE}"/><stop offset="0.5" stop-color="{VIOLET}"/>'
            f'<stop offset="1" stop-color="{BLUE}"/>{anim}</linearGradient>')


def appear(delay, dur=0.8, dy=12):
    """Fade and slide in, hidden from t=0 until `delay`."""
    total = delay + dur
    k = delay / total
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" dur="{total:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 {dy};0 {dy};0 0" '
            f'keyTimes="0;{k:.3f};1" calcMode="spline" keySplines="0 0 1 1;0.2 0.8 0.2 1" '
            f'dur="{total:.2f}s" fill="freeze"/>')


def svg(w, h, label, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(label)}"><defs>{defs}</defs>{body}</svg>')


def write(name, content):
    with open(os.path.join(ASSETS, name), "w") as f:
        f.write(content)
    print("wrote", name)


# ---------------------------------------------------------------- header
def header():
    W, H = 1280, 320
    X0, Y_ROLE, SIZE = 96, 214, 28
    roles = ["Front-End Developer", "Web Designer", "React · TypeScript · Tailwind CSS", "Open to new opportunities"]
    cycle = 3.6 * len(roles)

    parts, kts, xs = [], [], []
    for i, role in enumerate(roles):
        w = len(role) * SIZE * 0.6 + 4
        s, slot = i / len(roles), 1 / len(roles)
        kt = [s, s + slot * 0.4, s + slot * 0.8, s + slot * 0.97]
        vals = [0, w, w, 0]
        kts += kt
        xs += [X0 + v for v in vals]
        if s > 0:
            kt, vals = [0.0] + kt, [0] + vals
        kt, vals = kt + [1.0], vals + [0]
        parts.append(
            f'<clipPath id="c{i}"><rect x="{X0}" y="{Y_ROLE - 38}" height="52" width="0">'
            f'<animate attributeName="width" dur="{cycle}s" repeatCount="indefinite" '
            f'keyTimes="{";".join(f"{k:.4f}" for k in kt)}" values="{";".join(f"{v:.0f}" for v in vals)}"/></rect></clipPath>'
            f'<text x="{X0}" y="{Y_ROLE}" clip-path="url(#c{i})" class="role">{escape(role)}</text>')
    kts.append(1.0)
    xs.append(X0)
    cursor = (f'<rect y="{Y_ROLE - 26}" width="3" height="32" rx="1.5" fill="url(#g)">'
              f'<animate attributeName="x" dur="{cycle}s" repeatCount="indefinite" '
              f'keyTimes="{";".join(f"{k:.4f}" for k in kts)}" values="{";".join(f"{x + 4:.0f}" for x in xs)}"/>'
              f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="0.9s" repeatCount="indefinite"/></rect>')

    blobs = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="0.22" filter="url(#soft)">'
        f'<animate attributeName="cy" values="{cy};{cy - 26};{cy}" dur="{d}s" repeatCount="indefinite"/>'
        f'<animate attributeName="cx" values="{cx};{cx + 18};{cx}" dur="{d * 1.3:.1f}s" repeatCount="indefinite"/></circle>'
        for cx, cy, r, c, d in [(1010, 110, 150, BLUE, 9), (1160, 230, 120, VIOLET, 11), (860, 260, 90, VIOLET, 13)])

    cx, cy = 860, 66
    code = [
        ('<tspan fill="#d2a8ff">const</tspan> <tspan fill="#79c0ff">profile</tspan> = {', 0),
        ('name: <tspan fill="#a5d6ff">"Bekzhan"</tspan>,', 1),
        ('role: <tspan fill="#a5d6ff">"Front-End Developer"</tspan>,', 1),
        ('location: <tspan fill="#a5d6ff">"Aktobe, KZ"</tspan>,', 1),
        ('stack: [<tspan fill="#a5d6ff">"React"</tspan>, <tspan fill="#a5d6ff">"TypeScript"</tspan>],', 1),
        ('openToWork: <tspan fill="#d2a8ff">true</tspan>,', 1),
        ("};", 0),
    ]
    window = [f'<g>{appear(0.2, 1.0)}<rect x="{cx}" y="{cy}" width="350" height="200" rx="12" fill="{SURFACE}" '
              f'fill-opacity="0.9" stroke="url(#g)" stroke-opacity="0.7"/>']
    window += [f'<circle cx="{cx + 20 + i * 16}" cy="{cy + 18}" r="4.5" fill="{c}" opacity="{o}"/>'
               for i, (c, o) in enumerate([(BLUE, 0.9), ("#7d8cf8", 0.9), (VIOLET, 0.9)])]
    window += [f'<g>{appear(0.8 + i * 0.22, 0.4, 0)}<text x="{cx + 20 + ind * 18}" y="{cy + 50 + i * 21}" class="code">{t}</text></g>'
               for i, (t, ind) in enumerate(code)]
    window.append("</g>")

    body = f'''<g clip-path="url(#r)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#grid)" opacity="0.6"/>
{blobs}
<g>{appear(0)}
<text x="{X0}" y="94" class="kicker">PORTFOLIO</text>
<text x="{X0 - 3}" y="158" class="name">Bekzhan</text>
<rect x="{X0}" y="176" width="140" height="4" rx="2" fill="url(#g)"/>
</g>
{"".join(parts)}
{cursor}
<g>{appear(0.4)}
<circle cx="{X0 + 6}" cy="264" r="5" fill="url(#g)"><animate attributeName="r" values="5;7;5" dur="1.6s" repeatCount="indefinite"/>
<animate attributeName="opacity" values="1;.5;1" dur="1.6s" repeatCount="indefinite"/></circle>
<text x="{X0 + 20}" y="270" class="meta">Available for work  ·  Aktobe, Kazakhstan  ·  K. Zhubanov Aktobe Regional University</text>
</g>
{"".join(window)}
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="url(#g)" stroke-opacity="0.6"/>'''
    defs = f'''{gradient()}
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{SURFACE}"/></linearGradient>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#21262d"/></pattern>
<clipPath id="r"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<style>
.kicker{{font:600 15px {SANS};fill:{MUTED};letter-spacing:4px}}
.name{{font:700 64px {SANS};fill:{TEXT}}}
.role{{font:500 {SIZE}px {MONO};fill:url(#g)}}
.meta{{font:400 16px {SANS};fill:{MUTED}}}
.code{{font:400 13.5px {MONO};fill:#c9d1d9}}
</style>'''
    write("header.svg", svg(W, H, "Bekzhan, Front-End Developer and Web Designer", body, defs))


# ---------------------------------------------------------------- section titles
def section(slug, title):
    W, H = 1280, 64
    body = f'''<text x="0" y="40" style="font:700 26px {SANS}" fill="url(#g)">{escape(title)}</text>
<rect x="0" y="54" width="{W}" height="1" fill="{BORDER}"/>
<rect x="0" y="53" height="3" rx="1.5" fill="url(#g)" width="0">
<animate attributeName="width" values="0;180" dur="1.2s" calcMode="spline" keySplines="0.2 0.8 0.2 1" fill="freeze"/></rect>'''
    write(f"title-{slug}.svg", svg(W, H, title, body, gradient()))


# ---------------------------------------------------------------- tech stack
STACK = [
    ("Front-end", ["HTML5", "CSS3", "JavaScript", "TypeScript", "React", "Next.js", "Tailwind CSS", "Framer Motion", "Vite"]),
    ("Back-end & tooling", ["Python", "FastAPI", "Node.js", "Docker", "Vitest", "Git", "pnpm"]),
    ("Design", ["Figma", "Photoshop", "Canva", "UI / UX", "Responsive design"]),
]


def stack():
    W, cols, gap, chip_h = 1280, 6, 14, 44
    chip_w = (W - 220 - gap * (cols - 1)) / cols
    y, out, n = 8, [], 0
    for group, items in STACK:
        rows = (len(items) + cols - 1) // cols
        out.append(f'<g>{appear(0.1 + n * 0.03)}<text x="0" y="{y + 28}" style="font:600 13px {SANS};letter-spacing:2px" fill="{MUTED}">{escape(group.upper())}</text></g>')
        for i, item in enumerate(items):
            r, c = divmod(i, cols)
            x, yy = 220 + c * (chip_w + gap), y + r * (chip_h + gap)
            out.append(
                f'<g>{appear(0.15 + n * 0.05, 0.5, 8)}'
                f'<rect x="{x:.1f}" y="{yy}" width="{chip_w:.1f}" height="{chip_h}" rx="10" fill="{SURFACE}" stroke="url(#g)" stroke-opacity="0.75"/>'
                f'<text x="{x + chip_w / 2:.1f}" y="{yy + 28}" text-anchor="middle" style="font:600 15px {SANS}" fill="{TEXT}">{escape(item)}</text></g>')
            n += 1
        y += rows * (chip_h + gap) + 18
    H = y - 10
    write("stack.svg", svg(W, H, "Tech stack: " + ", ".join(i for _, items in STACK for i in items), "".join(out), gradient()))


# ---------------------------------------------------------------- project cards
PROJECTS = [
    ("fill-ai", "Fill AI", ["Real-time AI copilot for online lectures. Turns a live",
                            "lesson into a structured summary, quizzes and flashcards."],
     ["React", "TypeScript", "Tailwind", "FastAPI"], "github.com/b-beka/fill-ai"),
    ("kaytadan", "Kaytadan", ["Offline-first flashcard app with spaced repetition.",
                              "Installable as a PWA, data stays on the device."],
     ["React", "TypeScript", "Vite", "IndexedDB"], "github.com/b-beka/Kaytadan"),
    ("homeprise", "HomePrise", ["Web application that estimates house prices",
                                "from property parameters."],
     ["HTML", "CSS", "JavaScript"], "github.com/b-beka/HomePrise"),
    ("qazaq-loc-qa", "Qazaq Loc QA", ["Quality checks for Kazakh localization of Flutter",
                                      "ARB files. Built for Decentrathon 6.0."],
     ["Python", "CLI", "i18n"], "Private repository"),
]


def card(slug, title, desc, tags, link, idx):
    W, H = 620, 210
    lines = "".join(f'<text x="32" y="{102 + i * 24}" style="font:400 16px {SANS}" fill="#c9d1d9">{escape(l)}</text>'
                    for i, l in enumerate(desc))
    x, chips = 32, []
    for t in tags:
        w = len(t) * 7.6 + 24
        chips.append(f'<rect x="{x:.0f}" y="158" width="{w:.0f}" height="26" rx="13" fill="none" stroke="url(#g)" stroke-opacity="0.8"/>'
                     f'<text x="{x + w / 2:.0f}" y="176" text-anchor="middle" style="font:500 12.5px {MONO}" fill="url(#g)">{escape(t)}</text>')
        x += w + 8
    body = f'''<g>{appear(0.1 + idx * 0.15, 0.7, 10)}
<clipPath id="cc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14"/></clipPath>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{SURFACE}"/>
<rect x="0" y="0" width="{W}" height="5" fill="url(#g)" clip-path="url(#cc)"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="none" stroke="url(#g)" stroke-opacity="0.7"/>
<text x="32" y="60" style="font:700 26px {SANS}" fill="{TEXT}">{escape(title)}</text>
<text x="{W - 32}" y="58" text-anchor="end" style="font:400 13px {MONO}" fill="{MUTED}">{escape(link)}</text>
{lines}{"".join(chips)}
</g>'''
    write(f"card-{slug}.svg", svg(W, H, f"{title}: {' '.join(desc)}", body, gradient()))


# ---------------------------------------------------------------- achievements
ACHIEVEMENTS = [
    ("Decentrathon 6.0", "Hackathon participant", "Built a localization QA tool for the Qazaq Loc QA case."),
    ("ICPC", "Competitive programming", "Contestant in the International Collegiate Programming Contest."),
    ("K. Zhubanov University", "Education", "Student at K. Zhubanov Aktobe Regional University."),
]


def achievements():
    W, row = 1280, 76
    out = []
    for i, (title, kind, text) in enumerate(ACHIEVEMENTS):
        y = i * row
        out.append(f'''<g>{appear(0.1 + i * 0.18, 0.6, 8)}
<circle cx="14" cy="{y + 30}" r="7" fill="url(#g)"/>
{f'<rect x="13" y="{y + 40}" width="2" height="{row - 20}" fill="url(#g)" opacity="0.4"/>' if i < len(ACHIEVEMENTS) - 1 else ""}
<text x="44" y="{y + 36}" style="font:700 19px {SANS}" fill="{TEXT}">{escape(title)}</text>
<text x="44" y="{y + 60}" style="font:400 15px {SANS}" fill="{MUTED}">{escape(text)}</text>
<text x="{W}" y="{y + 36}" text-anchor="end" style="font:600 12px {SANS};letter-spacing:2px" fill="url(#g)">{escape(kind.upper())}</text>
</g>''')
    write("achievements.svg", svg(W, row * len(ACHIEVEMENTS), "Achievements: " + "; ".join(a[0] for a in ACHIEVEMENTS), "".join(out), gradient()))


# ---------------------------------------------------------------- contact buttons
def button(slug, label):
    W, H = 200, 48
    body = f'''<rect width="{W}" height="{H}" rx="10" fill="url(#g)"/>
<text x="{W / 2}" y="30" text-anchor="middle" style="font:600 16px {SANS};letter-spacing:1px" fill="#ffffff">{escape(label)}</text>'''
    write(f"btn-{slug}.svg", svg(W, H, label, body, gradient(dur=5)))


# ---------------------------------------------------------------- footer
def footer():
    W, H = 1280, 90
    body = f'''<rect x="0" y="10" width="{W}" height="2" rx="1" fill="url(#g)"/>
<text x="{W / 2}" y="54" text-anchor="middle" style="font:600 17px {SANS}" fill="{TEXT}">Open to full-time roles, internships and freelance projects.</text>
<text x="{W / 2}" y="80" text-anchor="middle" style="font:400 14px {SANS}" fill="{MUTED}">The fastest way to reach me is Telegram or email.</text>'''
    write("footer.svg", svg(W, H, "Open to full-time roles, internships and freelance projects.", body, gradient()))


if __name__ == "__main__":
    header()
    for slug, title in [("about", "About"), ("stack", "Tech Stack"), ("projects", "Featured Projects"),
                        ("achievements", "Achievements"), ("activity", "GitHub Activity"), ("contact", "Contact")]:
        section(slug, title)
    stack()
    for i, p in enumerate(PROJECTS):
        card(*p, i)
    achievements()
    for slug, label in [("email", "Email"), ("telegram", "Telegram"), ("github", "GitHub")]:
        button(slug, label)
    footer()
