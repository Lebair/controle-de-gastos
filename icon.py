"""
Gera icon.ico e icon.png para o launcher do Controle de Gastos.
Execute: python icon.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

SIZES = [16, 32, 48, 64, 128, 256]
OUT_ICO = os.path.join(os.path.dirname(__file__), "icon.ico")
OUT_PNG = os.path.join(os.path.dirname(__file__), "icon.png")

BG_COLOR     = (13, 27, 42)      # #0D1B2A
ACCENT_COLOR = (30, 77, 140)     # #1E4D8C
COIN_COLOR   = (230, 126, 34)    # #E67E22


def make_frame(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo arredondado
    radius = size // 6
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=BG_COLOR)

    # Gradiente lateral (faixa accent)
    for x in range(size // 3):
        alpha = int(180 * (1 - x / (size // 3)))
        draw.line([(size - size // 3 + x, 0), (size - size // 3 + x, size - 1)],
                  fill=(*ACCENT_COLOR, alpha))

    # Círculo moeda
    margin = int(size * 0.18)
    coin_r = size // 2 - margin
    cx, cy = size // 2, size // 2
    draw.ellipse(
        [cx - coin_r, cy - coin_r, cx + coin_r, cy + coin_r],
        fill=COIN_COLOR,
        outline=(255, 200, 100),
        width=max(1, size // 32),
    )

    # Símbolo R$ no centro
    symbol = "R$"
    font_size = max(8, int(size * 0.32))
    font = None
    for font_path in [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
    ]:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), symbol, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = cx - tw // 2
    ty = cy - th // 2 - bbox[1]
    draw.text((tx, ty), symbol, fill=(255, 255, 255), font=font)

    return img


def build():
    frames = [make_frame(s) for s in SIZES]
    # Salvar como .ico (multi-resolução)
    frames[-1].save(
        OUT_ICO,
        format="ICO",
        sizes=[(s, s) for s in SIZES],
        append_images=frames[:-1],
    )
    # Salvar PNG 256 para usar no tray
    frames[-1].save(OUT_PNG, format="PNG")
    print(f"Ícone gerado: {OUT_ICO}")
    print(f"PNG gerado:   {OUT_PNG}")


if __name__ == "__main__":
    build()
