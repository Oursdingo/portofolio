"""Verifie le budget de poids de la page (spec 9.3).

Deux mesures distinctes, parce qu'elles ne repondent pas a la meme question :

  - CHARGEMENT INITIAL : ce qu'un visiteur telecharge pour voir la page
    s'afficher. Les images `loading="lazy"` en sont exclues : elles ne
    partent que s'il descend jusqu'a elles. C'est le chiffre qui compte
    pour un recruteur sur un reseau lent.
  - POIDS TOTAL : tout, s'il parcourt la page jusqu'en bas.

Dans un <picture>, un navigateur telecharge le WebP OU le repli, jamais
les deux. Seul le WebP entre donc dans les mesures. Le repli est quand
meme plafonne, plus largement, pour qu'il ne derive pas.
"""
import os, sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BUDGET_INITIAL_KB = 800
BUDGET_TOTAL_KB = 1600
BUDGET_IMAGE_KB = 150
BUDGET_FALLBACK_KB = 400
MAX_IMAGE_WIDTH = 1200

# Poids gzip approximatifs des librairies CDN (mesures de reference, spec 9.1)
CDN_KB = {"gsap + ScrollTrigger": 60, "lenis": 8}
FONTS_KB = 80

echecs = []
initial = 0.0
differe = 0.0


def kb(path):
    return os.path.getsize(path) / 1024


try:
    from PIL import Image
    PILLOW = True
except ImportError:
    PILLOW = False

with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as fh:
    html = fh.read()


def auditer(rel, budget, compte):
    """Controle une image. `compte` vaut 'initial', 'differe' ou None."""
    global initial, differe
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.exists(path):
        echecs.append("image referencee introuvable : " + rel)
        print("  {:<34} {:>7}     <-- INTROUVABLE".format(rel, "?"))
        return
    taille = kb(path)
    note = ""
    if taille > budget:
        echecs.append("{} pese {:.0f} Ko (max {} Ko)".format(rel, taille, budget))
        note = "  <-- TROP LOURDE"
    if PILLOW:
        with Image.open(path) as im:
            if im.size[0] > MAX_IMAGE_WIDTH:
                echecs.append("{} fait {} px de large (max {})".format(
                    rel, im.size[0], MAX_IMAGE_WIDTH))
                note += "  <-- TROP LARGE"
    if compte == "initial":
        initial += taille
    elif compte == "differe":
        differe += taille
    print("  {:<34} {:7.1f} Ko{}".format(rel, taille, note))


print("== Fichiers locaux ==")
for rel in ["index.html"]:
    t = kb(os.path.join(ROOT, rel))
    initial += t
    print("  {:<34} {:7.1f} Ko".format(rel, t))

for dossier, ext in (("css", ".css"), ("js", ".js")):
    d = os.path.join(ROOT, dossier)
    if not os.path.isdir(d) or not os.listdir(d):
        echecs.append("repertoire {}/ absent ou vide".format(dossier))
        continue
    for nom in sorted(os.listdir(d)):
        if nom.endswith(ext):
            t = kb(os.path.join(d, nom))
            initial += t
            print("  {:<34} {:7.1f} Ko".format(dossier + "/" + nom, t))

# --- Tri des images : immediates, differees, replis ---
immediates, differees, replis = [], [], []

for bloc in re.findall(r"<picture>.*?</picture>", html, re.S):
    webp = re.findall(r'srcset="\.?/?(images/[^"\s]+)"', bloc)
    replis += re.findall(r'src="\.?/?(images/[^"\s]+)"', bloc)
    (differees if 'loading="lazy"' in bloc else immediates).extend(webp)

hors_picture = re.sub(r"<picture>.*?</picture>", "", html, flags=re.S)
for balise in re.findall(r"<img[^>]*>", hors_picture, re.S):
    src = re.findall(r'src="\.?/?(images/[^"\s]+)"', balise)
    (differees if 'loading="lazy"' in balise else immediates).extend(src)

print("\n== Images du chargement initial ==")
if not immediates:
    print("  aucune")
for rel in sorted(set(immediates)):
    auditer(rel, BUDGET_IMAGE_KB, "initial")

print("\n== Images differees (au defilement) ==")
if not differees:
    print("  aucune")
for rel in sorted(set(differees)):
    auditer(rel, BUDGET_IMAGE_KB, "differe")

print("\n== Replis (servis uniquement sans support WebP) ==")
if not replis:
    print("  aucun")
for rel in sorted(set(replis)):
    auditer(rel, BUDGET_FALLBACK_KB, None)

print("\n== Ressources externes (estimation) ==")
for nom, t in CDN_KB.items():
    initial += t
    print("  {:<34} {:7.1f} Ko".format(nom, t))
initial += FONTS_KB
print("  {:<34} {:7.1f} Ko".format("polices (woff2)", FONTS_KB))

total = initial + differe
print("\nCHARGEMENT INITIAL {:8.1f} Ko  /  budget {} Ko".format(initial, BUDGET_INITIAL_KB))
print("POIDS TOTAL        {:8.1f} Ko  /  budget {} Ko".format(total, BUDGET_TOTAL_KB))

if initial > BUDGET_INITIAL_KB:
    echecs.append("chargement initial {:.0f} Ko depasse le budget de {} Ko".format(
        initial, BUDGET_INITIAL_KB))
if total > BUDGET_TOTAL_KB:
    echecs.append("poids total {:.0f} Ko depasse le budget de {} Ko".format(
        total, BUDGET_TOTAL_KB))

if echecs:
    print("\nECHECS :")
    for e in echecs:
        print("  - " + e)
    sys.exit(1)
print("\nBudget respecte.")
