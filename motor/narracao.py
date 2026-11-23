"""Narração grátis (Kokoro TTS, roda local, licença Apache-2.0) com a voz masculina brasileira `pm_alex`.
Escolhida pelo Lucas em 23/11 ("a do Alex foi a melhor"; Azure fica pra depois).

Instalar (uma vez por sessão; baixa ~330 MB do GitHub):
    pip install --break-system-packages kokoro-onnx soundfile
    python3 motor/narracao.py --instalar
Teste: python3 motor/narracao.py "Olha como eu faço vídeo pro TikTok Shop" /tmp/teste.wav
"""
import re, subprocess, sys, urllib.request
from pathlib import Path

PASTA = Path.home() / "kokoro"
REL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
ARQS = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]
VOZ, VEL = "pm_alex", 1.08
_k = None


def instalar():
    PASTA.mkdir(exist_ok=True)
    for a in ARQS:
        p = PASTA / a
        if not p.exists() or p.stat().st_size < 1_000_000:
            print("baixando", a, file=sys.stderr)
            urllib.request.urlretrieve(REL + a, p)
    return PASTA


def _modelo():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        instalar()
        _k = Kokoro(str(PASTA / ARQS[0]), str(PASTA / ARQS[1]))
    return _k


def limpar(t):
    """Texto de slide -> texto falado (pronúncia em pt-BR)."""
    t = re.sub(r"\[\[|\]\]", "", t)
    t = re.sub(r"R\$\s*([\d.,]+)\s*mil", r"\1 mil reais", t)
    t = re.sub(r"R\$\s*([\d.,]+)", r"\1 reais", t)
    t = re.sub(r"\(estimado\)", "", t)
    t = re.sub(r"\bTTS\b", "tê tê ésse", t)
    t = re.sub(r"\bIA\b", "i a", t)  # "í á" sai "i agudo a"
    t = t.replace(":", ",").replace(" ", " ")
    t = re.sub(r"\s+", " ", t)
    return re.sub(r" ([.,!?])", r"\1", t).strip()


def falar(texto, saida, voz=VOZ, vel=VEL):
    """Gera a fala em WAV 44,1 kHz mono, com tratamento leve (graves, compressão, volume -16 LUFS).
    Devolve a duração em segundos."""
    import soundfile as sf
    amostras, sr = _modelo().create(limpar(texto), voice=voz, speed=vel, lang="pt-br")
    bruto = Path(saida).with_suffix(".bruto.wav")
    sf.write(bruto, amostras, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(bruto), "-af",
                    "highpass=f=70,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3500:t=q:w=1.5:g=2,"
                    "acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5,"
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                    "-ar", "44100", "-ac", "1", str(saida)], check=True)
    bruto.unlink()
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(saida)], capture_output=True, text=True).stdout)


if __name__ == "__main__":
    if sys.argv[1:] == ["--instalar"]:
        print(instalar())
    else:
        print(f"{falar(sys.argv[1], sys.argv[2]):.2f}s")
