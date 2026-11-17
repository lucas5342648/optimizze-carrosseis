"""Monta um carrossel no FigCraft (sem janela) a partir de um spec e exporta os PNGs.

Uso: python3 figcraft/montar.py <spec.json> <pasta_saida> <PREFIXO> [--cli caminho/figcraft-cli]
Gera <pasta_saida>/<PREFIXO>.figcraft (editável no app) e <PREFIXO>_01.png ... (1080x1920).

Spec (tipos de slide):
  {"tipo": "capa", "print": "assets/prints/<p>/s1.jpg", "linha1": "Esse vídeo rendeu", "linha2": "R$ 109 mil em 7 dias", "chip": "271 microfones vendidos (estimado)"}
  {"tipo": "lista", "linha1": "Salva esse", "linha2": "passo a passo", "itens": ["...", ...]}
  {"tipo": "passo", "n": 1, "total": 5, "titulo": "Acha um vídeo que já vende", "print": ".../s2.jpg", "corte_y": 0}
  {"tipo": "cta", "linha1": "Comenta", "linha2": "TTS", "sub": "pra receber o acesso à ferramenta"}
Área segura: todo conteúdo fica entre x 90..990 e y 170..1640 (o TikTok cobre bordas e a base).
"""
import json, os, subprocess, sys
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
FUNDO = {"type": "linearGradient", "stops": ["#0B0A12", "#1C1236"]}
AMARELO, BRANCO, CINZA = "#FFD600", "#FFFFFF", "#B9B3CC"
DISPLAY, CORPO = "Inter Display", "Inter"


class Doc:
    def __init__(self, pasta):
        self.cmds, self.prox, self.pasta = [], 2, Path(pasta)

    def _add(self, command, params, cria=True):
        self.cmds.append({"command": command, "params": params})
        if cria:
            i = self.prox; self.prox += 1; return i

    def frame(self, **p): return self._add("frame.create", p)
    def texto(self, **p): return self._add("text.create", p)
    def imagem(self, **p): return self._add("image.place", p)
    def efeito(self, ids, tipo, efeito): self._add("effect.add", {"ids": ids, "type": tipo, "effect": {"type": tipo, **efeito}}, cria=False)


def pilha(doc, pai, y, gap=28, nome="conteúdo"):
    """Coluna centralizada (auto layout vertical): os filhos empilham sem sobrepor."""
    return doc.frame(x=90, y=y, width=900, height=100, parent=pai, name=nome,
                     props={"fill": "none", "layout": "vertical", "gap": gap, "crossAlign": "center", "sizingV": "hug"})


def titulo(doc, pai, txt, y, tam, cor=BRANCO, fam=DISPLAY, estilo="Black", larg=900):
    return doc.texto(text=txt, x=(W - larg) // 2, y=y, width=larg, parent=pai,
                     props={"fontFamily": fam, "fontStyle": estilo, "fontSize": tam, "textAlign": "center",
                            "lineHeight": "106%", "letterSpacing": "-1%", "fills": [cor], "textAutoResize": "height"})


def pilula(doc, pai, txt, fundo=AMARELO, cor="#0B0A12", tam=30):
    p = doc.frame(x=0, y=0, width=200, height=60, parent=pai, name="pílula",
                  props={"fill": fundo, "cornerRadius": 999, "layout": "horizontal", "padding": [12, 28, 12, 28],
                         "sizingH": "hug", "sizingV": "hug"})
    doc.texto(text=txt, x=0, y=0, parent=p, props={"fontFamily": CORPO, "fontStyle": "Bold", "fontSize": tam,
                                                    "letterSpacing": "4%", "fills": [cor]})


def recorte(src, dst, larg, alt, y0=0):
    im = Image.open(ROOT / src).convert("RGB")
    w = im.width; h = int(w * alt / larg)
    y0 = max(0, min(y0, im.height - h))
    im.crop((0, y0, w, y0 + h)).resize((larg * 2 // 2, alt), Image.LANCZOS).save(dst, quality=93)
    return str(dst)


def card_da_capa(src, dst):
    """Recorta só o card do vídeo do s1 composto (fundo liso #0E0D14)."""
    im = Image.open(ROOT / src).convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((5, 5)))
    caixa = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 18 else 0).getbbox()
    im.crop(caixa).save(dst, quality=95)
    return str(dst), im.crop(caixa).size


def tela(doc, pai, img, x, y, w, h):
    f = doc.frame(x=x, y=y, width=w, height=h, parent=pai, name="tela",
                  props={"fill": "#000000", "cornerRadius": 44, "clip": True, "stroke": "#3A3352", "strokeWeight": 6, "strokeAlign": "outside"})
    doc.efeito([f], "dropShadow", {"color": "#00000AA0", "offset": [0, 30], "radius": 70, "spread": 0})
    doc.imagem(path=img, x=0, y=0, width=w, height=h, parent=f, mode="fill")
    return f


def slide(doc, i, tipo, s, tmp):
    fr = doc.frame(x=i * (W + 120), y=0, width=W, height=H, name=f"{i + 1:02d} {tipo}", props={"fills": [FUNDO], "clip": True})
    brilho = doc._add("node.create", {"type": "ellipse", "x": 140, "y": 700, "width": 800, "height": 800, "parent": fr,
                                       "props": {"fill": "#6D3BFF", "opacity": 0.35}})
    doc.efeito([brilho], "layerBlur", {"radius": 220})
    if tipo == "capa":
        col = pilha(doc, fr, 180, gap=30)
        bloco = doc.frame(x=0, y=0, width=900, height=100, parent=col, name="headline",
                          props={"fill": "none", "layout": "vertical", "gap": 0, "crossAlign": "center", "sizingV": "hug"})
        titulo(doc, bloco, s["linha1"], 0, 92)
        titulo(doc, bloco, s["linha2"], 0, 92, AMARELO)
        pilula(doc, col, s["chip"], fundo="#FFFFFF", cor="#0B0A12", tam=34)
        card, (cw, ch) = card_da_capa(s["print"], tmp / f"capa_{i}.jpg")
        h = 960; w = int(cw * h / ch)
        if w > 640: w = 640; h = int(ch * w / cw)
        tela(doc, col, card, 0, 0, w, h)
    elif tipo == "lista":
        col = pilha(doc, fr, 250, gap=56)
        bloco = doc.frame(x=0, y=0, width=900, height=100, parent=col, name="headline",
                          props={"fill": "none", "layout": "vertical", "gap": 0, "crossAlign": "center", "sizingV": "hug"})
        titulo(doc, bloco, s["linha1"], 0, 118)
        titulo(doc, bloco, s["linha2"], 0, 118, AMARELO)
        caixa = doc.frame(x=0, y=0, width=860, height=900, parent=col, name="lista",
                          props={"fill": "#17132A", "cornerRadius": 40, "stroke": "#2E2745", "strokeWeight": 3,
                                 "layout": "vertical", "gap": 34, "padding": [56, 50, 56, 50], "sizingV": "hug"})
        for n, item in enumerate(s["itens"], 1):
            row = doc.frame(x=0, y=0, width=760, height=80, parent=caixa, name=f"item {n}",
                            props={"fill": "none", "layout": "horizontal", "gap": 28, "crossAlign": "center", "sizingH": "fill", "sizingV": "hug"})
            bol = doc.frame(x=0, y=0, width=72, height=72, parent=row, name="nº",
                            props={"fill": AMARELO, "cornerRadius": 36, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"})
            doc.texto(text=str(n), x=0, y=0, parent=bol, props={"fontFamily": DISPLAY, "fontStyle": "Black", "fontSize": 40, "fills": ["#0B0A12"]})
            doc.texto(text=item, x=0, y=0, width=640, parent=row,
                      props={"fontFamily": CORPO, "fontStyle": "Bold", "fontSize": 42, "lineHeight": "120%", "fills": [BRANCO], "textAutoResize": "height", "sizingH": "fill"})
        titulo(doc, col, "arrasta pro lado  →", 0, 34, CINZA, CORPO, "Semi Bold")
    elif tipo == "passo":
        col = pilha(doc, fr, 190, gap=34)
        pilula(doc, col, f"PASSO {s['n']} DE {s['total']}")
        titulo(doc, col, s["titulo"], 0, 76)
        alt = 1000 if len(s["titulo"]) <= 34 else 920
        img = recorte(s["print"], tmp / f"passo_{i}.jpg", 760, alt, s.get("corte_y", 0))
        tela(doc, col, img, 0, 0, 760, alt)
    elif tipo == "cta":
        col = pilha(doc, fr, 400, gap=50)
        bloco = doc.frame(x=0, y=0, width=900, height=100, parent=col, name="headline",
                          props={"fill": "none", "layout": "vertical", "gap": 0, "crossAlign": "center", "sizingV": "hug"})
        titulo(doc, bloco, s["linha1"], 0, 150)
        titulo(doc, bloco, s["linha2"], 0, 300, AMARELO)
        # comentário de exemplo (posições fixas: mais estável que auto layout aninhado)
        bolha = doc.frame(x=190, y=1010, width=700, height=150, parent=fr, name="comentário",
                          props={"fill": "#FFFFFF", "cornerRadius": 36})
        doc.efeito([bolha], "dropShadow", {"color": "#00000080", "offset": [0, 20], "radius": 50, "spread": 0})
        doc._add("node.create", {"type": "ellipse", "x": 36, "y": 33, "width": 84, "height": 84, "parent": bolha, "props": {"fill": "#C9C3DA"}})
        doc.texto(text="você", x=148, y=28, parent=bolha, props={"fontFamily": CORPO, "fontStyle": "Semi Bold", "fontSize": 30, "fills": ["#8A8499"]})
        doc.texto(text="TTS", x=148, y=64, parent=bolha, props={"fontFamily": DISPLAY, "fontStyle": "Black", "fontSize": 52, "fills": ["#0B0A12"]})
        titulo(doc, fr, s["sub"], 1230, 50, BRANCO, CORPO, "Bold", 820)
    return fr


def main():
    spec_p, saida, pref = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
    cli = sys.argv[sys.argv.index("--cli") + 1] if "--cli" in sys.argv else "figcraft-cli"
    spec = json.load(open(spec_p))
    saida.mkdir(parents=True, exist_ok=True)
    tmp = saida / "_tmp"; tmp.mkdir(exist_ok=True)
    doc = Doc(saida)
    for i, s in enumerate(spec["slides"]):
        slide(doc, i, s["tipo"], s, tmp)
    script = tmp / "script.json"; json.dump(doc.cmds, open(script, "w"), ensure_ascii=False)
    arq = saida / f"{pref}.figcraft"
    r = subprocess.run([cli, "run", str(script), "--out", str(arq)], capture_output=True, text=True)
    erros = [l for l in r.stdout.splitlines() if '"ok":false' in l]
    if r.returncode or erros:
        print(r.stdout[-3000:], r.stderr[-2000:]); sys.exit(1)
    exp = tmp / "png"; exp.mkdir(exist_ok=True)
    r = subprocess.run([cli, "export", str(arq), "-o", str(exp), "--format", "png"], capture_output=True, text=True)
    if r.returncode: print(r.stdout, r.stderr); sys.exit(1)
    arquivos = sorted(exp.glob("*.png"))
    for n, f in enumerate(arquivos, 1):
        Image.open(f).convert("RGB").save(saida / f"{pref}_{n:02d}.jpg", quality=93)
    (saida / "legenda.txt").write_text(spec.get("legenda", ""), encoding="utf-8")
    print("ok", len(arquivos), "slides ->", saida)


if __name__ == "__main__":
    main()
