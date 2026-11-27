"""Carrossel "5 dicas" (desde 28/11, pedido do Lucas em 27/11; referência: carrossel "5 Hacks pra criar o hábito da
leitura" que ele mandou). Visual nativo do TikTok: foto/print em tela cheia (1080x1920) e o texto no meio, branco com
contorno preto, na fonte do próprio TikTok (TikTok Sans, OFL). Uma dica por slide, numerada "1)". A dica 3 é a
ferramenta, mostrada como PRINT REAL do app em tela cheia, SEM nome e sem vender (como o app de leitura da referência).
Sem CTA.

Não passa por seguro.enquadrar (a referência é tela cheia): o texto já fica no miolo (x 80..1000, y ~560..1300).

Uso: python3 motor/dicas.py <spec.json> <pasta_saida> <PREFIXO>
Spec: {"slides": [{"fundo": {...}, "titulo": "1) ...", "sub": "(...)", "y": 0.42}, ...], "legenda": "...", ...}
Fundos:
  {"tipo": "foto", "img": "caminho", "foco": [0.5, 0.5], "brilho": 0.9}   foto em tela cheia (corte central)
  {"tipo": "print", "img": "assets/prints/.../s4.jpg", "y": 0}             tela do app em tela cheia (860x1528)
  {"tipo": "produto", "img": "assets/produtos/x.jpg"}                       produto num card sobre o fundo desfocado dele
  {"tipo": "grade", "imgs": ["...", ...], "cor": "#f3e9e4"}                 prateleira de produtos (2 colunas)
  {"tipo": "cor", "cor": "#1c1b22"}                                         fundo liso
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont

W, H = 1080, 1920
RAIZ = Path(__file__).resolve().parent.parent
FONTE = {p: str(RAIZ / f"assets/fonts/TikTokSans-{p}.ttf") for p in (500, 600, 700)}


def cobrir(img, w=W, h=H, foco=(0.5, 0.5)):
    img = img.convert("RGB")
    e = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * e), round(img.height * e)), Image.LANCZOS)
    x = int((img.width - w) * foco[0]); y = int((img.height - h) * foco[1])
    return img.crop((x, y, x + w, y + h))


def cantos(img, r):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=r, fill=255)
    out = Image.new("RGBA", img.size); out.paste(img, (0, 0), m)
    return out


def com_sombra(fundo, peca, x, y, r=36, forca=150):
    s = Image.new("RGBA", fundo.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([x + 6, y + 18, x + peca.width + 6, y + peca.height + 18], radius=r, fill=(0, 0, 0, forca))
    s = s.filter(ImageFilter.GaussianBlur(26))
    fundo.paste(s, (0, 0), s)
    fundo.paste(peca, (x, y), peca)


def fundo(f):
    t = f.get("tipo", "cor")
    if t == "foto":
        im = cobrir(Image.open(RAIZ / f["img"]), foco=tuple(f.get("foco", (0.5, 0.5))))
        return ImageEnhance.Brightness(im).enhance(f.get("brilho", 0.92))
    if t == "print":
        im = Image.open(RAIZ / f["img"]).convert("RGB")
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
        y = min(int(f.get("y", 0)), max(0, im.height - H))
        tela = Image.new("RGB", (W, H), im.getpixel((5, im.height - 5)))
        tela.paste(im.crop((0, y, W, min(im.height, y + H))), (0, 0))
        return tela
    if t == "produto":
        p = Image.open(RAIZ / f["img"]).convert("RGB")
        base = ImageEnhance.Brightness(cobrir(p).filter(ImageFilter.GaussianBlur(40))).enhance(0.7)
        lado = 860; card = cantos(cobrir(p, lado, lado), 40)
        base = base.convert("RGBA"); com_sombra(base, card, (W - lado) // 2, 760)
        return base.convert("RGB")
    if t == "grade":
        cor = f.get("cor", "#f3e9e4"); base = Image.new("RGBA", (W, H), cor)
        imgs = f["imgs"]; lado = 440; gap = 40; x0 = (W - 2 * lado - gap) // 2
        linhas = (len(imgs) + 1) // 2; y0 = (H - (linhas * lado + (linhas - 1) * gap)) // 2
        for i, c in enumerate(imgs):
            card = cantos(cobrir(Image.open(RAIZ / c), lado, lado), 28)
            com_sombra(base, card, x0 + (i % 2) * (lado + gap), y0 + (i // 2) * (lado + gap), r=28, forca=90)
        return base.convert("RGB")
    return Image.new("RGB", (W, H), f.get("cor", "#1c1b22"))


def quebrar(d, texto, fonte, larg):
    linhas, atual = [], ""
    for p in texto.split():
        t = (atual + " " + p).strip()
        if d.textlength(t, font=fonte) <= larg or not atual:
            atual = t
        else:
            linhas.append(atual); atual = p
    if atual:
        linhas.append(atual)
    return linhas


def escrever(img, titulo, sub=None, y_rel=0.42, tam=64, tam_sub=46, escuro=0.0):
    """Texto nativo do TikTok: branco, contorno preto fino e sombra leve, centralizado."""
    d0 = ImageDraw.Draw(img)
    ft, fs = ImageFont.truetype(FONTE[600], tam), ImageFont.truetype(FONTE[500], tam_sub)
    blocos = [(l, ft, int(tam * 1.17)) for l in quebrar(d0, titulo, ft, 900)]
    if sub:
        blocos.append(("", fs, int(tam_sub * 0.7)))
        blocos += [(l, fs, int(tam_sub * 1.2)) for l in quebrar(d0, sub, fs, 900)]
    alt = sum(b[2] for b in blocos)
    y = int(H * y_rel - alt / 2)
    sombra = Image.new("RGBA", img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sombra)
    texto = Image.new("RGBA", img.size, (0, 0, 0, 0)); dt = ImageDraw.Draw(texto)
    for l, f, a in blocos:
        if l:
            x = (W - dt.textlength(l, font=f)) / 2
            ds.text((x + 2, y + 4), l, font=f, fill=(0, 0, 0, 150), stroke_width=6, stroke_fill=(0, 0, 0, 150))
            dt.text((x, y), l, font=f, fill="white", stroke_width=4 if f is ft else 3, stroke_fill="black")
        y += a
    img = img.convert("RGBA")
    if escuro:  # leve sombra atrás do bloco de texto (prints e fotos claras), sem cara de caixa
        y0 = int(H * y_rel - alt / 2)
        v = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(v).rounded_rectangle([40, y0 - 50, W - 40, y0 + alt + 40], radius=80, fill=(0, 0, 0, int(255 * escuro)))
        img.alpha_composite(v.filter(ImageFilter.GaussianBlur(45)))
    img.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(8)))
    img.alpha_composite(texto)
    return img.convert("RGB")


def main(spec_p, saida, prefixo):
    spec = json.load(open(spec_p)); saida = Path(saida); saida.mkdir(parents=True, exist_ok=True)
    assert len(spec["slides"]) <= 9, "máximo 9 slides"
    for i, s in enumerate(spec["slides"], 1):
        esc = s.get("escuro", {"print": 0.55, "foto": 0.25, "produto": 0.3, "grade": 0.45}.get(s["fundo"].get("tipo"), 0))
        img = escrever(fundo(s["fundo"]), s["titulo"], s.get("sub"), s.get("y", 0.42), s.get("tam", 64), s.get("tam_sub", 46), esc)
        img.save(saida / f"{prefixo}_{i:02d}.jpg", quality=92)
    print("ok", saida, len(spec["slides"]), "slides")


if __name__ == "__main__":
    main(*sys.argv[1:4])
