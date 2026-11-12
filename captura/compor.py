"""Transforma os prints capturados nos 6 fundos 9:16 do motor prints.py.
Uso: python3 captura/compor.py <pasta_capturas> <assets/prints/AAAA-MM-DD_slug>
s1 = card do vídeo centralizado sobre o fundo do app; s2..s6 = telas inteiras."""
import sys, os
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
card = Image.open(f"{src}/s1_card.png").convert("RGB")
W, H = 860, 1528
bg = Image.new("RGB", (W, H), (14, 13, 20))
w = 560; h = int(card.height * w / card.width)
if h > 1150: h = 1150; w = int(card.width * h / card.height)
c = card.resize((w, h), Image.LANCZOS)
m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill=255)
bg.paste(c, ((W - w) // 2, 280), m); bg.save(f"{dst}/s1.jpg", quality=92)
for i in range(2, 7): Image.open(f"{src}/s{i}.png").convert("RGB").save(f"{dst}/s{i}.jpg", quality=92)
print("ok", dst)
