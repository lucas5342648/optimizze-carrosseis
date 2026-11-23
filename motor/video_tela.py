"""Formato `video_tela`: vídeo vertical (1080x1920, 30 qps) com a GRAVAÇÃO DA TELA do app fazendo o
passo a passo + legenda no estilo nativo do TikTok (caixa branca, texto preto) no topo de cada trecho.
Sem música: o Lucas escolhe a música viral na hora de postar (o vídeo leva uma faixa de áudio muda).

Uso: python3 motor/video_tela.py <spec.json> <pasta_gravacao> <saida.mp4>
  <pasta_gravacao> = saída do captura/gravar.js (pastas t1_lista ... com os quadros).
Spec: {"gancho": ["linha 1", "linha 2 com [[destaque]]"], "gancho_seg": 2.2,
       "trechos": [{"pasta": "t1_lista", "texto": "..."}, ...],
       "cta": ["COMENTA [[TTS]]", "e receba o acesso à ferramenta"], "cta_seg": 2.8,
       "titulo_post": "...", "legenda": "..."}
Também salva capa.jpg na pasta da saída (o quadro do gancho), pra prévia e pra capa.
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
APP_W = 820; APP_H = int(APP_W * 1528 / 860); APP_X = (W - APP_W) // 2; APP_Y = 360
ROXO = (162, 123, 255)


def fonte(tam, peso="Bold"):
    """Inter do sistema (fc-match), no peso pedido (Bold, ExtraBold, Black...)."""
    arq = subprocess.run(["fc-match", f"Inter:style={peso}", "file"], capture_output=True, text=True).stdout.split("=", 1)[-1].strip()
    return ImageFont.truetype(arq, tam)


def fundo():
    img = Image.new("RGB", (W, H), (7, 6, 12))
    g = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(g)
    d.ellipse([-300, -200, 700, 700], fill=(70, 30, 150)); d.ellipse([500, 1300, 1400, 2200], fill=(55, 20, 120))
    return Image.blend(img, g.filter(ImageFilter.GaussianBlur(220)), 0.55)


def pedacos(linha):
    """'texto [[roxo]] texto' -> [(texto, cor), ...]"""
    out = []
    for i, p in enumerate(re.split(r"\[\[|\]\]", linha)):
        if p:
            out.append((p, ROXO if i % 2 else None))
    return out


def quebrar(d, texto, f, maxw):
    # o que está em [[...]] não quebra no meio (ex.: "TikTok Shop")
    texto = re.sub(r"\[\[(.+?)\]\]", lambda m: "[[" + m.group(1).replace(" ", "\u00a0") + "]]", texto)
    linhas, atual = [], ""
    for w in texto.split(" "):
        t = (atual + " " + w).strip()
        if d.textlength(re.sub(r"\[\[|\]\]", "", t), font=f) <= maxw:
            atual = t
        else:
            linhas.append(atual); atual = w
    if atual:
        linhas.append(atual)
    return linhas


def caixa_nativa(texto, tam=50, maxw=880):
    """Legenda no estilo nativo do TikTok: caixa branca arredondada, texto preto, por linha."""
    f = fonte(tam)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    linhas = quebrar(tmp, texto, f, maxw)
    alt_l = int(tam * 1.32); pad = 18
    larg = max(tmp.textlength(re.sub(r"\[\[|\]\]", "", l), font=f) for l in linhas) + 2 * pad + 8
    img = Image.new("RGBA", (int(larg), alt_l * len(linhas) + 2 * pad // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(linhas):
        lw = tmp.textlength(re.sub(r"\[\[|\]\]", "", l), font=f)
        x0 = (img.width - lw) / 2 - pad; y0 = i * alt_l
        d.rounded_rectangle([x0, y0, x0 + lw + 2 * pad, y0 + alt_l + 2], radius=14, fill=(255, 255, 255, 255))
        x = x0 + pad
        for p, cor in pedacos(l):
            d.text((x, y0 + (alt_l - tam) / 2 - 4), p, font=f, fill=(124, 58, 237) if cor else (0, 0, 0))
            x += tmp.textlength(p, font=f)
    return img


def texto_grande(linhas, tam=92):
    f = fonte(tam, "ExtraBold")
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    todas = [l2 for l in linhas for l2 in quebrar(tmp, l, f, 940)]
    alt = int(tam * 1.18)
    img = Image.new("RGBA", (W, alt * len(todas) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for i, l in enumerate(todas):
        lw = tmp.textlength(re.sub(r"\[\[|\]\]", "", l), font=f); x = (W - lw) / 2; y = i * alt + 10
        for p, cor in pedacos(l):
            d.text((x, y), p, font=f, fill=cor or (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
            x += tmp.textlength(p, font=f)
    return img


def moldura(app):
    """Tela do app com cantos arredondados e borda sutil, como um celular."""
    app = app.resize((APP_W, APP_H), Image.LANCZOS)
    m = Image.new("L", app.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, APP_W - 1, APP_H - 1], radius=42, fill=255)
    return app, m


def main(spec_p, grav, saida):
    spec = json.load(open(spec_p)); grav = Path(grav); saida = Path(saida); saida.parent.mkdir(parents=True, exist_ok=True)
    base = fundo()
    tmpd = Path(tempfile.mkdtemp()); n = 0

    def escreve(img):
        nonlocal n
        img.save(tmpd / f"{n:05d}.jpg", quality=90); n += 1

    def compor(app_img, legenda_img=None, escurecer=0.0, extra=None):
        fr = base.copy()
        a, m = moldura(app_img)
        sombra = Image.new("RGBA", (APP_W + 80, APP_H + 80), (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle([40, 40, APP_W + 40, APP_H + 40], radius=46, fill=(124, 58, 237, 120))
        fr.paste(sombra.filter(ImageFilter.GaussianBlur(30)), (APP_X - 40, APP_Y - 40), sombra.filter(ImageFilter.GaussianBlur(30)))
        fr.paste(a, (APP_X, APP_Y), m)
        if escurecer:
            fr = Image.blend(fr, Image.new("RGB", (W, H), (0, 0, 0)), escurecer)
        if legenda_img is not None:
            fr.paste(legenda_img, ((W - legenda_img.width) // 2, max(90, APP_Y - legenda_img.height - 40)), legenda_img)
        if extra is not None:
            fr.paste(extra, ((W - extra.width) // 2, (H - extra.height) // 2 - 80), extra)
        return fr

    trechos = spec["trechos"]
    primeiro = sorted((grav / trechos[0]["pasta"]).glob("*.jpg"))[0]
    # 1. Gancho: primeiro quadro escurecido + texto grande
    g = texto_grande(spec["gancho"])
    capa = compor(Image.open(primeiro).convert("RGB").filter(ImageFilter.GaussianBlur(6)), escurecer=0.62, extra=g)
    for _ in range(int(spec.get("gancho_seg", 2.2) * FPS)):
        escreve(capa)
    capa.save(saida.parent / "capa.jpg", quality=92)
    # 2. Trechos gravados, cada um com a sua legenda nativa
    ultimo = None
    for t in trechos:
        leg = caixa_nativa(t["texto"])
        for q in sorted((grav / t["pasta"]).glob("*.jpg")):
            ultimo = Image.open(q).convert("RGB")
            escreve(compor(ultimo, leg))
    # 3. CTA: último quadro escurecido + "Comenta TTS"
    cta = compor(ultimo, escurecer=0.6, extra=texto_grande(spec["cta"], tam=96))
    for _ in range(int(spec.get("cta_seg", 2.8) * FPS)):
        escreve(cta)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(tmpd / "%05d.jpg"),
                    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", "-movflags", "+faststart",
                    "-c:a", "aac", "-b:a", "96k", str(saida)], check=True)
    print(f"ok {saida} ({n / FPS:.1f}s, {n} quadros)")


if __name__ == "__main__":
    main(*sys.argv[1:4])
