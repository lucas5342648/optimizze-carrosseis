"""Carrossel no estilo NATIVO do TikTok: prints/fotos reais + legenda em caixa branca.

Usa as imagens de assets/base/ e o mapa de caixas assets/base/base.json.
A nova legenda é desenhada por cima da legenda antiga (cobrindo-a).

Uso: python3 motor/nativo.py spec.json pasta_saida PREFIXO
spec.json:
{
  "legenda": "texto do post...",
  "slides": [
    {"base": "01_capa_camiseta.jpg", "texto": "Gancho da capa", "tam": 62},
    {"base": "02_kalodata.jpg", "texto": "Passo 1: ..."},
    ...
    {"cta": {"base": "08_editor_pronto.jpg", "titulo": "Comenta TTS", "texto": "pra receber o acesso à ferramenta"}}
  ]
}
Emojis NÃO são renderizados (sem fonte de emoji); use emojis só na legenda do post.
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0, str(Path(__file__).resolve().parent))
from seguro import enquadrar

W, H = 1080, 1920
ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "assets" / "base"
FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_X = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"


def wrap(d, text, font, maxw):
    out = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=font) <= maxw:
                cur = t
            else:
                out.append(cur); cur = w
        out.append(cur)
    return out


def caixa(img, text, box, style="white", size=56):
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, size)
    lines = wrap(d, text, font, W * 0.80)
    lh = int(size * 1.22)
    tw = max(d.textlength(l, font=font) for l in lines)
    th = lh * len(lines)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    bw = max(tw + 60, box[2] - box[0] + 24)
    bh = max(th + 44, box[3] - box[1] + 24)
    x0, y0 = cx - bw / 2, cy - bh / 2
    bg, fg = ("white", "black") if style == "white" else ("black", "white")
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=18, fill=bg)
    y = cy - th / 2 + (lh - size) / 2 - size * 0.08
    for l in lines:
        d.text((cx - d.textlength(l, font=font) / 2, y), l, font=font, fill=fg)
        y += lh


def carregar(nome):
    im = Image.open(BASE / nome).convert("RGB")
    w, h = im.size
    off = 0
    if abs(w / h - 9 / 16) > 0.01:
        nw = int(h * 9 / 16); off = (w - nw) // 2
        im = im.crop((off, 0, off + nw, h))
    s = W / im.size[0]
    return im.resize((W, H), Image.LANCZOS), off, s


def slide_cta(c):
    im, off, sc = carregar(c["base"])
    b = json.load(open(BASE / "base.json")).get(c["base"], {}).get("box")
    if b:  # apaga a legenda antiga antes de desfocar
        box = [int((b[0] - off) * sc) - 20, int(b[1] * sc) - 20, int((b[2] - off) * sc) + 20, int(b[3] * sc) + 20]
        im.paste(im.filter(ImageFilter.GaussianBlur(60)).crop(box), box[:2])
    im = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(18))).enhance(0.35)
    d = ImageDraw.Draw(im)
    ft = ImageFont.truetype(FONT_X, 150)
    t = c.get("titulo", "Comenta TTS")
    lines_t = wrap(d, t, ft, W * 0.86)
    y = 640
    for l in lines_t:
        d.text(((W - d.textlength(l, font=ft)) / 2, y), l, font=ft, fill="white"); y += 170
    caixa(im, c["texto"], [140, y + 60, 940, y + 200], "white", 54)
    return im


def render(spec_path, out_dir, prefixo):
    mapa = json.load(open(BASE / "base.json"))
    spec = json.load(open(spec_path))
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    arquivos = []
    for i, s in enumerate(spec["slides"], 1):
        if "cta" in s:
            im = slide_cta(s["cta"])
        else:
            im, off, sc = carregar(s["base"])
            b = mapa[s["base"]]["box"]
            box = [(b[0] - off) * sc, b[1] * sc, (b[2] - off) * sc, b[3] * sc]
            caixa(im, s["texto"], box, mapa[s["base"]].get("style", "white"), s.get("tam", 56))
        f = out / f"{prefixo}_{i:02d}.jpg"
        enquadrar(im).save(f, quality=93); arquivos.append(f.name)
    (out / "legenda.txt").write_text(spec.get("legenda", ""), encoding="utf-8")
    print("ok", len(arquivos), "slides ->", out)
    return arquivos


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], sys.argv[3])
