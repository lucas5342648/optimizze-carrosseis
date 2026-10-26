"""Área segura para carrossel de fotos do TikTok.

O TikTok corta/cobre as bordas das fotos (topo, base com legenda/botões e laterais).
`enquadrar` reduz o slide pronto e o centraliza sobre um fundo desfocado dele mesmo,
para que textos e prints fiquem sempre no miolo da tela.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = 1080, 1920
ESCALA = 0.84          # conteúdo ocupa 84% da largura/altura
DESLOC_Y = -40         # sobe um pouco (a base do TikTok tem mais interface que o topo)


def enquadrar(img, escala=ESCALA, desloc_y=DESLOC_Y):
    img = img.convert("RGB").resize((W, H))
    fundo = ImageEnhance.Brightness(img.filter(ImageFilter.GaussianBlur(50))).enhance(0.55)
    w, h = int(W * escala), int(H * escala)
    fg = img.resize((w, h), Image.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=36, fill=255)
    x, y = (W - w) // 2, (H - h) // 2 + desloc_y
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle([x + 10, y + 20, x + w + 10, y + h + 20], radius=36, fill=(0, 0, 0, 140))
    fundo.paste(sombra.filter(ImageFilter.GaussianBlur(24)), (0, 0), sombra.filter(ImageFilter.GaussianBlur(24)))
    fundo.paste(fg, (x, y), mask)
    return fundo
