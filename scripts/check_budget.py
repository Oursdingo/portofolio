"""Verifie le budget de poids de la page (spec 9.3)."""
import os, sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUDGET_TOTAL_KB = 800
BUDGET_IMAGE_KB = 150
MAX_IMAGE_WIDTH = 1200

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

print("\n== Images referencees ==")
with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as fh:
    html = fh.read()
referenced = sorted(set(re.findall(r'(?:src|srcset)="\.?/?(images/[^"\s]+)"', html)))

try:
    from PIL import Image
    has_pillow = True
except ImportError:
    has_pillow = False

for rel in referenced:
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.exists(path):
        failed.append(f"image referencee introuvable : {rel}")
        continue
    size = kb(path)
    total += size
    note = ""
    if size > BUDGET_IMAGE_KB:
        failed.append(f"{rel} pese {size:.0f} Ko (max {BUDGET_IMAGE_KB} Ko)")
        note = "  <-- TROP LOURDE"
    if has_pillow:
        with Image.open(path) as im:
            if im.size[0] > MAX_IMAGE_WIDTH:
                failed.append(f"{rel} fait {im.size[0]} px de large (max {MAX_IMAGE_WIDTH})")
                note += "  <-- TROP LARGE"
    print(f"  {rel:<34} {size:7.1f} Ko{note}")

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
