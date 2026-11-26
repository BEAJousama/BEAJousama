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


SNAKE = ["#22d3ee", "#22d3ee", "#1fb8d0", "#1a9cb2", "#168196", "#11677a"]  # head → tail
LOOP_TARGET = 32.0  # seconds for one full hunt; per-step speed adapts to the route length


def lattice(a, b, rnd):
    """Random monotone grid walk from a to b (both (col, row)), excluding a."""
    (c, r), (c2, r2) = a, b
    moves = ["h"] * abs(c2 - c) + ["v"] * abs(r2 - r)
    rnd.shuffle(moves)
    out = []
    for m in moves:
        if m == "h":
            c += 1 if c2 > c else -1
        else:
            r += 1 if r2 > r else -1
        out.append((c, r))
    return out


def snake_route(food, start, rnd):
    """Head path: hunt every food cell (nearest-ish, random choices), then go home.
    Returns a closed list of grid points, one step apart."""
    route, pos, left = [start], start, set(food)
    left.discard(start)
    while left:
        near = sorted(left, key=lambda f: (abs(f[0] - pos[0]) + abs(f[1] - pos[1]), rnd.random()))
        target = rnd.choice(near[:3])
        for p in lattice(pos, target, rnd):
            route.append(p)
            left.discard(p)
        pos = target
    route += lattice(pos, start, rnd)
    return route  # route[-1] == start, so the loop is seamless


def heatmap(d):
    """One year of contributions. A snake hunts the green cells on a random route
    (re-rolled every night), the total counts down as it eats, then it slides back
    to the start, the grid grows back, and it goes again forever.
    Pure SMIL on one master clock, so it loops inside GitHub's <img> rendering."""
    import random
    days = d["days"][-52 * 7:]
    while dt.date.fromisoformat(days[0][0]).weekday() != 6:  # weeks start on Sunday
        days = days[1:]
    cols = [days[i:i + 7] for i in range(0, len(days), 7)]
    total = sum(c for _, c in days)
    mx = max([c for _, c in days] + [1])
    cell, gap, x0, y0 = 13, 2, 32, 96
    pitch = cell + gap
    w = x0 * 2 + len(cols) * pitch - gap
    h = y0 + 7 * pitch + 50
    cx = lambda ci: x0 + ci * pitch + cell / 2
    cy = lambda ri: y0 + ri * pitch + cell / 2

    rnd = random.Random(dt.date.today().isoformat())
    food = [(ci, ri) for ci, col in enumerate(cols) for ri, (_, c) in enumerate(col) if c]
    route = snake_route(food, (0, 3), rnd)
    steps = len(route) - 1
    STEP = min(0.09, max(0.035, LOOP_TARGET / max(steps, 1)))
    D = steps * STEP
    first = {}
    for i, p in enumerate(route):
        first.setdefault(p, i)
    T = lambda t: f"clk.begin+{t:.3f}s"

    b = [f'  <rect width="0" height="0"><animate id="clk" attributeName="x" from="0" to="0" begin="0s;clk.end" dur="{D:.3f}s"/></rect>']

    # count-down: one text per value, each visible only for its time window
    eats = sorted((first[(ci, ri)] * STEP, c)
                  for ci, col in enumerate(cols) for ri, (_, c) in enumerate(col) if c)
    windows, left, t0 = [], total, 0.0
    for t, c in eats:
        windows.append((left, t0, t))
        left, t0 = left - c, t
    windows.append((0, t0, D))
    for i, (val, a_, b_) in enumerate(windows):
        if b_ - a_ < 0.001 and i:
            continue
        sets = f'<set attributeName="visibility" to="visible" begin="{T(a_)}" dur="{max(b_-a_, 0.001):.3f}s"/>'
        if i == 0:
            sets += f'<set attributeName="visibility" to="hidden" begin="{T(b_)}" dur="{max(D-b_, 0.001):.3f}s"/>'
        b.append(f'  <text x="{x0}" y="50" class="b" font-size="22" fill="#f0f6fc" visibility="{"visible" if i == 0 else "hidden"}">{val:,}{sets}</text>')
    lx = x0 + cw(22) * len(f"{total:,}") + 10
    b.append(f'  <text x="{lx:.0f}" y="50" font-size="15" fill="#c9d1d9">contributions in the last year</text>')

    starts = []  # (column, month) where a month begins; drop a label squeezed by the next one
    for ci, col in enumerate(cols):
        m = dt.date.fromisoformat(col[0][0]).strftime("%b")
        if not starts or starts[-1][1] != m:
            starts.append((ci, m))
    starts = [s for i, s in enumerate(starts) if i + 1 == len(starts) or starts[i + 1][0] - s[0] >= 3]
    for ci, m in starts:
        b.append(f'  <text x="{x0 + ci * pitch}" y="{y0-10}" font-size="12" fill="#8b949e">{m}</text>')

    for ci, col in enumerate(cols):
        x = x0 + ci * pitch
        for ri, (_, c) in enumerate(col):
            y = y0 + ri * pitch
            lvl = 0 if c == 0 else min(4, 1 + int(3 * (c / mx) ** 0.5 + 0.5))
            fg = "#5c6470" if lvl == 0 else ("#0d1117" if lvl == 4 else "#e6edf3")
            fs = 7.5 if c < 100 else 6
            ty = y + cell / 2 + 2.6
            if c:
                t = first[(ci, ri)] * STEP
                eat = f'begin="{T(t)}" dur="{max(D-t, 0.001):.3f}s"'
                b.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[lvl]}">'
                         f'<set attributeName="fill" to="{HEAT[0]}" {eat}/></rect>'
                         f'<text x="{x+cell/2}" y="{ty:.1f}" text-anchor="middle" class="b" font-size="{fs}" fill="{fg}">{c}'
                         f'<set attributeName="opacity" to="0" {eat}/></text>'
                         f'<text x="{x+cell/2}" y="{ty:.1f}" text-anchor="middle" class="b" font-size="7.5" fill="#5c6470" opacity="0">0'
                         f'<set attributeName="opacity" to="1" {eat}/></text>')
            else:
                b.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[0]}"/>'
                         f'<text x="{x+cell/2}" y="{ty:.1f}" text-anchor="middle" class="b" font-size="{fs}" fill="{fg}">0</text>')

    # snake: every segment rides the same closed route, k steps behind the head,
    # so the body is always on screen and the loop has no seam
    closed = route[:-1]
    for k in reversed(range(len(SNAKE))):
        pts = closed[-k:] + closed[:-k] if k else closed
        pts = pts + [pts[0]]
        path = "M" + " L".join(f"{cx(c):.1f} {cy(r):.1f}" for c, r in pts)
        sz = cell + 1 if k == 0 else cell - 2 - k * 0.6
        eyes = ('<circle cx="-2.6" cy="-2.4" r="1.4" fill="#0d1117"/><circle cx="2.6" cy="-2.4" r="1.4" fill="#0d1117"/>'
                if k == 0 else "")
        b.append(f'  <g><rect x="{-sz/2:.1f}" y="{-sz/2:.1f}" width="{sz:.1f}" height="{sz:.1f}" rx="{4 if k == 0 else 3}" fill="{SNAKE[k]}"/>{eyes}'
                 f'<animateMotion path="{path}" begin="clk.begin" dur="{D:.3f}s" calcMode="linear"/></g>')

    ly = h - 24
    b.append(f'  <text x="{x0}" y="{ly+4}" font-size="12" fill="#8b949e">contributions per day · new snake route every night</text>')
    lx = w - x0 - 5 * 16 - 76
    b.append(f'  <text x="{lx}" y="{ly+4}" font-size="12" fill="#8b949e">Less</text>')
    for i, c in enumerate(HEAT):
        b.append(f'  <rect x="{lx+36+i*16}" y="{ly-7}" width="12" height="12" rx="2.5" fill="{c}"/>')
    b.append(f'  <text x="{lx+36+5*16+4}" y="{ly+4}" font-size="12" fill="#8b949e">More</text>')
    return frame(w, h, "\n".join(b), f"{total} contributions in the last year, per-day heatmap, eaten by a snake")


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
