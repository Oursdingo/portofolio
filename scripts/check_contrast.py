"""Verifie les ratios de contraste WCAG AA des jetons de couleur de la spec."""
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def luminance(hex_color):
    hex_color = hex_color.lstrip("#")
    channels = []
    for i in (0, 2, 4):
        c = int(hex_color[i:i + 2], 16) / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    l1, l2 = luminance(fg), luminance(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


# (nom, premier plan, arriere-plan, ratio minimum)
#
# L'accent et le logo partagent desormais le meme rouge. Le rouge sur blanc
# a moins de marge que l'indigo precedent (4.83 contre 7.90) : chaque paire
# qui l'implique est donc testee, y compris le texte des boutons.
PAIRS = [
    ("clair  texte / fond",          "#0D1117", "#FFFFFF", 4.5),
    ("clair  texte attenue / fond",  "#5B6472", "#FFFFFF", 4.5),
    ("clair  accent / fond",         "#DC2626", "#FFFFFF", 4.5),
    ("clair  accent / surface",      "#DC2626", "#F7F8FA", 4.5),
    ("clair  blanc sur accent",      "#FFFFFF", "#DC2626", 4.5),
    ("clair  blanc sur accent survol", "#FFFFFF", "#B91C1C", 4.5),
    ("clair  texte / surface",       "#0D1117", "#F7F8FA", 4.5),
    ("sombre texte / fond",          "#E8EAF0", "#0B0D12", 4.5),
    ("sombre texte attenue / fond",  "#9AA3B2", "#0B0D12", 4.5),
    ("sombre accent / fond",         "#F05252", "#0B0D12", 4.5),
    ("sombre accent / surface",      "#F05252", "#12151C", 4.5),
    ("sombre fond sur accent",       "#0B0D12", "#F05252", 4.5),
    ("sombre texte / surface",       "#E8EAF0", "#12151C", 4.5),
]

failed = 0
for name, fg, bg, minimum in PAIRS:
    r = ratio(fg, bg)
    ok = r >= minimum
    if not ok:
        failed += 1
    print(f"{'OK   ' if ok else 'ECHEC'} {name:<30} {r:5.2f}:1  (min {minimum})")

print()
if failed:
    print(f"{failed} paire(s) sous le seuil WCAG AA.")
    sys.exit(1)
print("Tous les contrastes respectent WCAG AA.")
