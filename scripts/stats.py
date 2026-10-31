"""Render assets/stats.svg (misty-forest style) from the GitHub GraphQL API.

Run by .github/workflows/stats.yml with GITHUB_TOKEN. Standard library only.
"""
import datetime as dt
import json
import os
import urllib.request
from xml.sax.saxutils import escape

LOGIN = os.environ.get("GH_LOGIN", "b-beka")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "stats.svg")

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

INK, INK2, INK3, MUTED = "#e6edf3", "#c9d1d9", "#8b949e", "#8b949e"
BG, LINE = "#0d1117", "#30363d"
SHADES = ["#161b22", "#0d3a6b", "#1f6feb", "#58a6ff", "#a5d6ff"]
LANG_COLORS = {"TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3572A5", "HTML": "#e34c26",
               "CSS": "#663399", "Dart": "#00B4AB", "Shell": "#89e051", "PowerShell": "#012456",
               "Go": "#00ADD8", "Java": "#b07219", "C++": "#f34b7d", "Vue": "#41b883"}
FALLBACK = ["#a371f7", "#3fb950", "#d29922", "#f778ba", "#79c0ff", "#ffa657"]
FONT = "'Segoe UI', Inter, -apple-system, Helvetica, Arial, sans-serif"


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


def fade(delay, dur=0.6):
    total = delay + dur
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{delay / total:.3f};1" '
            f'dur="{total:.2f}s" fill="freeze"/>')


def color(name, i):
    return LANG_COLORS.get(name, FALLBACK[i % len(FALLBACK)])


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
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    langs = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]

    W, H = 1280, 430
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub stats for {LOGIN}">',
         f'<rect width="{W}" height="{H}" rx="18" fill="{BG}" stroke="{LINE}"/>',
         f'<style>text{{font-family:{FONT}}}</style>']

    tiles = [
        ("contributions", cc["contributionCalendar"]["totalContributions"], "last 12 months"),
        ("commits", cc["totalCommitContributions"] + cc["restrictedContributionsCount"], "incl. private"),
        ("pull requests", cc["totalPullRequestContributions"], "last 12 months"),
        ("current streak", current, f"longest · {longest} days"),
        ("repositories", u["repositories"]["totalCount"], f"{stars} star{'' if stars == 1 else 's'} · {u['followers']['totalCount']} follower{'' if u['followers']['totalCount'] == 1 else 's'}"),
    ]
    tw = (W - 80) / len(tiles)
    for i, (label, val, sub) in enumerate(tiles):
        x = 40 + i * tw + tw / 2
        if i:
            o.append(f'<rect x="{40 + i * tw:.0f}" y="44" width="1" height="92" fill="{LINE}"/>')
        o.append(f'<g>{fade(0.1 + i * 0.12)}')
        o.append(f'<text x="{x:.0f}" y="62" text-anchor="middle" font-size="12" letter-spacing="2" fill="{MUTED}">{escape(label.upper())}</text>')
        o.append(f'<text x="{x:.0f}" y="108" text-anchor="middle" font-size="40" font-weight="600" fill="{INK}">{val}</text>')
        o.append(f'<text x="{x:.0f}" y="132" text-anchor="middle" font-size="12" fill="{INK3}">{escape(sub)}</text></g>')

    # language bar
    y = 180
    o.append(f'<text x="40" y="{y}" font-size="12" letter-spacing="3" fill="{MUTED}">LANGUAGES</text>')
    o.append(f'<rect x="40" y="{y + 14}" width="{W - 80}" height="10" rx="5" fill="#21262d"/>')
    o.append(f'<clipPath id="bar"><rect x="40" y="{y + 14}" width="{W - 80}" height="10" rx="5"/></clipPath>'
             f'<clipPath id="grow"><rect x="40" y="{y + 10}" height="20" width="0"><animate attributeName="width" values="0;0;{W - 80}" keyTimes="0;0.3;1" dur="2s" calcMode="spline" keySplines="0 0 1 1;0.2 0.8 0.2 1" fill="freeze"/></rect></clipPath>'
             f'<g clip-path="url(#bar)"><g clip-path="url(#grow)">')
    x = 40.0
    for i, (name, size) in enumerate(top):
        w = (W - 80) * size / total
        o.append(f'<rect x="{x:.1f}" y="{y + 14}" width="{w + 1:.1f}" height="10" fill="{color(name, i)}"/>')
        x += w
    o.append('</g></g>')
    x = 40.0
    for i, (name, size) in enumerate(top):
        label = f"{name} {100 * size / total:.1f}%"
        o.append(f'<g>{fade(0.9 + i * 0.1)}<circle cx="{x + 5:.0f}" cy="{y + 45}" r="5" fill="{color(name, i)}"/>')
        o.append(f'<text x="{x + 16:.0f}" y="{y + 49}" font-size="13" fill="{INK2}">{escape(label)}</text></g>')
        x += 30 + len(label) * 7.4

    # contribution calendar
    y0, cell, gap = 268, 15, 4
    o.append(f'<text x="40" y="{y0 - 14}" font-size="12" letter-spacing="3" fill="{MUTED}">CONTRIBUTIONS</text>')
    peak = max((d["contributionCount"] for d in days), default=0) or 1
    gx = (W - len(weeks) * (cell + gap)) / 2
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            wd = dt.date.fromisoformat(d["date"]).isoweekday() % 7
            c = d["contributionCount"]
            shade = SHADES[0] if not c else SHADES[min(4, 1 + int(3.999 * c / peak))]
            o.append(f'<rect x="{gx + wi * (cell + gap):.1f}" y="{y0 + wd * (cell + gap)}" width="{cell}" height="{cell}" rx="3" fill="{shade}">{fade(1.2 + wi * 0.025, 0.4)}<title>{d["date"]}: {c}</title></rect>')
    o.append(f'<text x="{W - 40}" y="{H - 12}" text-anchor="end" font-size="11" fill="{MUTED}">updated {dt.date.today().isoformat()}</text>')
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    with open(OUT, "w") as f:
        f.write(render(fetch()))
    print("wrote", OUT)
