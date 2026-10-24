"""Motor de carrosséis Optimizze: lê um JSON de carrossel e gera PNGs 1080x1920.

Uso: python3 render.py carrossel.json pasta_saida
"""
import json, os, re, sys, html
from pathlib import Path
from playwright.sync_api import sync_playwright

FONT_DIR = "/usr/share/fonts/opentype/inter"
HERE = Path(__file__).parent

CSS = f"""
@font-face {{ font-family: I; src: url('file://{FONT_DIR}/Inter-Regular.otf'); font-weight: 400; }}
@font-face {{ font-family: I; src: url('file://{FONT_DIR}/Inter-Medium.otf'); font-weight: 500; }}
@font-face {{ font-family: I; src: url('file://{FONT_DIR}/Inter-SemiBold.otf'); font-weight: 600; }}
@font-face {{ font-family: I; src: url('file://{FONT_DIR}/Inter-Bold.otf'); font-weight: 700; }}
@font-face {{ font-family: D; src: url('file://{FONT_DIR}/InterDisplay-ExtraBold.otf'); font-weight: 800; }}
@font-face {{ font-family: D; src: url('file://{FONT_DIR}/InterDisplay-Black.otf'); font-weight: 900; }}
:root {{
  --bg:#0B0A12; --s1:#15131F; --s2:#1D1A2B; --bd:#2C2742; --p:#8B5CF6; --pl:#C4B5FD;
  --t:#F4F4F5; --m:#A1A1AA; --g:#22C55E;
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ width:1080px; height:1920px; background:var(--bg); }}
body {{ font-family:I; color:var(--t); -webkit-font-smoothing:antialiased; }}
.slide {{ position:relative; width:1080px; height:1920px; overflow:hidden; padding:120px 80px 90px;
  display:flex; flex-direction:column; }}
.glow {{ position:absolute; width:1100px; height:1100px; border-radius:50%; left:-10px; top:900px;
  background:radial-gradient(circle, rgba(124,58,237,.42), rgba(124,58,237,0) 65%); pointer-events:none; }}
.glow.up {{ top:-450px; left:250px; }}
.grid {{ position:absolute; inset:0; opacity:.07;
  background-image:linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px);
  background-size:72px 72px; mask-image:linear-gradient(#000,transparent 55%); }}
.top {{ position:relative; display:flex; align-items:center; justify-content:space-between; margin-bottom:44px; }}
.pill {{ font-weight:700; font-size:30px; letter-spacing:.08em; color:var(--pl); background:rgba(139,92,246,.14);
  border:1.5px solid rgba(139,92,246,.45); padding:14px 28px; border-radius:999px; }}
.dots {{ display:flex; gap:10px; }}
.dots i {{ width:14px; height:14px; border-radius:50%; background:#3A3452; }}
.dots i.on {{ background:var(--p); width:40px; border-radius:8px; }}
h1 {{ position:relative; font-family:D; font-weight:800; font-size:86px; line-height:1.04; letter-spacing:-.025em; }}
h1 em, .big em {{ font-style:normal; color:var(--pl); }}
.sub {{ position:relative; margin-top:30px; font-size:40px; line-height:1.38; color:#C9C9D1; font-weight:500; }}
.sub b {{ color:var(--t); font-weight:700; }}
.stage {{ position:relative; flex:1; display:flex; align-items:center; justify-content:center; margin-top:56px; }}
.foot {{ position:relative; display:flex; justify-content:space-between; align-items:center; margin-top:44px;
  font-size:28px; color:var(--m); font-weight:600; }}
/* phone */
.phone {{ zoom:1.1; width:830px; background:var(--s1); border:2px solid var(--bd); border-radius:56px; padding:34px 34px 40px;
  box-shadow:0 40px 120px rgba(0,0,0,.6), 0 0 0 10px #0F0D18; }}
.url {{ display:flex; align-items:center; gap:14px; background:#0F0D18; border-radius:20px; padding:16px 24px;
  font-size:26px; color:var(--m); margin-bottom:30px; }}
.url svg {{ width:22px; height:22px; }}
.apphead {{ display:flex; align-items:center; gap:16px; font-weight:700; font-size:34px; margin-bottom:28px; }}
.logo {{ width:48px; height:48px; border-radius:14px; background:linear-gradient(135deg,#A78BFA,#6D28D9);
  display:grid; place-items:center; font-family:D; font-weight:900; font-size:28px; color:#fff; }}
.lbl {{ font-size:24px; color:var(--m); font-weight:600; letter-spacing:.06em; text-transform:uppercase; margin-bottom:14px; }}
.card {{ background:var(--s2); border:1.5px solid var(--bd); border-radius:28px; padding:28px; }}
.btn {{ display:inline-flex; align-items:center; gap:12px; background:var(--p); color:#fff; font-weight:700;
  font-size:30px; padding:22px 38px; border-radius:20px; }}
.btn.ghost {{ background:transparent; border:2px solid var(--bd); color:var(--t); }}
.row {{ display:flex; align-items:center; gap:22px; }}
.thumb {{ position:relative; width:150px; height:200px; border-radius:20px; flex:none; display:grid; place-items:center; overflow:hidden; }}
.thumb svg.ic {{ width:84px; height:84px; opacity:.9; }}
.thumb .dur {{ position:absolute; left:10px; bottom:10px; font-size:20px; font-weight:700; background:rgba(0,0,0,.55);
  padding:4px 10px; border-radius:8px; }}
.rank {{ font-family:D; font-weight:900; font-size:38px; color:var(--pl); width:44px; }}
.vt {{ font-size:28px; font-weight:600; line-height:1.3; }}
.stats {{ display:flex; gap:30px; margin-top:12px; }}
.stats div {{ font-size:22px; color:var(--m); }}
.stats b {{ display:block; font-size:32px; color:var(--g); font-weight:700; }}
.tag {{ display:inline-block; font-size:20px; font-weight:700; color:var(--m); border:1.5px solid var(--bd);
  border-radius:8px; padding:4px 10px; margin-left:10px; vertical-align:middle; }}
.drop {{ border:3px dashed rgba(139,92,246,.6); border-radius:28px; padding:50px 30px; text-align:center; }}
.drop svg {{ width:76px; height:76px; }}
.file {{ display:flex; align-items:center; gap:20px; background:rgba(34,197,94,.1); border:1.5px solid rgba(34,197,94,.45);
  border-radius:22px; padding:22px 26px; font-size:28px; font-weight:600; margin-top:26px; }}
.check {{ width:44px; height:44px; border-radius:50%; border:3px solid var(--g); display:grid; place-items:center; flex:none; }}
.check svg {{ width:24px; height:24px; }}
.prompt {{ font-family:ui-monospace,monospace; font-size:25px; line-height:1.55; color:#B9B6C8; }}
.prompt b {{ color:var(--pl); font-weight:700; }}
.tabs {{ display:flex; gap:16px; }}
.tabs div {{ flex:1; text-align:center; border:2px solid var(--bd); border-radius:22px; padding:22px 10px; font-size:24px; color:var(--m); }}
.tabs div b {{ display:block; font-family:D; font-weight:800; font-size:40px; color:var(--t); }}
.tabs div.on {{ border-color:var(--p); background:rgba(139,92,246,.16); color:var(--pl); }}
.tabs div.on b {{ color:var(--pl); }}
.clip {{ flex:1; height:120px; border-radius:14px; display:grid; place-items:center; font-weight:700; font-size:24px; }}
.big {{ font-family:D; font-weight:900; font-size:150px; line-height:1; letter-spacing:-.03em; }}
.chips {{ display:flex; gap:16px; flex-wrap:wrap; margin-top:40px; position:relative; }}
.chip {{ font-size:30px; font-weight:600; padding:16px 26px; border-radius:999px; background:var(--s2); border:1.5px solid var(--bd); }}
.chip::before {{ content:''; display:inline-block; width:12px; height:12px; border-radius:50%; background:var(--g); margin-right:14px; vertical-align:middle; }}
.bad {{ border-color:rgba(239,68,68,.5); background:rgba(239,68,68,.08); }}
.good {{ border-color:rgba(34,197,94,.5); background:rgba(34,197,94,.08); }}
.quote {{ font-size:36px; font-weight:600; line-height:1.35; margin-top:10px; }}
"""

ICONS = {
    "shirt": '<path d="M8 3 12 5l4-2 5 3.5-2.5 4-2.5-1.3V21H8V9.2L5.5 10.5 3 6.5z" fill="currentColor"/>',
    "bed": '<path d="M3 18V6h2v6h6V9h7a3 3 0 0 1 3 3v6h-2v-2H5v2z M6.5 10.8a1.6 1.6 0 1 0 0-.1z" fill="currentColor"/>',
    "bottle": '<path d="M10 2h4v3l2 2v14a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V7l2-2z" fill="currentColor"/>',
    "bag": '<path d="M6 7h12l1.5 14h-15zM9 7a3 3 0 0 1 6 0" fill="none" stroke="currentColor" stroke-width="2"/>',
    "shoe": '<path d="M3 16v-5l4-1 3 3 5 1.5 5 1V19H3z" fill="currentColor"/>',
}
GRADS = {
    "shirt": "linear-gradient(160deg,#334155,#0F172A)", "bed": "linear-gradient(160deg,#78716C,#292524)",
    "bottle": "linear-gradient(160deg,#BE185D,#4C0519)", "bag": "linear-gradient(160deg,#B45309,#451A03)",
    "shoe": "linear-gradient(160deg,#0E7490,#083344)",
}
CHECK = '<svg viewBox="0 0 24 24"><path d="M5 12.5 10 17 19 7" fill="none" stroke="#22C55E" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
LOCK = '<svg viewBox="0 0 24 24"><path d="M7 11V8a5 5 0 0 1 10 0v3M5 11h14v10H5z" fill="none" stroke="#A1A1AA" stroke-width="2"/></svg>'
UP = '<svg viewBox="0 0 24 24"><path d="M12 16V4m0 0-5 5m5-5 5 5M4 15v5h16v-5" fill="none" stroke="#A78BFA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
COPY = '<svg viewBox="0 0 24 24" width="30" height="30"><path d="M9 9h11v11H9zM5 15H4V4h11v1" fill="none" stroke="#fff" stroke-width="2"/></svg>'
SPARK = '<svg viewBox="0 0 24 24" width="30" height="30"><path d="M12 2l2.2 6.6L21 11l-6.8 2.4L12 20l-2.2-6.6L3 11l6.8-2.4z" fill="#fff"/></svg>'


def md(s):
    """*texto* vira destaque roxo; **texto** vira negrito."""
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s.replace("\n", "<br>")


def icon(name, color="#fff"):
    return f'<svg class="ic" viewBox="0 0 24 24" style="color:{color}">{ICONS[name]}</svg>'


def thumb(prod, dur=None, w=150, h=200):
    d = f'<span class="dur">{dur}</span>' if dur else ""
    return f'<div class="thumb" style="background:{GRADS[prod]};width:{w}px;height:{h}px">{icon(prod)}{d}</div>'


def phone(inner, url="optimizzeai.com", app="Optimizze AI"):
    u = f'<div class="url">{LOCK}{url}</div>' if url else ""
    a = f'<div class="apphead"><div class="logo">O</div>{app}</div>' if app else ""
    return f'<div class="phone">{u}{a}{inner}</div>'


# ---------- componentes (mockups) ----------
def c_ranking(d):
    rows = ""
    for i, v in enumerate(d["videos"], 1):
        rows += f'''<div class="row" style="padding:22px 0;border-top:1.5px solid var(--bd)">
          <div class="rank">{i}</div>{thumb(v["prod"], v.get("dur"), 120, 160)}
          <div><div class="vt">{html.escape(v["title"])}</div>
          <div class="stats"><div><b>{v["vendidos"]}</b>vendidos</div><div><b>{v["receita"]}</b>em vendas</div></div></div></div>'''
    head = f'<div class="lbl">Mais vendidos · últimos 7 dias <span class="tag">exemplo</span></div>'
    return phone(head + rows, url=d.get("url", "ferramenta de dados de vendas"), app=None)


def c_upload(d):
    inner = f'''<div class="lbl">{html.escape(d.get("modo","Remix Inteligente"))}</div>
      <div style="font-family:D;font-weight:800;font-size:46px;margin-bottom:26px">Vídeo original</div>
      <div class="drop">{UP}<div style="font-size:30px;font-weight:600;margin-top:16px">Arraste o .mp4 ou toque pra enviar</div>
      <div style="font-size:24px;color:var(--m);margin-top:10px">até ~2 minutos · funciona no celular</div></div>
      <div class="file"><div class="check">{CHECK}</div><div style="flex:1">{html.escape(d.get("arquivo","video_que_vendeu.mp4"))}</div>
      <span style="color:var(--g);font-size:24px">enviado</span></div>
      <div style="display:flex;justify-content:flex-end;margin-top:30px"><span class="btn">Analisar vídeo →</span></div>'''
    return phone(inner)


def c_gauge(d):
    items = "".join(f'''<div class="row" style="margin-top:22px;align-items:flex-start"><div class="check">{CHECK}</div>
        <div><div style="font-size:30px;font-weight:700">{html.escape(k)}</div>
        <div style="font-size:25px;color:var(--m);margin-top:4px;line-height:1.35">{html.escape(v)}</div></div></div>'''
        for k, v in d["itens"])
    svg = '''<svg viewBox="0 0 400 220" width="560" style="display:block;margin:0 auto">
      <defs><linearGradient id="gg"><stop offset="0" stop-color="#EF4444"/><stop offset=".5" stop-color="#EAB308"/><stop offset="1" stop-color="#22C55E"/></linearGradient></defs>
      <path d="M40 200 A160 160 0 0 1 360 200" fill="none" stroke="#2C2742" stroke-width="30" stroke-linecap="round"/>
      <path d="M40 200 A160 160 0 0 1 360 200" fill="none" stroke="url(#gg)" stroke-width="30" stroke-linecap="round"/>
      <line x1="200" y1="200" x2="318" y2="104" stroke="#A78BFA" stroke-width="12" stroke-linecap="round"/>
      <circle cx="200" cy="200" r="26" fill="#7C3AED"/><circle cx="200" cy="200" r="10" fill="#15131F"/></svg>'''
    inner = f'''<div style="font-family:D;font-weight:800;font-size:38px;margin-bottom:10px">Resumo da otimização</div>{svg}
      <div style="text-align:center;color:var(--g);font-weight:700;font-size:32px;margin:30px 0 10px">✓ Copy otimizada</div>{items}'''
    return phone(inner)


def c_prompts(d):
    inner = f'''<div class="lbl">Prompts de vídeo por cena</div>
      <div class="card"><div style="display:flex;justify-content:space-between;margin-bottom:18px">
      <span style="font-weight:700;font-size:32px">Cena 1</span><span style="color:var(--m);font-size:24px">~8s</span></div>
      <div class="prompt">{d["prompt"]}</div>
      <div style="display:flex;justify-content:flex-end;margin-top:24px"><span class="btn">{COPY}Copiar</span></div></div>
      <div class="card" style="margin-top:20px;opacity:.55"><span style="font-weight:700;font-size:32px">Cena 2</span>
      <div class="prompt" style="margin-top:10px">{d.get("prompt2","[AÇÃO DA CENA] close no detalhe do produto…")}</div></div>'''
    return phone(inner)


def c_generator(d):
    p = d.get("prod", "shirt")
    tiles = "".join(thumb(p, None, 150, 150) for _ in range(3))
    inner = f'''<div class="lbl">Prompt</div>
      <div class="card prompt" style="min-height:200px">{d["prompt"]}<span style="color:var(--p)">▍</span></div>
      <div class="lbl" style="margin-top:28px">Imagem do produto</div>
      <div class="row" style="gap:16px">{tiles}</div>
      <div style="margin-top:32px;background:#0F0D18;border-radius:999px;height:18px;overflow:hidden">
        <div style="width:{d.get("progresso",64)}%;height:100%;background:linear-gradient(90deg,#7C3AED,#C4B5FD)"></div></div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:18px;font-size:26px;color:var(--m)">
        <span>Gerando cena 1…</span><span class="btn">{SPARK}Gerar</span></div>'''
    return phone(inner, url=None, app=d.get("app", "Gerador de vídeo com IA"))


def c_timeline(d):
    p = d.get("prod", "shirt")
    cols = ["#4C1D95", "#5B21B6", "#6D28D9", "#7C3AED", "#8B5CF6", "#A78BFA"]
    clips = "".join(f'<div class="clip" style="background:{c}">C{i+1}</div>' for i, c in enumerate(cols))
    inner = f'''<div style="display:flex;justify-content:center">{thumb(p, None, 380, 520)}</div>
      <div class="lbl" style="margin-top:30px">Linha do tempo · 6 cenas</div>
      <div class="row" style="gap:8px">{clips}</div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:32px">
      <span style="font-size:26px;color:var(--m)">0:48 · 1080p</span><span class="btn">Exportar e postar</span></div>'''
    return phone(inner, url=None, app="Editor de vídeo")


def c_variants(d):
    tabs = "".join(f'<div class="{"on" if i==0 else ""}"><b>V{i+1}</b>{html.escape(t)}</div>' for i, t in enumerate(d["tabs"]))
    mel = "".join(f'''<div class="row" style="margin-top:16px;align-items:flex-start"><div class="check" style="width:38px;height:38px">{CHECK}</div>
        <div><div style="font-size:27px;font-weight:700">{html.escape(k)}</div>
        <div style="font-size:23px;color:var(--m);margin-top:2px;line-height:1.35">{html.escape(v)}</div></div></div>''' for k, v in d["melhorias"])
    c = d["cena"]
    cena = f'''<div class="card" style="margin-top:24px;padding:24px 26px">
        <div class="row" style="gap:16px;margin-bottom:14px"><div style="width:44px;height:44px;border-radius:50%;background:rgba(139,92,246,.25);
        display:grid;place-items:center;font-weight:700;font-size:24px;color:var(--pl)">1</div><span style="font-weight:700;font-size:28px">{html.escape(c["nome"])}</span></div>
        <div style="font-size:22px;font-weight:700;color:#A78BFA;letter-spacing:.05em">FALA</div>
        <div style="font-size:27px;font-weight:600;line-height:1.38;margin:4px 0 12px">{html.escape(c["fala"])}</div>
        <div style="font-size:22px;font-weight:700;color:#4ADE80;letter-spacing:.05em">AÇÃO</div>
        <div style="font-size:25px;color:#C9C9D1;line-height:1.38;margin:4px 0 12px">{html.escape(c["acao"])}</div>
        <div style="font-size:22px;font-weight:700;color:#FACC15;letter-spacing:.05em">TOM</div>
        <div style="font-size:25px;color:#C9C9D1;font-style:italic;margin-top:4px">{html.escape(c["tom"])}</div></div>'''
    inner = f'''<div class="tabs">{tabs}</div>
      <div style="font-family:D;font-weight:800;font-size:36px;margin:26px 0 4px">Resumo da otimização</div>{mel}
      <div style="font-family:D;font-weight:800;font-size:36px;margin-top:28px">Modo Gravação</div>{cena}'''
    return phone(inner, url=None, app="Remix Inteligente")


def c_compare(d):
    return f'''<div style="width:100%">
      <div class="card bad"><div class="lbl" style="color:#F87171">Gancho que não vende</div><div class="quote">“{html.escape(d["antes"])}”</div></div>
      <div style="text-align:center;font-size:60px;color:var(--pl);margin:18px 0">↓</div>
      <div class="card good"><div class="lbl" style="color:#4ADE80">Gancho reescrito</div><div class="quote">“{html.escape(d["depois"])}”</div></div>
      <div style="font-size:26px;color:var(--m);margin-top:24px;text-align:center">{md(d.get("nota",""))}</div></div>'''


def c_cover(d):
    p = d.get("prod", "shirt")
    phones = f'''<div style="position:relative;width:820px;height:760px">
      <div style="position:absolute;left:40px;top:90px;transform:rotate(-8deg);opacity:.55">{thumb("bed", None, 300, 520)}</div>
      <div style="position:absolute;right:40px;top:90px;transform:rotate(8deg);opacity:.55">{thumb("bottle", None, 300, 520)}</div>
      <div style="position:absolute;left:220px;top:0;border-radius:40px;box-shadow:0 30px 100px rgba(124,58,237,.55);border:6px solid #2C2742;border-radius:46px">
        {thumb(p, None, 380, 680)}</div>
      <div style="position:absolute;left:340px;top:500px;width:140px;height:140px;border-radius:50%;background:rgba(255,255,255,.16);
        border:2px solid rgba(255,255,255,.35);display:grid;place-items:center"><svg viewBox="0 0 24 24" width="64"><path d="M8 5v14l11-7z" fill="#fff"/></svg></div>
      </div>'''
    return phones


def c_cta(d):
    return f'''<div style="width:100%">
      <div class="card" style="display:flex;gap:22px;align-items:center;padding:30px">
        <div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#F472B6,#8B5CF6);flex:none"></div>
        <div><div style="font-size:26px;color:var(--m);font-weight:600">você · agora</div>
        <div style="font-size:44px;font-weight:700;margin-top:4px">{html.escape(d.get("palavra","TTS"))}</div></div>
        <div style="margin-left:auto;font-size:44px;color:#F472B6">♥</div></div>
      <div class="card" style="margin-top:20px;margin-left:120px;padding:30px;border-color:rgba(139,92,246,.5)">
        <div style="font-size:26px;color:var(--pl);font-weight:600">resposta no privado</div>
        <div style="font-size:34px;font-weight:600;margin-top:6px;line-height:1.35">{html.escape(d.get("resposta","Te mandei o link e o passo a passo completo"))}</div></div></div>'''


COMP = dict(ranking=c_ranking, upload=c_upload, gauge=c_gauge, prompts=c_prompts, generator=c_generator,
            timeline=c_timeline, variants=c_variants, compare=c_compare, cover=c_cover, cta=c_cta)


def slide_html(s, i, n):
    dots = "".join(f'<i class="{"on" if k==i else ""}"></i>' for k in range(1, n + 1))
    pill = f'<span class="pill">{html.escape(s["pill"])}</span>' if s.get("pill") else "<span></span>"
    title_cls = ' class="big"' if s.get("tipo") == "cta" else ""
    title_tag = "div" if title_cls else "h1"
    size = f' style="font-size:{s["tam"]}px"' if s.get("tam") else ""
    sub = f'<p class="sub">{md(s["sub"])}</p>' if s.get("sub") else ""
    chips = ""
    if s.get("chips"):
        chips = '<div class="chips">' + "".join(f'<span class="chip">{html.escape(c)}</span>' for c in s["chips"]) + "</div>"
    comp = COMP[s["tipo"]](s.get("dados", {})) if s.get("tipo") else ""
    foot_r = "arrasta pro lado →" if i == 1 else f"{i}/{n}"
    glow = "glow up" if i % 2 else "glow"
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
      <div class="slide"><div class="grid"></div><div class="{glow}"></div>
      <div class="top">{pill}<div class="dots">{dots}</div></div>
      <{title_tag}{title_cls}{size}>{md(s["titulo"])}</{title_tag}>{sub}{chips}
      <div class="stage">{comp}</div>
      <div class="foot"><span>{html.escape(s.get("rodape",""))}</span><span>{foot_r}</span></div></div></body></html>'''


def render(spec_path, out_dir):
    spec = json.load(open(spec_path))
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    n = len(spec["slides"])
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for i, s in enumerate(spec["slides"], 1):
            f = out / f"_s{i}.html"
            f.write_text(slide_html(s, i, n), encoding="utf-8")
            pg.goto(f"file://{f.resolve()}"); pg.wait_for_timeout(150)
            over = pg.evaluate("(()=>{const st=document.querySelector('.stage');return [...st.children].some(c=>c.getBoundingClientRect().bottom>st.getBoundingClientRect().bottom+2||c.getBoundingClientRect().top<st.getBoundingClientRect().top-2)})()")
            if over: print(f"AVISO: slide {i} estourou a altura")
            pg.screenshot(path=str(out / f"slide_{i:02d}.png"))
            f.unlink()
        b.close()
    (out / "legenda.txt").write_text(spec.get("legenda", ""), encoding="utf-8")
    print("ok", spec_path, n, "slides")


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
