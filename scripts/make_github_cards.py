#!/usr/bin/env python3
"""Generate the hero, link pills, "On GitHub" stats panel and contribution
heatmap used at the top of README.md (assets/gh/*.svg).

Live numbers come from the GitHub GraphQL API. Token: $GITHUB_TOKEN, or
`gh auth token` when run locally.    python3 scripts/make_github_cards.py
Runs every night from .github/workflows/cards.yml.
"""
import datetime as dt
import json
import os
import subprocess
import urllib.request
from html import escape
from pathlib import Path

USER = "BEAJousama"
OUT = Path(__file__).resolve().parent.parent / "assets" / "gh"

# ---- static profile facts (edit here) ---------------------------------------
NAME = "Ousama"
LOGO = "ob"
TAGLINE = "Software engineer: fullstack, systems & security, in production."
DOMAIN = "obeaj.me"
PILLS = [("fullstack", "blue"), ("systems & kernels", "amber"),
         ("security", "purple"), ("open to PFE", "red")]
LINKS = [  # file, label, color, icon
    ("portfolio", "obeaj.me", "#e8553d", "globe"),
    ("linkedin", "LinkedIn", "#0a66c2", "in"),
    ("email", "ousama@obeaj.me", "#3fb950", "mail"),
    ("blog", "blog.obeaj.me", "#a371f7", "pen"),
]
FIXED_TILES = [  # big, sub, color (live contributions tile is added first)
    ("16 months", "in production,\nFutureCorp Paris", "green"),
    ("20.43", "level at 1337 / 42,\nRNCP 7 title", "amber"),
    ("3 apps", "live in production,\nself-hosted", "purple"),
]

# ---- palette (matches the reference design) ---------------------------------
MONO = 'ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace'
PANEL, PANEL_EDGE, DOT = "#161b2e", "#2a3150", "#252c47"
TILE = {  # bg, border, hard shadow, accent
    "blue":   ("#2a5d93", "#3d7cc0", "#0e2340", "#ff8a5c"),
    "green":  ("#2e6b3f", "#43905a", "#10301b", "#ff8a5c"),
    "amber":  ("#87561f", "#b0772f", "#3a240c", "#ff8a5c"),
    "purple": ("#56428f", "#7a62c4", "#231a44", "#ff8a5c"),
    "slate":  ("#1f3442", "#2f4d60", "#0c161d", "#ff8a5c"),
}
PILL = {"blue": ("#1d4e89", "#cfe3ff"), "amber": ("#7a4c12", "#ffd9a0"),
        "purple": ("#4a3a85", "#e0d4ff"), "red": ("#7a2335", "#ffd0d8")}
HEAT = ["#2a303c", "#0e4429", "#006d32", "#26a641", "#39d353"]


def cw(size):  # monospace advance width
    return size * 0.61


def frame(w, h, body, label):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">
  <defs>
    <pattern id="dots" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{DOT}"/></pattern>
  </defs>
  <style>text {{ font-family: {MONO}; }} .b {{ font-weight: 800; }}</style>
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{PANEL}" stroke="{PANEL_EDGE}" stroke-width="1.5"/>
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#dots)"/>
{body}
</svg>
'''


def tile(x, y, w, h, color, inner):
    bg, edge, shadow, _ = TILE[color]
    return (f'  <rect x="{x+5}" y="{y+5}" width="{w}" height="{h}" rx="10" fill="{shadow}"/>\n'
            f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{bg}" stroke="{edge}" stroke-width="1.5"/>\n'
            + inner)


# ---- data --------------------------------------------------------------------
def gql(query):
    token = os.environ.get("GITHUB_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": query}).encode(),
                                 headers={"Authorization": f"bearer {token}"})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]


def fetch():
    u = gql(f'''{{ user(login: "{USER}") {{
      createdAt
      contributionsCollection {{ contributionCalendar {{ totalContributions
        weeks {{ contributionDays {{ date contributionCount }} }} }} }}
      repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {{
        totalCount nodes {{ stargazerCount }} }} }} }}''')["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]
    return {
        "total": cal["totalContributions"],
        "days": days,
        "repos": u["repositories"]["totalCount"],
        "stars": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        "since": int(u["createdAt"][:4]),
    }


# ---- cards ---------------------------------------------------------------------
def hero():
    w, h = 880, 230
    b = []
    # logo
    b.append(tile(36, 40, 92, 92, "slate", ""))
    b.append(f'  <rect x="36" y="40" width="92" height="92" rx="12" fill="#f0f6fc"/>')
    b.append(f'  <rect x="50" y="54" width="64" height="64" rx="8" fill="#0d1117"/>')
    b.append(f'  <text x="82" y="97" text-anchor="middle" class="b" font-size="34" fill="#22d3ee">{LOGO}</text>')
    # title with highlighted name
    fs, tx, ty = 46, 156, 98
    pre = "Hi, I'm "
    nx = tx + cw(fs) * len(pre)
    nw = cw(fs) * len(NAME) + 20
    b.append(f'  <rect x="{nx-10:.0f}" y="{ty-44}" width="{nw:.0f}" height="58" rx="6" fill="#b4344d"/>')
    b.append(f'  <text x="{tx}" y="{ty}" class="b" font-size="{fs}" fill="#f0f6fc">{escape(pre)}<tspan fill="#ffffff">{escape(NAME)}</tspan></text>')
    b.append(f'  <text x="{tx}" y="{ty+38}" font-size="16" fill="#c9d1d9">{escape(TAGLINE)}</text>')
    # pills
    px = tx
    for text, c in PILLS:
        bg, fg = PILL[c]
        pw = cw(13) * len(text) + 24
        b.append(f'  <rect x="{px}" y="{ty+60}" width="{pw:.0f}" height="26" rx="6" fill="{bg}"/>')
        b.append(f'  <text x="{px+pw/2:.0f}" y="{ty+78}" text-anchor="middle" class="b" font-size="13" fill="{fg}">{escape(text)}</text>')
        px += pw + 10
    # domain sticker
    dw = cw(15) * len(DOMAIN) + 28
    b.append(f'  <g transform="rotate(-4 {w-40-dw/2:.0f} 46)">'
             f'<rect x="{w-40-dw+4:.0f}" y="{30+4}" width="{dw:.0f}" height="34" rx="6" fill="#5c1d12"/>'
             f'<rect x="{w-40-dw:.0f}" y="30" width="{dw:.0f}" height="34" rx="6" fill="#e8553d"/>'
             f'<text x="{w-40-dw/2:.0f}" y="52" text-anchor="middle" class="b" font-size="15" fill="#fff">{DOMAIN}</text></g>')
    return frame(w, h, "\n".join(b), f"Hi, I'm {NAME}. {TAGLINE} " + ", ".join(p for p, _ in PILLS))


ICONS = {
    "globe": '<circle cx="0" cy="0" r="7" fill="none" stroke="#fff" stroke-width="1.6"/><ellipse cx="0" cy="0" rx="3" ry="7" fill="none" stroke="#fff" stroke-width="1.4"/><line x1="-7" y1="0" x2="7" y2="0" stroke="#fff" stroke-width="1.4"/>',
    "in": '<rect x="-7" y="-7" width="14" height="14" rx="2" fill="#fff"/><text x="0" y="4.5" text-anchor="middle" class="b" font-size="11" fill="#0a66c2">in</text>',
    "mail": '<rect x="-8" y="-5.5" width="16" height="11" rx="2" fill="none" stroke="#fff" stroke-width="1.6"/><path d="M-8 -5 L0 1 L8 -5" fill="none" stroke="#fff" stroke-width="1.6"/>',
    "pen": '<path d="M-6 6 L-5 2 L3 -6 L6 -3 L-2 5 Z" fill="none" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/>',
}


def link_pill(label, color, icon):
    w = int(cw(14) * len(label) + 62)
    h = 40
    body = (f'  <rect x="4" y="4" width="{w-8}" height="{h-8}" rx="6" fill="#0c0f1a"/>\n'
            f'  <rect x="1" y="1" width="{w-8}" height="{h-8}" rx="6" fill="#1b2133" stroke="{color}" stroke-width="1.5"/>\n'
            f'  <rect x="9" y="8" width="22" height="18" rx="4" fill="{color}"/>\n'
            f'  <g transform="translate(20 17) scale(0.85)">{ICONS[icon]}</g>\n'
            f'  <text x="41" y="22" class="b" font-size="14" fill="#f0f6fc">{escape(label)}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">\n'
            f'  <style>text {{ font-family: {MONO}; }} .b {{ font-weight: 800; }}</style>\n{body}\n</svg>\n')


def big_tile(x, y, w, h, color, big, sub, icon):
    t = [f'  <text x="{x+18}" y="{y+52}" class="b" font-size="26" fill="#ffffff">{escape(big)}</text>']
    for i, line in enumerate(sub.split("\n")):
        t.append(f'  <text x="{x+18}" y="{y+80+i*18}" font-size="13" fill="#e6edf3" opacity=".92">{escape(line)}</text>')
    t.append(f'  <g transform="translate({x+w-26} {y+22})">{icon}</g>')
    return tile(x, y, w, h, color, "\n".join(t) + "\n")


TILE_ICONS = {
    "cal": '<rect x="-8" y="-7" width="16" height="14" rx="2" fill="#ff8a5c"/><rect x="-8" y="-7" width="16" height="4" fill="#d9542e"/>',
    "flame": '<path d="M0 -9 C5 -3 7 1 5 5 C3 9 -3 9 -5 5 C-7 1 -3 -2 0 -9 Z" fill="#ff8a5c"/>',
    "trophy": '<path d="M-6 -8 H6 V-2 C6 3 -6 3 -6 -2 Z" fill="#ffd166"/><rect x="-1.5" y="2" width="3" height="4" fill="#ffd166"/><rect x="-5" y="6" width="10" height="3" rx="1" fill="#ffd166"/>',
    "bars": '<rect x="-8" y="0" width="4" height="8" fill="#ff8a5c"/><rect x="-2" y="-5" width="4" height="13" fill="#ff8a5c"/><rect x="4" y="-9" width="4" height="17" fill="#ff8a5c"/>',
    "folder": '<path d="M-10 -6 H-3 L-1 -3 H10 V8 H-10 Z" fill="#e8763d"/>',
    "star": '<path d="M0 -9 L2.6 -2.8 L9 -2.8 L3.9 1.2 L5.8 8 L0 4 L-5.8 8 L-3.9 1.2 L-9 -2.8 L-2.6 -2.8 Z" fill="#ff6b6b"/>',
    "clock": '<circle cx="0" cy="0" r="9" fill="#3fb950"/><path d="M0 -5 V0 L4 3" stroke="#0d1117" stroke-width="2" fill="none"/>',
}


def stats(d):
    w, h = 880, 330
    b = [f'  <text x="32" y="50" class="b" font-size="24" fill="#f0f6fc">On GitHub</text>',
         f'  <text x="{w-32}" y="48" text-anchor="end" font-size="13" fill="#8b949e">refreshes every night · {dt.date.today().strftime("%d %b %Y")}</text>']
    tiles = [(f"{d['total']:,}", "contributions in\nthe last year", "blue", "cal")]
    icons = ["flame", "trophy", "bars"]
    tiles += [(big, sub, c, icons[i]) for i, (big, sub, c) in enumerate(FIXED_TILES)]
    tw, gap, x0 = 190, 17, 32
    for i, (big, sub, c, ic) in enumerate(tiles):
        b.append(big_tile(x0 + i * (tw + gap), 78, tw, 130, c, big, sub, TILE_ICONS[ic]))
    years = dt.date.today().year - d["since"]
    small = [(d["repos"], "public repos", "folder"), (d["stars"], "stars earned", "star"),
             (years, f"years on GitHub", "clock")]
    sw = (w - 64 - 2 * 20) / 3
    for i, (n, label, ic) in enumerate(small):
        x = 32 + i * (sw + 20)
        inner = (f'  <g transform="translate({x+28:.0f} 263)">{TILE_ICONS[ic]}</g>\n'
                 f'  <text x="{x+52:.0f}" y="272" class="b" font-size="24" fill="#ffffff">{n}</text>\n'
                 f'  <text x="{x+52+cw(24)*len(str(n))+10:.0f}" y="270" class="b" font-size="14" fill="#c9d1d9">{label}</text>\n')
        b.append(tile(x, 236, sw, 52, "slate", inner))
    label = (f"On GitHub: {d['total']} contributions in the last year. " +
             " ".join(f"{a}: {s.replace(chr(10), ' ')}." for a, s, _ in FIXED_TILES) +
             f" {d['repos']} public repos, {d['stars']} stars, {years} years on GitHub.")
    return frame(w, h, "\n".join(b), label)


def heatmap(d):
    days = d["days"][-26 * 7:]
    # align to full weeks starting Sunday
    while dt.date.fromisoformat(days[0][0]).weekday() != 6:
        days = days[1:]
    cols = [days[i:i + 7] for i in range(0, len(days), 7)]
    total = sum(c for _, c in days)
    mx = max([c for _, c in days] + [1])
    cell, gap, x0, y0 = 26, 4, 36, 104
    w = x0 * 2 + len(cols) * (cell + gap) - gap
    h = y0 + 7 * (cell + gap) + 52
    b = [f'  <text x="{x0}" y="50" class="b" font-size="22" fill="#f0f6fc">{total:,}<tspan font-weight="400" font-size="15" fill="#c9d1d9"> contributions in the last 6 months</tspan></text>']
    starts = []  # (column, month) where a month begins; drop a label squeezed by the next one
    for ci, col in enumerate(cols):
        m = dt.date.fromisoformat(col[0][0]).strftime("%b")
        if not starts or starts[-1][1] != m:
            starts.append((ci, m))
    starts = [s for i, s in enumerate(starts) if i + 1 == len(starts) or starts[i + 1][0] - s[0] >= 3]
    for ci, m in starts:
        b.append(f'  <text x="{x0 + ci * (cell + gap)}" y="{y0-12}" font-size="13" fill="#8b949e">{m}</text>')
    for ci, col in enumerate(cols):
        x = x0 + ci * (cell + gap)
        for ri, (_, c) in enumerate(col):
            y = y0 + ri * (cell + gap)
            lvl = 0 if c == 0 else min(4, 1 + int(3 * (c / mx) ** 0.5 + 0.5))
            fg = "#6e7681" if lvl == 0 else ("#0d1117" if lvl == 4 else "#e6edf3")
            b.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="{HEAT[lvl]}"/>'
                     f'<text x="{x+cell/2}" y="{y+17}" text-anchor="middle" class="b" font-size="{10 if c < 100 else 8}" fill="{fg}">{c}</text>')
    ly = h - 26
    b.append(f'  <text x="{x0}" y="{ly+4}" font-size="12" fill="#8b949e">contributions per day</text>')
    lx = w - x0 - 5 * 18 - 80
    b.append(f'  <text x="{lx}" y="{ly+4}" font-size="12" fill="#8b949e">Less</text>')
    for i, c in enumerate(HEAT):
        b.append(f'  <rect x="{lx+38+i*18}" y="{ly-8}" width="14" height="14" rx="3" fill="{c}"/>')
    b.append(f'  <text x="{lx+38+5*18+4}" y="{ly+4}" font-size="12" fill="#8b949e">More</text>')
    return frame(w, h, "\n".join(b), f"{total} contributions in the last 6 months, per day heatmap")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = fetch()
    (OUT / "hero.svg").write_text(hero())
    for f, label, color, icon in LINKS:
        (OUT / f"link-{f}.svg").write_text(link_pill(label, color, icon))
    (OUT / "stats.svg").write_text(stats(d))
    (OUT / "heatmap.svg").write_text(heatmap(d))
    print(f"wrote {OUT} · {d['total']} contributions, {d['repos']} repos, {d['stars']} stars")


if __name__ == "__main__":
    main()
