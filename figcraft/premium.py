"""Carrossel "premium" (estilo dos virais de passo a passo) montado no FigCraft, sem janela.

Formato 1080x1350 (4:5). Paleta escura com roxo. Tipos de slide:
  capa  : card do vídeo de referência COM as métricas + selo do faturamento + tela da variação
          (sem linhas ligando as telas) + "Roube a / Estrutura / de um vídeo que fez R$ X"
  lista : "Salva esse passo a passo" com os 5 passos numerados
  passo : pílula "Passo N" + título (leve + **negrito**) + faixa com o print + texto com **negrito** e __sublinhado__
  cta   : card + tela + "COMENTA TTS E RECEBA O / Acesso à ferramenta" (só o acesso: nada de prometer brinde)
Marcação nos textos: **negrito**, __sublinhado__, [[roxo]] (cor de destaque).
Uso: python3 figcraft/premium.py <spec.json> <saida> <PREFIXO> --cli <figcraft-cli>
"""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1350
BG = "#07060C"
ROXO = "#A27BFF"
GRAD = {"type": "linearGradient", "stops": ["#E4D7FF", "#B08CFF", "#7A3CF5"]}
SANS, DISP, SERIF, COND, MONO = "Inter", "Inter Display", "Playfair Display", "Bebas Neue", "Space Mono"


def marcar(txt):
    """'a **b** __c__ [[d]]' -> texto limpo + lista de (ini, fim, tipo)."""
    out, ranges, i = "", [], 0
    pat = re.compile(r"\*\*(.+?)\*\*|__(.+?)__|\[\[(.+?)\]\]")
    for m in pat.finditer(txt):
        out += txt[i:m.start()]
        trecho = next(g for g in m.groups() if g is not None)
        tipo = "b" if m.group(1) else ("u" if m.group(2) else "c")
        ranges.append((len(out), len(out) + len(trecho), tipo)); out += trecho; i = m.end()
    return out + txt[i:], ranges


class Doc:
    def __init__(self): self.cmds, self.prox = [], 2
    def add(self, c, p, cria=True):
        self.cmds.append({"command": c, "params": p})
        if cria:
            i = self.prox; self.prox += 1; return i
    def frame(self, **p): return self.add("frame.create", p)
    def img(self, **p): return self.add("image.place", p)
    def node(self, **p): return self.add("node.create", p)
    def fx(self, ids, tipo, e): self.add("effect.add", {"ids": ids, "type": tipo, "effect": {"type": tipo, **e}}, cria=False)

    def texto(self, txt, x, y, w, pai, fam, est, tam, cor="#FFFFFF", alin="center", lh="112%", ls="-1%", negrito="Bold", **extra):
        limpo, rg = marcar(txt)
        props = {"fontFamily": fam, "fontStyle": est, "fontSize": tam, "textAlign": alin, "lineHeight": lh,
                 "letterSpacing": ls, "fills": [cor], "textAutoResize": "height", **extra}
        t = self.add("text.create", {"text": limpo, "x": x, "y": y, "width": w, "parent": pai, "props": props})
        for a, b, tp in rg:
            if tp == "b": self.add("text.style", {"id": t, "start": a, "end": b, "fontStyle": negrito}, cria=False)
            if tp == "u": self.add("text.style", {"id": t, "start": a, "end": b, "textDecoration": "underline"}, cria=False)
            if tp == "c": self.add("text.style", {"id": t, "start": a, "end": b, "fontStyle": negrito, "textFills": [ROXO]}, cria=False)
        return t


def recorte(src, dst, w, h, y0=0, x0=0, larg=None):
    im = Image.open(ROOT / src).convert("RGB")
    larg = larg or im.width - x0
    alt = int(larg * h / w)
    y0 = max(0, min(y0, im.height - alt))
    im.crop((x0, y0, x0 + larg, y0 + alt)).resize((w * 2, h * 2), Image.LANCZOS).save(dst, quality=93)
    return str(dst)


def fundo(doc, i, nome):
    fr = doc.frame(x=i * (W + 120), y=0, width=W, height=H, name=nome, props={"fill": BG, "clip": True})
    g = doc.node(type="ellipse", x=-200, y=-260, width=900, height=700, parent=fr, props={"fill": "#3B1D8F", "opacity": 0.55})
    doc.fx([g], "layerBlur", {"radius": 260})
    g2 = doc.node(type="ellipse", x=520, y=900, width=800, height=600, parent=fr, props={"fill": "#24125E", "opacity": 0.6})
    doc.fx([g2], "layerBlur", {"radius": 260})
    return fr


def rodape(doc, fr, handle, seta=True):
    if seta:
        doc.node(type="vector", x=730, y=1222, width=290, height=30, parent=fr,
                 path="M0 15 H285 M265 0 L287 15 L265 30", props={"fill": "none", "stroke": "#FFFFFF", "strokeWeight": 5, "strokeCap": "round", "strokeJoin": "round"})
    doc.texto(handle, 560, 1268, 460, fr, SANS, "Semi Bold", 40, alin="right", ls="0%")


def quadro(doc, pai, img, x, y, w, h, raio=28, rotulo=None, borda="#2A2340"):
    f = doc.frame(x=x, y=y, width=w, height=h, parent=pai, name=rotulo or "print",
                  props={"fill": "#000000", "cornerRadius": raio, "clip": True, "stroke": borda, "strokeWeight": 2, "strokeAlign": "inside"})
    doc.fx([f], "dropShadow", {"color": "#7A3CF566", "offset": [0, 0], "radius": 60, "spread": 0})
    doc.img(path=img, x=0, y=0, width=w, height=h, parent=f, mode="fill")
    if rotulo:
        doc.texto(rotulo.upper(), x, y - 34, w, pai, MONO, "Regular", 20, cor="#A9A3BF", ls="4%")
    return f


def bbox_card(src):
    """Caixa do card do vídeo (com as métricas) dentro do s1 composto (fundo liso)."""
    from PIL import ImageChops
    im = Image.open(ROOT / src).convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((5, 5)))
    return ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 18 else 0).getbbox()


def vitrine(doc, fr, s, tmp, i, topo=80, ch=600, vh=470):
    """Card do vídeo de referência (com vendas/faturamento/views) + tela da variação, sem linhas ligando."""
    x0, y0, x1, y1 = bbox_card(s["card"])
    im = Image.open(ROOT / s["card"]).convert("RGB").crop((x0, y0, x1, y1))
    cw = int(im.width * ch / im.height)
    a = tmp / f"card{i}.jpg"; im.resize((cw * 2, ch * 2), Image.LANCZOS).save(a, quality=94)
    quadro(doc, fr, str(a), 70, topo + 40, cw, ch, raio=26, rotulo="vídeo de referência")
    vx = 70 + cw + 50; vw = W - vx - 50
    v = recorte(s["tela"][0], tmp / f"tela{i}.jpg", vw, vh, s["tela"][1])
    quadro(doc, fr, v, vx, topo + 110, vw, vh, raio=26, rotulo=s["tela"][2])
    # selo com o faturamento embaixo da tela da variação (não cobre as métricas do card)
    selo = doc.frame(x=vx, y=topo + 110 + vh + 26, width=10, height=10, parent=fr, name="selo",
                     props={"fills": [{"type": "linearGradient", "stops": ["#9B6BFF", "#6A2FE8"]}], "cornerRadius": 999,
                            "layout": "horizontal", "padding": [12, 26, 12, 26], "sizingH": "hug", "sizingV": "hug"})
    doc.fx([selo], "dropShadow", {"color": "#00000099", "offset": [0, 10], "radius": 30, "spread": 0})
    doc.add("text.create", {"text": s["selo"], "x": 0, "y": 0, "parent": selo,
                            "props": {"fontFamily": DISP, "fontStyle": "Bold", "fontSize": 38, "fills": ["#FFFFFF"]}})


def slide(doc, i, s, tmp, handle):
    t = s["tipo"]
    fr = fundo(doc, i, f"{i + 1:02d} {t}")
    if t == "capa":
        k = bool(s.get("kicker"))
        vitrine(doc, fr, s, tmp, i, topo=40, ch=540 if k else 600, vh=420 if k else 470)
        dy = 0
        if k:  # nicho: fala direto com o afiliado do TikTok Shop
            dy = 42
            pil = doc.frame(x=0, y=696, width=W, height=64, parent=fr, name="kicker",
                            props={"fill": "none", "layout": "horizontal", "mainAlign": "center"})
            p = doc.frame(x=0, y=0, width=10, height=10, parent=pil, props={"fill": "#FFFFFF", "cornerRadius": 14, "layout": "horizontal",
                          "padding": [6, 22, 6, 22], "sizingH": "hug", "sizingV": "hug"})
            doc.add("text.create", {"text": s["kicker"], "x": 0, "y": 0, "parent": p,
                                    "props": {"fontFamily": MONO, "fontStyle": "Bold", "fontSize": 36, "fills": ["#000000"]}})
        doc.texto(s["l1"], 60, 745 + dy, 960, fr, DISP, "Bold", 88, ls="-2%")
        doc.texto(s["l2"], 20, 812 + dy, 1040, fr, SERIF, "ExtraBold Italic", 190, cor=GRAD, lh="100%", ls="-2%")
        doc.texto(s["l3"], 60, 1030 + dy, 960, fr, DISP, "Bold", 52, ls="-1%")
        doc.texto(s["l4"], 60, 1094 + dy, 960, fr, DISP, "Light", 42, cor="#D9D3EA")
        rodape(doc, fr, handle)
    elif t == "lista":
        pil = doc.frame(x=0, y=110, width=W, height=70, parent=fr, name="pílula",
                        props={"fill": "none", "layout": "horizontal", "mainAlign": "center"})
        p = doc.frame(x=0, y=0, width=10, height=10, parent=pil, props={"fill": "#FFFFFF", "cornerRadius": 14, "layout": "horizontal",
                      "padding": [6, 22, 6, 22], "sizingH": "hug", "sizingV": "hug"})
        doc.add("text.create", {"text": s["pilula"], "x": 0, "y": 0, "parent": p, "props": {"fontFamily": MONO, "fontStyle": "Regular", "fontSize": 40, "fills": ["#000000"]}})
        doc.texto(s["titulo"], 70, 210, 940, fr, DISP, "Light", 78, lh="108%", ls="-2%")
        y = 520
        for n, item in enumerate(s["itens"], 1):
            doc.texto(f"{n:02d}", 110, y + 4, 120, fr, MONO, "Bold", 44, cor=ROXO, alin="left", ls="0%")
            doc.texto(item, 240, y, 740, fr, SANS, "Regular", 50, alin="left", lh="118%", ls="-1%")
            doc.node(type="rectangle", x=110, y=y + 100, width=860, height=2, parent=fr, props={"fill": "#2A2340"})
            y += 124
        rodape(doc, fr, handle)
    elif t == "passo":
        pil = doc.frame(x=0, y=48, width=W, height=70, parent=fr, name="pílula",
                        props={"fill": "none", "layout": "horizontal", "mainAlign": "center"})
        p = doc.frame(x=0, y=0, width=10, height=10, parent=pil, props={"fill": "#FFFFFF", "cornerRadius": 14, "layout": "horizontal",
                      "padding": [4, 20, 4, 20], "sizingH": "hug", "sizingV": "hug"})
        doc.add("text.create", {"text": f"Passo {s['n']}", "x": 0, "y": 0, "parent": p, "props": {"fontFamily": MONO, "fontStyle": "Regular", "fontSize": 40, "fills": ["#000000"]}})
        doc.texto(s["titulo"], 60, 130, 960, fr, DISP, "Light", 68, lh="106%", ls="-2%")
        img = recorte(s["print"], tmp / f"p{i}.jpg", 1000, 560, s.get("y", 0), s.get("x", 0), s.get("larg"))
        quadro(doc, fr, img, 40, 330, 1000, 560, raio=30)
        doc.texto(s["texto"], 100, 930, 880, fr, SANS, "Regular", 50, alin="left", lh="116%", ls="-2%")
        rodape(doc, fr, handle)
    elif t == "cta":
        vitrine(doc, fr, s, tmp, i, topo=20)
        col = doc.frame(x=20, y=740, width=1040, height=100, parent=fr, name="cta",
                        props={"fill": "none", "layout": "vertical", "gap": 6, "crossAlign": "center", "sizingV": "hug"})
        doc.texto(s["l1"], 0, 0, 1040, col, COND, "Regular", 112, lh="100%", ls="0%", negrito="Regular")
        doc.texto(s["l2"], 0, 0, 1040, col, SERIF, "ExtraBold Italic", 104, cor=GRAD, lh="104%", ls="-2%")
        if s.get("l3"):
            doc.texto(s["l3"], 0, 0, 1040, col, COND, "Regular", 112, lh="100%", ls="0%")
        rodape(doc, fr, handle, seta=False)
    return fr


def main():
    spec_p, saida, pref = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
    cli = sys.argv[sys.argv.index("--cli") + 1] if "--cli" in sys.argv else "figcraft-cli"
    spec = json.load(open(spec_p)); saida.mkdir(parents=True, exist_ok=True)
    tmp = saida / "_tmp"; tmp.mkdir(exist_ok=True)
    doc = Doc()
    for i, s in enumerate(spec["slides"]):
        slide(doc, i, s, tmp, spec.get("handle", "@silvaa.bnss"))
    sc = tmp / "script.json"; json.dump(doc.cmds, open(sc, "w"), ensure_ascii=False)
    arq = saida / f"{pref}.figcraft"
    r = subprocess.run([cli, "run", str(sc), "--out", str(arq)], capture_output=True, text=True)
    if r.returncode or '"ok":false' in r.stdout:
        print([l for l in r.stdout.splitlines() if '"ok":false' in l][:3], r.stderr[-1500:]); sys.exit(1)
    exp = tmp / "png"; exp.mkdir(exist_ok=True)
    for f in exp.glob("*.png"): f.unlink()
    r = subprocess.run([cli, "export", str(arq), "-o", str(exp), "--format", "png"], capture_output=True, text=True)
    if r.returncode: print(r.stdout, r.stderr); sys.exit(1)
    for n, f in enumerate(sorted(exp.glob("*.png")), 1):
        Image.open(f).convert("RGB").save(saida / f"{pref}_{n:02d}.jpg", quality=94)
    (saida / "legenda.txt").write_text(spec.get("legenda", ""), encoding="utf-8")
    print("ok", len(list(exp.glob('*.png'))), "slides ->", saida)


if __name__ == "__main__":
    main()
