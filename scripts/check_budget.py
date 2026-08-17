"""Verifie le budget de poids de la page (spec 9.3)."""
import os, sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUDGET_TOTAL_KB = 800
BUDGET_IMAGE_KB = 150
MAX_IMAGE_WIDTH = 1200

# Dans un <picture>, un navigateur telecharge le WebP OU le repli, jamais
# les deux. Seul le WebP entre donc dans le budget transfere. Le repli est
# quand meme plafonne, plus largement, pour qu'il ne derive pas.
BUDGET_FALLBACK_KB = 400

# Poids gzip approximatifs des librairies CDN (mesures de reference, spec 9.1)
CDN_KB = {"gsap + ScrollTrigger": 60, "lenis": 8}
FONTS_KB = 80


def kb(path):
    return os.path.getsize(path) / 1024


def collect(rel_dir, extensions):
    d = os.path.join(ROOT, rel_dir)
    if not os.path.isdir(d):
        return []
    return [
        (rel_dir + "/" + f, kb(os.path.join(d, f)))
        for f in sorted(os.listdir(d))
        if f.lower().endswith(extensions)
    ]


failed = []
total = 0

print("== Fichiers locaux ==")
for name, size in [("index.html", kb(os.path.join(ROOT, "index.html")))]:
    total += size
    print(f"  {name:<34} {size:7.1f} Ko")

for rel, exts in (("css", (".css",)), ("js", (".js",))):
    found = collect(rel, exts)
    if not found:
        failed.append(f"repertoire {rel}/ absent ou vide")
    for name, size in found:
        total += size
        print(f"  {name:<34} {size:7.1f} Ko")

with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as fh:
    html = fh.read()

try:
    from PIL import Image
    has_pillow = True
except ImportError:
    has_pillow = False


def audit(rel, budget, counts_toward_total):
    """Controle une image et renvoie son poids si elle compte dans le total."""
    global total
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.exists(path):
        failed.append(f"image referencee introuvable : {rel}")
        print(f"  {rel:<34} {'?':>7}     <-- INTROUVABLE")
        return
    size = kb(path)
    note = ""
    if size > budget:
        failed.append(f"{rel} pese {size:.0f} Ko (max {budget} Ko)")
        note = "  <-- TROP LOURDE"
    if has_pillow:
        with Image.open(path) as im:
            if im.size[0] > MAX_IMAGE_WIDTH:
                failed.append(f"{rel} fait {im.size[0]} px de large (max {MAX_IMAGE_WIDTH})")
                note += "  <-- TROP LARGE"
    if counts_toward_total:
        total += size
    print(f"  {rel:<34} {size:7.1f} Ko{note}")


# Chaque <picture> sert son <source> WebP aux navigateurs modernes et son
# <img> uniquement aux autres : les deux ne sont jamais telecharges ensemble.
pictures = re.findall(r"<picture>(.*?)</picture>", html, re.S)
primaries, fallbacks = [], []
for block in pictures:
    primaries += re.findall(r'srcset="\.?/?(images/[^"\s]+)"', block)
    fallbacks += re.findall(r'src="\.?/?(images/[^"\s]+)"', block)

# Les <img> hors <picture> sont telecharges tels quels.
standalone = re.findall(
    r'<img[^>]+src="\.?/?(images/[^"\s]+)"', re.sub(r"<picture>.*?</picture>", "", html, flags=re.S)
)

print("\n== Images transferees (comptees dans le budget) ==")
for rel in sorted(set(primaries + standalone)):
    audit(rel, BUDGET_IMAGE_KB, counts_toward_total=True)

print("\n== Replis (servis uniquement sans support WebP) ==")
if not fallbacks:
    print("  aucun")
for rel in sorted(set(fallbacks)):
    audit(rel, BUDGET_FALLBACK_KB, counts_toward_total=False)

print("\n== Ressources externes (estimation) ==")
for name, size in CDN_KB.items():
    total += size
    print(f"  {name:<34} {size:7.1f} Ko")
total += FONTS_KB
print(f"  {'polices (woff2)':<34} {FONTS_KB:7.1f} Ko")

print(f"\nTOTAL {total:.1f} Ko  /  budget {BUDGET_TOTAL_KB} Ko")

if total > BUDGET_TOTAL_KB:
    failed.append(f"total {total:.0f} Ko depasse le budget de {BUDGET_TOTAL_KB} Ko")

if failed:
    print("\nECHECS :")
    for f in failed:
        print(f"  - {f}")
    sys.exit(1)
print("\nBudget respecte.")
