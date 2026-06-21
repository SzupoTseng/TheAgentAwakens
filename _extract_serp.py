#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, html, sys, json
SRC = "/mnt/c/Users/user/Desktop/prompt/龍蝦, OpenClaw, Hermes Agent - Google 搜索.html"
raw = open(SRC, encoding="utf-8", errors="ignore").read()
print("loaded", len(raw), "chars", file=sys.stderr)

# strip script/style/noscript/svg
for tag in ("script","style","noscript","svg","head"):
    raw = re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", " ", raw, flags=re.S|re.I)

# pull links (result anchors): href + visible text
links = []
for m in re.finditer(r'<a\s[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', raw, flags=re.S|re.I):
    url = m.group(1)
    txt = re.sub(r"<[^>]+>"," ", m.group(2))
    txt = html.unescape(re.sub(r"\s+"," ", txt)).strip()
    if "google.com" in url or "gstatic" in url or "googleusercontent" in url.split('/')[2]: 
        continue
    if len(txt) >= 4:
        links.append((txt, url))

# visible text blocks
body = re.sub(r"<[^>]+>", "\n", raw)
body = html.unescape(body)
lines = [re.sub(r"\s+"," ", l).strip() for l in body.split("\n")]
lines = [l for l in lines if len(l) >= 12]
# dedupe preserve order
seen=set(); uniq=[]
for l in lines:
    if l not in seen:
        seen.add(l); uniq.append(l)

# filter obvious chrome
CHROME = re.compile(r"^(登入|設定|工具|圖片|新聞|影片|地圖|購物|更多|安全搜尋|意見|說明|隱私|關於|無障礙|Google|所有篩選器|大約.*項結果|下一頁|頁\d|繁體中文)$")
content = [l for l in uniq if not CHROME.match(l)]

open("docs/book/_serp_links.txt","w",encoding="utf-8").write("\n".join(f"{t}\t{u}" for t,u in links))
open("docs/book/_serp_text.txt","w",encoding="utf-8").write("\n".join(content))
print(f"links={len(links)} unique_text_lines={len(content)}", file=sys.stderr)
