"""GitHub social preview banner (1200x630) - dashboard gorunumu taklidi."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG, PANEL, BORDER = "#0e1117", "#161b22", "#21262d"
BLUE, GREEN, YELLOW, RED = "#58a6ff", "#3fb950", "#d29922", "#f85149"
TXT, MUTED = "#e6e6e6", "#8b949e"

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

def font(size, bold=True):
    p = f"segoeuib.ttf" if bold else "segoeui.ttf"
    try:
        return ImageFont.truetype(f"C:/Windows/Fonts/{p}", size)
    except OSError:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size)

f_big = font(64); f_sub = font(26, False); f_h = font(22)
f_cell = font(18, False); f_small = font(15, False)

# Baslik bloklari (sol taraf) - emoji font yok, para/parasut manuel cizilir
d.ellipse((70, 96, 130, 156), fill=GREEN)
d.ellipse((84, 110, 116, 142), fill="#1f3a26")
d.text((70, 170), "CoinBot", font=f_big, fill=TXT)
d.text((74, 250), "Crypto Airdrop Tracker", font=font(34), fill=BLUE)
d.text((74, 300), "& Trust Score Dashboard", font=font(34), fill=BLUE)
d.text((74, 375), "airdrops.io · gemdrops.io · alphadrops.net", font=f_sub, fill=MUTED)
d.text((74, 410), "defillama.com · coingabbar.com", font=f_sub, fill=MUTED)

# Ozet + durum rozetleri (banner alt sol, mockup disinda)
badges = [("0-100 Trust Score", GREEN), ("5 Sources", BLUE), ("Free & Open Source", YELLOW)]
x = 74
for label, col in badges:
    w = d.textlength(label, font=f_small) + 36
    d.rounded_rectangle((x, 475, x + w, 517), radius=21, fill=PANEL, outline=col, width=2)
    d.text((x + 18, 483), label, font=f_small, fill=col)
    x += w + 14

# Sag taraf: dashboard mockup
PX, PY, PW, PH = 620, 70, 510, 490
d.rounded_rectangle((PX, PY, PX + PW, PY + PH), radius=16, fill=PANEL, outline=BORDER, width=2)
d.ellipse((PX + 24, PY + 20, PX + 46, PY + 42), fill=GREEN)
d.text((PX + 56, PY + 18), "Airdrop Listesi", font=f_h, fill=TXT)

rows = [
    ("Sectora",     "100%", GREEN,  1.00),
    ("Miaoushi",    "100%", GREEN,  1.00),
    ("Pheasant",    "97%",  GREEN,  0.97),
    ("Servo",       "97%",  GREEN,  0.97),
    ("Calendar",    "81%",  GREEN,  0.81),
    ("Nullmask",    "76%",  YELLOW, 0.76),
    ("ZetaChain",   "76%",  YELLOW, 0.76),
    ("0xAstra",     "34%",  RED,    0.34),
]
TY = PY + 64
for name, pct, col, ratio in rows:
    d.text((PX + 24, TY), name[:14], font=f_cell, fill=TXT)
    d.text((PX + 200, TY), pct, font=f_cell, fill=col)
    bw = 220
    d.rounded_rectangle((PX + 258, TY + 6, PX + 258 + bw, TY + 22), radius=8, fill="#30363d")
    d.rounded_rectangle((PX + 258, TY + 6, PX + 258 + int(bw * ratio), TY + 22),
                        radius=8, fill=col)
    TY += 48

# Aktif/Bitti rozetleri (mockup altina)
d.rounded_rectangle((PX + 24, PY + PH - 52, PX + 130, PY + PH - 16), radius=8,
                    fill="#1f3a26", outline=GREEN, width=1)
d.text((PX + 44, PY + PH - 43), "68 Aktif", font=f_cell, fill=GREEN)
d.rounded_rectangle((PX + 140, PY + PH - 52, PX + 246, PY + PH - 16), radius=8,
                    fill="#21262d", outline=MUTED, width=1)
d.text((PX + 166, PY + PH - 43), "8 Bitti", font=f_cell, fill=MUTED)

img.save("docs/assets/banner.png")
print("OK -> docs/assets/banner.png")
