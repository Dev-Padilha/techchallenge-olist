"""
build_video.py — Monta o video executivo de ate 5 min a partir das figuras + narracao TTS.

Pipeline:
  1. renderiza um slide 1920x1080 (PNG) por bloco do roteiro;
  2. gera a narracao de cada bloco com o TTS nativo do macOS (`say`);
  3. junta tudo num .mp4 com ffmpeg, cada slide durando o tempo da sua narracao.

Uso:
    VOICE=Luciana python src/build_video.py
Pre-requisitos: macOS (`say`), ffmpeg e ffprobe no PATH ou em ~/bin, figures/ gerado.
Saida: presentation/video_olist.mp4
"""
import os
import json
import subprocess
import urllib.request
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import image as mpimg

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
BUILD = ROOT / "build_video"
OUT = ROOT / "presentation" / "video_olist.mp4"

HOME_BIN = Path.home() / "bin"
FFMPEG = str(HOME_BIN / "ffmpeg") if (HOME_BIN / "ffmpeg").exists() else "ffmpeg"
FFPROBE = str(HOME_BIN / "ffprobe") if (HOME_BIN / "ffprobe").exists() else "ffprobe"

VOICE = os.environ.get("VOICE", "Luciana")
RATE = os.environ.get("RATE", "")  # palavras/min; vazio = padrao da voz

# Backend de narracao: "say" (TTS nativo macOS) ou "elevenlabs" (voz neural).
TTS_BACKEND = os.environ.get("TTS_BACKEND", "say")
EL_VOICE_ID = os.environ.get("EL_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")  # George
EL_MODEL = os.environ.get("EL_MODEL", "eleven_multilingual_v2")
EL_KEY_FILE = Path.home() / ".elevenlabs_key"
AUDIO_EXT = "mp3" if TTS_BACKEND == "elevenlabs" else "aiff"

AZUL = "#1F4E79"
VERMELHO = "#C0392B"
CINZA = "#7F8C8D"

# (id, tipo, titulo, conteudo, figura, narracao)
SLIDES = [
    ("01", "capa",
     "O paradoxo do crescimento",
     "A Olist vende mais, mas a entrega ameaça o futuro",
     None,
     "Olá. Nos próximos cinco minutos, vou mostrar uma história que parece boa, e é, mas que "
     "esconde um risco que todo investidor da Olist precisa enxergar. O título resume tudo: a "
     "Olist vende cada vez mais, mas a forma como entrega pode ameaçar esse crescimento. Vamos aos fatos."),

    ("02", "figura", "O crescimento, a boa notícia", None, "01_crescimento_receita.png",
     "Primeiro, a boa notícia. Entre dois mil e dezessete e dois mil e dezoito, a Olist quase dobrou "
     "de tamanho: o volume de pedidos cresceu oitenta por cento, somando mais de treze milhões de "
     "reais em vendas, com pico na Black Friday. Mas reparem na curva: em dois mil e dezoito ela "
     "achata. A fase de crescimento explosivo está dando lugar à maturidade. E maturidade exige uma "
     "palavra: eficiência."),

    ("03", "figura", "A pergunta de investidor", None, "04_recompra_benchmark.png",
     "Aí vem a pergunta que todo investidor faz: esse crescimento se sustenta? Olhem este número. "
     "Apenas três por cento dos clientes da Olist compram uma segunda vez. No comércio eletrônico "
     "maduro, esse número fica perto de trinta por cento. Ou seja, quase todo cliente compra uma "
     "única vez e não volta. Isso significa que a Olist não vive de fidelizar, vive de conquistar "
     "clientes novos o tempo todo. E quem traz o próximo cliente? A reputação. As boas avaliações."),

    ("04", "figura", "Onde está o risco", None, "02_lead_time_decomposicao.png",
     "Agora, onde está o risco. O prazo médio de entrega é de cerca de doze dias, e oito por cento "
     "dos pedidos chegam atrasados. Mas o detalhe importa: o tempo não se perde no escritório, no "
     "processamento. Ele se perde na estrada, na entrega final, na porta do cliente. É a chamada "
     "última milha. É ali que mora o problema."),

    ("05", "figura", "O elo que conecta tudo", None, "03_atraso_x_nota.png",
     "E é aqui que tudo se conecta. Quando a Olist entrega no prazo, a nota média do cliente é "
     "quatro vírgula três, excelente. Quando entrega com atraso, a nota despenca para dois vírgula "
     "seis. E mais: entre os pedidos atrasados, mais da metade dos clientes vira crítico da marca, "
     "dando as piores notas. Lembram que a reputação é o que traz cliente novo? Pois é exatamente "
     "ela que o atraso está destruindo. O atraso não é só um problema de operação, é um vazamento "
     "no motor de crescimento."),

    ("06", "bignum", "Quanto isso custa", "R$ 1,2 milhão\nde receita exposta a má experiência (8,8%)", None,
     "E isso tem tamanho. No período analisado, mais de um milhão e duzentos mil reais em vendas "
     "passaram por uma experiência de entrega ruim. Isso representa quase nove por cento de toda a "
     "receita: receita exposta, vulnerável, ligada a um cliente que provavelmente saiu insatisfeito "
     "e falando mal da marca."),

    ("07", "figura", "O valor de agir", None, "05_simulacao_financeira.png",
     "A boa notícia é que dá para agir, e o retorno é claro. Se a Olist reduzir os atrasos pela "
     "metade, ela protege cerca de quinhentos e oitenta mil reais em receita e evita que quase mil "
     "e oitocentos clientes virem detratores da marca. Não é custo. É proteção do crescimento que "
     "já foi conquistado."),

    ("08", "figura", "Dá para prever quem vai reclamar", None, "08_modelo_fatores_risco.png",
     "Nós fomos além e construímos um modelo que antecipa quais pedidos têm risco de gerar uma "
     "avaliação ruim. E ele revelou algo importante: o maior sinal de alerta é o tempo total de "
     "entrega, mais até do que o atraso em si. Ou seja, entrega lenta irrita o cliente mesmo quando "
     "cumpre o prazo combinado. A alavanca é clara: entregar mais rápido."),

    ("09", "bullets", "Recomendações",
     "1. Atacar a última milha nas regiões mais críticas\n"
     "2. Prometer prazos realistas por região (custo quase zero)\n"
     "3. Criar um programa para o cliente voltar a comprar\n"
     "4. Priorizar os sellers com entrega rápida e boa nota", None,
     "Então o que fazer? Três frentes, da maior para a menor prioridade. Primeira: atacar a última "
     "milha nas regiões mais críticas. Segunda: prometer prazos realistas por região, não prometer "
     "o que não se cumpre, e isso custa quase nada. Terceira: criar um programa para fazer o cliente "
     "voltar a comprar. Baixo custo, baixo risco, alto retorno."),

    ("10", "capa", "Proteger a entrega é proteger o crescimento",
     "A Olist já provou que sabe crescer. O desafio agora é entregar melhor.", None,
     "Para fechar: a Olist já provou que sabe crescer. O desafio agora não é vender mais, é entregar "
     "melhor. Porque proteger a entrega é proteger a reputação, e proteger a reputação é proteger o "
     "futuro do negócio. Obrigado."),
]


def render_slide(slide, path):
    sid, tipo, titulo, conteudo, figura, _ = slide
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor("white")

    if tipo == "figura":
        # barra de titulo no topo
        fig.text(0.06, 0.92, titulo, fontsize=40, fontweight="bold", color=AZUL, va="center")
        fig.add_artist(plt.Line2D([0.06, 0.94], [0.875, 0.875], color=AZUL, lw=3))
        img = mpimg.imread(str(FIG / figura))
        ax = fig.add_axes([0.08, 0.06, 0.84, 0.76])
        ax.imshow(img)
        ax.axis("off")
    elif tipo == "capa":
        fig.add_artist(plt.Rectangle((0, 0), 1, 1, color=AZUL))
        fig.text(0.5, 0.58, titulo, fontsize=54, fontweight="bold", color="white",
                 ha="center", va="center", wrap=True)
        fig.text(0.5, 0.42, conteudo, fontsize=30, color="#D6E0EA", ha="center", va="center", wrap=True)
        fig.text(0.5, 0.1, "Tech Challenge  |  Data Analytics  |  Olist 2017-2018",
                 fontsize=20, color="#9BB2C9", ha="center")
    elif tipo == "bignum":
        fig.text(0.5, 0.82, titulo, fontsize=40, fontweight="bold", color=AZUL, ha="center")
        partes = conteudo.split("\n")
        fig.text(0.5, 0.52, partes[0], fontsize=110, fontweight="bold", color=VERMELHO, ha="center", va="center")
        if len(partes) > 1:
            fig.text(0.5, 0.3, partes[1], fontsize=30, color=CINZA, ha="center", va="center")
    elif tipo == "bullets":
        fig.text(0.08, 0.88, titulo, fontsize=42, fontweight="bold", color=AZUL, va="center")
        fig.add_artist(plt.Line2D([0.08, 0.92], [0.82, 0.82], color=AZUL, lw=3))
        y = 0.66
        for linha in conteudo.split("\n"):
            fig.text(0.12, y, linha, fontsize=34, color="#222222", va="center")
            y -= 0.15

    fig.savefig(path, facecolor="white")
    plt.close(fig)


def make_audio_say(text, path):
    cmd = ["say", "-v", VOICE]
    if RATE:
        cmd += ["-r", RATE]
    cmd += ["-o", str(path), text]
    subprocess.run(cmd, check=True)


def make_audio_elevenlabs(text, path):
    key = EL_KEY_FILE.read_text().strip()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{EL_VOICE_ID}"
    payload = json.dumps({
        "text": text,
        "model_id": EL_MODEL,
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.0,
                           "use_speaker_boost": True},
    }).encode()
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        path.write_bytes(resp.read())


def make_audio(text, path):
    if TTS_BACKEND == "elevenlabs":
        make_audio_elevenlabs(text, path)
    else:
        make_audio_say(text, path)


def duration(path):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def concat_segments(segments, out_path):
    """Junta os segmentos re-codificando num unico fluxo continuo.

    Usa o concat *filter* (e nao o demuxer com -c copy): isso evita o descasamento
    de timestamps do AAC entre trechos, que fazia o audio sumir depois de alguns slides.
    """
    inputs = []
    for s in segments:
        inputs += ["-i", str(s)]
    n = len(segments)
    streams = "".join(f"[{i}:v][{i}:a]" for i in range(n))
    filt = f"{streams}concat=n={n}:v=1:a=1[v][a]"
    subprocess.run([
        FFMPEG, "-y", *inputs, "-filter_complex", filt,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
        str(out_path)
    ], check=True, capture_output=True)


def make_segment(png, audio, out_path):
    subprocess.run([
        FFMPEG, "-y", "-loop", "1", "-i", str(png), "-i", str(audio),
        "-c:v", "libx264", "-tune", "stillimage", "-r", "25",
        "-vf", "scale=1920:1080,format=yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_path)
    ], check=True, capture_output=True)


def main():
    BUILD.mkdir(exist_ok=True)
    segments = []
    total = 0.0
    if TTS_BACKEND == "elevenlabs":
        print(f"Backend: elevenlabs (voz {EL_VOICE_ID}, modelo {EL_MODEL})")
    else:
        print(f"Backend: say (voz {VOICE}{(' rate ' + RATE) if RATE else ''})")
    for slide in SLIDES:
        sid = slide[0]
        narr = slide[5]
        png = BUILD / f"slide_{sid}.png"
        audio = BUILD / f"audio_{sid}.{AUDIO_EXT}"
        seg = BUILD / f"seg_{sid}.mp4"
        render_slide(slide, png)
        make_audio(narr, audio)
        d = duration(audio)
        total += d
        make_segment(png, audio, seg)
        segments.append(seg)
        print(f"  slide {sid}: {d:5.1f}s")

    concat_segments(segments, OUT)

    mm, ss = divmod(round(total), 60)
    print(f"\nDuracao total: {mm}:{ss:02d}  ({total:.1f}s)")
    print(f"Video: {OUT.relative_to(ROOT)}")
    if total > 300:
        print("AVISO: passou de 5:00. Rode de novo com RATE maior, ex.: RATE=200")


if __name__ == "__main__":
    main()
