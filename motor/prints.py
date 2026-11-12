"""Carrossel com PRINTS REAIS da Optimizze (telas abertas com o código do app + dados do conector).

Cada slide = um print (9:16) + legenda em caixa branca no estilo nativo, depois `enquadrar`.
Os prints são gerados pela ferramenta de captura (ver README em assets/prints/).

Uso: python3 motor/prints.py spec.json pasta_saida PREFIXO
spec.json:
{
  "legenda": "texto do post...",
  "slides": [
    {"print": "assets/prints/<pasta>/s1.jpg", "texto": "Gancho da capa", "y": 0.16, "tam": 64},
    ...
    {"cta": {"print": "assets/prints/<pasta>/s4.jpg", "titulo": "Comenta TTS", "texto": "pra receber o acesso à ferramenta"}}
  ]
}
Capa com headline: {"print": ..., "headline": {"texto": "Afiliado: ...", "y": 0.06, "tam": 92, "cor": "white|amarelo"},
                    "texto": "subtítulo na caixa branca", "y": 0.27}
Slide de dor/promessa: {"cta": {"print": ..., "titulo": "O segredo é a estrutura", "tam": 120, "y": 0.30,
                                "texto": "caixa branca abaixo"}}
{
  "slides": [
  ]
}
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0, str(Path(__file__).resolve().parent))
from seguro import enquadrar
from nativo import caixa, wrap, FONT_X, W, H

ROOT = Path(__file__).resolve().parent.parent


def carregar(caminho):
    im = Image.open(ROOT / caminho).convert("RGB")
    w, h = im.size
    if abs(w / h - 9 / 16) > 0.01:  # corta pra 9:16 a partir do topo
        nh = int(w * 16 / 9)
        im = im.crop((0, 0, w, min(h, nh))) if h > nh else im
    return im.resize((W, H), Image.LANCZOS)


AMARELO = (255, 214, 0)


def headline(im, texto, y, tam=92, cor="white", maxw=0.88):
    """Título grande com contorno preto (estilo legenda de TikTok). y = topo do bloco (0-1)."""
    d = ImageDraw.Draw(im)
    ft = ImageFont.truetype(FONT_X, tam)
    cor = AMARELO if cor == "amarelo" else cor
    yy = H * y
    for l in wrap(d, texto, ft, W * maxw):
        d.text(((W - d.textlength(l, font=ft)) / 2, yy), l, font=ft, fill=cor, stroke_width=max(4, tam // 14), stroke_fill="black")
        yy += int(tam * 1.12)
    return yy


def slide_cta(c):
    """Slide de texto sobre um print desfocado: CTA ou slide de "dor/promessa"."""
    im = ImageEnhance.Brightness(carregar(c["print"]).filter(ImageFilter.GaussianBlur(18))).enhance(0.35)
    d = ImageDraw.Draw(im)
    tam = c.get("tam", 150)
    ft = ImageFont.truetype(FONT_X, tam)
    y = H * c.get("y", 0.333)
    for l in wrap(d, c.get("titulo", "Comenta TTS"), ft, W * 0.86):
        d.text(((W - d.textlength(l, font=ft)) / 2, y), l, font=ft, fill=AMARELO if c.get("cor") == "amarelo" else "white"); y += int(tam * 1.13)
    if c.get("texto"):
        caixa(im, c["texto"], [140, y + 60, 940, y + 200], "white", c.get("tam_texto", 54))
    return im


def render(spec_path, out_dir, prefixo):
    spec = json.load(open(spec_path))
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    n = 0
    for i, s in enumerate(spec["slides"], 1):
        if "cta" in s:
            im = slide_cta(s["cta"])
        else:
            im = carregar(s["print"])
            if s.get("headline"):  # título grande no topo (gancho da capa)
                h = s["headline"]
                headline(im, h["texto"], h.get("y", 0.06), h.get("tam", 92), h.get("cor", "white"))
            if s.get("texto"):
                cy = H * s.get("y", 0.16)
                caixa(im, s["texto"], [120, cy - 60, W - 120, cy + 60], s.get("estilo", "white"), s.get("tam", 58))
        enquadrar(im).save(out / f"{prefixo}_{i:02d}.jpg", quality=93); n += 1
    (out / "legenda.txt").write_text(spec.get("legenda", ""), encoding="utf-8")
    print("ok", n, "slides ->", out)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], sys.argv[3])
