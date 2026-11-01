#!/usr/bin/env python3
"""从 data/repos.json 生成静态 index.html。更新流程：改 seed.json → fetch_repos.py → build.py → git push。"""
import json, html
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data" / "repos.json").read_text(encoding="utf-8"))
repos, cats = data["repos"], {c["id"]: c["name"] for c in data["categories"]}
today = date.today().strftime("%Y-%m-%d")

LANG_COLORS = {"Python": "#3572A5", "Go": "#00ADD8", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
               "Rust": "#dea584", "Java": "#b07219", "Vue": "#41b883", "Svelte": "#ff3e00",
               "C++": "#f34b7d", "C": "#555555", "C#": "#178600", "Ruby": "#701516", "PHP": "#4F5D95",
               "Shell": "#89e051", "MDX": "#fcb32c", "Blade": "#f7523f", "Astro": "#ff5a03",
               "Dockerfile": "#384d54", "Zsh": "#89e051", "Jinja": "#a52a22", "HTML": "#e34c26",
               "CSS": "#563d7c", "ShaderLab": "#222c37", "Nix": "#7e7eff", "Stylus": "#ff6347"}

def fmt_stars(n):
    return f"{n/10000:.1f}万" if n >= 10000 else str(n)

def stale_badge(pushed):
    if pushed >= "2026-07": return ""
    if pushed >= "2025-11": return '<span class="badge warm">近一年低活跃</span>'
    return '<span class="badge cold">停更</span>'

def card(r):
    name = r["repo"].split("/", 1)[1]
    color = LANG_COLORS.get(r["lang"], "#8b949e")
    lang = f'<span class="lang"><i style="background:{color}"></i>{html.escape(r["lang"])}</span>' if r["lang"] else ""
    home = f'<a class="home" href="{html.escape(r["homepage"])}" target="_blank" rel="noopener" title="官网">⌂</a>' if r.get("homepage","").startswith("http") else ""
    return f'''<a class="card" href="https://github.com/{r["repo"]}" target="_blank" rel="noopener" data-search="{html.escape((r['repo']+' '+r['zh']+' '+r['lang']).lower())}">
  <div class="card-top"><span class="name">{html.escape(name)}</span>{home}</div>
  <p class="desc">{html.escape(r["zh"])}</p>
  <div class="meta">{lang}<span class="stars">★ {fmt_stars(r["stars"])}</span><span class="pushed">{r["pushed"]}</span>{stale_badge(r["pushed"])}</div>
</a>'''

sections = []
for cid, cname in cats.items():
    items = sorted([r for r in repos if r["cat"] == cid], key=lambda r: -r["stars"])
    if not items: continue
    sections.append(f'''
<section id="{cid}">
  <h2><a href="#{cid}">#</a> {html.escape(cname)}<span class="count">{len(items)}</span></h2>
  <div class="grid">{''.join(card(r) for r in items)}</div>
</section>''')

nav_links = "".join(f'<a href="#{c["id"]}" data-cat="{c["id"]}">{html.escape(c["name"])}</a>' for c in data["categories"])

total = len(repos)

page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GitHub 精选导航 · 中文开发者的开源项目指南</title>
<meta name="description" content="人工精选 {total} 个优质 GitHub 开源项目：AI 大模型、前端、后端、自托管、运维、学习资源、命令行工具、中文原创。中文导读，持续更新。">
<meta name="keywords" content="GitHub导航,开源项目,程序员导航,开发工具,AI工具,自托管,中文开源">
<meta property="og:title" content="GitHub 精选导航 · 中文开发者的开源项目指南">
<meta property="og:description" content="人工精选 {total} 个优质开源项目，中文导读，持续更新。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://nav.3o-8.com/">
<link rel="canonical" href="https://nav.3o-8.com/">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧭</text></svg>">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"WebSite","name":"GitHub 精选导航","alternateName":"GitHub Nav","url":"https://nav.3o-8.com/","inLanguage":"zh-CN","description":"人工精选 {total} 个优质 GitHub 开源项目，中文导读，持续更新。","dateModified":"{today}","about":[{{"@type":"Thing","name":"开源软件"}},{{"@type":"Thing","name":"GitHub"}}]}}
</script>
<style>
:root{{--bg:#0d1117;--panel:#161b22;--border:#30363d;--text:#e6edf3;--dim:#8b949e;--accent:#58a6ff;--green:#3fb950;--amber:#d29922;--red:#f85149}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth;scroll-padding-top:110px}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;line-height:1.6}}
header{{position:sticky;top:0;z-index:9;background:rgba(13,17,23,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--border)}}
.hd{{max-width:1200px;margin:0 auto;padding:14px 24px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}}
h1{{font-size:20px;font-weight:600;letter-spacing:.5px;white-space:nowrap}}
h1 b{{color:var(--accent);font-weight:600}}
.search{{flex:1;min-width:180px;max-width:420px;position:relative}}
.search input{{width:100%;padding:8px 14px;background:var(--panel);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:14px;outline:none;transition:border .15s}}
.search input:focus{{border-color:var(--accent)}}
.updated{{font-size:12px;color:var(--dim);white-space:nowrap}}
nav{{max-width:1200px;margin:0 auto;padding:0 24px 12px;display:flex;gap:4px;overflow-x:auto;flex-wrap:wrap}}
nav a{{color:var(--dim);text-decoration:none;font-size:13px;padding:4px 10px;border-radius:12px;white-space:nowrap;transition:all .15s}}
nav a:hover{{color:var(--text);background:var(--panel)}}
main{{max-width:1200px;margin:0 auto;padding:32px 24px 80px}}
section{{margin-bottom:48px}}
h2{{font-size:22px;font-weight:600;margin-bottom:18px;letter-spacing:.5px}}
h2 a{{color:var(--accent);text-decoration:none;opacity:0;transition:opacity .15s}}
h2:hover a{{opacity:1}}
h2 .count{{font-size:13px;font-weight:400;color:var(--dim);margin-left:10px;background:var(--panel);border:1px solid var(--border);padding:1px 9px;border-radius:10px;vertical-align:2px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}}
.card{{display:block;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:16px 18px;text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}}
.card:hover{{border-color:var(--accent);transform:translateY(-2px)}}
.card.hide{{display:none}}
.card-top{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}}
.name{{font-size:16px;font-weight:600;color:var(--accent);letter-spacing:.3px}}
.home{{color:var(--dim);font-size:14px;text-decoration:none;padding:0 4px}}
.home:hover{{color:var(--text)}}
.desc{{font-size:13.5px;color:var(--dim);margin-bottom:12px;min-height:42px}}
.meta{{display:flex;gap:14px;align-items:center;font-size:12.5px;color:var(--dim);flex-wrap:wrap}}
.lang i{{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:-1px}}
.stars{{color:#e3b341}}
.badge{{font-size:11px;padding:0 7px;border-radius:9px;border:1px solid}}
.warm{{color:var(--amber);border-color:var(--amber)}}
.cold{{color:var(--red);border-color:var(--red)}}
footer{{border-top:1px solid var(--border);padding:28px 24px;text-align:center;color:var(--dim);font-size:13px}}
footer a{{color:var(--accent);text-decoration:none}}
.nores{{display:none;text-align:center;color:var(--dim);padding:60px 0;font-size:15px}}
@media(max-width:640px){{.grid{{grid-template-columns:1fr}}.desc{{min-height:0}}h1{{font-size:17px}}}}
</style>
</head>
<body>
<header>
  <div class="hd">
    <h1>🧭 GitHub <b>精选导航</b></h1>
    <div class="search"><input id="q" type="search" placeholder="搜索项目名 / 用途 / 语言…（如：笔记、Go、监控）" autocomplete="off"></div>
    <span class="updated">数据更新于 {today} · 共 {total} 个项目</span>
  </div>
  <nav>{nav_links}</nav>
</header>
<main>
{''.join(sections)}
  <p class="nores" id="nores">没有匹配的项目，换个关键词试试</p>
</main>
<footer>
  <p>收录标准：中文开发者视角人工精选，星数与更新时间每月核实 · 星数与日期由 GitHub API 实时拉取</p>
  <p style="margin-top:6px"><a href="https://nav.3o-8.com/llms.txt">llms.txt</a> · 本站欢迎 AI 助手引用 · <a href="https://github.com/zhangtianshi3o8-lgtm/nav">GitHub 仓库</a></p>
</footer>
<script>
const q=document.getElementById('q'),cards=[...document.querySelectorAll('.card')],nores=document.getElementById('nores');
let t;q.addEventListener('input',()=>{{clearTimeout(t);t=setTimeout(()=>{{
  const s=q.value.trim().toLowerCase();let n=0;
  cards.forEach(c=>{{const hit=!s||c.dataset.search.includes(s);c.classList.toggle('hide',!hit);if(hit)n++;}});
  nores.style.display=n?'none':'block';
}},120)}});
</script>
</body>
</html>'''

out = ROOT / "docs" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(page, encoding="utf-8")
print(f"OK -> {out} ({len(page)//1024}KB, {total} repos, updated {today})")
