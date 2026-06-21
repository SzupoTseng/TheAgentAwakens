#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the English edition of《代理覺醒》/ "The Agent Awakens":
  1) merged single Markdown  TheAgentAwakens_full.md
  2) illustrated HTML (sticky side-nav)  TheAgentAwakens.html
Same layout/CSS as the Chinese _build.py; English heading parsing.
Usage: python3 _build.py
"""
import os, re, glob, html, base64

BOOK = os.path.dirname(os.path.abspath(__file__))
COVER = os.path.join(os.path.dirname(BOOK), "TheAgentAwakens.png")  # 封面在倉庫根目錄 / cover lives in repo root
BOOK_TITLE = "The Agent Awakens"
BOOK_SUB   = "OpenClaw, Hermes Agent, and a Hundred Battles across SRE, Fab & R&D"

def order():
    fs = []
    pre = glob.glob(os.path.join(BOOK, "00_*.md"))
    if pre: fs.append(os.path.basename(pre[0]))
    for n in range(1, 40):
        cand = glob.glob(os.path.join(BOOK, f"{n:02d}_*.md"))
        if cand: fs.append(os.path.basename(cand[0]))
    return fs

FILES = order()

def anchor_for(base):
    if base.startswith("00_"): return "fm"
    m = re.match(r'(\d{2})_', base)
    return f"ch{m.group(1)}" if m else "apx"

def title_for(base, text):
    if base.startswith("00_"):
        m = re.search(r'^##\s+(Preface.*)$', text, re.M)
        return m.group(1).strip() if m else "Preface"
    m = re.search(r'^#\s+(Chapter\s+\d+.*)$', text, re.M)
    if m: return m.group(1).strip()
    m = re.search(r'^#\s+(Appendix\s+\w+.*)$', text, re.M)
    return m.group(1).strip() if m else base

def part_for(text):
    m = re.search(r'^#\s+(Part\s+\d+.*)$', text, re.M)
    return m.group(1).strip() if m else None

def build_merged():
    parts = [f"# {BOOK_TITLE}\n### — {BOOK_SUB}\n"]
    if os.path.exists(COVER):
        parts.append("![The Agent Awakens — cover poster](../TheAgentAwakens.png)\n")
    parts += ["> Merged single-file edition. Compiled from a public technical search corpus (OpenClaw / Hermes Agent comparison + SRE/Fab/R&D field scenarios).\n",
              "\n---\n\n## Table of Contents\n"]
    for base in FILES:
        text = open(os.path.join(BOOK, base), encoding="utf-8").read()
        p = part_for(text); t = title_for(base, text)
        if p: parts.append(f"\n**{p}**\n")
        parts.append(f"- {t}")
    parts.append("\n\n---\n")
    for base in FILES:
        parts.append("\n\n" + open(os.path.join(BOOK, base), encoding="utf-8").read().rstrip() + "\n\n---\n")
    out = os.path.join(BOOK, f"TheAgentAwakens_full.md")
    open(out, "w", encoding="utf-8").write("\n".join(parts)); return out

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t

def md_to_html(text):
    lines = text.split("\n"); out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        if re.match(r'^---+\s*$', ln): out.append('<hr/>'); i += 1; continue
        m = re.match(r'^(#{1,4})\s+(.*)$', ln)
        if m: out.append(f'<h{len(m.group(1))}>{inline(m.group(2))}</h{len(m.group(1))}>'); i += 1; continue
        if ln.startswith(">"):
            blk = []
            while i < n and lines[i].startswith(">"): blk.append(re.sub(r'^>\s?', '', lines[i])); i += 1
            if any("🔍" in b for b in blk): cls = "review"
            elif any(("🧠" in b or "💡" in b) for b in blk): cls = "concept"
            else: cls = "quote"
            inner, buf = [], []
            def flush():
                if buf: inner.append("<p>" + "<br/>".join(inline(x) for x in buf) + "</p>"); buf.clear()
            for b in blk:
                hm = re.match(r'^(#{1,4})\s+(.*)$', b)
                if hm: flush(); inner.append(f'<p class="box-title">{inline(hm.group(2))}</p>')
                elif b.strip() == "": flush()
                else: buf.append(b)
            flush(); out.append(f'<blockquote class="{cls}">' + "".join(inner) + '</blockquote>'); continue
        if ln.strip().startswith("|") and i + 1 < n and re.match(r'^\s*\|[\s:\-|]+\|\s*$', lines[i+1]):
            header = [c.strip() for c in ln.strip().strip("|").split("|")]; i += 2; rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in header)
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f'<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'); continue
        if re.match(r'^\s*\d+\.\s+', ln):
            items = []
            while i < n and re.match(r'^\s*\d+\.\s+', lines[i]): items.append(re.sub(r'^\s*\d+\.\s+', '', lines[i])); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>"); continue
        if re.match(r'^\s*[-*]\s+', ln):
            items = []
            while i < n and re.match(r'^\s*[-*]\s+', lines[i]): items.append(re.sub(r'^\s*[-*]\s+', '', lines[i])); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"); continue
        if ln.strip() == "": i += 1; continue
        para = [ln]; i += 1
        while i < n and lines[i].strip() != "" and not re.match(r'^(#{1,4}\s|>|\s*[-*]\s|\s*\d+\.\s|---+\s*$|\s*\|)', lines[i]):
            para.append(lines[i]); i += 1
        out.append("<p>" + "<br/>".join(inline(x) for x in para) + "</p>")
    return "\n".join(out)

CSS = """
:root{--ink:#1d2230;--mut:#5a6378;--line:#e3e0d6;--pa:#fbf8f0;--accent:#9a3b2f;--accent2:#2f5d7a;--box:#fdf3e3;--boxln:#e8c88a}
*{box-sizing:border-box}
body{margin:0;font-family:Georgia,"Iowan Old Style","Noto Serif",serif;color:var(--ink);background:var(--pa);line-height:1.75;font-size:18px}
#wrap{display:flex;align-items:flex-start}
#side{position:sticky;top:0;height:100vh;overflow-y:auto;width:310px;min-width:310px;background:#14182a;color:#cdd2e6;padding:26px 18px;font-family:-apple-system,"Segoe UI",Roboto,sans-serif;font-size:13.5px;line-height:1.55}
#side h1{font-size:21px;color:#f4b860;margin:0 0 4px;letter-spacing:1px}
#side .sub{color:#8b93b0;font-size:12px;margin-bottom:18px;line-height:1.5}
#side .part{color:#49c5e0;font-size:11.5px;margin:16px 0 6px;letter-spacing:.5px;border-bottom:1px solid #2a3150;padding-bottom:4px}
#side a{display:block;color:#cdd2e6;text-decoration:none;padding:5px 8px;border-radius:6px}
#side a:hover{background:#222a45;color:#fff}
#side a.active{background:#2f3a60;color:#ffd98a}
main{flex:1;max-width:840px;margin:0 auto;padding:64px 56px 120px}
h1{font-size:29px;letter-spacing:.3px;line-height:1.3;margin:8px 0 18px}
h1+h1{font-size:24px;color:var(--accent)}
h2{font-size:21px;margin:42px 0 14px;color:var(--accent);border-left:5px solid var(--accent);padding-left:12px}
h3{font-size:18px;margin:28px 0 10px}
h4{font-size:16px;margin:20px 0 8px;color:var(--accent2)}
p{margin:14px 0;text-align:justify}
strong{color:#111;font-weight:700;background:linear-gradient(transparent 62%,#ffe6a0 62%)}
code{background:#eee;padding:1px 5px;border-radius:4px;font-size:.88em;font-family:"SF Mono",Consolas,monospace}
a{color:var(--accent2)}
hr{border:0;border-top:1px solid var(--line);margin:36px 0}
ul,ol{margin:14px 0;padding-left:24px}
li{margin:6px 0}
table{border-collapse:collapse;width:100%;margin:20px 0;font-size:14.5px;font-family:-apple-system,"Segoe UI",Roboto,sans-serif}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:#f0ebdd}
blockquote.quote{margin:22px 0;padding:14px 22px;border-left:4px solid var(--boxln);background:#faf4e6;color:#4a4334}
blockquote.concept{margin:34px 0;padding:22px 26px;background:var(--box);border:1px solid var(--boxln);border-radius:14px;box-shadow:0 4px 14px rgba(180,140,60,.12)}
blockquote.concept .box-title{font-size:17px;font-weight:700;color:#9a6a1a;font-family:-apple-system,"Segoe UI",sans-serif;margin:0 0 10px}
blockquote.concept p{margin:10px 0}
blockquote.review{margin:30px 0;padding:20px 24px;background:#eef5f7;border:1px solid #bcd6df;border-left:5px solid #2f5d7a;border-radius:12px;box-shadow:0 4px 14px rgba(47,93,122,.1)}
blockquote.review .box-title{font-size:16px;font-weight:700;color:#2f5d7a;font-family:-apple-system,"Segoe UI",sans-serif;margin:0 0 10px}
blockquote.review p{margin:10px 0;font-size:16px;color:#274050}
section.chapter{padding-top:10px}
figure.cover{margin:0 0 10px;text-align:center}
figure.cover img{width:100%;max-width:680px;border-radius:12px;box-shadow:0 12px 36px rgba(20,24,42,.3)}
@page{size:A4;margin:16mm 17mm}
@media print{html,body{background:#fff;font-size:10.8pt;line-height:1.55}#side{display:none}main{max-width:100%;margin:0;padding:0}h1{font-size:19pt}h2{font-size:14pt;margin-top:20pt}h3{font-size:12.5pt}section.chapter{page-break-before:always}section.cover-page{page-break-before:avoid}figure.cover img{max-width:100%;box-shadow:none}h2,h3{break-after:avoid}table,blockquote{break-inside:avoid}blockquote.concept,blockquote.review{box-shadow:none}}
@media(max-width:820px){#side{display:none}main{padding:30px 18px}}
"""
JS = """
const links=[...document.querySelectorAll('#side a')];
const secs=links.map(a=>document.querySelector(a.getAttribute('href')));
const obs=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){links.forEach(l=>l.classList.remove('active'));const i=secs.indexOf(e.target);if(i>=0)links[i].classList.add('active');}})},{rootMargin:'-10% 0px -80% 0px'});
secs.forEach(s=>s&&obs.observe(s));
"""

def cover_section():
    if not os.path.exists(COVER): return "", ""
    data = base64.b64encode(open(COVER, "rb").read()).decode()
    fig = (f'<section class="chapter cover-page" id="cover">'
           f'<figure class="cover"><img src="data:image/png;base64,{data}" '
           f'alt="{html.escape(BOOK_TITLE)} — cover poster"/></figure></section>')
    return '<a href="#cover">Cover</a>', fig

def build_html():
    nav, body = [], []
    nav.append(f'<h1>{html.escape(BOOK_TITLE)}</h1><div class="sub">{html.escape(BOOK_SUB)}</div>')
    cnav, cbody = cover_section()
    if cbody: nav.append(cnav); body.append(cbody)
    for base in FILES:
        text = open(os.path.join(BOOK, base), encoding="utf-8").read()
        a = anchor_for(base); p = part_for(text); t = title_for(base, text)
        if p: nav.append(f'<div class="part">{html.escape(p)}</div>')
        nav.append(f'<a href="#{a}">{html.escape(t)}</a>')
        body.append(f'<section class="chapter" id="{a}">{md_to_html(text)}</section>')
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{html.escape(BOOK_TITLE)} — {html.escape(BOOK_SUB)}</title><style>{CSS}</style></head>
<body><div id="wrap"><nav id="side">{''.join(nav)}</nav><main>{''.join(body)}</main></div>
<script>{JS}</script></body></html>"""
    out = os.path.join(BOOK, f"TheAgentAwakens.html")
    open(out, "w", encoding="utf-8").write(page); return out

if __name__ == "__main__":
    m = build_merged(); print("merged:", m, f"({os.path.getsize(m)//1024} KB)")
    h = build_html(); print("HTML:", h, f"({os.path.getsize(h)//1024} KB)")
