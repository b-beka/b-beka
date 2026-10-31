"""Render assets/header.svg: animated profile header (typing roles, floating shapes)."""
import os
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "header.svg")

NAME = "Bekzhan"
ROLES = [
    "Front-End Developer",
    "Web Designer",
    "React · TypeScript · Tailwind",
    "Open to work",
]
W, H = 1280, 320
SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, Inter, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
ROLE_SIZE, CHAR_W = 30, 0.6  # monospace advance ~0.6em
X0, Y_ROLE = 96, 212
CYCLE = 3.6 * len(ROLES)


def typing():
    n = len(ROLES)
    out, kts, xs = [], [], []
    for i, role in enumerate(ROLES):
        w = len(role) * ROLE_SIZE * CHAR_W + 4
        s, slot = i / n, 1 / n
        kt = [s, s + slot * 0.4, s + slot * 0.8, s + slot * 0.97]
        vals = [0, w, w, 0]
        kts += kt
        xs += [X0 + v for v in vals]
        if s > 0:
            kt, vals = [0.0] + kt, [0] + vals
        kt, vals = kt + [1.0], vals + [0]
        out.append(
            f'<clipPath id="c{i}"><rect x="{X0}" y="{Y_ROLE - 40}" height="56" width="0">'
            f'<animate attributeName="width" dur="{CYCLE}s" repeatCount="indefinite" '
            f'keyTimes="{";".join(f"{k:.4f}" for k in kt)}" values="{";".join(f"{v:.0f}" for v in vals)}"/></rect></clipPath>'
            f'<text x="{X0}" y="{Y_ROLE}" clip-path="url(#c{i})" class="role">{escape(role)}</text>'
        )
    kts.append(1.0)
    xs.append(X0)
    cursor = (
        f'<rect y="{Y_ROLE - 28}" width="3" height="34" rx="1.5" fill="url(#accent)">'
        f'<animate attributeName="x" dur="{CYCLE}s" repeatCount="indefinite" '
        f'keyTimes="{";".join(f"{k:.4f}" for k in kts)}" values="{";".join(f"{x + 4:.0f}" for x in xs)}"/>'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="0.9s" repeatCount="indefinite"/></rect>'
    )
    return "\n".join(out) + "\n" + cursor


def blobs():
    spec = [(1010, 120, 150, "#58a6ff", 0.22, 9), (1150, 230, 110, "#a371f7", 0.22, 11), (880, 260, 80, "#3fb950", 0.14, 13)]
    out = []
    for cx, cy, r, c, op, d in spec:
        out.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{op}" filter="url(#soft)">'
            f'<animate attributeName="cy" values="{cy};{cy - 26};{cy}" dur="{d}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cx" values="{cx};{cx + 18};{cx}" dur="{d * 1.3:.1f}s" repeatCount="indefinite"/></circle>'
        )
    return "\n".join(out)


def appear(delay, dur=0.8, dy=14):
    """SMIL fade+slide in; element is hidden from t=0 until it appears."""
    total = delay + dur
    k = delay / total
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" dur="{total:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 {dy};0 {dy};0 0" keyTimes="0;{k:.3f};1" '
            f'calcMode="spline" keySplines="0 0 1 1;0.2 0.8 0.2 1" dur="{total:.2f}s" fill="freeze"/>')


def code_window():
    x, y = 860, 70
    lines = [
        ('<tspan fill="#ff7b72">const</tspan> <tspan fill="#d2a8ff">bekzhan</tspan> = {', 0),
        ('role: <tspan fill="#a5d6ff">"Front-End Developer"</tspan>,', 1),
        ('city: <tspan fill="#a5d6ff">"Aktobe, KZ"</tspan>,', 1),
        ('stack: [<tspan fill="#a5d6ff">"React"</tspan>, <tspan fill="#a5d6ff">"TS"</tspan>],', 1),
        ('openToWork: <tspan fill="#79c0ff">true</tspan>,', 1),
        ("};", 0),
    ]
    out = [
        f'<g>{appear(0.2, 1.0)}<rect x="{x}" y="{y}" width="340" height="190" rx="12" fill="#161b22" fill-opacity="0.85" stroke="#30363d"/>',
        *[f'<circle cx="{x + 20 + i * 16}" cy="{y + 18}" r="5" fill="{c}"/>' for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"])],
    ]
    for i, (t, ind) in enumerate(lines):
        out.append(
            f'<g>{appear(0.8 + i * 0.25, 0.4, 0)}<text x="{x + 20 + ind * 18}" y="{y + 54 + i * 22}" class="code">{t}</text></g>'
        )
    out.append("</g>")
    return "\n".join(out)


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Bekzhan — Front-End Developer and Web Designer">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#161b22"/></linearGradient>
<linearGradient id="accent" x1="0" x2="1"><stop offset="0" stop-color="#58a6ff"/><stop offset="0.5" stop-color="#a371f7"/><stop offset="1" stop-color="#58a6ff"/>
<animate attributeName="x1" values="0;-1;0" dur="6s" repeatCount="indefinite"/><animate attributeName="x2" values="1;0;1" dur="6s" repeatCount="indefinite"/></linearGradient>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#21262d" stroke-width="1"/></pattern>
<clipPath id="r"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<style>
.name{{font:700 64px {SANS};fill:#e6edf3}}
.hi{{font:500 20px {SANS};fill:#8b949e;letter-spacing:1px}}
.role{{font:500 {ROLE_SIZE}px {MONO};fill:#79c0ff}}
.meta{{font:400 16px {SANS};fill:#8b949e}}
.code{{font:400 14px {MONO};fill:#c9d1d9}}
</style>
</defs>
<g clip-path="url(#r)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#grid)" opacity="0.6"/>
{blobs()}
<g>{appear(0)}
<text x="{X0}" y="96" class="hi">HI THERE, I'M</text>
<text x="{X0 - 3}" y="160" class="name">{NAME}</text>
<rect x="{X0}" y="176" width="120" height="4" rx="2" fill="url(#accent)"/>
</g>
{typing()}
<g>{appear(0.4)}
<circle cx="{X0 + 6}" cy="262" r="5" fill="#3fb950"><animate attributeName="r" values="5;7;5" dur="1.6s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;.5;1" dur="1.6s" repeatCount="indefinite"/></circle>
<text x="{X0 + 20}" y="268" class="meta">Available for work  ·  Aktobe, Kazakhstan  ·  K. Zhubanov University</text>
</g>
{code_window()}
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="#30363d"/>
</svg>'''

with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT)
