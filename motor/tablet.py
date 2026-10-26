"""Estilo TABLET (inspirado em carrossel viral do nicho: 8,8 mil curtidas / 8,9 mil saves).

Cada slide: print real dentro de um aparelho (tablet/celular) inclinado sobre fundo desfocado
e quente, com legenda em 2 camadas: caixa BRANCA (título) + caixa VERMELHA (complemento).

Uso: python3 motor/tablet.py spec.json pasta_saida PREFIXO
spec.json:
{"legenda": "...", "slides": [
   {"base": "01_capa_camiseta.jpg", "branco": "Título", "vermelho": "Complemento", "fullbleed": true},
   {"base": "02_kalodata.jpg", "branco": "1) ...", "vermelho": "..."},
   ...]}
"fullbleed": true usa a imagem inteira (bom pra capa com foto POV); senão, a imagem vai dentro do aparelho.
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H = 1080, 1920
ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "assets" / "base"
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
RED = (232, 44, 60)


def wrap(d, text, font, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            out.append(cur); cur = w
    out.append(cur)
    return out


def box(img, y, text, bg, fg, size, font_path):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(font_path, size)
    lines = wrap(d, text, f, W * 0.78)
    lh = int(size * 1.2)
    tw = max(d.textlength(l, font=f) for l in lines)
    bw, bh = tw + 48, lh * len(lines) + 26
    x0 = (W - bw) / 2
    d.rounded_rectangle([x0, y, x0 + bw, y + bh], radius=14, fill=bg)
    ty = y + 13 + (lh - size) / 2 - size * 0.08
    for l in lines:
        d.text(((W - d.textlength(l, font=f)) / 2, ty), l, font=f, fill=fg); ty += lh
    return y + bh


def legendas(img, s, y=150):
    y = box(img, y, s["branco"], "white", "black", 54, FB)
    if s.get("vermelho"):
        y = box(img, y + 6, s["vermelho"], RED, "white", 40, FS)
    return y


def abrir(nome):
    """Abre o print e APAGA a legenda antiga (área de base.json) com um remendo desfocado."""
    im = Image.open(BASE / nome).convert("RGB")
    mapa = json.load(open(BASE / "base.json"))
    b = mapa.get(nome, {}).get("box")
    if b:
        x0, y0, x1, y1 = b[0] - 14, b[1] - 14, b[2] + 14, b[3] + 14
        borrado = im.filter(ImageFilter.GaussianBlur(45))
        im.paste(borrado.crop((x0, y0, x1, y1)), (x0, y0))
    w, h = im.size
    if abs(w / h - 9 / 16) > 0.01:
        nw = int(h * 9 / 16); off = (w - nw) // 2
        im = im.crop((off, 0, off + nw, h))
    return im


def fundo(im):
    bg = im.resize((W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    quente = Image.new("RGB", (W, H), (120, 70, 30))
    return Image.blend(bg, quente, 0.25)


def aparelho(im, angulo):
    tela = im.resize((640, 1138))
    pad = 26
    dev = Image.new("RGBA", (640 + 2 * pad, 1138 + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(dev)
    d.rounded_rectangle([0, 0, dev.width - 1, dev.height - 1], radius=58, fill=(18, 18, 20, 255))
    mask = Image.new("L", tela.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, tela.width - 1, tela.height - 1], radius=34, fill=255)
    dev.paste(tela, (pad, pad), mask)
    return dev.rotate(angulo, resample=Image.BICUBIC, expand=True)


def slide(s, i):
    im = abrir(s["base"])
    if s.get("fullbleed"):
        out = im.resize((W, H), Image.LANCZOS)
        legendas(out, s, 260)
        return out
    out = fundo(im)
    dev = aparelho(im, -4 if i % 2 else 4)
    sombra = Image.new("RGBA", dev.size, (0, 0, 0, 0))
    sombra.paste((0, 0, 0, 150), (0, 0), dev.split()[3])
    sombra = sombra.filter(ImageFilter.GaussianBlur(30))
    x, y = (W - dev.width) // 2, 560
    out.paste(sombra, (x + 20, y + 30), sombra)
    out.paste(dev, (x, y), dev)
    legendas(out, s, 150)
    return out


def render(spec_path, out_dir, prefixo):
    spec = json.load(open(spec_path))
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(spec["slides"], 1):
        slide(s, i).save(out / f"{prefixo}_{i:02d}.jpg", quality=92)
    (out / "legenda.txt").write_text(spec.get("legenda", ""), encoding="utf-8")
    print("ok", len(spec["slides"]), "slides ->", out)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], sys.argv[3])
