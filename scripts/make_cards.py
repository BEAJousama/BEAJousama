#!/usr/bin/env python3
"""Generate the project cards used in README.md (assets/cards/*.svg).

Edit PROJECTS below, then run:  python3 scripts/make_cards.py
Pure SVG + CSS, no external fonts or services, same look as assets/boot.svg.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "cards"

# name, accent, live?, footer, description, chips, size ("big" | "small")
PROJECTS = [
    ("pongmasters", "#22d3ee", True, "pongmasters.obeaj.me",
     "Real-time multiplayer Pong + chat platform. I owned the chat system and took the app to production.",
     ["Next.js", "NestJS", "Socket.IO", "PostgreSQL"], "big"),
    ("Leetube", "#f778ba", True, "leetube.obeaj.me",
     "Streams films from BitTorrent while they download: HTTP range responses, on-the-fly remux with FFmpeg.",
     ["React", "Express", "Prisma", "FFmpeg"], "big"),
    ("red-tetris", "#ff7b72", True, "tetris.obeaj.me",
     "Multiplayer Tetris with an authoritative game server: every board runs server-side, one seed per round.",
     ["React", "TypeScript", "Socket.IO"], "big"),
    ("MoralAi", "#a371f7", False, "github.com/BEAJousama/MoralAi",
     "Workplace mental-health check-in companion: LLM chat and assessments with Gemini or a local Llama.",
     ["React", "Node.js", "Ollama", "Gemini"], "big"),

    ("kfs", "#3fb950", False, "kfs_2 · kfs_3",
     "i386 kernel from scratch: GDT, IDT, IRQs, keyboard, paging, kmalloc / vmalloc.",
     ["C", "x86 asm", "QEMU"], "small"),
    ("rainfall · override", "#e3b341", False, "binary exploitation",
     "CTF wargames: stack overflows, format strings, shellcode, ROP, with writeups.",
     ["gdb", "x86", "reverse eng."], "small"),
    ("beaj-shell", "#3fb950", False, "github.com/BEAJousama/beaj-shell",
     "Unix shell in C: lexer → parser → executor, pipes, redirections, heredocs.",
     ["C", "POSIX"], "small"),
    ("websrv", "#22d3ee", False, "team of 3",
     "HTTP/1.1 server in C++98 on a single poll() loop: chunked bodies, CGI.",
     ["C++98", "sockets", "poll()"], "small"),
    ("BADASS", "#a371f7", False, "GNS3 · FRRouting",
     "BGP-EVPN / VXLAN data-center network with route reflection.",
     ["BGP", "VXLAN", "Docker"], "small"),
    ("inception · Cloud-I", "#f778ba", False, "Docker · Ansible",
     "Multi-container stack from my own images; Ansible provisioning on DigitalOcean.",
     ["Docker", "Nginx", "Ansible"], "small"),
]

MONO = 'ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace'
SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'


def wrap(text, width):
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    return lines


def card(name, accent, live, footer, desc, chips, size):
    big = size == "big"
    w, h = 430, (190 if big else 162)
    slug = name.split(" ")[0].lower()
    desc_lines = wrap(desc, 54 if big else 56)[: 3 if big else 2]
    title_y = 46 if big else 40

    chip_svg, x = [], 24
    chip_y = h - 62 if big else h - 60
    for c in chips:
        cw = int(len(c) * 7.3) + 18
        chip_svg.append(
            f'<rect x="{x}" y="{chip_y}" width="{cw}" height="22" rx="11" fill="{accent}" fill-opacity=".12" stroke="{accent}" stroke-opacity=".35"/>'
            f'<text x="{x + cw / 2}" y="{chip_y + 15}" text-anchor="middle" class="chip">{escape(c)}</text>'
        )
        x += cw + 8

    live_svg = ""
    if live:
        live_svg = (
            f'<rect x="{w - 84}" y="{title_y - 16}" width="62" height="22" rx="11" fill="#3fb950" fill-opacity=".12" stroke="#3fb950" stroke-opacity=".5"/>'
            f'<circle class="pulse" cx="{w - 70}" cy="{title_y - 5}" r="4" fill="#3fb950"/>'
            f'<text x="{w - 60}" y="{title_y}" class="live">LIVE</text>'
        )

    desc_svg = "".join(
        f'<text x="24" y="{title_y + 30 + i * 20}" class="desc">{escape(l)}</text>' for i, l in enumerate(desc_lines)
    )
    icon = "↗" if live else "›"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(name)}: {escape(desc)}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0f17"/><stop offset="1" stop-color="#111827"/></linearGradient>
    <linearGradient id="ac" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>
    <clipPath id="c"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12"/></clipPath>
  </defs>
  <style>
    .title {{ font-family: {MONO}; font-size: 17px; font-weight: 700; fill: #f0f6fc; }}
    .tilde {{ font-family: {MONO}; font-size: 17px; fill: {accent}; }}
    .desc  {{ font-family: {SANS}; font-size: 13.5px; fill: #9da7b3; }}
    .chip  {{ font-family: {MONO}; font-size: 11.5px; fill: {accent}; }}
    .foot  {{ font-family: {MONO}; font-size: 12px; fill: #6e7681; }}
    .live  {{ font-family: {MONO}; font-size: 11px; font-weight: 700; fill: #3fb950; }}
    .pulse {{ animation: p 1.6s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
    @keyframes p {{ 0%,100% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: .35; transform: scale(.7); }} }}
    .glow {{ animation: g 4s ease-in-out infinite; }}
    @keyframes g {{ 0%,100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
  </style>
  <g clip-path="url(#c)">
    <rect width="{w}" height="{h}" fill="url(#bg)"/>
    <rect class="glow" width="{w}" height="3" fill="url(#ac)"/>
    <circle cx="{w - 30}" cy="{h + 30}" r="110" fill="{accent}" fill-opacity=".05"/>
    <text x="24" y="{title_y}"><tspan class="tilde">~/</tspan><tspan class="title">{escape(name)}</tspan></text>
    {live_svg}
    {desc_svg}
    {"".join(chip_svg)}
    <line x1="24" y1="{h - 26}" x2="{w - 24}" y2="{h - 26}" stroke="#21262d"/>
    <text x="24" y="{h - 10}" class="foot">{escape(footer)}</text>
    <text x="{w - 24}" y="{h - 10}" text-anchor="end" class="foot" style="fill:{accent}">{icon}</text>
  </g>
  <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="#30363d"/>
</svg>
''', slug


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for p in PROJECTS:
        svg, slug = card(*p)
        (OUT / f"{slug}.svg").write_text(svg)
        print("wrote", f"assets/cards/{slug}.svg")


# ---------------------------------------------------------------- about card
STATS = [  # big number, label, accent
    ("16 mo", "production experience", "#22d3ee"),
    ("3", "apps live in production", "#3fb950"),
    ("20.43", "level at 1337 / 42", "#00babc"),
    ("RNCP 7", "master's level title", "#f778ba"),
]
COLUMNS = [  # heading, accent, title line, body
    ("EXPERIENCE", "#22d3ee", "FutureCorp · Paris (remote)",
     "Main engineer on CMS-driven Next.js platforms for Beige Pill and Fleming Watch. Maintained sites for Saatchi & Saatchi UK and The Brooklyn Tower."),
    ("1337 / 42", "#3fb950", "Final year · common core 100%",
     "Went deep on the layers underneath: x86 kernel, Unix shell, HTTP server, binary exploitation, BGP-EVPN, Kubernetes with GitOps."),
    ("NOW", "#e3b341", "Fullstack, end to end",
     "I build full-stack systems and run them myself in production on cloud VMs: Caddy, Nginx, TLS, Docker, PostgreSQL."),
]


def about_card():
    w, h = 880, 306
    tiles, tw, gap = [], 196, 13
    for i, (num, label, ac) in enumerate(STATS):
        x = 24 + i * (tw + gap)
        tiles.append(
            f'<g class="t" style="animation-delay:{.2 + i * .15:.2f}s">'
            f'<rect x="{x}" y="60" width="{tw}" height="78" rx="10" fill="{ac}" fill-opacity=".07" stroke="{ac}" stroke-opacity=".3"/>'
            f'<text x="{x + 16}" y="98" class="num" style="fill:{ac}">{escape(num)}</text>'
            f'<text x="{x + 16}" y="122" class="lbl">{escape(label)}</text></g>'
        )
    cols, cw = [], 264
    for i, (head, ac, line, body) in enumerate(COLUMNS):
        x = 24 + i * (cw + 20)
        body_svg = "".join(
            f'<text x="{x}" y="{226 + j * 19}" class="body">{escape(l)}</text>'
            for j, l in enumerate(wrap(body, 40)[:4])
        )
        cols.append(
            f'<g class="t" style="animation-delay:{.9 + i * .15:.2f}s">'
            f'<rect x="{x}" y="166" width="22" height="3" rx="1.5" fill="{ac}"/>'
            f'<text x="{x}" y="188" class="head" style="fill:{ac}">{escape(head)}</text>'
            f'<text x="{x}" y="206" class="line">{escape(line)}</text>{body_svg}</g>'
        )
    alt = " ".join(f"{n} {l}." for n, l, _ in STATS) + " " + " ".join(f"{hd}: {ln}. {b}" for hd, _, ln, b in COLUMNS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(alt)}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0f17"/><stop offset="1" stop-color="#111827"/></linearGradient>
    <linearGradient id="ac" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset=".5" stop-color="#3fb950"/><stop offset="1" stop-color="#e3b341" stop-opacity="0"/></linearGradient>
    <clipPath id="c"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12"/></clipPath>
  </defs>
  <style>
    .title {{ font-family: {MONO}; font-size: 17px; font-weight: 700; fill: #f0f6fc; }}
    .tilde {{ font-family: {MONO}; font-size: 17px; fill: #22d3ee; }}
    .sub   {{ font-family: {MONO}; font-size: 12px; fill: #6e7681; }}
    .num   {{ font-family: {MONO}; font-size: 26px; font-weight: 800; }}
    .lbl   {{ font-family: {SANS}; font-size: 12.5px; fill: #9da7b3; }}
    .head  {{ font-family: {MONO}; font-size: 11.5px; font-weight: 700; letter-spacing: 1.5px; }}
    .line  {{ font-family: {SANS}; font-size: 14px; font-weight: 600; fill: #f0f6fc; }}
    .body  {{ font-family: {SANS}; font-size: 13px; fill: #9da7b3; }}
    .t {{ opacity: 0; animation: in .5s ease-out forwards; }}
    @keyframes in {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
    .glow {{ animation: g 4s ease-in-out infinite; }}
    @keyframes g {{ 0%,100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
  </style>
  <g clip-path="url(#c)">
    <rect width="{w}" height="{h}" fill="url(#bg)"/>
    <rect class="glow" width="{w}" height="3" fill="url(#ac)"/>
    <circle cx="{w - 40}" cy="{h + 40}" r="160" fill="#22d3ee" fill-opacity=".04"/>
    <text x="24" y="40"><tspan class="tilde">~/</tspan><tspan class="title">about</tspan></text>
    <text x="{w - 24}" y="40" text-anchor="end" class="sub">Ousama Beaj · software engineer · Morocco</text>
    {"".join(tiles)}
    <line x1="24" y1="152" x2="{w - 24}" y2="152" stroke="#21262d"/>
    {"".join(cols)}
  </g>
  <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="#30363d"/>
</svg>
'''


if __name__ == "__main__":
    (OUT / "about.svg").write_text(about_card())
    print("wrote assets/cards/about.svg")
