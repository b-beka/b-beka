"""Render the profile graphics into assets/.

Palette comes from the banner photo (assets/banner.jpg): sky blue, cloud white and
field green. The sky-to-field gradient is used only for thin accents.
Animations use SMIL and play once (GitHub does not run CSS animations in README images).
Run: python scripts/make_assets.py
"""
import base64
import os
from xml.sax.saxutils import escape

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

SKY, GRASS = "#3c688a", "#3f7a2a"
CLOUD, CLOUD_LINE = "#f7f6ef", "#dcdccd"
INK, INK_SOFT, MUTED = "#1f2f3a", "#33454f", "#5e6b72"
NEUTRAL = "#7a8a94"  # readable on both GitHub light and dark backgrounds
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

GRADIENT = (f'<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{SKY}"/>'
            f'<stop offset="1" stop-color="{GRASS}"/></linearGradient>')


def appear(delay=0.0, dur=0.7, dy=10):
    """Fade and slide in once."""
    total = delay + dur
    k = delay / total
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" dur="{total:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 {dy};0 {dy};0 0" '
            f'keyTimes="0;{k:.3f};1" calcMode="spline" keySplines="0 0 1 1;0.2 0.8 0.2 1" dur="{total:.2f}s" fill="freeze"/>')


def text(x, y, s, size, fill, weight=400, anchor="start", family=SANS, spacing=0):
    ls = f";letter-spacing:{spacing}px" if spacing else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{fill}" '
            f'style="font:{weight} {size}px {family}{ls}">{escape(s)}</text>')


def svg(w, h, label, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(label)}"><defs>{GRADIENT}{defs}</defs>{body}</svg>')


def write(name, content):
    with open(os.path.join(ASSETS, name), "w") as f:
        f.write(content)
    print("wrote", name)


def data_uri(name):
    with open(os.path.join(ASSETS, name), "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


# ---------------------------------------------------------------- header: photo + profile card
def header():
    W, PH = 1280, 360            # photo height matches banner.jpg aspect (2400x674)
    CX, CY, CW, CH = 48, 268, 760, 168
    H = CY + CH + 14
    card = f'''<g>{appear(0.3, 0.8, 14)}
<rect x="{CX}" y="{CY + 6}" width="{CW}" height="{CH}" rx="14" fill="{INK}" opacity="0.12" filter="url(#shadow)"/>
<rect x="{CX}" y="{CY}" width="{CW}" height="{CH}" rx="14" fill="{CLOUD}" stroke="{CLOUD_LINE}"/>
{text(CX + 36, CY + 64, "Bekzhan", 44, INK, 700)}
{text(CX + 36, CY + 98, "Front-End Developer  ·  Web Designer", 18, INK_SOFT, 500)}
<rect x="{CX + 36}" y="{CY + 116}" height="3" rx="1.5" fill="url(#g)" width="0">
<animate attributeName="width" values="0;0;120" keyTimes="0;0.5;1" dur="1.6s" calcMode="spline" keySplines="0 0 1 1;0.2 0.8 0.2 1" fill="freeze"/></rect>
<circle cx="{CX + 42}" cy="{CY + 142}" r="4.5" fill="{GRASS}"/>
{text(CX + 54, CY + 147, "Open to work  ·  Aktobe, Kazakhstan  ·  K. Zhubanov Aktobe Regional University", 14, MUTED)}
</g>'''
    body = (f'<image x="0" y="0" width="{W}" height="{PH}" preserveAspectRatio="xMidYMid slice" '
            f'clip-path="url(#photo)" href="{data_uri("banner.jpg")}"/>\n{card}')
    defs = (f'<clipPath id="photo"><rect width="{W}" height="{PH}" rx="16"/></clipPath>'
            f'<filter id="shadow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="8"/></filter>')
    write("header.svg", svg(W, H, "Bekzhan, Front-End Developer and Web Designer, Aktobe, Kazakhstan", body, defs))


# ---------------------------------------------------------------- section titles (centred label between two lines)
def title(slug, label):
    W, H = 1280, 56
    half = len(label) * 6.2 + 28
    body = f'''<rect x="{W / 2 - half - 340:.0f}" y="31" width="340" height="1.5" fill="url(#l)"/>
<rect x="{W / 2 + half:.0f}" y="31" width="340" height="1.5" fill="url(#r)"/>
{text(W / 2, 37, label.upper(), 15, NEUTRAL, 600, "middle", spacing=4)}'''
    defs = (f'<linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{SKY}" stop-opacity="0"/><stop offset="1" stop-color="{SKY}"/></linearGradient>'
            f'<linearGradient id="r" x1="1" x2="0"><stop offset="0" stop-color="{GRASS}" stop-opacity="0"/><stop offset="1" stop-color="{GRASS}"/></linearGradient>')
    write(f"title-{slug}.svg", svg(W, H, label, body, defs))


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


def card(slug, name, desc, tags, link, i):
    W, H = 620, 200
    lines = "".join(text(32, 98 + n * 24, l, 15.5, INK_SOFT) for n, l in enumerate(desc))
    x, chips = 32, []
    for t in tags:
        w = len(t) * 7.4 + 22
        chips.append(f'<rect x="{x:.0f}" y="150" width="{w:.0f}" height="26" rx="6" fill="#ecebe0"/>'
                     + text(x + w / 2, 167.5, t, 12.5, SKY, 500, "middle", MONO))
        x += w + 8
    body = f'''<g>{appear(0.1 + i * 0.12)}
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{CLOUD}" stroke="{CLOUD_LINE}"/>
<rect x="0" y="0" width="{W}" height="4" fill="url(#g)" clip-path="url(#c)"/>
{text(32, 58, name, 24, INK, 700)}
{text(W - 32, 56, link, 12.5, MUTED, 400, "end", MONO)}
{lines}{"".join(chips)}
</g>'''
    write(f"card-{slug}.svg", svg(W, H, f"{name}: {' '.join(desc)}", body,
                                  f'<clipPath id="c"><rect width="{W}" height="{H}" rx="14"/></clipPath>'))


# ---------------------------------------------------------------- footer: field strip from the photo
def footer():
    W, H = 1280, 147  # footer.jpg is 2400x276
    body = (f'<image width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" clip-path="url(#f)" '
            f'href="{data_uri("footer.jpg")}"/>')
    write("footer.svg", svg(W, H, "Green field under a cloudy sky", body,
                            f'<clipPath id="f"><rect width="{W}" height="{H}" rx="16"/></clipPath>'))


if __name__ == "__main__":
    header()
    for slug, label in [("about", "About"), ("stack", "Tech Stack"), ("projects", "Projects"),
                        ("achievements", "Achievements"), ("activity", "Activity"), ("contact", "Contact")]:
        title(slug, label)
    for i, p in enumerate(PROJECTS):
        card(*p, i)
    footer()
