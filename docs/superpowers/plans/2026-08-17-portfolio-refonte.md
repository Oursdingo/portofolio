# Refonte du portfolio — Plan d'implémentation

> **Pour les agents :** SOUS-COMPÉTENCE REQUISE — utiliser `superpowers:subagent-driven-development` (recommandé) ou `superpowers:executing-plans` pour dérouler ce plan tâche par tâche. Les étapes utilisent la syntaxe case à cocher (`- [ ]`).

**Objectif :** transformer un portfolio étudiant de 8,8 Mo en une vitrine professionnelle de moins de 800 Ko, alignée sur le CV actuel, avec des animations fluides et un thème clair par défaut.

**Architecture :** site statique sans build. Le HTML porte tout le contenu (indexable, résistant à une panne de CDN). Le CSS est découpé en quatre fichiers thématiques, le JS en quatre modules ES à responsabilité unique. GSAP + ScrollTrigger + Lenis remplacent ScrollReveal, Typed.js et la police d'icônes Boxicons — l'ensemble est plus léger que ce qu'il remplace.

**Stack :** HTML5, CSS3 (custom properties), JavaScript modules ES, GSAP 3 + ScrollTrigger, Lenis, Pillow 10.4 pour le traitement d'images.

**Spec :** [`docs/superpowers/specs/2026-08-17-portfolio-refonte-design.md`](../specs/2026-08-17-portfolio-refonte-design.md)

## Note sur la vérification

Le dépôt ne contient aucun framework de test et n'en justifie pas un : c'est une page vitrine statique, sans logique métier. Le cycle « test rouge → vert » est donc remplacé par :

- **trois scripts Python** vérifiant ce qui se mesure objectivement — dimensions et poids des images, budget total de la page, ratios de contraste WCAG. Ceux-là suivent bien un cycle rouge → vert.
- **des vérifications navigateur** à critère unique et non ambigu pour le rendu, avec l'outil navigateur intégré (`preview_start`, `read_console_messages`, `read_page`).

Toute étape « vérifier » indique le résultat attendu exact. Une étape sans critère observable est un défaut de plan.

## Contraintes globales

Valeurs reprises telles quelles de la spec. Elles s'appliquent à **toutes** les tâches.

- **Thème par défaut :** le choix mémorisé prime ; à défaut la **préférence système** (`prefers-color-scheme`) ; clair si le système n'en exprime aucune (spec §12).
- **Palette claire :** `--bg #FFFFFF` · `--surface #F7F8FA` · `--text #0D1117` · `--text-muted #5B6472` · `--accent #4338CA` · `--border rgba(13,17,23,.08)` · `--logo-red #DC2626`
- **Palette sombre :** `--bg #0B0D12` · `--surface #12151C` · `--text #E8EAF0` · `--text-muted #9AA3B2` · `--accent #818CF8` · `--border rgba(255,255,255,.09)` · `--logo-red #F05252`
- **Polices :** Sora (titres, 600–700) · Inter (corps, 400–600) · JetBrains Mono (labels, 500)
- **Budget :** premier chargement < 800 Ko · LCP < 1,5 s · Lighthouse Performance ≥ 95 · Accessibilité ≥ 95
- **Images :** 1200 px de large maximum, WebP qualité 82, repli PNG. **Les originaux ne sont jamais écrasés.**
- **Contraste :** WCAG AA sur les deux thèmes (4.5:1 texte courant, 3:1 texte large)
- **`prefers-reduced-motion` :** Lenis non instancié, GSAP réduit aux changements d'opacité, marquees figés
- **Contenu :** aucune donnée absente du CV. Ordre des projets imposé (spec §4.4), non négociable.
- **Langue :** français. `lang="fr"`.
- **Zéro erreur en console** à la fin de chaque tâche.

---

## Structure des fichiers

| Fichier | Responsabilité |
|---|---|
| `index.html` | contenu statique intégral |
| `merci.html` | confirmation d'envoi du formulaire |
| `favicon.svg` | icône d'onglet `</>` |
| `css/base.css` | reset, jetons, typographie, utilitaires |
| `css/layout.css` | en-tête, sections, grilles, pied de page |
| `css/components.css` | boutons, cartes, timeline, badges, formulaire |
| `css/responsive.css` | points de rupture |
| `js/theme.js` | bascule et persistance du thème |
| `js/nav.js` | burger, section active, en-tête au scroll |
| `js/animations.js` | Lenis + GSAP + ScrollTrigger + effet machine à écrire |
| `js/main.js` | orchestration |
| `scripts/optimize_images.py` | génération de `images/optimized/` |
| `scripts/check_budget.py` | vérification du budget de poids |
| `scripts/check_contrast.py` | vérification des contrastes WCAG |

Les anciens `style.css` et `app.js` sont supprimés en toute fin de plan (Tâche 14), une fois leur contenu entièrement repris.

---

## Tâche 1 : Scripts de vérification

Ils viennent en premier : ils définissent objectivement ce que « réussi » veut dire pour les tâches suivantes.

**Fichiers :**
- Créer : `scripts/check_contrast.py`
- Créer : `scripts/check_budget.py`

**Interfaces :**
- Consomme : rien
- Produit : `python scripts/check_contrast.py` et `python scripts/check_budget.py`, code de sortie 0 si conforme, 1 sinon. Les tâches suivantes les invoquent.

- [ ] **Étape 1 : écrire le vérificateur de contraste**

Créer `scripts/check_contrast.py` :

```python
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
PAIRS = [
    ("clair  texte / fond",        "#0D1117", "#FFFFFF", 4.5),
    ("clair  texte attenue / fond", "#5B6472", "#FFFFFF", 4.5),
    ("clair  accent / fond",       "#4338CA", "#FFFFFF", 4.5),
    ("clair  logo rouge / fond",   "#DC2626", "#FFFFFF", 3.0),
    ("clair  texte / surface",     "#0D1117", "#F7F8FA", 4.5),
    ("sombre texte / fond",        "#E8EAF0", "#0B0D12", 4.5),
    ("sombre texte attenue / fond", "#9AA3B2", "#0B0D12", 4.5),
    ("sombre accent / fond",       "#818CF8", "#0B0D12", 4.5),
    ("sombre logo rouge / fond",   "#F05252", "#0B0D12", 3.0),
    ("sombre texte / surface",     "#E8EAF0", "#12151C", 4.5),
]

failed = 0
for name, fg, bg, minimum in PAIRS:
    r = ratio(fg, bg)
    ok = r >= minimum
    if not ok:
        failed += 1
    print(f"{'OK ' if ok else 'ECHEC'} {name:<30} {r:5.2f}:1  (min {minimum})")

print()
if failed:
    print(f"{failed} paire(s) sous le seuil WCAG AA.")
    sys.exit(1)
print("Tous les contrastes respectent WCAG AA.")
```

- [ ] **Étape 2 : lancer le vérificateur de contraste**

```bash
python scripts/check_contrast.py
```

Attendu : dix lignes `OK`, puis `Tous les contrastes respectent WCAG AA.`, code de sortie 0.

Si une paire échoue, **ne pas modifier le seuil** — corriger la couleur dans la spec et ici, puis relancer.

- [ ] **Étape 3 : écrire le vérificateur de budget**

Créer `scripts/check_budget.py` :

```python
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
        (os.path.join(rel_dir, f), kb(os.path.join(d, f)))
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
    for name, size in collect(rel, exts):
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
```

- [ ] **Étape 4 : lancer le vérificateur de budget (échec attendu)**

```bash
python scripts/check_budget.py
```

Attendu : **ÉCHEC**, code de sortie 1. `css/` et `js/` n'existent pas encore et `index.html` référence les images non optimisées. C'est le rouge de départ — il vire au vert en Tâche 14.

- [ ] **Étape 5 : commit**

```bash
git add scripts/check_contrast.py scripts/check_budget.py
git commit -m "chore: ajoute les verificateurs de contraste et de budget"
```

---

## Tâche 2 : Optimisation des images

**Fichiers :**
- Créer : `scripts/optimize_images.py`
- Créer : `images/optimized/` (généré)

**Interfaces :**
- Consomme : `scripts/check_budget.py` (Tâche 1)
- Produit : `images/optimized/<nom>.webp` et `images/optimized/<nom>.png` pour les cinq images conservées. Les tâches 6, 8 et 9 y référencent leurs visuels via `<picture>`.

- [ ] **Étape 1 : écrire l'optimiseur**

Créer `scripts/optimize_images.py` :

```python
"""Redimensionne et convertit les images conservees (spec 9.2).

Les originaux dans images/ ne sont JAMAIS modifies.
La sortie va dans images/optimized/.
"""
import os, sys, io
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "images")
OUT = os.path.join(SRC, "optimized")

# (fichier source, nom de sortie, largeur max)
TARGETS = [
    ("profile_1.png", "profil-hero",   800),
    ("profil2.png",   "profil-about",  800),
    ("projet7.png",   "luxonera",     1200),
    ("projet-2.png",  "etrack",       1200),
    ("projet_6.png",  "hotellerie",   1200),
]

WEBP_QUALITY = 82

os.makedirs(OUT, exist_ok=True)

before_total = 0
after_total = 0

for src_name, out_name, max_w in TARGETS:
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

        png_path = os.path.join(OUT, out_name + ".png")
        im.save(png_path, "PNG", optimize=True)

        w_kb = os.path.getsize(webp_path) / 1024
        p_kb = os.path.getsize(png_path) / 1024
        after_total += w_kb
        print(
            f"{src_name:<16} {before:7.1f} Ko -> "
            f"{out_name}.webp {w_kb:6.1f} Ko / .png {p_kb:6.1f} Ko  ({im.width}x{im.height})"
        )

print(f"\nWebP cumule : {before_total:.1f} Ko -> {after_total:.1f} Ko "
      f"({100 - after_total / before_total * 100:.0f} % economises)")
```

- [ ] **Étape 2 : lancer l'optimiseur**

```bash
python scripts/optimize_images.py
```

Attendu : cinq lignes de conversion, chaque `.webp` **sous 150 Ko**, et une économie cumulée **supérieure à 85 %**.

Si un `.webp` dépasse 150 Ko, baisser `WEBP_QUALITY` à 78 et relancer. Ne pas descendre sous 75 : les captures d'interface deviennent visiblement floues.

- [ ] **Étape 3 : vérifier que les originaux sont intacts**

```bash
git status --short images/
```

Attendu : **aucun** fichier `images/*.png` listé comme modifié (`M`). Seul `images/optimized/` apparaît en non suivi (`??`).

Si un original apparaît en modifié, le script écrase sa source — corriger avant d'aller plus loin.

- [ ] **Étape 4 : commit**

```bash
git add scripts/optimize_images.py images/optimized/
git commit -m "perf: genere les images optimisees en WebP (8,6 Mo -> ~400 Ko)"
```

---

## Tâche 3 : Identité visuelle — logo et favicon

**Fichiers :**
- Créer : `favicon.svg`
- Créer : `images/og-image.png` (généré)
- Créer : `scripts/make_og_image.py`

**Interfaces :**
- Consomme : `--logo-red #DC2626`
- Produit : le fragment SVG du logo, réutilisé tel quel dans l'en-tête en Tâche 5. `favicon.svg` et `images/og-image.png` sont référencés en Tâche 13.

- [ ] **Étape 1 : créer le favicon**

Créer `favicon.svg`. Les glyphes sont des **tracés vectoriels**, pas du `<text>` : un `<text>` dépend d'une police que le navigateur ne charge pas pour un favicon, le rendu serait imprévisible.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <rect width="32" height="32" rx="7" fill="#FFFFFF"/>
  <g fill="none" stroke="#DC2626" stroke-width="3"
     stroke-linecap="round" stroke-linejoin="round">
    <path d="M11 10 L6 16 L11 22"/>
    <path d="M19 8.5 L13 23.5"/>
    <path d="M21 10 L26 16 L21 22"/>
  </g>
</svg>
```

- [ ] **Étape 2 : vérifier la lisibilité à 16 px**

Ouvrir `favicon.svg` dans le navigateur et le réduire à 16 px.

Attendu : les trois glyphes `<`, `/`, `>` restent distincts, aucun ne fusionne avec son voisin.

Si les traits se touchent, réduire `stroke-width` à `2.6` et écarter la barre oblique (`M 19.5 8.5 L 12.5 23.5`). Ne pas empiler les glyphes.

- [ ] **Étape 3 : générer l'image de partage Open Graph**

Créer `scripts/make_og_image.py` :

```python
"""Genere l'image de partage Open Graph (1200x630, spec 11)."""
import os, sys, io
from PIL import Image, ImageDraw

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
BG = (255, 255, 255)
RED = (220, 38, 38)
INK = (13, 17, 23)
MUTED = (91, 100, 114)
ACCENT = (67, 56, 202)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# Barre d'accent superieure
d.rectangle([0, 0, W, 8], fill=ACCENT)

# Glyphe </> vectoriel, echelle x9 depuis le viewBox 32
sx, sy, s = 90, 90, 9
def pts(coords):
    return [(sx + x * s / 4, sy + y * s / 4) for x, y in coords]

for path in (
    [(11, 10), (6, 16), (11, 22)],
    [(19, 8.5), (13, 23.5)],
    [(21, 10), (26, 16), (21, 22)],
):
    d.line(pts(path), fill=RED, width=11, joint="curve")

# On dessine le texte avec la police par defaut de Pillow puis on l'agrandit :
# aucune police systeme n'est garantie presente sur la machine de build.
def big_text(text, size, color, xy):
    tmp = Image.new("RGBA", (W, 120), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((0, 0), text, fill=color)
    bbox = tmp.getbbox()
    if not bbox:
        return
    crop = tmp.crop(bbox)
    scale = size / crop.height
    crop = crop.resize((int(crop.width * scale), size), Image.LANCZOS)
    img.paste(crop, xy, crop)

big_text("SAWADOGO ADAM SHARIF", 58, INK, (90, 250))
big_text("Developpeur Full Stack, Web & Mobile", 34, ACCENT, (90, 340))
big_text("Angular  .  Spring Boot  .  Flutter  .  Next.js", 26, MUTED, (90, 410))

out = os.path.join(ROOT, "images", "og-image.png")
img.save(out, "PNG", optimize=True)
print(f"Genere : images/og-image.png  {os.path.getsize(out) / 1024:.1f} Ko  {W}x{H}")
```

- [ ] **Étape 4 : générer et vérifier**

```bash
python scripts/make_og_image.py
```

Attendu : `images/og-image.png` créé, **1200×630**, sous 150 Ko. Ouvrir le fichier : le glyphe `</>` rouge est visible en haut à gauche, le nom et le titre sont lisibles.

- [ ] **Étape 5 : commit**

```bash
git add favicon.svg scripts/make_og_image.py images/og-image.png
git commit -m "feat: ajoute le logo </> et l'image de partage Open Graph"
```

---

## Tâche 4 : Fondations CSS et thème

**Fichiers :**
- Créer : `css/base.css`
- Créer : `js/theme.js`
- Créer : `index.html` (squelette, remplace l'existant)

**Interfaces :**
- Consomme : les jetons des contraintes globales
- Produit :
  - `js/theme.js` exporte `initTheme(): void`, `toggleTheme(): void`, `applyTheme(theme: "light" | "dark"): void`
  - `css/base.css` définit tous les jetons, la classe `.container`, `.section`, `.section-title`, `.eyebrow`, `.sr-only`, `.skip-link`
  - Le bouton de bascule a l'`id` `theme-toggle` — attendu par la Tâche 5

- [ ] **Étape 1 : écrire `css/base.css`**

```css
/* ============================================================
   base.css — reset, jetons, typographie, utilitaires
   ============================================================ */

@import url("https://fonts.googleapis.com/css2?family=Sora:wght@600..700&family=Inter:wght@400..600&family=JetBrains+Mono:wght@500&display=swap");

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* ---------- Jetons : thème clair (défaut) ---------- */
:root {
  --bg: #ffffff;
  --surface: #f7f8fa;
  --surface-2: #eff1f5;
  --text: #0d1117;
  --text-muted: #5b6472;
  --accent: #4338ca;
  --accent-hover: #3730a3;
  --accent-soft: rgba(67, 56, 202, 0.08);
  --accent-contrast: #ffffff;
  --border: rgba(13, 17, 23, 0.08);
  --border-strong: rgba(13, 17, 23, 0.16);
  --logo-red: #dc2626;

  --shadow-sm: 0 1px 2px rgba(13, 17, 23, 0.06), 0 1px 3px rgba(13, 17, 23, 0.04);
  --shadow-md: 0 4px 12px rgba(13, 17, 23, 0.07), 0 2px 4px rgba(13, 17, 23, 0.04);
  --shadow-lg: 0 12px 32px rgba(13, 17, 23, 0.1), 0 4px 8px rgba(13, 17, 23, 0.05);

  --font-display: "Sora", system-ui, -apple-system, sans-serif;
  --font-body: "Inter", system-ui, -apple-system, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", monospace;

  /* Échelle fluide : plus de hack html{font-size:62.5%} */
  --fs-xs: clamp(0.75rem, 0.72rem + 0.15vw, 0.8125rem);
  --fs-sm: clamp(0.875rem, 0.84rem + 0.17vw, 0.9375rem);
  --fs-base: clamp(1rem, 0.96rem + 0.2vw, 1.0625rem);
  --fs-lg: clamp(1.125rem, 1.06rem + 0.32vw, 1.25rem);
  --fs-xl: clamp(1.375rem, 1.25rem + 0.6vw, 1.75rem);
  --fs-2xl: clamp(1.75rem, 1.5rem + 1.2vw, 2.5rem);
  --fs-3xl: clamp(2.25rem, 1.8rem + 2.2vw, 3.5rem);
  --fs-4xl: clamp(2.75rem, 2rem + 3.4vw, 4.75rem);

  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-24: 6rem;

  --radius-sm: 0.5rem;
  --radius: 0.875rem;
  --radius-lg: 1.25rem;
  --radius-full: 999px;

  --container: 1200px;
  --header-h: 72px;
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
}

/* ---------- Jetons : thème sombre ---------- */
[data-theme="dark"] {
  --bg: #0b0d12;
  --surface: #12151c;
  --surface-2: #1a1f29;
  --text: #e8eaf0;
  --text-muted: #9aa3b2;
  --accent: #818cf8;
  --accent-hover: #a5b0ff;
  --accent-soft: rgba(129, 140, 248, 0.14);
  --accent-contrast: #0b0d12;
  --border: rgba(255, 255, 255, 0.09);
  --border-strong: rgba(255, 255, 255, 0.18);
  --logo-red: #f05252;

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.45);
  --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.55);
}

/* ---------- Éléments ---------- */
html {
  -webkit-text-size-adjust: 100%;
  scroll-behavior: smooth;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  font-size: var(--fs-base);
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
  transition: background 0.3s var(--ease-out), color 0.3s var(--ease-out);
}

h1, h2, h3, h4 {
  font-family: var(--font-display);
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: var(--text);
}

a {
  color: inherit;
  text-decoration: none;
}

img, svg {
  display: block;
  max-width: 100%;
}

ul, ol {
  list-style: none;
}

button, input, textarea {
  font: inherit;
  color: inherit;
}

:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
  border-radius: var(--radius-sm);
}

/* ---------- Utilitaires ---------- */
.container {
  width: 100%;
  max-width: var(--container);
  margin-inline: auto;
  padding-inline: var(--space-6);
}

.section {
  padding-block: var(--space-24);
}

.section--surface {
  background: var(--surface);
}

.eyebrow {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: var(--space-3);
}

.section-title {
  font-size: var(--fs-3xl);
  margin-bottom: var(--space-4);
}

.section-title span {
  color: var(--accent);
}

.section-lead {
  font-size: var(--fs-lg);
  color: var(--text-muted);
  max-width: 60ch;
  margin-bottom: var(--space-16);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.skip-link {
  position: absolute;
  top: var(--space-2);
  left: var(--space-2);
  z-index: 999;
  padding: var(--space-3) var(--space-4);
  background: var(--accent);
  color: var(--accent-contrast);
  border-radius: var(--radius-sm);
  transform: translateY(-200%);
  transition: transform 0.2s var(--ease-out);
}

.skip-link:focus {
  transform: translateY(0);
}

/* ---------- Mouvement réduit ---------- */
@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }
  *,
  *::before,
  *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }
}
```

- [ ] **Étape 2 : écrire `js/theme.js`**

```js
/**
 * Gestion du thème clair/sombre (spec §12).
 *
 * Ordre de priorité :
 *   1. le choix mémorisé par le visiteur ;
 *   2. sinon la préférence système ;
 *   3. sinon le clair.
 *
 * Tant qu'aucun choix n'est mémorisé, le site suit les changements système
 * en direct.
 */
const STORAGE_KEY = "theme";
const root = document.documentElement;
const darkQuery = window.matchMedia("(prefers-color-scheme: dark)");

function storedChoice() {
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    return value === "dark" || value === "light" ? value : null;
  } catch {
    // localStorage indisponible (navigation privée stricte).
    return null;
  }
}

export function applyTheme(theme) {
  root.setAttribute("data-theme", theme);
  const btn = document.querySelector("#theme-toggle");
  if (btn) {
    btn.setAttribute("aria-pressed", String(theme === "dark"));
    btn.setAttribute(
      "aria-label",
      theme === "dark" ? "Activer le thème clair" : "Activer le thème sombre"
    );
  }
}

export function initTheme() {
  const saved = storedChoice();
  applyTheme(saved ?? (darkQuery.matches ? "dark" : "light"));

  // Suit le système en direct, mais seulement tant que le visiteur
  // n'a pas tranché lui-même.
  darkQuery.addEventListener("change", (e) => {
    if (storedChoice() === null) applyTheme(e.matches ? "dark" : "light");
  });
}

export function toggleTheme() {
  const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
  try {
    localStorage.setItem(STORAGE_KEY, next);
  } catch {
    // Le thème s'appliquera quand même, sans persistance.
  }
  applyTheme(next);
}
```

- [ ] **Étape 3 : écrire le squelette `index.html`**

Remplacer intégralement `index.html`. Le script inline dans `<head>` est **obligatoire** : sans lui, `js/main.js` étant chargé en `defer`, la page peindrait en clair avant de basculer en sombre — un flash blanc visible à chaque chargement pour un visiteur en thème sombre.

```html
<!DOCTYPE html>
<html lang="fr" data-theme="light">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sawadogo Adam Sharif — Développeur Full Stack, Web & Mobile</title>

  <!-- Applique le thème avant la première peinture pour éviter tout flash. -->
  <script>
    (function () {
      var t = null;
      try { t = localStorage.getItem("theme"); } catch (e) {}
      if (t !== "dark" && t !== "light") {
        t = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }
      document.documentElement.setAttribute("data-theme", t);
    })();
  </script>

  <link rel="icon" href="favicon.svg" type="image/svg+xml" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="css/base.css" />
  <link rel="stylesheet" href="css/layout.css" />
  <link rel="stylesheet" href="css/components.css" />
  <link rel="stylesheet" href="css/responsive.css" />
  <script type="module" src="js/main.js"></script>
</head>

<body>
  <a class="skip-link" href="#main">Aller au contenu principal</a>

  <!-- L'en-tête arrive en Tâche 5 -->

  <main id="main">
    <!-- Les sections arrivent en Tâches 6 à 11 -->
    <p class="container">Squelette en place.</p>
  </main>

  <!-- Le pied de page arrive en Tâche 11 -->
</body>

</html>
```

- [ ] **Étape 4 : écrire `js/main.js` provisoire**

```js
import { initTheme } from "./theme.js";

initTheme();
```

- [ ] **Étape 5 : créer les trois fichiers CSS restants, vides**

Ils sont déjà référencés par `index.html` ; sans eux, la console affiche trois 404.

```bash
printf '/* layout.css — Tâche 5 */\n' > css/layout.css
printf '/* components.css — Tâche 5 */\n' > css/components.css
printf '/* responsive.css — Tâche 12 */\n' > css/responsive.css
```

- [ ] **Étape 6 : vérifier dans le navigateur**

Démarrer le serveur avec `preview_start`, puis :

1. Ouvrir la page. Attendu : fond **blanc**, texte « Squelette en place. » en Inter.
2. `read_console_messages` — attendu : **zéro erreur**, aucun 404.
3. Console : `localStorage.setItem("theme","dark"); location.reload()` — attendu : la page **repeint directement en sombre**, sans flash blanc.
4. Console : `localStorage.removeItem("theme"); location.reload()` — attendu : retour au clair.
5. Sans clé en `localStorage`, émuler `prefers-color-scheme: dark` dans les outils de développement (Rendering → Emulate CSS media feature) et recharger — attendu : la page s'ouvre **en sombre**, sans flash blanc.
6. Toujours sans clé en `localStorage`, basculer l'émulation de sombre vers clair **sans recharger** — attendu : la page repasse en clair toute seule.
7. Cliquer sur la bascule pour choisir explicitement, puis rebasculer l'émulation système — attendu : la page **ne suit plus** le système, le choix du visiteur prime.

- [ ] **Étape 7 : commit**

```bash
git add index.html css/ js/
git commit -m "feat: fondations CSS, jetons de theme et thème clair par défaut"
```

---

## Tâche 5 : En-tête, navigation et sprite d'icônes

**Fichiers :**
- Modifier : `index.html`
- Modifier : `css/layout.css`, `css/components.css`
- Créer : `js/nav.js`
- Modifier : `js/main.js`

**Interfaces :**
- Consomme : `applyTheme`, `toggleTheme` (Tâche 4) ; le tracé du logo (Tâche 3)
- Produit :
  - `js/nav.js` exporte `initNav(): void` — gère le burger, la fermeture au clic sur un lien, et l'état masqué/visible de l'en-tête
  - Sprite `<svg id="icons">` en tête de `<body>`, icônes appelées via `<svg class="icon"><use href="#i-github"></use></svg>`
  - La mise en surbrillance de la section active est **déléguée à ScrollTrigger** en Tâche 12, pas à `nav.js`

- [ ] **Étape 1 : ajouter le sprite d'icônes**

Insérer juste après `<body>`, avant le lien d'évitement. Ce bloc remplace la police Boxicons entière (~180 Ko) par ~6 Ko.

```html
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <g id="i-github"><path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.16-1.1-1.47-1.1-1.47-.9-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.89 1.52 2.34 1.08 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.56-1.11-4.56-4.95 0-1.09.39-1.99 1.03-2.69-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02a9.5 9.5 0 0 1 5 0c1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.6 1.03 2.69 0 3.85-2.34 4.7-4.57 4.95.36.31.68.92.68 1.85v2.74c0 .27.18.58.69.48A10 10 0 0 0 12 2Z"/></g>
    <g id="i-linkedin"><path d="M6.94 5a1.94 1.94 0 1 1-3.88 0 1.94 1.94 0 0 1 3.88 0ZM3.25 8.4h3.5V21h-3.5V8.4Zm5.75 0h3.35v1.72h.05c.47-.85 1.6-1.75 3.3-1.75 3.53 0 4.18 2.25 4.18 5.18V21h-3.5v-6.2c0-1.48-.03-3.38-2.1-3.38-2.1 0-2.42 1.6-2.42 3.27V21H9V8.4Z"/></g>
    <g id="i-whatsapp"><path d="M12.04 2a9.9 9.9 0 0 0-8.5 14.96L2 22l5.2-1.5A9.9 9.9 0 1 0 12.04 2Zm0 1.8a8.1 8.1 0 1 1-4.1 15.08l-.3-.17-3.08.9.9-3-.19-.31A8.1 8.1 0 0 1 12.04 3.8Zm4.6 10.3c-.25-.13-1.47-.72-1.7-.8-.23-.09-.4-.13-.56.12-.17.25-.65.8-.8.97-.14.16-.29.18-.54.06a6.6 6.6 0 0 1-3.3-2.88c-.25-.43.25-.4.71-1.33.08-.16.04-.3-.02-.42-.06-.13-.56-1.34-.76-1.84-.2-.48-.4-.41-.56-.42h-.47c-.16 0-.42.06-.64.3-.22.25-.84.83-.84 2.02s.86 2.34.98 2.5c.12.17 1.7 2.6 4.12 3.64 1.53.66 2.13.72 2.9.6.46-.06 1.47-.6 1.68-1.18.2-.58.2-1.07.15-1.18-.06-.1-.23-.17-.48-.29Z"/></g>
    <g id="i-x"><path d="M17.53 3h3.02l-6.6 7.54L21.75 21h-5.9l-4.63-6.05L5.92 21H2.9l7.06-8.07L2.5 3h6.05l4.18 5.53L17.53 3Zm-1.06 16.2h1.67L7.6 4.72H5.8L16.47 19.2Z"/></g>
    <g id="i-mail"><path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Zm9 7.1L4.4 7H19.6L12 12.1ZM4 8.9V17h16V8.9l-8 5.35L4 8.9Z"/></g>
    <g id="i-phone"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1.03-.24c1.12.37 2.33.57 3.57.57a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.24.2 2.45.57 3.57a1 1 0 0 1-.25 1.03l-2.2 2.2Z"/></g>
    <g id="i-pin"><path d="M12 2a7 7 0 0 1 7 7c0 5.25-7 13-7 13S5 14.25 5 9a7 7 0 0 1 7-7Zm0 9.5A2.5 2.5 0 1 0 12 6.5a2.5 2.5 0 0 0 0 5Z"/></g>
    <g id="i-download"><path d="M12 3v10.2l3.6-3.6 1.4 1.4-6 6-6-6 1.4-1.4L10 13.2V3h2ZM4 19h16v2H4v-2Z"/></g>
    <g id="i-external"><path d="M14 3h7v7h-2V6.4l-8.3 8.3-1.4-1.4L17.6 5H14V3ZM5 5h5v2H6v11h11v-4h2v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z"/></g>
    <g id="i-arrow-up"><path d="M12 4l7 7-1.4 1.4L13 7.8V20h-2V7.8l-4.6 4.6L5 11l7-7Z"/></g>
    <g id="i-menu"><path d="M3 6h18v2H3V6Zm0 5h18v2H3v-2Zm0 5h18v2H3v-2Z"/></g>
    <g id="i-close"><path d="M18.3 5.7 12 12l6.3 6.3-1.4 1.4L10.6 13.4 4.3 19.7 2.9 18.3 9.2 12 2.9 5.7l1.4-1.4L10.6 10.6l6.3-6.3 1.4 1.4Z"/></g>
    <g id="i-sun"><path d="M12 17a5 5 0 1 1 0-10 5 5 0 0 1 0 10Zm0-2a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm-1-13h2v3h-2V2Zm0 17h2v3h-2v-3ZM2 11h3v2H2v-2Zm17 0h3v2h-3v-2ZM4.2 5.6l1.4-1.4 2.1 2.1L6.3 7.7 4.2 5.6Zm12.1 12.1 1.4-1.4 2.1 2.1-1.4 1.4-2.1-2.1Zm2.1-13.5 1.4 1.4-2.1 2.1-1.4-1.4 2.1-2.1ZM5.6 19.8l-1.4-1.4 2.1-2.1 1.4 1.4-2.1 2.1Z"/></g>
    <g id="i-moon"><path d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9Z"/></g>
    <g id="i-code"><path d="M8.7 7.3 4 12l4.7 4.7-1.4 1.4L1.2 12l6.1-6.1 1.4 1.4Zm6.6 0 1.4-1.4L22.8 12l-6.1 6.1-1.4-1.4L20 12l-4.7-4.7Z"/></g>
    <g id="i-mobile"><path d="M7 2h10a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm0 2v16h10V4H7Zm4 14h2v1h-2v-1Z"/></g>
    <g id="i-server"><path d="M4 3h16a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Zm1 2v4h14V5H5Zm-1 8h16a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-6a1 1 0 0 1 1-1Zm1 2v4h14v-4H5Zm2-8h2v2H7V7Zm0 10h2v2H7v-2Z"/></g>
    <g id="i-sparkle"><path d="M12 2l2.2 6.1L20 10l-5.8 1.9L12 18l-2.2-6.1L4 10l5.8-1.9L12 2Zm7 12l1 2.6 2.6 1-2.6 1-1 2.6-1-2.6-2.6-1 2.6-1 1-2.6Z"/></g>
    <g id="i-graduation"><path d="M12 3 1 8l11 5 9-4.09V16h2V8L12 3ZM5 13.18v3.82L12 21l7-4v-3.82l-7 3.18-7-3.18Z"/></g>
    <g id="i-briefcase"><path d="M9 3h6a1 1 0 0 1 1 1v2h4a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h4V4a1 1 0 0 1 1-1Zm1 3h4V5h-4v1ZM5 8v10h14V8H5Z"/></g>
    <g id="i-check"><path d="M9.6 16.2 4.8 11.4l1.4-1.4 3.4 3.4 8-8 1.4 1.4-9.4 9.4Z"/></g>
  </defs>
</svg>
```

- [ ] **Étape 2 : ajouter l'en-tête au HTML**

Insérer entre le lien d'évitement et `<main>` :

```html
<div class="scroll-progress" id="scroll-progress" aria-hidden="true"></div>

<header class="header" id="header">
  <div class="header__inner container">
    <a href="#accueil" class="logo" aria-label="Adam's Coding — retour en haut">
      <svg class="logo__mark" viewBox="0 0 32 32" width="30" height="30" aria-hidden="true">
        <g fill="none" stroke="var(--logo-red)" stroke-width="2.6"
           stroke-linecap="round" stroke-linejoin="round">
          <path d="M11.5 10 L6.5 16 L11.5 22" />
          <path d="M19 9 L13 23" />
          <path d="M20.5 10 L25.5 16 L20.5 22" />
        </g>
      </svg>
      <span class="logo__text">Adam's<strong>Coding</strong></span>
    </a>

    <nav class="nav" id="nav" aria-label="Navigation principale">
      <a href="#accueil" class="nav__link is-active">Accueil</a>
      <a href="#a-propos" class="nav__link">À propos</a>
      <a href="#experience" class="nav__link">Expérience</a>
      <a href="#projets" class="nav__link">Projets</a>
      <a href="#competences" class="nav__link">Compétences</a>
      <a href="#contact" class="nav__link">Contact</a>
    </nav>

    <div class="header__actions">
      <button type="button" class="theme-toggle" id="theme-toggle"
              aria-pressed="false" aria-label="Activer le thème sombre">
        <svg class="icon theme-toggle__sun" aria-hidden="true"><use href="#i-sun" /></svg>
        <svg class="icon theme-toggle__moon" aria-hidden="true"><use href="#i-moon" /></svg>
      </button>

      <button type="button" class="burger" id="burger"
              aria-expanded="false" aria-controls="nav" aria-label="Ouvrir le menu">
        <svg class="icon burger__open" aria-hidden="true"><use href="#i-menu" /></svg>
        <svg class="icon burger__close" aria-hidden="true"><use href="#i-close" /></svg>
      </button>
    </div>
  </div>
</header>
```

- [ ] **Étape 3 : écrire `js/nav.js`**

```js
/**
 * Menu burger, état de l'en-tête au scroll.
 * La surbrillance de la section active est gérée par ScrollTrigger
 * dans animations.js — pas ici.
 */
export function initNav() {
  const header = document.querySelector("#header");
  const nav = document.querySelector("#nav");
  const burger = document.querySelector("#burger");

  const closeMenu = () => {
    nav.classList.remove("is-open");
    burger.classList.remove("is-open");
    burger.setAttribute("aria-expanded", "false");
    burger.setAttribute("aria-label", "Ouvrir le menu");
  };

  burger.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    burger.classList.toggle("is-open", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.setAttribute("aria-label", open ? "Fermer le menu" : "Ouvrir le menu");
  });

  nav.querySelectorAll(".nav__link").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && nav.classList.contains("is-open")) {
      closeMenu();
      burger.focus();
    }
  });

  // Ombre de l'en-tête dès qu'on quitte le haut de page.
  let lastY = window.scrollY;
  const onScroll = () => {
    const y = window.scrollY;
    header.classList.toggle("is-stuck", y > 8);
    // Masquage au scroll descendant, uniquement menu fermé et hors du haut.
    const hide = y > 240 && y > lastY && !nav.classList.contains("is-open");
    header.classList.toggle("is-hidden", hide);
    lastY = y;
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}
```

- [ ] **Étape 4 : écrire les styles d'en-tête dans `css/layout.css`**

```css
/* ============================================================
   layout.css — en-tête, sections, grilles, pied de page
   ============================================================ */

.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  width: 100%;
  transform: scaleX(0);
  transform-origin: 0 50%;
  background: var(--accent);
  z-index: 200;
}

.header {
  position: fixed;
  inset: 0 0 auto 0;
  z-index: 100;
  height: var(--header-h);
  background: color-mix(in srgb, var(--bg) 86%, transparent);
  backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid transparent;
  transition: transform 0.35s var(--ease-out), border-color 0.3s,
    background 0.3s;
}

.header.is-stuck {
  border-bottom-color: var(--border);
  box-shadow: var(--shadow-sm);
}

.header.is-hidden {
  transform: translateY(-100%);
}

.header__inner {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-6);
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-display);
  font-size: var(--fs-lg);
  font-weight: 600;
  letter-spacing: -0.02em;
  flex-shrink: 0;
}

.logo__text strong {
  color: var(--accent);
  font-weight: 700;
}

.nav {
  display: flex;
  align-items: center;
  gap: var(--space-8);
}

.nav__link {
  position: relative;
  font-size: var(--fs-sm);
  font-weight: 500;
  color: var(--text-muted);
  padding-block: var(--space-2);
  transition: color 0.2s var(--ease-out);
}

.nav__link::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: 0;
  height: 2px;
  width: 100%;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: 0 50%;
  transition: transform 0.25s var(--ease-out);
}

.nav__link:hover,
.nav__link.is-active {
  color: var(--text);
}

.nav__link.is-active::after {
  transform: scaleX(1);
}

.header__actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

main {
  padding-top: var(--header-h);
}
```

- [ ] **Étape 5 : écrire les composants dans `css/components.css`**

```css
/* ============================================================
   components.css — boutons, icônes, cartes, badges, formulaire
   ============================================================ */

.icon {
  width: 1.25em;
  height: 1.25em;
  fill: currentColor;
  flex-shrink: 0;
}

/* ---------- Boutons ---------- */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: 0.8em 1.6em;
  border-radius: var(--radius-full);
  font-size: var(--fs-sm);
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: transform 0.2s var(--ease-out), background 0.2s,
    border-color 0.2s, box-shadow 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
}

.btn--primary {
  background: var(--accent);
  color: var(--accent-contrast);
  box-shadow: var(--shadow-md);
}

.btn--primary:hover {
  background: var(--accent-hover);
  box-shadow: var(--shadow-lg);
}

.btn--ghost {
  background: transparent;
  color: var(--text);
  border-color: var(--border-strong);
}

.btn--ghost:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-soft);
}

/* ---------- Bascule de thème ---------- */
.theme-toggle,
.burger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}

.theme-toggle:hover,
.burger:hover {
  color: var(--accent);
  border-color: var(--accent);
  background: var(--accent-soft);
}

.theme-toggle__moon,
[data-theme="dark"] .theme-toggle__sun {
  display: none;
}

[data-theme="dark"] .theme-toggle__moon {
  display: block;
}

.burger {
  display: none;
}

.burger__close,
.burger.is-open .burger__open {
  display: none;
}

.burger.is-open .burger__close {
  display: block;
}
```

- [ ] **Étape 6 : câbler `js/main.js`**

```js
import { initTheme, toggleTheme } from "./theme.js";
import { initNav } from "./nav.js";

initTheme();
initNav();

document.querySelector("#theme-toggle").addEventListener("click", toggleTheme);
```

- [ ] **Étape 7 : vérifier dans le navigateur**

1. `read_console_messages` — attendu : **zéro erreur**.
2. L'en-tête est visible, le logo `</>` s'affiche en **rouge**, les six liens de navigation sont présents.
3. Cliquer sur la bascule de thème : la page passe en sombre, l'icône devient une lune, `aria-pressed` passe à `true`. Recharger : le sombre persiste.
4. En sombre, le logo reste rouge (teinte `#F05252`, plus claire).
5. Redimensionner à 375 px : la navigation disparaît, le burger apparaît. Cliquer : le menu s'ouvre, `aria-expanded="true"`. Cliquer sur un lien : il se ferme. Touche Échap : il se ferme.
6. Naviguer uniquement au clavier depuis le haut de la page — attendu : le lien « Aller au contenu principal » apparaît au premier Tab, chaque contrôle reçoit un contour de focus visible.

Les styles responsives du burger arrivent en Tâche 12 ; à cette étape, tester en ajoutant temporairement `.burger{display:inline-flex}` via les outils de développement.

- [ ] **Étape 8 : commit**

```bash
git add index.html css/ js/
git commit -m "feat: en-tête, navigation, bascule de thème et sprite SVG (remplace Boxicons)"
```

---

## Tâche 6 : Hero et bandeau de statistiques

**Fichiers :**
- Modifier : `index.html`, `css/layout.css`, `css/components.css`

**Interfaces :**
- Consomme : le sprite d'icônes (Tâche 5), `images/optimized/profil-hero.*` (Tâche 2)
- Produit :
  - `#accueil`, `#stats`
  - `.hero__role` — cible de l'effet machine à écrire (Tâche 12)
  - `.stat__value[data-count-to]` — cible des compteurs animés (Tâche 12)

- [ ] **Étape 1 : ajouter le HTML du hero et des stats**

Remplacer le contenu provisoire de `<main>` :

```html
<section class="hero" id="accueil">
  <div class="hero__inner container">
    <div class="hero__content">
      <p class="eyebrow">Ouagadougou, Burkina Faso</p>
      <h1 class="hero__name">Sawadogo<br />Adam Sharif</h1>
      <p class="hero__tagline">
        <span class="hero__role" data-roles="Développeur Full Stack|Développeur Mobile Flutter|Architecte logiciel|Intégrateur de modèles IA">Développeur Full Stack</span><span class="hero__caret" aria-hidden="true"></span>
      </p>
      <p class="hero__pitch">
        Développeur Full Stack polyvalent, web et mobile, avec plus de 3 ans
        d'expérience. Je conçois des applications modernes avec Angular,
        Spring Boot et Flutter, et j'intègre des modèles d'intelligence
        artificielle via API. Modélisation UML, architecture logicielle,
        méthodologie Agile.
      </p>

      <div class="hero__actions">
        <a href="#projets" class="btn btn--primary">
          Voir mes projets
          <svg class="icon" aria-hidden="true"><use href="#i-arrow-up" /></svg>
        </a>
        <a href="./documents/CV_Sawadogo_Adam_Sharif.pdf" class="btn btn--ghost"
           download="CV_Sawadogo_Adam_Sharif.pdf">
          <svg class="icon" aria-hidden="true"><use href="#i-download" /></svg>
          Télécharger mon CV
        </a>
      </div>

      <ul class="social">
        <li><a href="https://github.com/Oursdingo" target="_blank" rel="noopener noreferrer" aria-label="GitHub"><svg class="icon" aria-hidden="true"><use href="#i-github" /></svg></a></li>
        <li><a href="https://www.linkedin.com/in/sharif-sawadogo-280197223/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><svg class="icon" aria-hidden="true"><use href="#i-linkedin" /></svg></a></li>
        <li><a href="https://wa.me/22677468876" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp"><svg class="icon" aria-hidden="true"><use href="#i-whatsapp" /></svg></a></li>
        <li><a href="https://x.com/SharifSawa51023" target="_blank" rel="noopener noreferrer" aria-label="X"><svg class="icon" aria-hidden="true"><use href="#i-x" /></svg></a></li>
      </ul>
    </div>

    <div class="hero__visual">
      <picture>
        <source srcset="images/optimized/profil-hero.webp" type="image/webp" />
        <img src="images/optimized/profil-hero.png"
             alt="Portrait de Sawadogo Adam Sharif"
             width="800" height="800" fetchpriority="high" />
      </picture>
    </div>
  </div>
</section>

<section class="stats" id="stats" aria-label="Chiffres clés">
  <div class="container">
    <ul class="stats__grid">
      <li class="stat">
        <span class="stat__value" data-count-to="3" data-suffix="+">0</span>
        <span class="stat__label">Années d'expérience</span>
      </li>
      <li class="stat">
        <span class="stat__value" data-count-to="10" data-suffix="+">0</span>
        <span class="stat__label">Projets réalisés</span>
      </li>
      <li class="stat">
        <span class="stat__value" data-count-to="2" data-suffix="">0</span>
        <span class="stat__label">Applications mobiles</span>
      </li>
      <li class="stat">
        <span class="stat__value" data-count-to="20" data-suffix="+">0</span>
        <span class="stat__label">Technologies maîtrisées</span>
      </li>
    </ul>
  </div>
</section>
```

- [ ] **Étape 2 : styliser dans `css/layout.css`**

Ajouter à la fin :

```css
/* ---------- Hero ---------- */
.hero {
  padding-block: var(--space-24) var(--space-16);
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: "";
  position: absolute;
  top: -20%;
  right: -10%;
  width: 55vw;
  height: 55vw;
  max-width: 700px;
  max-height: 700px;
  background: radial-gradient(circle, var(--accent-soft) 0%, transparent 68%);
  pointer-events: none;
}

.hero__inner {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  align-items: center;
  gap: var(--space-16);
  position: relative;
}

.hero__name {
  font-size: var(--fs-4xl);
  margin-bottom: var(--space-4);
}

.hero__tagline {
  font-family: var(--font-mono);
  font-size: var(--fs-xl);
  font-weight: 500;
  color: var(--accent);
  min-height: 1.6em;
  margin-bottom: var(--space-6);
}

.hero__caret {
  display: inline-block;
  width: 2px;
  height: 1em;
  margin-left: 2px;
  background: var(--accent);
  vertical-align: -0.12em;
  animation: caret-blink 1s steps(2) infinite;
}

@keyframes caret-blink {
  50% { opacity: 0; }
}

.hero__pitch {
  color: var(--text-muted);
  max-width: 56ch;
  margin-bottom: var(--space-8);
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}

.hero__visual img {
  width: 100%;
  height: auto;
  border-radius: var(--radius-lg);
}

/* ---------- Statistiques ---------- */
.stats {
  padding-block: var(--space-12);
  border-block: 1px solid var(--border);
  background: var(--surface);
}

.stats__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-8);
}

.stat {
  text-align: center;
}

.stat__value {
  display: block;
  font-family: var(--font-display);
  font-size: var(--fs-3xl);
  font-weight: 700;
  color: var(--accent);
  line-height: 1;
}

.stat__label {
  display: block;
  margin-top: var(--space-2);
  font-size: var(--fs-sm);
  color: var(--text-muted);
}
```

- [ ] **Étape 3 : styliser les réseaux sociaux dans `css/components.css`**

```css
.social {
  display: flex;
  gap: var(--space-3);
}

.social a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border);
  color: var(--text-muted);
  transition: color 0.2s var(--ease-out), border-color 0.2s,
    background 0.2s, transform 0.2s var(--ease-out);
}

.social a:hover {
  color: var(--accent);
  border-color: var(--accent);
  background: var(--accent-soft);
  transform: translateY(-3px);
}
```

- [ ] **Étape 4 : vérifier**

1. `read_console_messages` — zéro erreur, aucun 404 sur `profil-hero.webp`.
2. Le portrait s'affiche. Dans l'onglet réseau, le fichier chargé est le **`.webp`**, pas le `.png`.
3. Les quatre statistiques affichent `0` (elles s'animeront en Tâche 12).
4. Les quatre icônes sociales s'affichent, **GitHub inclus**.
5. Survoler une icône : elle prend la couleur d'accent et se soulève.
6. `.hero__role` affiche « Développeur Full Stack » en dur — le texte reste lisible si le JS échoue.

- [ ] **Étape 5 : commit**

```bash
git add index.html css/
git commit -m "feat: section hero et bandeau de statistiques"
```

---

## Tâche 7 : À propos et Services

**Fichiers :**
- Modifier : `index.html`, `css/layout.css`, `css/components.css`

**Interfaces :**
- Consomme : le sprite (Tâche 5), `images/optimized/profil-about.*` (Tâche 2)
- Produit : `#a-propos`, `#services` ; la classe `.card` réutilisée en Tâches 9 et 10

- [ ] **Étape 1 : ajouter le HTML**

Après la section `stats` :

```html
<section class="section" id="a-propos">
  <div class="container about">
    <div class="about__visual">
      <picture>
        <source srcset="images/optimized/profil-about.webp" type="image/webp" />
        <img src="images/optimized/profil-about.png"
             alt="Sawadogo Adam Sharif au travail"
             width="800" height="800" loading="lazy" />
      </picture>
    </div>

    <div class="about__content">
      <p class="eyebrow">À propos</p>
      <h2 class="section-title">Développeur <span>Full Stack</span>, web et mobile</h2>
      <p class="about__text">
        Développeur Full Stack polyvalent, avec plus de 3 ans d'expérience
        académique et professionnelle. Mon expertise couvre la conception
        d'applications modernes avec Angular, Spring Boot et Flutter, la
        modélisation UML et les architectures logicielles, ainsi que
        l'intégration de modèles d'intelligence artificielle via API.
      </p>
      <p class="about__text">
        Je suis à l'aise avec les outils de développement assisté par IA.
        Autonome, responsable et respectueux, avec un sens aigu du travail en
        équipe et une capacité à travailler efficacement sous pression.
      </p>

      <ul class="about__facts">
        <li><svg class="icon" aria-hidden="true"><use href="#i-pin" /></svg> Nagrin, Ouagadougou — Burkina Faso</li>
        <li><svg class="icon" aria-hidden="true"><use href="#i-briefcase" /></svg> Switch Maker — depuis juin 2025</li>
        <li><svg class="icon" aria-hidden="true"><use href="#i-graduation" /></svg> Licence Informatique</li>
        <li><svg class="icon" aria-hidden="true"><use href="#i-check" /></svg> Français natif · Anglais B2</li>
      </ul>

      <a href="./documents/CV_Sawadogo_Adam_Sharif.pdf" class="btn btn--primary"
         download="CV_Sawadogo_Adam_Sharif.pdf">
        <svg class="icon" aria-hidden="true"><use href="#i-download" /></svg>
        Télécharger mon CV
      </a>
    </div>
  </div>
</section>

<section class="section section--surface" id="services">
  <div class="container">
    <p class="eyebrow">Services</p>
    <h2 class="section-title">Ce que je <span>réalise</span></h2>
    <p class="section-lead">
      De la conception de l'architecture au déploiement, sur le web comme sur mobile.
    </p>

    <div class="card-grid">
      <article class="card">
        <svg class="card__icon" aria-hidden="true"><use href="#i-code" /></svg>
        <h3 class="card__title">Développement Web</h3>
        <p class="card__text">
          Applications modernes et performantes avec Angular, Next.js et
          TypeScript. Interfaces soignées, ergonomiques, orientées expérience
          utilisateur.
        </p>
      </article>

      <article class="card">
        <svg class="card__icon" aria-hidden="true"><use href="#i-mobile" /></svg>
        <h3 class="card__title">Développement Mobile</h3>
        <p class="card__text">
          Applications mobiles multiplateformes avec Flutter et Dart. Deux
          applications livrées en production : KEL et LONIA.
        </p>
      </article>

      <article class="card">
        <svg class="card__icon" aria-hidden="true"><use href="#i-server" /></svg>
        <h3 class="card__title">Back-End & API</h3>
        <p class="card__text">
          API REST robustes et sécurisées avec Spring Boot, authentification
          Keycloak, architectures modulaires et microservices.
        </p>
      </article>

      <article class="card">
        <svg class="card__icon" aria-hidden="true"><use href="#i-sparkle" /></svg>
        <h3 class="card__title">Intégration IA</h3>
        <p class="card__text">
          Intégration de modèles d'intelligence artificielle via API, avec
          FastAPI et Python. Microservices d'analyse et de génération de contenu.
        </p>
      </article>

      <article class="card">
        <svg class="card__icon" aria-hidden="true"><use href="#i-graduation" /></svg>
        <h3 class="card__title">Formation JavaScript</h3>
        <p class="card__text">
          Fondamentaux du développement moderne : JavaScript, TypeScript,
          Angular, bonnes pratiques et organisation du code.
        </p>
        <a href="https://www.facebook.com/share/v/1Ewaoy9zYP/" class="card__link"
           target="_blank" rel="noopener noreferrer">
          En savoir plus
          <svg class="icon" aria-hidden="true"><use href="#i-external" /></svg>
        </a>
      </article>
    </div>
  </div>
</section>
```

- [ ] **Étape 2 : styliser dans `css/layout.css`**

```css
/* ---------- À propos ---------- */
.about {
  display: grid;
  grid-template-columns: 0.85fr 1.15fr;
  align-items: center;
  gap: var(--space-16);
}

.about__visual img {
  width: 100%;
  height: auto;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.about__text {
  color: var(--text-muted);
  margin-bottom: var(--space-4);
  max-width: 60ch;
}

.about__facts {
  display: grid;
  gap: var(--space-3);
  margin-block: var(--space-8);
}

.about__facts li {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--fs-sm);
  color: var(--text-muted);
}

.about__facts .icon {
  color: var(--accent);
}

/* ---------- Grille de cartes ---------- */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-6);
}
```

- [ ] **Étape 3 : styliser la carte dans `css/components.css`**

```css
.card {
  display: flex;
  flex-direction: column;
  padding: var(--space-8);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  transition: transform 0.3s var(--ease-out), border-color 0.3s,
    box-shadow 0.3s;
}

.card:hover {
  transform: translateY(-4px);
  border-color: var(--accent);
  box-shadow: var(--shadow-lg);
}

.card__icon {
  width: 40px;
  height: 40px;
  fill: var(--accent);
  margin-bottom: var(--space-4);
}

.card__title {
  font-size: var(--fs-lg);
  margin-bottom: var(--space-3);
}

.card__text {
  font-size: var(--fs-sm);
  color: var(--text-muted);
  flex-grow: 1;
}

.card__link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-4);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--accent);
}

.card__link:hover {
  text-decoration: underline;
}
```

- [ ] **Étape 4 : vérifier**

1. Zéro erreur console, `profil-about.webp` chargé.
2. Les **cinq** cartes de service s'affichent, chacune avec son icône en couleur d'accent.
3. Survol d'une carte : elle se soulève, sa bordure passe à l'accent.
4. Les quatre faits « À propos » affichent leur icône.
5. Le bouton de CV télécharge bien `CV_Sawadogo_Adam_Sharif.pdf`.
6. Basculer en thème sombre : les cartes restent lisibles, aucune ne devient blanche sur blanc.

- [ ] **Étape 5 : commit**

```bash
git add index.html css/
git commit -m "feat: sections À propos et Services (5 cartes)"
```

---

## Tâche 8 : Expérience professionnelle

**Fichiers :**
- Modifier : `index.html`, `css/components.css`

**Interfaces :**
- Consomme : le sprite (Tâche 5)
- Produit : `#experience`, `.timeline`, `.timeline__line` — cible de l'animation de tracé (Tâche 12)

- [ ] **Étape 1 : ajouter le HTML**

```html
<section class="section" id="experience">
  <div class="container">
    <p class="eyebrow">Parcours</p>
    <h2 class="section-title">Expérience <span>professionnelle</span></h2>
    <p class="section-lead">
      Deux postes menés en parallèle : le développement de plateformes
      institutionnelles et le pilotage de projets en agence.
    </p>

    <ol class="timeline">
      <span class="timeline__line" aria-hidden="true"></span>

      <li class="timeline__item">
        <div class="timeline__dot" aria-hidden="true"></div>
        <div class="timeline__body">
          <p class="timeline__period">Juin 2025 — Présent</p>
          <h3 class="timeline__role">Développeur Full Stack</h3>
          <p class="timeline__company">Switch Maker</p>
          <ul class="timeline__list">
            <li>Développement de plateformes web pour des institutions.</li>
            <li><strong>SIG</strong> — Système Intégré de Gestion, avec Odoo et Metabase pour les tableaux de bord. En cours de développement.</li>
            <li><strong>DAICE</strong> — plateforme de promotion des investissements pour le CEPICI (Côte d'Ivoire).</li>
            <li>Conception du socle applicatif : architecture logicielle, modules métier, sécurité avec Keycloak.</li>
            <li>Intégration de modèles d'intelligence artificielle via API, développés avec FastAPI et Python.</li>
            <li><strong>LONIA</strong> — application mobile d'apprentissage en ligne, réalisée avec Flutter.</li>
            <li><strong>KEL</strong> — application mobile de gestion de livraison, suivi des commandes et des courses, réalisée avec Flutter.</li>
            <li>Analyse des besoins, modélisation UML, rédaction de comptes rendus, méthodologie Agile.</li>
          </ul>
          <ul class="tag-list">
            <li class="tag">Angular</li><li class="tag">Spring Boot</li>
            <li class="tag">Flutter</li><li class="tag">FastAPI</li>
            <li class="tag">Keycloak</li><li class="tag">Odoo</li>
            <li class="tag">Metabase</li><li class="tag">PostgreSQL</li>
          </ul>
        </div>
      </li>

      <li class="timeline__item">
        <div class="timeline__dot" aria-hidden="true"></div>
        <div class="timeline__body">
          <p class="timeline__period">En parallèle</p>
          <h3 class="timeline__role">Responsable des projets informatiques</h3>
          <p class="timeline__company">BlendBloc — agence web marketing</p>
          <ul class="timeline__list">
            <li>Pilotage des projets techniques.</li>
            <li>Mise en place d'un espace de gestion de projet avec Notion : suivi des tâches, réunions et documents.</li>
            <li>Développement du site vitrine de l'agence.</li>
          </ul>
          <ul class="tag-list">
            <li class="tag">Gestion de projet</li><li class="tag">Notion</li>
            <li class="tag">Next.js</li>
          </ul>
        </div>
      </li>
    </ol>
  </div>
</section>
```

- [ ] **Étape 2 : styliser dans `css/components.css`**

```css
/* ---------- Timeline ---------- */
.timeline {
  position: relative;
  padding-left: var(--space-12);
}

.timeline__line {
  position: absolute;
  left: 7px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: var(--border-strong);
  transform-origin: 50% 0;
}

.timeline__item {
  position: relative;
  padding-bottom: var(--space-16);
}

.timeline__item:last-child {
  padding-bottom: 0;
}

.timeline__dot {
  position: absolute;
  left: calc(var(--space-12) * -1);
  top: 6px;
  width: 16px;
  height: 16px;
  border-radius: var(--radius-full);
  background: var(--bg);
  border: 3px solid var(--accent);
  z-index: 1;
}

.timeline__period {
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: var(--space-2);
}

.timeline__role {
  font-size: var(--fs-xl);
}

.timeline__company {
  font-size: var(--fs-base);
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: var(--space-4);
}

.timeline__list {
  display: grid;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
}

.timeline__list li {
  position: relative;
  padding-left: var(--space-6);
  font-size: var(--fs-sm);
  color: var(--text-muted);
}

.timeline__list li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.65em;
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  background: var(--accent);
  opacity: 0.5;
}

.timeline__list strong {
  color: var(--text);
  font-weight: 600;
}

/* ---------- Étiquettes ---------- */
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.tag {
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  padding: 0.35em 0.8em;
  border-radius: var(--radius-full);
  background: var(--accent-soft);
  color: var(--accent);
  border: 1px solid transparent;
}
```

- [ ] **Étape 3 : vérifier**

1. Zéro erreur console.
2. Les deux postes s'affichent, Switch Maker **en premier**.
3. La ligne verticale relie les deux pastilles sans dépasser ni au-dessus de la première, ni sous la dernière.
4. Les huit points de Switch Maker sont présents, SIG / DAICE / LONIA / KEL en gras.
5. Les étiquettes de technologies s'affichent en JetBrains Mono sur fond d'accent atténué.
6. En thème sombre, les étiquettes restent lisibles.

- [ ] **Étape 4 : commit**

```bash
git add index.html css/components.css
git commit -m "feat: section Expérience professionnelle en timeline"
```

---

## Tâche 9 : Projets

La tâche la plus sensible du plan : l'ordre des neuf projets est imposé et non négociable.

**Fichiers :**
- Modifier : `index.html`, `css/layout.css`, `css/components.css`
- Créer : `js/filters.js`
- Modifier : `js/main.js`

**Interfaces :**
- Consomme : le sprite (Tâche 5), `images/optimized/{luxonera,etrack,hotellerie}.*` (Tâche 2)
- Produit :
  - `#projets`, `.project-card[data-category]`
  - `js/filters.js` exporte `initFilters(): void`
  - Catégories possibles : `pro`, `web`, `mobile`, `academique` — un projet peut en cumuler plusieurs, séparées par une espace

- [ ] **Étape 1 : ajouter l'en-tête de section et les filtres**

```html
<section class="section section--surface" id="projets">
  <div class="container">
    <p class="eyebrow">Réalisations</p>
    <h2 class="section-title">Mes <span>projets</span></h2>
    <p class="section-lead">
      Des plateformes institutionnelles aux applications mobiles, en passant
      par le e-commerce et les projets académiques.
    </p>

    <div class="filters" role="group" aria-label="Filtrer les projets">
      <button type="button" class="filter is-active" data-filter="all" aria-pressed="true">Tous</button>
      <button type="button" class="filter" data-filter="pro" aria-pressed="false">Professionnels</button>
      <button type="button" class="filter" data-filter="web" aria-pressed="false">Web</button>
      <button type="button" class="filter" data-filter="mobile" aria-pressed="false">Mobile</button>
      <button type="button" class="filter" data-filter="academique" aria-pressed="false">Académiques</button>
    </div>

    <p class="filters__status sr-only" id="filters-status" role="status" aria-live="polite"></p>

    <div class="project-grid" id="project-grid">
      <!-- Les neuf cartes, étapes 2 et 3 -->
    </div>
  </div>
</section>
```

- [ ] **Étape 2 : ajouter les six cartes sans capture**

Dans `#project-grid`, **dans cet ordre exact**. Aucun bouton de lien n'est ajouté aux projets sans URL — un lien mort est pire qu'une absence de lien.

```html
<!-- 1 -->
<article class="project-card project-card--noimage" data-category="pro web">
  <div class="project-card__thumb" aria-hidden="true"><span class="project-card__mono">SIG</span></div>
  <div class="project-card__body">
    <div class="project-card__head">
      <h3 class="project-card__title">SIG — Système Intégré de Gestion</h3>
      <span class="badge badge--wip">En cours</span>
    </div>
    <p class="project-card__text">
      Plateforme institutionnelle de gestion développée chez Switch Maker,
      avec Odoo pour le socle métier et Metabase pour les tableaux de bord.
    </p>
    <ul class="tag-list">
      <li class="tag">Odoo</li><li class="tag">Metabase</li><li class="tag">PostgreSQL</li>
    </ul>
  </div>
</article>

<!-- 2 -->
<article class="project-card project-card--noimage" data-category="pro web">
  <div class="project-card__thumb" aria-hidden="true"><span class="project-card__mono">DAICE</span></div>
  <div class="project-card__body">
    <div class="project-card__head">
      <h3 class="project-card__title">DAICE — CEPICI</h3>
      <span class="badge badge--pro">Projet professionnel</span>
    </div>
    <p class="project-card__text">
      Plateforme de promotion des investissements pour le CEPICI, en Côte
      d'Ivoire. Gestion de dossiers et de procédures administratives.
    </p>
    <ul class="tag-list">
      <li class="tag">Angular</li><li class="tag">Spring Boot</li><li class="tag">Keycloak</li>
    </ul>
  </div>
</article>

<!-- 4 -->
<article class="project-card project-card--noimage" data-category="mobile">
  <div class="project-card__thumb" aria-hidden="true"><span class="project-card__mono">E-W</span></div>
  <div class="project-card__body">
    <div class="project-card__head">
      <h3 class="project-card__title">E-Wari</h3>
      <span class="badge">Projet personnel</span>
    </div>
    <p class="project-card__text">
      Application de gestion des finances personnelles pensée pour les jeunes
      d'Afrique de l'Ouest. Conception complète menée à terme : diagrammes UML
      détaillés, cahier des charges, architecture technique, documentation
      centralisée.
    </p>
    <ul class="tag-list">
      <li class="tag">Flutter</li><li class="tag">Spring Boot</li><li class="tag">PostgreSQL</li>
    </ul>
  </div>
</article>

<!-- 5 -->
<article class="project-card project-card--noimage" data-category="pro mobile">
  <div class="project-card__thumb" aria-hidden="true"><span class="project-card__mono">KEL</span></div>
  <div class="project-card__body">
    <div class="project-card__head">
      <h3 class="project-card__title">KEL</h3>
      <span class="badge badge--pro">Projet professionnel</span>
    </div>
    <p class="project-card__text">
      Application mobile de gestion de livraison permettant le suivi des
      commandes et des courses. Réalisée avec Flutter chez Switch Maker.
    </p>
    <ul class="tag-list">
      <li class="tag">Flutter</li><li class="tag">Dart</li><li class="tag">API REST</li>
    </ul>
  </div>
</article>

<!-- 6 -->
<article class="project-card project-card--noimage" data-category="pro mobile">
  <div class="project-card__thumb" aria-hidden="true"><span class="project-card__mono">LON</span></div>
  <div class="project-card__body">
    <div class="project-card__head">
      <h3 class="project-card__title">LONIA</h3>
      <span class="badge badge--pro">Projet professionnel</span>
    </div>
    <p class="project-card__text">
      Application mobile d'apprentissage en ligne, réalisée avec Flutter chez
      Switch Maker.
    </p>
    <ul class="tag-list">
      <li class="tag">Flutter</li><li class="tag">Dart</li>
    </ul>
  </div>
</article>

<!-- 7 -->
<article class="project-card project-card--noimage" data-category="academique web">
  <div class="project-card__thumb" aria-hidden="true"><span class="project-card__mono">DAO</span></div>
  <div class="project-card__body">
    <div class="project-card__head">
      <h3 class="project-card__title">Plateforme de gestion des DAO</h3>
      <span class="badge badge--academic">Projet de fin d'études</span>
    </div>
    <p class="project-card__text">
      Application d'analyse des dossiers d'appel d'offres avec suivi de la
      progression en temps réel, permissions par rôle (administrateur,
      rédacteur, relecteur, observateur) et architecture complète, du frontend
      jusqu'au microservice d'intelligence artificielle.
    </p>
    <ul class="tag-list">
      <li class="tag">Angular</li><li class="tag">Spring Boot</li><li class="tag">FastAPI</li>
      <li class="tag">Keycloak</li><li class="tag">PostgreSQL</li>
    </ul>
  </div>
</article>
```

- [ ] **Étape 3 : ajouter les trois cartes illustrées**

La carte 3 (Luxonera) s'insère **entre** DAICE et E-Wari. Les cartes 8 et 9 vont en fin de grille.

```html
<!-- 3 : à placer entre DAICE et E-Wari -->
<article class="project-card" data-category="web">
  <div class="project-card__thumb">
    <picture>
      <source srcset="images/optimized/luxonera.webp" type="image/webp" />
      <img src="images/optimized/luxonera.png" alt="Interface de la plateforme Luxonera"
           width="1200" height="563" loading="lazy" />
    </picture>
  </div>
  <div class="project-card__body">
    <div class="project-card__head">
      <h3 class="project-card__title">Luxonera</h3>
      <span class="badge badge--live">En ligne</span>
    </div>
    <p class="project-card__text">
      Plateforme e-commerce de montres de luxe pour le marché burkinabè, avec
      prise de commande via WhatsApp.
    </p>
    <ul class="tag-list">
      <li class="tag">Next.js</li><li class="tag">Three.js</li>
    </ul>
    <a class="project-card__link" href="https://luxonera-app.vercel.app/"
       target="_blank" rel="noopener noreferrer">
      Voir le site
      <svg class="icon" aria-hidden="true"><use href="#i-external" /></svg>
    </a>
  </div>
</article>

<!-- 8 : fin de grille -->
<article class="project-card" data-category="web">
  <div class="project-card__thumb">
    <picture>
      <source srcset="images/optimized/etrack.webp" type="image/webp" />
      <img src="images/optimized/etrack.png" alt="Tableau de bord de l'application eTrack"
           width="1200" height="675" loading="lazy" />
    </picture>
  </div>
  <div class="project-card__body">
    <div class="project-card__head">
      <h3 class="project-card__title">eTrack</h3>
      <span class="badge">Projet personnel</span>
    </div>
    <p class="project-card__text">
      Application de suivi des dépenses et de gestion financière personnelle,
      avec tableaux de bord pour visualiser les habitudes de consommation.
    </p>
    <ul class="tag-list"><li class="tag">Next.js</li></ul>
  </div>
</article>

<!-- 9 : fin de grille -->
<article class="project-card" data-category="academique web">
  <div class="project-card__thumb">
    <picture>
      <source srcset="images/optimized/hotellerie.webp" type="image/webp" />
      <img src="images/optimized/hotellerie.png" alt="Interface de la plateforme hôtelière"
           width="1200" height="606" loading="lazy" />
    </picture>
  </div>
  <div class="project-card__body">
    <div class="project-card__head">
      <h3 class="project-card__title">Plateforme hôtelière</h3>
      <span class="badge badge--academic">Projet académique</span>
    </div>
    <p class="project-card__text">
      Application de gestion des réservations et des services d'un
      établissement hôtelier.
    </p>
    <ul class="tag-list"><li class="tag">Java</li><li class="tag">MySQL</li></ul>
  </div>
</article>
```

- [ ] **Étape 4 : écrire `js/filters.js`**

```js
/**
 * Filtrage des projets par catégorie.
 * Masque via l'attribut `hidden` plutôt que `display:none` en CSS :
 * les lecteurs d'écran ignorent alors réellement les cartes filtrées.
 */
export function initFilters() {
  const grid = document.querySelector("#project-grid");
  const buttons = document.querySelectorAll(".filter");
  const status = document.querySelector("#filters-status");
  if (!grid || !buttons.length) return;

  const cards = [...grid.querySelectorAll(".project-card")];

  const apply = (filter) => {
    let visible = 0;
    cards.forEach((card) => {
      const categories = (card.dataset.category || "").split(/\s+/);
      const show = filter === "all" || categories.includes(filter);
      card.hidden = !show;
      if (show) visible += 1;
    });
    status.textContent =
      visible > 1 ? `${visible} projets affichés` : `${visible} projet affiché`;
  };

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => {
        b.classList.remove("is-active");
        b.setAttribute("aria-pressed", "false");
      });
      btn.classList.add("is-active");
      btn.setAttribute("aria-pressed", "true");
      apply(btn.dataset.filter);
    });
  });
}
```

- [ ] **Étape 5 : câbler dans `js/main.js`**

```js
import { initTheme, toggleTheme } from "./theme.js";
import { initNav } from "./nav.js";
import { initFilters } from "./filters.js";

initTheme();
initNav();
initFilters();

document.querySelector("#theme-toggle").addEventListener("click", toggleTheme);
```

- [ ] **Étape 6 : styliser dans `css/layout.css`**

```css
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-6);
}
```

- [ ] **Étape 7 : styliser dans `css/components.css`**

```css
/* ---------- Filtres ---------- */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-8);
}

.filter {
  padding: 0.5em 1.2em;
  border-radius: var(--radius-full);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  font-size: var(--fs-sm);
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s, background 0.2s, border-color 0.2s;
}

.filter:hover {
  color: var(--accent);
  border-color: var(--accent);
}

.filter.is-active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--accent-contrast);
}

/* ---------- Carte projet ---------- */
.project-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  transition: transform 0.3s var(--ease-out), border-color 0.3s,
    box-shadow 0.3s;
}

.project-card[hidden] {
  display: none;
}

.project-card:hover {
  transform: translateY(-6px);
  border-color: var(--accent);
  box-shadow: var(--shadow-lg);
}

.project-card__thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: var(--surface-2);
}

.project-card__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s var(--ease-out);
}

.project-card:hover .project-card__thumb img {
  transform: scale(1.06);
}

/* Carte sans capture : dégradé + monogramme */
.project-card--noimage .project-card__thumb {
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
}

.project-card__mono {
  font-family: var(--font-mono);
  font-size: clamp(2rem, 6vw, 3rem);
  font-weight: 500;
  letter-spacing: 0.05em;
  color: #fff;
  opacity: 0.92;
}

.project-card__body {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  padding: var(--space-6);
}

.project-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.project-card__title {
  font-size: var(--fs-lg);
}

.project-card__text {
  font-size: var(--fs-sm);
  color: var(--text-muted);
  flex-grow: 1;
  margin-bottom: var(--space-4);
}

.project-card__link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-4);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--accent);
}

.project-card__link:hover {
  text-decoration: underline;
}

/* ---------- Badges de statut ---------- */
.badge {
  flex-shrink: 0;
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  padding: 0.3em 0.7em;
  border-radius: var(--radius-full);
  background: var(--surface-2);
  color: var(--text-muted);
  white-space: nowrap;
}

.badge--live {
  background: rgba(22, 163, 74, 0.12);
  color: #15803d;
}

[data-theme="dark"] .badge--live {
  background: rgba(74, 222, 128, 0.16);
  color: #4ade80;
}

.badge--pro,
.badge--wip {
  background: var(--accent-soft);
  color: var(--accent);
}

.badge--academic {
  background: rgba(217, 119, 6, 0.12);
  color: #b45309;
}

[data-theme="dark"] .badge--academic {
  background: rgba(251, 191, 36, 0.16);
  color: #fbbf24;
}
```

- [ ] **Étape 8 : vérifier l'ordre — le point critique**

Dans la console du navigateur :

```js
[...document.querySelectorAll(".project-card__title")].map(e => e.textContent.trim())
```

Attendu, **exactement** :

```
["SIG — Système Intégré de Gestion", "DAICE — CEPICI", "Luxonera", "E-Wari",
 "KEL", "LONIA", "Plateforme de gestion des DAO", "eTrack", "Plateforme hôtelière"]
```

Neuf entrées, dans cet ordre. Toute divergence est un échec de la tâche.

- [ ] **Étape 9 : vérifier l'absence des projets retirés**

```js
document.body.textContent.match(/Forkify|Bankist|colis|transport/i)
```

Attendu : `null`.

- [ ] **Étape 10 : vérifier les filtres**

1. Cliquer sur « Mobile » — attendu : 3 cartes visibles (E-Wari, KEL, LONIA).
2. Cliquer sur « Professionnels » — attendu : 4 cartes (SIG, DAICE, KEL, LONIA).
3. Cliquer sur « Académiques » — attendu : 2 cartes (DAO, Plateforme hôtelière).
4. Cliquer sur « Tous » — attendu : 9 cartes.
5. Naviguer aux filtres au clavier et activer avec Entrée — attendu : le filtre s'applique, `aria-pressed` bascule.
6. Les six cartes sans capture affichent leur monogramme sur dégradé indigo, aucune n'a de bouton de lien.
7. Seul Luxonera affiche « Voir le site ».

- [ ] **Étape 11 : commit**

```bash
git add index.html css/ js/
git commit -m "feat: section Projets avec 9 projets ordonnes et filtres par categorie"
```

---

## Tâche 10 : Compétences et Formation

**Fichiers :**
- Modifier : `index.html`, `css/components.css`

**Interfaces :**
- Consomme : `.card`, `.tag-list` (Tâches 7 et 8)
- Produit : `#competences`, `#formation`, `.marquee__track` — cible de l'animation (Tâche 12)

- [ ] **Étape 1 : ajouter la section Compétences**

```html
<section class="section" id="competences">
  <div class="container">
    <p class="eyebrow">Stack</p>
    <h2 class="section-title">Mes <span>compétences</span></h2>
    <p class="section-lead">
      Les technologies que j'utilise au quotidien, du front-end à
      l'infrastructure.
    </p>

    <div class="skills-grid">
      <article class="skill-block">
        <h3 class="skill-block__title">Langages & Frameworks</h3>
        <ul class="tag-list">
          <li class="tag">Angular</li><li class="tag">Spring Boot</li>
          <li class="tag">Flutter (Dart)</li><li class="tag">Next.js</li>
          <li class="tag">JavaScript</li><li class="tag">TypeScript</li>
          <li class="tag">Python</li><li class="tag">Java</li>
        </ul>
      </article>

      <article class="skill-block">
        <h3 class="skill-block__title">Architecture & Méthodes</h3>
        <ul class="tag-list">
          <li class="tag">Architecture logicielle</li><li class="tag">Modélisation UML</li>
          <li class="tag">Méthodologie Agile</li><li class="tag">API REST</li>
          <li class="tag">Microservices</li>
        </ul>
      </article>

      <article class="skill-block">
        <h3 class="skill-block__title">Intelligence artificielle</h3>
        <ul class="tag-list">
          <li class="tag">Intégration de modèles via API</li>
          <li class="tag">FastAPI</li><li class="tag">Python</li>
          <li class="tag">Développement assisté par IA</li>
        </ul>
      </article>

      <article class="skill-block">
        <h3 class="skill-block__title">Outils & Infrastructure</h3>
        <ul class="tag-list">
          <li class="tag">Git</li><li class="tag">GitHub</li><li class="tag">GitLab</li>
          <li class="tag">Docker</li><li class="tag">Odoo</li><li class="tag">Metabase</li>
          <li class="tag">MySQL</li><li class="tag">PostgreSQL</li>
          <li class="tag">Swagger</li><li class="tag">Keycloak</li>
        </ul>
      </article>

      <article class="skill-block">
        <h3 class="skill-block__title">CMS</h3>
        <ul class="tag-list"><li class="tag">Drupal (formation en cours)</li></ul>
      </article>

      <article class="skill-block">
        <h3 class="skill-block__title">Langues</h3>
        <ul class="tag-list">
          <li class="tag">Français — langue maternelle</li>
          <li class="tag">Anglais — intermédiaire B2</li>
        </ul>
      </article>
    </div>

    <div class="marquee" aria-hidden="true">
      <div class="marquee__track" id="marquee-track">
        <!-- Dupliqué une fois pour la boucle sans couture -->
        <span class="marquee__item">Angular</span><span class="marquee__item">Spring Boot</span>
        <span class="marquee__item">Flutter</span><span class="marquee__item">Next.js</span>
        <span class="marquee__item">TypeScript</span><span class="marquee__item">Python</span>
        <span class="marquee__item">Docker</span><span class="marquee__item">PostgreSQL</span>
        <span class="marquee__item">Keycloak</span><span class="marquee__item">FastAPI</span>
        <span class="marquee__item">Odoo</span><span class="marquee__item">Metabase</span>
        <span class="marquee__item">Angular</span><span class="marquee__item">Spring Boot</span>
        <span class="marquee__item">Flutter</span><span class="marquee__item">Next.js</span>
        <span class="marquee__item">TypeScript</span><span class="marquee__item">Python</span>
        <span class="marquee__item">Docker</span><span class="marquee__item">PostgreSQL</span>
        <span class="marquee__item">Keycloak</span><span class="marquee__item">FastAPI</span>
        <span class="marquee__item">Odoo</span><span class="marquee__item">Metabase</span>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Étape 2 : ajouter la section Formation**

```html
<section class="section section--surface" id="formation">
  <div class="container">
    <p class="eyebrow">Bagage</p>
    <h2 class="section-title">Formation & <span>certifications</span></h2>

    <div class="card-grid">
      <article class="card">
        <svg class="card__icon" aria-hidden="true"><use href="#i-graduation" /></svg>
        <h3 class="card__title">Licence Informatique</h3>
        <p class="card__text">Formation initiale en informatique.</p>
      </article>

      <article class="card">
        <svg class="card__icon" aria-hidden="true"><use href="#i-code" /></svg>
        <h3 class="card__title">CMS Drupal</h3>
        <p class="card__text">Formation en cours.</p>
        <span class="badge badge--wip">En cours</span>
      </article>

      <article class="card">
        <svg class="card__icon" aria-hidden="true"><use href="#i-sparkle" /></svg>
        <h3 class="card__title">Python, Bases de données & IA</h3>
        <p class="card__text">Certificats délivrés par Coursera.</p>
      </article>

      <article class="card">
        <svg class="card__icon" aria-hidden="true"><use href="#i-check" /></svg>
        <h3 class="card__title">Marketing Digital</h3>
        <p class="card__text">Certificat délivré par Force N.</p>
      </article>

      <article class="card">
        <svg class="card__icon" aria-hidden="true"><use href="#i-server" /></svg>
        <h3 class="card__title">Spring Boot & Angular</h3>
        <p class="card__text">Formation dispensée par Switch Maker.</p>
      </article>
    </div>
  </div>
</section>
```

- [ ] **Étape 3 : styliser dans `css/components.css`**

```css
/* ---------- Compétences ---------- */
.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-8);
  margin-bottom: var(--space-16);
}

.skill-block__title {
  font-size: var(--fs-base);
  font-weight: 600;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--border);
}

/* ---------- Marquee ---------- */
.marquee {
  overflow: hidden;
  padding-block: var(--space-4);
  -webkit-mask-image: linear-gradient(to right, transparent, #000 12%, #000 88%, transparent);
  mask-image: linear-gradient(to right, transparent, #000 12%, #000 88%, transparent);
}

.marquee__track {
  display: flex;
  gap: var(--space-8);
  width: max-content;
  will-change: transform;
}

.marquee__item {
  font-family: var(--font-mono);
  font-size: var(--fs-lg);
  color: var(--text-muted);
  opacity: 0.55;
  white-space: nowrap;
}
```

- [ ] **Étape 4 : vérifier**

1. Zéro erreur console.
2. Les six blocs de compétences s'affichent, avec 27 étiquettes au total (`document.querySelectorAll('.skill-block .tag').length` → `27`).
3. Le marquee affiche 24 éléments (12 × 2) — le défilement arrive en Tâche 12, il est immobile pour l'instant.
4. Les cinq cartes de formation s'affichent, Drupal porte le badge « En cours ».
5. `aria-hidden="true"` est bien présent sur `.marquee` : son contenu duplique les étiquettes déjà lues au-dessus, un lecteur d'écran ne doit pas les répéter.

- [ ] **Étape 5 : commit**

```bash
git add index.html css/components.css
git commit -m "feat: sections Compétences et Formation & certifications"
```

---

## Tâche 11 : Contact, page de remerciement et pied de page

**Fichiers :**
- Modifier : `index.html`, `css/layout.css`, `css/components.css`
- Créer : `merci.html`

**Interfaces :**
- Consomme : le sprite (Tâche 5), `css/base.css` (Tâche 4)
- Produit : `#contact`, `footer`, `merci.html`

- [ ] **Étape 1 : ajouter la section Contact**

L'attribut `_next` doit pointer vers l'URL **absolue** de production : FormSubmit exige une URL complète, une valeur relative est rejetée.

```html
<section class="section" id="contact">
  <div class="container contact">
    <div class="contact__intro">
      <p class="eyebrow">Contact</p>
      <h2 class="section-title">Travaillons <span>ensemble</span></h2>
      <p class="section-lead">
        Une opportunité, une collaboration ou une question ? Écrivez-moi, je
        réponds rapidement.
      </p>

      <ul class="contact__list">
        <li>
          <svg class="icon" aria-hidden="true"><use href="#i-mail" /></svg>
          <a href="mailto:sawadogosharif20@gmail.com">sawadogosharif20@gmail.com</a>
        </li>
        <li>
          <svg class="icon" aria-hidden="true"><use href="#i-phone" /></svg>
          <a href="tel:+22677468876">+226 77 46 88 76</a>
        </li>
        <li>
          <svg class="icon" aria-hidden="true"><use href="#i-pin" /></svg>
          <span>Nagrin, Ouagadougou — Burkina Faso</span>
        </li>
        <li>
          <svg class="icon" aria-hidden="true"><use href="#i-github" /></svg>
          <a href="https://github.com/Oursdingo" target="_blank" rel="noopener noreferrer">github.com/Oursdingo</a>
        </li>
      </ul>
    </div>

    <form class="contact__form" action="https://formsubmit.co/sawadogosharif20@gmail.com" method="POST">
      <input type="hidden" name="_subject" value="Nouveau message depuis votre portfolio" />
      <input type="hidden" name="_captcha" value="false" />
      <input type="hidden" name="_template" value="table" />
      <input type="hidden" name="_next" value="https://portofolio-jade-mu.vercel.app/merci.html" />

      <div class="field-row">
        <p class="field">
          <label class="field__label" for="nom">Nom</label>
          <input class="field__input" type="text" id="nom" name="nom" required autocomplete="name" />
        </p>
        <p class="field">
          <label class="field__label" for="email">Email</label>
          <input class="field__input" type="email" id="email" name="email" required autocomplete="email" />
        </p>
      </div>

      <div class="field-row">
        <p class="field">
          <label class="field__label" for="telephone">Téléphone <span class="field__optional">(facultatif)</span></label>
          <input class="field__input" type="tel" id="telephone" name="telephone" autocomplete="tel" />
        </p>
        <p class="field">
          <label class="field__label" for="objet">Objet</label>
          <input class="field__input" type="text" id="objet" name="objet" required
                 placeholder="Collaboration, opportunité…" />
        </p>
      </div>

      <p class="field">
        <label class="field__label" for="message">Message</label>
        <textarea class="field__input" id="message" name="message" rows="6" required></textarea>
      </p>

      <button type="submit" class="btn btn--primary">Envoyer le message</button>
    </form>
  </div>
</section>
```

- [ ] **Étape 2 : ajouter le pied de page**

Après `</main>` :

```html
<footer class="footer">
  <div class="container footer__inner">
    <p class="footer__copy">© 2026 Sawadogo Adam Sharif. Tous droits réservés.</p>
    <ul class="social social--sm">
      <li><a href="https://github.com/Oursdingo" target="_blank" rel="noopener noreferrer" aria-label="GitHub"><svg class="icon" aria-hidden="true"><use href="#i-github" /></svg></a></li>
      <li><a href="https://www.linkedin.com/in/sharif-sawadogo-280197223/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><svg class="icon" aria-hidden="true"><use href="#i-linkedin" /></svg></a></li>
      <li><a href="https://wa.me/22677468876" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp"><svg class="icon" aria-hidden="true"><use href="#i-whatsapp" /></svg></a></li>
      <li><a href="https://x.com/SharifSawa51023" target="_blank" rel="noopener noreferrer" aria-label="X"><svg class="icon" aria-hidden="true"><use href="#i-x" /></svg></a></li>
    </ul>
  </div>
</footer>

<a href="#accueil" class="to-top" id="to-top" aria-label="Retour en haut de page">
  <svg class="icon" aria-hidden="true"><use href="#i-arrow-up" /></svg>
</a>
```

- [ ] **Étape 3 : créer `merci.html`**

```html
<!DOCTYPE html>
<html lang="fr" data-theme="light">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Message envoyé — Sawadogo Adam Sharif</title>
  <meta name="robots" content="noindex" />
  <script>
    (function () {
      var t = null;
      try { t = localStorage.getItem("theme"); } catch (e) {}
      if (t !== "dark" && t !== "light") {
        t = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }
      document.documentElement.setAttribute("data-theme", t);
    })();
  </script>
  <link rel="icon" href="favicon.svg" type="image/svg+xml" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="css/base.css" />
  <link rel="stylesheet" href="css/components.css" />
</head>

<body>
  <main class="thanks">
    <svg class="thanks__mark" viewBox="0 0 32 32" width="64" height="64" aria-hidden="true">
      <g fill="none" stroke="var(--logo-red)" stroke-width="2.6"
         stroke-linecap="round" stroke-linejoin="round">
        <path d="M11.5 10 L6.5 16 L11.5 22" />
        <path d="M19 9 L13 23" />
        <path d="M20.5 10 L25.5 16 L20.5 22" />
      </g>
    </svg>
    <h1 class="thanks__title">Message bien reçu</h1>
    <p class="thanks__text">
      Merci de m'avoir écrit. Je vous réponds dans les meilleurs délais.
    </p>
    <a href="index.html" class="btn btn--primary">Retour au portfolio</a>
  </main>

  <style>
    .thanks {
      min-height: 100vh;
      display: grid;
      place-content: center;
      justify-items: center;
      text-align: center;
      gap: var(--space-4);
      padding: var(--space-8);
    }
    .thanks__title { font-size: var(--fs-3xl); }
    .thanks__text { color: var(--text-muted); max-width: 44ch; }
    .thanks .btn { margin-top: var(--space-4); }
  </style>
</body>

</html>
```

- [ ] **Étape 4 : styliser dans `css/layout.css`**

```css
/* ---------- Contact ---------- */
.contact {
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  gap: var(--space-16);
  align-items: start;
}

.contact__list {
  display: grid;
  gap: var(--space-4);
}

.contact__list li {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--fs-sm);
  color: var(--text-muted);
}

.contact__list .icon {
  color: var(--accent);
}

.contact__list a:hover {
  color: var(--accent);
  text-decoration: underline;
}

/* ---------- Pied de page ---------- */
.footer {
  border-top: 1px solid var(--border);
  background: var(--surface);
  padding-block: var(--space-8);
}

.footer__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.footer__copy {
  font-size: var(--fs-sm);
  color: var(--text-muted);
}
```

- [ ] **Étape 5 : styliser dans `css/components.css`**

```css
/* ---------- Formulaire ---------- */
.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.field__label {
  font-size: var(--fs-sm);
  font-weight: 500;
}

.field__optional {
  color: var(--text-muted);
  font-weight: 400;
}

.field__input {
  width: 100%;
  padding: 0.85em 1em;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: var(--fs-sm);
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}

.field__input::placeholder {
  color: var(--text-muted);
  opacity: 0.7;
}

.field__input:focus {
  outline: none;
  border-color: var(--accent);
  background: var(--bg);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

textarea.field__input {
  resize: vertical;
  min-height: 140px;
}

/* ---------- Retour en haut ---------- */
.social--sm a {
  width: 38px;
  height: 38px;
}

.to-top {
  position: fixed;
  right: var(--space-6);
  bottom: var(--space-6);
  z-index: 90;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border-radius: var(--radius-full);
  background: var(--accent);
  color: var(--accent-contrast);
  box-shadow: var(--shadow-lg);
  opacity: 0;
  visibility: hidden;
  transform: translateY(12px);
  transition: opacity 0.3s var(--ease-out), transform 0.3s var(--ease-out),
    visibility 0.3s;
}

.to-top.is-visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}
```

- [ ] **Étape 6 : afficher le bouton de retour en haut**

Ajouter à la fin de `initNav()` dans `js/nav.js`, à l'intérieur de la fonction `onScroll` — juste avant `lastY = y;` :

```js
    document.querySelector("#to-top")?.classList.toggle("is-visible", y > 600);
```

- [ ] **Étape 7 : vérifier**

1. Zéro erreur console.
2. Chaque champ possède un `<label>` réellement associé — en console : `[...document.querySelectorAll('.field__input')].every(i => document.querySelector(`label[for="${i.id}"]`))` → `true`.
3. Cliquer sur un libellé place le focus dans le champ correspondant.
4. Le focus sur un champ produit une bordure d'accent et un halo.
5. Soumettre le formulaire vide : le navigateur bloque et signale les champs requis.
6. Ouvrir `merci.html` directement : la page s'affiche centrée, avec le logo `</>` rouge, et respecte le thème enregistré.
7. Descendre de plus de 600 px : le bouton de retour en haut apparaît. Cliquer : retour en haut de page.
8. L'email dans `action` est en **minuscules**.

- [ ] **Étape 8 : commit**

```bash
git add index.html merci.html css/ js/
git commit -m "feat: section Contact, page de remerciement et pied de page"
```

---

## Tâche 12 : Animations — GSAP, ScrollTrigger et Lenis

**Fichiers :**
- Créer : `js/animations.js`
- Modifier : `index.html`, `js/main.js`, `css/responsive.css`

**Interfaces :**
- Consomme : toutes les cibles produites par les Tâches 6 à 11
- Produit : `js/animations.js` exporte `initAnimations(): void`

- [ ] **Étape 1 : charger les librairies**

Dans `index.html`, juste avant `</head>`, **avant** le module `main.js` : GSAP doit exister sur `window` au moment où `animations.js` s'exécute.

```html
  <script defer src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/ScrollTrigger.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/lenis@1.1.20/dist/lenis.min.js"></script>
```

Vérifier que les trois URL répondent en 200 avant de continuer :

```bash
curl -sI https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.min.js | head -1
curl -sI https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/ScrollTrigger.min.js | head -1
curl -sI https://cdn.jsdelivr.net/npm/lenis@1.1.20/dist/lenis.min.js | head -1
```

Attendu : trois `HTTP/2 200`. Si une version n'existe plus, prendre la dernière `3.x` de GSAP et la dernière `1.x` de Lenis, et corriger les trois lignes.

- [ ] **Étape 2 : écrire `js/animations.js`**

```js
/**
 * Couche d'animation : Lenis (scroll fluide) + GSAP/ScrollTrigger.
 *
 * Tout est court-circuité si l'utilisateur demande un mouvement réduit.
 * Le contenu reste alors intégralement visible — jamais figé à opacité 0.
 */
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Effet machine à écrire. Remplace Typed.js (~12 Ko) par 20 lignes. */
function typewriter(el) {
  const words = (el.dataset.roles || "").split("|").filter(Boolean);
  if (words.length < 2) return;

  let wordIndex = 0;
  let charCount = words[0].length;
  let deleting = true;

  const tick = () => {
    const word = words[wordIndex];
    charCount += deleting ? -1 : 1;
    el.textContent = word.slice(0, charCount);

    let delay = deleting ? 45 : 90;
    if (!deleting && charCount === word.length) {
      deleting = true;
      delay = 1800;
    } else if (deleting && charCount === 0) {
      deleting = false;
      wordIndex = (wordIndex + 1) % words.length;
      delay = 300;
    }
    setTimeout(tick, delay);
  };

  setTimeout(tick, 2200);
}

function initLenis() {
  const lenis = new window.Lenis({ duration: 1.1, smoothWheel: true });
  lenis.on("scroll", window.ScrollTrigger.update);
  window.gsap.ticker.add((time) => lenis.raf(time * 1000));
  window.gsap.ticker.lagSmoothing(0);
  // Les ancres passent par Lenis, sinon le scroll natif et Lenis se disputent.
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const target = document.querySelector(a.getAttribute("href"));
      if (!target) return;
      e.preventDefault();
      lenis.scrollTo(target, { offset: -72 });
    });
  });
}

export function initAnimations() {
  const role = document.querySelector(".hero__role");
  if (role && !reduced) typewriter(role);

  if (reduced) {
    // Aucune animation. Le contenu est déjà visible : rien à révéler.
    return;
  }

  const { gsap, ScrollTrigger } = window;
  if (!gsap || !ScrollTrigger) {
    console.warn("GSAP indisponible — le site reste entièrement utilisable.");
    return;
  }
  gsap.registerPlugin(ScrollTrigger);
  initLenis();

  // --- Barre de progression ---
  gsap.to("#scroll-progress", {
    scaleX: 1,
    ease: "none",
    scrollTrigger: { trigger: document.body, start: "top top", end: "bottom bottom", scrub: 0.3 },
  });

  // --- Cascade du hero ---
  gsap.from(
    ".hero__content > *",
    { y: 28, opacity: 0, duration: 0.8, stagger: 0.09, ease: "power3.out", delay: 0.15 }
  );
  gsap.from(".hero__visual", { scale: 0.94, opacity: 0, duration: 1, ease: "power3.out", delay: 0.3 });

  // --- Révélation des sections ---
  gsap.utils.toArray(".section > .container > *, .stats__grid").forEach((el) => {
    gsap.from(el, {
      y: 32,
      opacity: 0,
      duration: 0.7,
      ease: "power3.out",
      scrollTrigger: { trigger: el, start: "top 88%", once: true },
    });
  });

  // --- Compteurs de statistiques ---
  gsap.utils.toArray(".stat__value").forEach((el) => {
    const target = Number(el.dataset.countTo);
    const suffix = el.dataset.suffix || "";
    const counter = { value: 0 };
    gsap.to(counter, {
      value: target,
      duration: 1.6,
      ease: "power2.out",
      scrollTrigger: { trigger: el, start: "top 92%", once: true },
      onUpdate: () => {
        el.textContent = Math.round(counter.value) + suffix;
      },
    });
  });

  // --- Ligne de timeline qui se dessine ---
  const line = document.querySelector(".timeline__line");
  if (line) {
    gsap.fromTo(
      line,
      { scaleY: 0 },
      {
        scaleY: 1,
        ease: "none",
        scrollTrigger: { trigger: ".timeline", start: "top 75%", end: "bottom 85%", scrub: 0.5 },
      }
    );
  }

  // --- Cartes projet en cascade ---
  gsap.from(".project-card", {
    y: 36,
    opacity: 0,
    duration: 0.6,
    stagger: 0.06,
    ease: "power3.out",
    scrollTrigger: { trigger: "#project-grid", start: "top 85%", once: true },
  });

  // --- Marquee ---
  const track = document.querySelector("#marquee-track");
  if (track) {
    // La liste est dupliquée : décaler de la moitié boucle sans couture.
    gsap.to(track, {
      xPercent: -50,
      duration: 26,
      ease: "none",
      repeat: -1,
    });
  }

  // --- Surbrillance de la section active ---
  // Remplace l'écouteur `scroll` manuel : ScrollTrigger ne recalcule
  // pas la position de chaque section à chaque pixel défilé.
  document.querySelectorAll(".nav__link").forEach((link) => {
    const id = link.getAttribute("href");
    const section = document.querySelector(id);
    if (!section) return;

    const setActive = () => {
      document.querySelectorAll(".nav__link").forEach((l) => l.classList.remove("is-active"));
      link.classList.add("is-active");
    };

    ScrollTrigger.create({
      trigger: section,
      start: "top 45%",
      end: "bottom 45%",
      onEnter: setActive,
      onEnterBack: setActive,
    });
  });
}
```

- [ ] **Étape 3 : câbler dans `js/main.js`**

```js
import { initTheme, toggleTheme } from "./theme.js";
import { initNav } from "./nav.js";
import { initFilters } from "./filters.js";
import { initAnimations } from "./animations.js";

initTheme();
initNav();
initFilters();

document.querySelector("#theme-toggle").addEventListener("click", toggleTheme);

// GSAP et Lenis sont chargés en `defer` : ils ne sont prêts qu'au DOMContentLoaded.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initAnimations);
} else {
  initAnimations();
}
```

- [ ] **Étape 4 : figer le marquee en mouvement réduit**

Ajouter dans `css/responsive.css` :

```css
@media (prefers-reduced-motion: reduce) {
  .marquee__track {
    transform: none !important;
  }
  .hero__caret {
    animation: none;
  }
}
```

- [ ] **Étape 5 : vérifier les animations**

1. `read_console_messages` — zéro erreur.
2. Au chargement : les éléments du hero apparaissent en cascade, le portrait en fondu et léger zoom.
3. Après ~2 s, le titre du hero commence à se réécrire : « Développeur Full Stack » → « Développeur Mobile Flutter » → « Architecte logiciel » → « Intégrateur de modèles IA », en boucle.
4. La barre de progression en haut se remplit au scroll et atteint la largeur pleine en bas de page.
5. En atteignant les statistiques, les quatre compteurs montent de 0 à leur valeur, et s'arrêtent sur `3+`, `10+`, `2`, `20+`.
6. La ligne de la timeline se dessine du haut vers le bas à mesure qu'on descend.
7. Le marquee défile en continu et **boucle sans saut visible**.
8. Le lien de navigation actif change au fil des sections.
9. Le scroll est perceptiblement plus doux qu'un scroll natif.
10. Cliquer sur un lien de navigation : défilement animé, sans que la section finisse cachée sous l'en-tête.

- [ ] **Étape 6 : vérifier le mouvement réduit**

Activer l'émulation `prefers-reduced-motion: reduce` dans les outils de développement (Rendering → Emulate CSS media feature), puis recharger.

1. Le scroll redevient **natif**, pas fluidifié.
2. Tout le contenu est **visible immédiatement** — aucune section ne reste invisible faute d'animation déclenchée. C'est le piège classique : une révélation qui part d'`opacity: 0` en CSS laisse la page vide quand l'animation est désactivée. Ici l'opacité de départ est posée par GSAP, jamais par le CSS.
3. Le marquee est figé.
4. Le titre du hero affiche « Développeur Full Stack » en fixe, sans réécriture.
5. Le curseur clignotant ne clignote pas.

- [ ] **Étape 7 : vérifier la résistance à une panne de CDN**

Dans l'onglet réseau, bloquer le domaine `cdn.jsdelivr.net`, puis recharger.

Attendu : un avertissement en console, **et la page reste entièrement lisible et navigable** — tout le contenu visible, la navigation fonctionnelle, les filtres opérationnels.

- [ ] **Étape 8 : commit**

```bash
git add index.html css/responsive.css js/
git commit -m "feat: animations GSAP + ScrollTrigger + Lenis (remplace ScrollReveal et Typed.js)"
```

---

## Tâche 13 : SEO et métadonnées de partage

**Fichiers :**
- Modifier : `index.html`

**Interfaces :**
- Consomme : `images/og-image.png`, `favicon.svg` (Tâche 3)
- Produit : rien de consommé par les tâches suivantes

- [ ] **Étape 1 : ajouter les métadonnées**

Dans `<head>`, après le `<title>` :

```html
  <meta name="description" content="Sawadogo Adam Sharif — Développeur Full Stack web et mobile à Ouagadougou. Angular, Spring Boot, Flutter, Next.js. Plus de 3 ans d'expérience, intégration de modèles IA via API." />
  <meta name="author" content="Sawadogo Adam Sharif" />
  <link rel="canonical" href="https://portofolio-jade-mu.vercel.app/" />
  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#0b0d12" media="(prefers-color-scheme: dark)" />

  <meta property="og:type" content="website" />
  <meta property="og:locale" content="fr_FR" />
  <meta property="og:url" content="https://portofolio-jade-mu.vercel.app/" />
  <meta property="og:title" content="Sawadogo Adam Sharif — Développeur Full Stack, Web & Mobile" />
  <meta property="og:description" content="Développeur Full Stack web et mobile à Ouagadougou. Angular, Spring Boot, Flutter, Next.js et intégration de modèles IA." />
  <meta property="og:image" content="https://portofolio-jade-mu.vercel.app/images/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Sawadogo Adam Sharif — Développeur Full Stack, Web & Mobile" />
  <meta name="twitter:description" content="Développeur Full Stack web et mobile à Ouagadougou. Angular, Spring Boot, Flutter, Next.js et intégration de modèles IA." />
  <meta name="twitter:image" content="https://portofolio-jade-mu.vercel.app/images/og-image.png" />
```

- [ ] **Étape 2 : ajouter le JSON-LD**

Juste avant `</body>` :

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Sawadogo Adam Sharif",
  "jobTitle": "Développeur Full Stack, Web & Mobile",
  "email": "mailto:sawadogosharif20@gmail.com",
  "telephone": "+22677468876",
  "url": "https://portofolio-jade-mu.vercel.app/",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Ouagadougou",
    "addressCountry": "BF"
  },
  "worksFor": { "@type": "Organization", "name": "Switch Maker" },
  "alumniOf": { "@type": "EducationalOrganization", "name": "Licence Informatique" },
  "knowsLanguage": ["fr", "en"],
  "knowsAbout": [
    "Angular", "Spring Boot", "Flutter", "Next.js", "TypeScript",
    "Python", "FastAPI", "Docker", "PostgreSQL", "Keycloak", "UML"
  ],
  "sameAs": [
    "https://github.com/Oursdingo",
    "https://www.linkedin.com/in/sharif-sawadogo-280197223/",
    "https://x.com/SharifSawa51023"
  ]
}
</script>
```

- [ ] **Étape 3 : vérifier la structure des titres**

En console :

```js
[...document.querySelectorAll("h1,h2,h3")].map(h => h.tagName + " " + h.textContent.trim().slice(0, 45))
```

Attendu : **un seul `H1`** (« Sawadogo Adam Sharif »), puis des `H2` de section, puis des `H3`. Aucun `H3` n'apparaît avant le premier `H2`.

- [ ] **Étape 4 : vérifier le JSON-LD**

En console :

```js
JSON.parse(document.querySelector('script[type="application/ld+json"]').textContent)
```

Attendu : un objet analysé sans erreur, `@type` valant `"Person"`.

- [ ] **Étape 5 : commit**

```bash
git add index.html
git commit -m "feat: metadonnees SEO, Open Graph et JSON-LD Person"
```

---

## Tâche 14 : Responsive, accessibilité et vérification finale

**Fichiers :**
- Modifier : `css/responsive.css`
- Supprimer : `style.css`, `app.js`

**Interfaces :**
- Consomme : tout ce qui précède
- Produit : le site livrable

- [ ] **Étape 1 : écrire `css/responsive.css`**

Conserver le bloc `prefers-reduced-motion` déjà présent (Tâche 12) et ajouter au-dessus :

```css
/* ============================================================
   responsive.css — points de rupture
   ============================================================ */

@media (max-width: 1024px) {
  .hero__inner,
  .about,
  .contact {
    grid-template-columns: 1fr;
    gap: var(--space-12);
  }

  .hero__visual,
  .about__visual {
    max-width: 420px;
    margin-inline: auto;
  }

  .stats__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-8) var(--space-4);
  }
}

@media (max-width: 860px) {
  .burger {
    display: inline-flex;
  }

  .nav {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    padding: var(--space-4) var(--space-6) var(--space-6);
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    box-shadow: var(--shadow-lg);
    display: none;
  }

  .nav.is-open {
    display: flex;
  }

  .nav__link {
    padding-block: var(--space-4);
    font-size: var(--fs-base);
    border-bottom: 1px solid var(--border);
  }

  .nav__link::after {
    display: none;
  }

  .nav__link.is-active {
    color: var(--accent);
  }

  .section {
    padding-block: var(--space-16);
  }
}

@media (max-width: 640px) {
  .container {
    padding-inline: var(--space-4);
  }

  .field-row {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .hero {
    padding-block: var(--space-16) var(--space-12);
  }

  .hero__actions .btn {
    width: 100%;
  }

  .project-grid,
  .card-grid,
  .skills-grid {
    grid-template-columns: 1fr;
  }

  .timeline {
    padding-left: var(--space-8);
  }

  .timeline__dot {
    left: calc(var(--space-8) * -1);
  }

  .footer__inner {
    flex-direction: column;
    text-align: center;
  }

  .to-top {
    right: var(--space-4);
    bottom: var(--space-4);
  }
}

@media (max-width: 400px) {
  .stats__grid {
    grid-template-columns: 1fr;
  }

  .logo__text {
    font-size: var(--fs-base);
  }
}
```

- [ ] **Étape 2 : vérifier le responsive**

Tester à **320, 375, 768, 1024, 1440 et 2560 px** de large. À chaque largeur :

1. Aucun défilement horizontal — en console : `document.documentElement.scrollWidth <= window.innerWidth` → `true`.
2. Aucun texte tronqué ni superposé.
3. Sous 860 px : le burger est visible, la navigation horizontale masquée.
4. Le menu mobile s'ouvre, se ferme au clic sur un lien et à la touche Échap.

- [ ] **Étape 3 : supprimer les anciens fichiers**

Leur contenu a été intégralement repris.

```bash
git rm style.css app.js
```

- [ ] **Étape 4 : vérifier qu'ils ne sont plus référencés**

```bash
grep -rn "style.css\|app.js\|boxicons\|scrollreveal\|typed" index.html merci.html css/ js/
```

Attendu : **aucun résultat**. Toute occurrence est une référence morte à corriger.

- [ ] **Étape 5 : lancer les vérificateurs**

```bash
python scripts/check_contrast.py
python scripts/check_budget.py
```

Attendu : les deux réussissent, code de sortie 0. `check_budget.py` doit afficher un total **sous 800 Ko** — c'est le passage au vert du rouge posé en Tâche 1.

- [ ] **Étape 6 : vérification finale complète**

1. **Console** : zéro erreur, zéro 404, sur `index.html` **et** `merci.html`.
2. **Ordre des projets** : relancer la vérification de la Tâche 9 étape 8 — les neuf titres, dans l'ordre imposé.
3. **Projets retirés** : `document.body.textContent.match(/Forkify|Bankist/i)` → `null`.
4. **Session vierge** : vider `localStorage`, recharger — la page s'ouvre dans le mode du **système**, clair si le système n'exprime rien.
5. **Persistance** : passer en sombre, recharger — reste en sombre, sans flash blanc.
6. **Lighthouse** (mode navigation privée, profil mobile) : Performance ≥ 95, Accessibilité ≥ 95, Bonnes pratiques ≥ 95, SEO ≥ 95.
7. **Poids réseau** : rechargement forcé sans cache — total transféré **sous 800 Ko**.
8. **Clavier seul** : parcourir toute la page au Tab. Chaque élément interactif est atteignable, avec un focus visible, dans un ordre logique.
9. **Favicon** : l'onglet affiche le `</>` rouge.

- [ ] **Étape 7 : commit final**

```bash
git add -A
git commit -m "feat: finalise la refonte du portfolio — responsive, accessibilite, nettoyage"
```

---

## Auto-relecture du plan

**Couverture de la spec**

| Section de la spec | Tâche(s) |
|---|---|
| §4.1 Identité | 6, 11, 13 |
| §4.2 Statistiques | 6, 12 |
| §4.3 Expérience | 8 |
| §4.4 Projets (ordre) | 9 |
| §4.5 Compétences | 10 |
| §4.6 Services | 7 |
| §4.7 Formation | 10 |
| §5.1 Typographie | 4 |
| §5.2 Couleurs | 1, 4 |
| §5.3 Logo et favicon | 3 |
| §6 Architecture des fichiers | 4, 5, 14 |
| §7 Structure des sections | 6–11 |
| §7.1 Carte sans capture | 9 |
| §8 Animations | 12 |
| §9 Performance | 1, 2, 14 |
| §10 Accessibilité | 5, 9, 11, 14 |
| §11 SEO | 13 |
| §12 Correctifs | 4 (thème, flash), 11 (`_next`, email), 12 (`typeSpeed`, écouteur scroll), 6 (GitHub) |
| §14 Critères d'acceptation | 14 étape 6 |

Aucune exigence de la spec n'est orpheline.

**Cohérence des noms**

- `initTheme` / `toggleTheme` / `applyTheme` — définis Tâche 4, appelés Tâches 4 et 5
- `initNav` — défini Tâche 5, appelé Tâches 5 et 9 ; étendu Tâche 11 étape 6
- `initFilters` — défini Tâche 9, appelé Tâche 9
- `initAnimations` — défini Tâche 12, appelé Tâche 12
- `#theme-toggle`, `#burger`, `#nav`, `#header`, `#to-top`, `#project-grid`, `#marquee-track`, `#scroll-progress`, `#filters-status` — chaque identifiant est créé dans le HTML avant d'être interrogé en JS
- `data-count-to` / `data-suffix` (Tâche 6) → lus en `dataset.countTo` / `dataset.suffix` (Tâche 12)
- `data-roles` (Tâche 6) → lu en `dataset.roles` (Tâche 12)
- `data-category` (Tâche 9) → lu en `dataset.category` (Tâche 9)
- Noms d'images : `profil-hero`, `profil-about`, `luxonera`, `etrack`, `hotellerie` — produits Tâche 2, consommés Tâches 6, 7, 9

**Piège identifié et neutralisé**

Les révélations au scroll partent d'une opacité posée **par GSAP**, jamais par le CSS. Une révélation dont l'`opacity: 0` vit dans la feuille de style laisse la page vide chez tout visiteur en mouvement réduit ou en cas d'échec du CDN. La Tâche 12 étapes 6 et 7 vérifie explicitement ces deux scénarios.
