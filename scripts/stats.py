"""Render assets/stats.svg and assets/activity.svg (plus dark/ variants) from the GitHub GraphQL API.

Run by .github/workflows/stats.yml with GITHUB_TOKEN. Standard library only.
"""
import datetime as dt
import json
import os
import urllib.request
from xml.sax.saxutils import escape

LOGIN = os.environ.get("GH_LOGIN", "b-beka")
TOKEN = os.environ["GITHUB_TOKEN"]
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

# Palette taken from the profile banner: sky blue, cloud white and field green.
# Black and white, matching the rest of the profile; one palette per GitHub theme.
THEMES = {
    "stats.svg": dict(
        INK="#0f0f0f", INK2="#3a3a3a", MUTED="#8a8a8a", FAINT="#c9c9c9",
        PAPER="#ffffff", LINE="#ebebeb", TRACK="#f0f0f0", SHADOW=0.06,
        GRAIN="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.022 0",
        SHADES=["#f0f0f0", "#cfcfcf", "#9a9a9a", "#5c5c5c", "#111111"],
        LANG_SHADES=["#111111", "#444444", "#6e6e6e", "#959595", "#b9b9b9", "#d6d6d6"]),
    "dark/stats.svg": dict(
        INK="#f2f2f2", INK2="#cfcfcf", MUTED="#8a8a8a", FAINT="#4a4a4a",
        PAPER="#0e0e0e", LINE="#232323", TRACK="#1c1c1c", SHADOW=0.5,
        GRAIN="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.035 0",
        SHADES=["#1c1c1c", "#3d3d3d", "#6e6e6e", "#a8a8a8", "#efefef"],
        LANG_SHADES=["#efefef", "#bdbdbd", "#949494", "#6e6e6e", "#4f4f4f", "#383838"]),
}
globals().update(THEMES["stats.svg"])
FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def fade(delay, dur=0.5):
    total = delay + dur
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{delay / total:.3f};1" '
            f'dur="{total:.2f}s" fill="freeze"/>')


def odometer(value, x, y, size, uid, delay):
    """Number whose digits roll up from 0 like a mechanical counter. x is the centre."""
    digits = str(value)
    adv, lh = size * 0.62, size * 1.15
    left = x - adv * len(digits) / 2
    out = [f'<clipPath id="od{uid}"><rect x="{left - 4:.1f}" y="{y - size:.1f}" width="{adv * len(digits) + 8:.1f}" height="{lh:.1f}"/></clipPath>',
           f'<g clip-path="url(#od{uid})" style="font:600 {size}px {FONT};font-variant-numeric:tabular-nums" fill="{INK}">']
    for i, d in enumerate(digits):
        target = 10 + int(d)                     # spin through one full turn, then land
        col = "".join(f'<tspan x="{left + i * adv + adv / 2:.1f}" dy="{lh if k else 0:.1f}">{k % 10}</tspan>' for k in range(target + 1))
        dur = 1.4 + 0.18 * (len(digits) - i)
        out.append(f'<text y="{y}" text-anchor="middle">{col}'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 {-target * lh:.1f}" '
                   f'keyTimes="0;{delay / (delay + dur):.3f};1" calcMode="spline" keySplines="0 0 1 1;0.3 0 0.15 1" '
                   f'dur="{delay + dur:.2f}s" fill="freeze"/></text>')
    out.append("</g>")
    return "".join(out)


def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today not started yet
        i -= 1
    while i >= 0 and counts[i]:
        current += 1
        i -= 1
    return current, longest


def render(u):
    cc = u["contributionsCollection"]
    weeks = cc["contributionCalendar"]["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    current, longest = streaks(days)
    langs = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]

    W, M, P = 1280, 16, 56
    cell, gap = 15, 5
    y_cal = M + 318
    H = y_cal + 7 * (cell + gap) + 44 + M
    CW, CH = W - 2 * M, H - 2 * M - 8
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub activity for {LOGIN}">',
         f'<defs><filter id="shadow" x="-10%" y="-20%" width="120%" height="150%"><feGaussianBlur stdDeviation="10"/></filter>'
         '<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/>'
         f'<feColorMatrix values="{GRAIN}"/></filter></defs>',
         f'<style>text{{font-family:{FONT}}}</style>',
         f'<rect x="{M}" y="{M + 8}" width="{CW}" height="{CH}" rx="22" fill="#000" opacity="{SHADOW}" filter="url(#shadow)"/>',
         f'<rect x="{M}" y="{M}" width="{CW}" height="{CH}" rx="22" fill="{PAPER}" stroke="{LINE}"/>',
         f'<rect x="{M}" y="{M}" width="{CW}" height="{CH}" rx="22" fill="none" stroke="{FAINT}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
         '<animate attributeName="stroke-dashoffset" values="1;0" dur="1.6s" calcMode="spline" keySplines="0.4 0 0.2 1" fill="freeze"/>'
         '<animate attributeName="stroke-opacity" values="1;0" begin="1.6s" dur="1.2s" fill="freeze"/></rect>']

    metrics = [
        (cc["contributionCalendar"]["totalContributions"], "Contributions", "last 12 months"),
        (cc["totalCommitContributions"] + cc["restrictedContributionsCount"], "Commits", "including private"),
        (cc["totalPullRequestContributions"], "Pull requests", "last 12 months"),
        (current, "Current streak", "days"),
        (longest, "Longest streak", "days"),
    ]
    tw = (W - 2 * M - 2 * P) / len(metrics)
    for i, (val, label, sub) in enumerate(metrics):
        cx = M + P + i * tw + tw / 2
        if i:
            o.append(f'<path d="M{M + P + i * tw:.0f} {M + 52} v96" stroke="{LINE}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
                     f'<animate attributeName="stroke-dashoffset" values="1;1;0" keyTimes="0;0.4;1" dur="1.4s" fill="freeze"/></path>')
        o.append(f'<g>{fade(0.1 + i * 0.1)}<text x="{cx:.0f}" y="{M + 70}" text-anchor="middle" font-size="12" font-weight="600" letter-spacing="2.5" fill="{MUTED}">{escape(label.upper())}</text></g>')
        o.append(odometer(val, cx, M + 122, 44, i, 0.3 + i * 0.12))
        o.append(f'<g>{fade(0.6 + i * 0.1)}<text x="{cx:.0f}" y="{M + 148}" text-anchor="middle" font-size="12.5" fill="{FAINT}">{escape(sub)}</text></g>')

    # languages: bar draws from the left
    y = M + 206
    x0, bw = M + P, W - 2 * M - 2 * P
    o.append(f'<text x="{x0}" y="{y}" font-size="12" font-weight="600" letter-spacing="2.5" fill="{MUTED}">LANGUAGES</text>')
    o.append(f'<clipPath id="bar"><rect x="{x0}" y="{y + 16}" width="{bw}" height="6" rx="3"/></clipPath>'
             f'<clipPath id="grow"><rect x="{x0}" y="{y + 10}" height="20" width="0"><animate attributeName="width" values="0;0;{bw}" keyTimes="0;0.3;1" dur="2.2s" calcMode="spline" keySplines="0 0 1 1;0.4 0 0.2 1" fill="freeze"/></rect></clipPath>'
             f'<rect x="{x0}" y="{y + 16}" width="{bw}" height="6" rx="3" fill="{TRACK}"/>'
             f'<g clip-path="url(#bar)"><g clip-path="url(#grow)">')
    x = float(x0)
    for i, (name, size) in enumerate(top):
        w = bw * size / total
        o.append(f'<rect x="{x:.1f}" y="{y + 16}" width="{w + 1:.1f}" height="6" fill="{LANG_SHADES[i]}"/>')
        x += w
    o.append("</g></g>")
    x = float(x0)
    for i, (name, size) in enumerate(top):
        label = f"{name}  {100 * size / total:.1f}%"
        o.append(f'<g>{fade(1.0 + i * 0.08)}<circle cx="{x + 4:.0f}" cy="{y + 45}" r="4" fill="{LANG_SHADES[i]}" stroke="{LINE}"/>'
                 f'<text x="{x + 14:.0f}" y="{y + 49}" font-size="13" fill="{INK2}" xml:space="preserve">{escape(label)}</text></g>')
        x += 34 + len(label) * 7.2

    # contribution calendar: fills in a wave from left to right
    o.append(f'<text x="{x0}" y="{y_cal - 18}" font-size="12" font-weight="600" letter-spacing="2.5" fill="{MUTED}">CONTRIBUTIONS</text>')
    peak = max((d["contributionCount"] for d in days), default=0) or 1
    gx = M + (CW - len(weeks) * (cell + gap) + gap) / 2
    for wi, w in enumerate(weeks):
        cells = []
        for d in w["contributionDays"]:
            wd = dt.date.fromisoformat(d["date"]).isoweekday() % 7
            c = d["contributionCount"]
            shade = SHADES[0] if not c else SHADES[min(4, 1 + int(3.999 * c / peak))]
            cells.append(f'<rect x="{gx + wi * (cell + gap):.1f}" y="{y_cal + wd * (cell + gap)}" width="{cell}" height="{cell}" rx="3.5" fill="{shade}">'
                         f'<title>{d["date"]}: {c}</title></rect>')
        delay = 1.2 + wi * 0.03
        o.append(f'<g>{fade(delay, 0.35)}'
                 f'<animateTransform attributeName="transform" type="translate" values="0 6;0 6;0 0" keyTimes="0;{delay / (delay + 0.5):.3f};1" dur="{delay + 0.5:.2f}s" fill="freeze"/>'
                 + "".join(cells) + "</g>")
    o.append(f'<text x="{W - M - P}" y="{H - M - 26}" text-anchor="end" font-size="11.5" fill="{FAINT}" font-family="{MONO}">updated {dt.date.today().isoformat()}</text>')
    o.append(f'<rect x="{M}" y="{M}" width="{CW}" height="{CH}" rx="22" fill="#fff" filter="url(#grain)"/>')
    o.append("</svg>")
    return "\n".join(o)


def render_activity(u):
    """Weekly contributions as a line graph that draws itself from left to right."""
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    starts = [dt.date.fromisoformat(w["contributionDays"][0]["date"]) for w in weeks]
    peak = max(weekly) or 1
    W, H, M, P = 1280, 330, 16, 56
    CW, CH = W - 2 * M, H - 2 * M - 8
    x0, x1, yb, yt = M + P + 24, W - M - P, M + 236, M + 76
    n = max(1, len(weekly) - 1)
    pts = [(x0 + i * (x1 - x0) / n, yb - v / peak * (yb - yt)) for i, v in enumerate(weekly)]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = line + f" L{x1} {yb} L{x0} {yb}Z"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Weekly contributions over the last 12 months, peak {peak} in a week">',
         f'<defs><filter id="shadow" x="-10%" y="-20%" width="120%" height="150%"><feGaussianBlur stdDeviation="10"/></filter>'
         '<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/>'
         f'<feColorMatrix values="{GRAIN}"/></filter>'
         f'<clipPath id="draw"><rect x="{x0 - 6}" y="0" height="{H}" width="0"><animate attributeName="width" values="0;0;{x1 - x0 + 12}" '
         'keyTimes="0;0.2;1" dur="2.8s" calcMode="spline" keySplines="0 0 1 1;0.4 0 0.2 1" fill="freeze"/></rect></clipPath></defs>',
         f'<style>text{{font-family:{FONT}}}</style>',
         f'<rect x="{M}" y="{M + 8}" width="{CW}" height="{CH}" rx="22" fill="#000" opacity="{SHADOW}" filter="url(#shadow)"/>',
         f'<rect x="{M}" y="{M}" width="{CW}" height="{CH}" rx="22" fill="{PAPER}" stroke="{LINE}"/>',
         f'<text x="{M + P}" y="{M + 46}" font-size="12" font-weight="600" letter-spacing="2.5" fill="{MUTED}">WEEKLY CONTRIBUTIONS</text>',
         f'<text x="{W - M - P}" y="{M + 46}" text-anchor="end" font-size="12.5" fill="{FAINT}" font-family="{MONO}">peak {peak} / week</text>']
    for k in range(4):
        y = yb - k * (yb - yt) / 3
        o.append(f'<path d="M{x0} {y:.1f} H{x1}" stroke="{LINE}"/>'
                 f'<text x="{x0 - 14}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="{FAINT}" font-family="{MONO}">{round(peak * k / 3)}</text>')
    seen = set()
    for i, d in enumerate(starts):
        if d.day <= 7 and d.month not in seen:
            seen.add(d.month)
            o.append(f'<text x="{pts[i][0]:.1f}" y="{yb + 26}" text-anchor="middle" font-size="11.5" fill="{MUTED}">{d.strftime("%b")}</text>')
    o.append(f'<g clip-path="url(#draw)"><path d="{area}" fill="{INK}" opacity="0.06"/>'
             f'<path d="{line}" fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    for (x, y), v in zip(pts, weekly):
        if v:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"><title>{v}</title></circle>')
    o.append("</g>")
    o.append(f'<rect x="{M}" y="{M}" width="{CW}" height="{CH}" rx="22" fill="#fff" filter="url(#grain)"/>')
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    user = fetch()
    for name, theme in THEMES.items():
        globals().update(theme)
        outputs = {name: render(user), name.replace("stats.svg", "activity.svg"): render_activity(user)}
        for out_name, content in outputs.items():
            path = os.path.join(ASSETS, out_name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            print("wrote", path)
