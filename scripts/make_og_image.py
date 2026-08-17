"""Genere l'image de partage Open Graph (1200x630, spec 11)."""
import os, sys, io
from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
BG = (255, 255, 255)
RED = (220, 38, 38)
INK = (13, 17, 23)
MUTED = (91, 100, 114)
ACCENT = (67, 56, 202)

# Polices candidates, de la plus proche du site (grotesque geometrique) a la
# plus generique. La premiere qui se charge gagne. Aucune n'est garantie
# presente, d'ou la liste et le repli final.
FONTS_BOLD = [
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONTS_REGULAR = [
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    print("AVERTISSEMENT : aucune police systeme trouvee, rendu degrade.")
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# Barre d'accent superieure
d.rectangle([0, 0, W, 8], fill=ACCENT)

# ---------------------------------------------------------------------------
# Glyphe </> : exactement les traces du favicon, remis a l'echelle.
# L'epaisseur suit l'echelle (3 unites de viewBox) pour garder la meme
# silhouette qu'a 32 px ; une epaisseur fixe transformerait le glyphe en pate.
# ---------------------------------------------------------------------------
GLYPH = (
    [(11, 10), (6, 16), (11, 22)],
    [(19, 8.5), (13, 23.5)],
    [(21, 10), (26, 16), (21, 22)],
)
SCALE = 4.0
ORIGIN_X, ORIGIN_Y = 90, 96
MIN_X, MIN_Y = 6, 8.5

for path in GLYPH:
    points = [
        (ORIGIN_X + (x - MIN_X) * SCALE, ORIGIN_Y + (y - MIN_Y) * SCALE)
        for x, y in path
    ]
    d.line(points, fill=RED, width=round(3 * SCALE), joint="curve")
    # `joint="curve"` n'arrondit que les angles : on ferme les extremites
    # a la main pour reproduire le stroke-linecap="round" du SVG.
    r = 3 * SCALE / 2
    for px, py in (points[0], points[-1]):
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED)

# ---------------------------------------------------------------------------
# Texte
# ---------------------------------------------------------------------------
name_font = load_font(FONTS_BOLD, 66)
role_font = load_font(FONTS_BOLD, 38)
stack_font = load_font(FONTS_REGULAR, 28)

d.text((90, 268), "SAWADOGO ADAM SHARIF", font=name_font, fill=INK)
d.text((90, 366), "Développeur Full Stack, Web & Mobile", font=role_font, fill=ACCENT)
d.text((90, 440), "Angular · Spring Boot · Flutter · Next.js · FastAPI",
       font=stack_font, fill=MUTED)

out = os.path.join(ROOT, "images", "og-image.png")
img.save(out, "PNG", optimize=True)
print(f"Genere : images/og-image.png  {os.path.getsize(out) / 1024:.1f} Ko  {W}x{H}")
