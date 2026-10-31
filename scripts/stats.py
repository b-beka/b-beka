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

INK, INK2, INK3, MUTED = "#2c3f41", "#3d5254", "#5f7674", "#7d908e"
BG, LINE = "#e8ecec", "#c9d1d1"
SHADES = ["#d5dcdc", "#a9b8b6", "#7d938f", "#4f6a68", "#22383b"]
LANG_SHADES = ["#22383b", "#40585a", "#5f7674", "#7d908e", "#98a9a7", "#b9c4c3"]
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
        o.append(f'<text x="{x:.0f}" y="62" text-anchor="middle" font-size="12" letter-spacing="3" fill="{MUTED}">{escape(label.upper())}</text>')
        o.append(f'<text x="{x:.0f}" y="108" text-anchor="middle" font-size="40" font-weight="300" fill="{INK}">{val}</text>')
        o.append(f'<text x="{x:.0f}" y="132" text-anchor="middle" font-size="12" fill="{INK3}">{escape(sub)}</text>')

    # language bar
    y = 180
    o.append(f'<text x="40" y="{y}" font-size="12" letter-spacing="3" fill="{MUTED}">LANGUAGES</text>')
    o.append(f'<clipPath id="bar"><rect x="40" y="{y + 14}" width="{W - 80}" height="10" rx="5"/></clipPath><g clip-path="url(#bar)">')
    x = 40.0
    for i, (name, size) in enumerate(top):
        w = (W - 80) * size / total
        o.append(f'<rect x="{x:.1f}" y="{y + 14}" width="{w + 1:.1f}" height="10" fill="{LANG_SHADES[i]}"/>')
        x += w
    o.append(f'<rect x="{x:.1f}" y="{y + 14}" width="{W:.0f}" height="10" fill="{LINE}"/></g>')
    x = 40.0
    for i, (name, size) in enumerate(top):
        label = f"{name} {100 * size / total:.1f}%"
        o.append(f'<circle cx="{x + 5:.0f}" cy="{y + 45}" r="5" fill="{LANG_SHADES[i]}"/>')
        o.append(f'<text x="{x + 16:.0f}" y="{y + 49}" font-size="13" fill="{INK2}">{escape(label)}</text>')
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
            o.append(f'<rect x="{gx + wi * (cell + gap):.1f}" y="{y0 + wd * (cell + gap)}" width="{cell}" height="{cell}" rx="3" fill="{shade}"><title>{d["date"]}: {c}</title></rect>')
    o.append(f'<text x="{W - 40}" y="{H - 12}" text-anchor="end" font-size="11" fill="{MUTED}">updated {dt.date.today().isoformat()}</text>')
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    with open(OUT, "w") as f:
        f.write(render(fetch()))
    print("wrote", OUT)
