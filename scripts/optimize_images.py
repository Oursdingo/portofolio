"""Redimensionne et convertit les images conservees (spec 9.2).

Les originaux dans images/ ne sont JAMAIS modifies.
La sortie va dans images/optimized/.

Chaque image produit deux fichiers :
  - un WebP, servi a la quasi-totalite des visiteurs ;
  - un repli, servi aux navigateurs sans WebP.

Le format du repli depend du contenu, mesure sur les sources :
  - les deux portraits sont detoures (73 % et 82 % de pixels non opaques),
    la transparence est indispensable -> PNG ;
  - les trois captures sont integralement opaques (alpha = 255 partout),
    un PNG y coute 3 a 7 fois le poids d'un JPEG pour un rendu identique
    -> JPEG.
"""
import os, sys, io, glob
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "images")
OUT = os.path.join(SRC, "optimized")

# (fichier source, nom de sortie, largeur max, format de repli)
TARGETS = [
    ("profile_1.png", "profil-hero",   800, "png"),
    ("profil2.png",   "profil-about",  800, "png"),
    ("projet7.png",   "luxonera",     1200, "jpg"),
    ("projet-2.png",  "etrack",       1200, "jpg"),
    ("projet_6.png",  "hotellerie",   1200, "jpg"),
]

WEBP_QUALITY = 82
JPEG_QUALITY = 82

os.makedirs(OUT, exist_ok=True)
# Repart d'un repertoire propre : un changement de format de repli
# laisserait sinon des fichiers orphelins derriere lui.
for stale in glob.glob(os.path.join(OUT, "*")):
    os.remove(stale)

before_total = 0
webp_total = 0
fallback_total = 0

for src_name, out_name, max_w, fallback in TARGETS:
    src_path = os.path.join(SRC, src_name)
    if not os.path.exists(src_path):
        print(f"ECHEC source introuvable : {src_name}")
        sys.exit(1)

    before = os.path.getsize(src_path) / 1024
    before_total += before

    with Image.open(src_path) as im:
        im = im.convert("RGBA")
        if im.width > max_w:
            ratio = max_w / im.width
            im = im.resize((max_w, round(im.height * ratio)), Image.LANCZOS)

        webp_path = os.path.join(OUT, out_name + ".webp")
        im.save(webp_path, "WEBP", quality=WEBP_QUALITY, method=6)

        if fallback == "jpg":
            # Aplatit sur blanc : le JPEG ne porte pas de canal alpha.
            flat = Image.new("RGB", im.size, (255, 255, 255))
            flat.paste(im, mask=im.getchannel("A"))
            fb_path = os.path.join(OUT, out_name + ".jpg")
            flat.save(fb_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        else:
            fb_path = os.path.join(OUT, out_name + ".png")
            im.save(fb_path, "PNG", optimize=True)

        w_kb = os.path.getsize(webp_path) / 1024
        f_kb = os.path.getsize(fb_path) / 1024
        webp_total += w_kb
        fallback_total += f_kb
        print(
            f"{src_name:<16} {before:7.1f} Ko -> "
            f"{out_name}.webp {w_kb:6.1f} Ko / .{fallback} {f_kb:6.1f} Ko  "
            f"({im.width}x{im.height})"
        )

print(f"\nSources        : {before_total:7.1f} Ko")
print(f"WebP (servi)   : {webp_total:7.1f} Ko  "
      f"({100 - webp_total / before_total * 100:.0f} % economises)")
print(f"Replis         : {fallback_total:7.1f} Ko  (non servis aux navigateurs modernes)")
