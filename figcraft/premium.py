"""Carrossel "premium" (estilo dos virais de passo a passo) montado no FigCraft, sem janela.

Formato 1080x1350 (4:5). Paleta escura com roxo. Tipos de slide:
  capa  : colagem de 3 telas ligadas por linhas + "Roube a / Estrutura / de um vídeo que..."
  lista : "Salva esse passo a passo" com os 5 passos numerados
  passo : pílula "Passo N" + título (leve + **negrito**) + faixa com o print + texto com **negrito** e __sublinhado__
  cta   : colagem + "COMENTA TTS E RECEBA / Ferramenta + Estrutura / PRA COPIAR E GRAVAR"
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


def linha(doc, pai, path, x, y, w, h):
    doc.node(type="vector", x=x, y=y, width=w, height=h, parent=pai, path=path,
             props={"fill": "none", "stroke": "#8B63FF", "strokeWeight": 2})


def colagem(doc, fr, ims, tmp, i, topo=70):
    def r(k, w, h):
        it = ims[k]
        return recorte(it[0], tmp / f"c{i}{k}.jpg", w, h, it[1], it[3] if len(it) > 3 else 0, it[4] if len(it) > 4 else None)
    a, b, c = r(0, 300, 400), r(1, 230, 260), r(2, 400, 560)
    linha(doc, fr, "M0 0 H60 L120 -90", 335, topo + 370, 130, 100)
    linha(doc, fr, "M0 0 V60 H200", 455, topo + 270, 210, 70)
    quadro(doc, fr, a, 40, topo + 110, 300, 400, rotulo=ims[0][2])
    quadro(doc, fr, b, 350, topo + 10, 230, 260, rotulo=ims[1][2])
    quadro(doc, fr, c, 640, topo + 30, 400, 560, rotulo=ims[2][2])


def slide(doc, i, s, tmp, handle):
    t = s["tipo"]
    fr = fundo(doc, i, f"{i + 1:02d} {t}")
    if t == "capa":
        colagem(doc, fr, s["colagem"], tmp, i, topo=60)
        doc.texto(s["l1"], 60, 700, 960, fr, DISP, "Bold", 92, ls="-2%")
        doc.texto(s["l2"], 20, 772, 1040, fr, SERIF, "ExtraBold Italic", 200, cor=GRAD, lh="100%", ls="-2%")
        doc.texto(s["l3"], 60, 1000, 960, fr, DISP, "Bold", 54, ls="-1%")
        doc.texto(s["l4"], 60, 1066, 960, fr, DISP, "Light", 44, cor="#D9D3EA")
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
        img = recorte(s["print"], tmp / f"p{i}.jpg", 1000, 560, s.get("y", 0))
        quadro(doc, fr, img, 40, 330, 1000, 560, raio=30)
        doc.texto(s["texto"], 100, 930, 880, fr, SANS, "Regular", 50, alin="left", lh="116%", ls="-2%")
        rodape(doc, fr, handle)
    elif t == "cta":
        colagem(doc, fr, s["colagem"], tmp, i, topo=40)
        col = doc.frame(x=20, y=680, width=1040, height=100, parent=fr, name="cta",
                        props={"fill": "none", "layout": "vertical", "gap": 6, "crossAlign": "center", "sizingV": "hug"})
        doc.texto(s["l1"], 0, 0, 1040, col, COND, "Regular", 112, lh="100%", ls="0%", negrito="Regular")
        doc.texto(s["l2"], 0, 0, 1040, col, SERIF, "ExtraBold Italic", 104, cor=GRAD, lh="104%", ls="-2%")
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
