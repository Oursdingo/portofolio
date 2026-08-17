"""Redimensionne et convertit les images du portfolio (spec 9.2).

Les originaux dans images/ ne sont JAMAIS modifies.
La sortie va dans images/optimized/, qui est ENTIEREMENT REGENERE a chaque
lancement : ne jamais y deposer de fichier source, il serait detruit.

Chaque image produit deux fichiers :
  - un WebP, servi a la quasi-totalite des visiteurs ;
  - un repli, servi aux navigateurs sans WebP.

Le format du repli est DEDUIT de l'image : transparence reelle detectee ->
PNG, sinon JPEG, trois a sept fois plus leger pour un rendu identique sur
une capture opaque.

Les bornes et le cadrage sont en revanche DECLARES par image. Les deduire
du rapport largeur/hauteur revenait a confondre deux usages : un portrait
detoure du hero et une capture de projet dans un cadre paysage n'obeissent
pas aux memes regles.

  cover   : la capture remplit le cadre, les bords deborde sont rognes.
  contain : la capture tient entiere dans le cadre. Reserve aux visuels
            mobiles, qu'un rognage paysage reduirait a une bande.
"""
import os, sys, io, glob
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "images")
OUT = os.path.join(SRC, "optimized")

# (source, nom de sortie, largeur max, hauteur max, cadrage)
# Les bornes valent deux fois la taille d'affichage, pour les ecrans denses.
TARGETS = [
    # Portraits du hero et de la section A propos : affiches a 560 px au plus.
    ("profile_1.png", "profil-hero",  800, None, "cover"),
    ("profil2.png",   "profil-about", 800, None, "cover"),

    # Captures web : le cadre paysage leur va, on remplit.
    ("sig.png",       "sig",       1200, None, "cover"),
    ("daice.png",     "daice",     1200, None, "cover"),
    ("blendbloc.png", "blendbloc", 1200, None, "cover"),
    ("projet7.png",   "luxonera",  1200, None, "cover"),
    ("kel.png",       "kel",       1200, None, "cover"),
    ("dao.png",       "dao",       1200, None, "cover"),
    ("projet-2.png",  "etrack",    1200, None, "cover"),
    ("projet_6.png",  "hotellerie",1200, None, "cover"),

    # Visuels mobiles : deux telephones cote a cote pour e-Wari, un mockup
    # incline pour LONIA. Un rognage paysage couperait les ecrans.
    ("e-wari.png",    "e-wari",     900, None, "contain"),
    ("lonia.png",     "lonia",     None,  900, "contain"),
]

WEBP_QUALITY = 82
JPEG_QUALITY = 82
SEUIL_ALPHA = 0.01    # 1 % de pixels non opaques suffit a exiger le PNG


def alpha_significatif(im):
    """Vrai si l'image a une transparence reelle, pas un simple canal vide."""
    if "A" not in im.getbands():
        return False
    hist = im.getchannel("A").histogram()
    non_opaques = sum(hist[:255])
    return non_opaques / (im.width * im.height) > SEUIL_ALPHA


os.makedirs(OUT, exist_ok=True)
# Repart d'un repertoire propre : un changement de format de repli
# laisserait sinon des fichiers orphelins derriere lui.
for stale in glob.glob(os.path.join(OUT, "*")):
    os.remove(stale)

before_total = webp_total = fallback_total = 0
rapport = []

for src_name, out_name, max_w, max_h, cadrage in TARGETS:
    src_path = os.path.join(SRC, src_name)
    if not os.path.exists(src_path):
        print(f"ECHEC source introuvable : {src_name}")
        sys.exit(1)

    before = os.path.getsize(src_path) / 1024
    before_total += before

    with Image.open(src_path) as im:
        im = im.convert("RGBA")
        transparent = alpha_significatif(im)

        if max_w and im.width > max_w:
            r = max_w / im.width
            im = im.resize((max_w, round(im.height * r)), Image.LANCZOS)
        if max_h and im.height > max_h:
            r = max_h / im.height
            im = im.resize((round(im.width * r), max_h), Image.LANCZOS)

        webp_path = os.path.join(OUT, out_name + ".webp")
        im.save(webp_path, "WEBP", quality=WEBP_QUALITY, method=6)

        if transparent:
            ext = "png"
            fb_path = os.path.join(OUT, out_name + ".png")
            im.save(fb_path, "PNG", optimize=True)
        else:
            ext = "jpg"
            # Aplatit sur blanc : le JPEG ne porte pas de canal alpha.
            plat = Image.new("RGB", im.size, (255, 255, 255))
            plat.paste(im, mask=im.getchannel("A"))
            fb_path = os.path.join(OUT, out_name + ".jpg")
            plat.save(fb_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)

        w_kb = os.path.getsize(webp_path) / 1024
        f_kb = os.path.getsize(fb_path) / 1024
        webp_total += w_kb
        fallback_total += f_kb

        rapport.append((out_name, im.width, im.height, ext, cadrage))
        print(f"{src_name:<16} {before:7.1f} Ko -> {out_name}.webp {w_kb:6.1f} Ko"
              f" / .{ext} {f_kb:6.1f} Ko  {im.width}x{im.height}"
              f"  [{cadrage}]{'  alpha' if transparent else ''}")

print(f"\nSources        : {before_total:8.1f} Ko")
print(f"WebP (servi)   : {webp_total:8.1f} Ko  "
      f"({100 - webp_total / before_total * 100:.0f} % economises)")
print(f"Replis         : {fallback_total:8.1f} Ko  (non servis aux navigateurs modernes)")

print("\nA reporter dans index.html :")
for nom, w, h, ext, mode in rapport:
    print(f"  {nom:<14} {w:>4}x{h:<4} repli .{ext:<4} cadrage {mode}")
