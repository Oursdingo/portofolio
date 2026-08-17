"""Genere les logos de technologies a partir de Simple Icons.

Produit deux choses :
  - les <symbol> des logos, injectes dans le sprite d'index.html entre les
    marqueurs TECH-ICONS ;
  - css/tech-icons.css, qui porte la couleur de marque de chaque logo.

Les logos sont integres en dur : aucune requete au chargement de la page.

Simple Icons publie ses SVG en CC0. Les marques restent la propriete de
leurs detenteurs ; les afficher pour indiquer les technologies employees
releve de l'usage nominatif.

Relancer ce script suffit a ajouter une technologie : il suffit de
l'ajouter a TECHNOS ci-dessous.
"""
import json
import os
import re
import sys
import io
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = "13"
BASE = f"https://cdn.jsdelivr.net/npm/simple-icons@{VERSION}"

# (identifiant local, slug Simple Icons, libelle affiche)
TECHNOS = [
    ("angular",    "angular",    "Angular"),
    ("springboot", "springboot", "Spring Boot"),
    ("flutter",    "flutter",    "Flutter"),
    ("dart",       "dart",       "Dart"),
    ("nextjs",     "nextdotjs",  "Next.js"),
    ("typescript", "typescript", "TypeScript"),
    ("javascript", "javascript", "JavaScript"),
    ("python",     "python",     "Python"),
    ("java",       "openjdk",    "Java"),
    ("fastapi",    "fastapi",    "FastAPI"),
    ("docker",     "docker",     "Docker"),
    ("postgresql", "postgresql", "PostgreSQL"),
    ("mysql",      "mysql",      "MySQL"),
    ("keycloak",   "keycloak",   "Keycloak"),
    ("odoo",       "odoo",       "Odoo"),
    ("metabase",   "metabase",   "Metabase"),
    ("git",        "git",        "Git"),
    ("github",     "github",     "GitHub"),
    ("gitlab",     "gitlab",     "GitLab"),
    ("swagger",    "swagger",    "Swagger"),
    ("drupal",     "drupal",     "Drupal"),
    ("threejs",    "threedotjs", "Three.js"),
]

# Sous ce seuil de luminance relative, un logo devient invisible sur le fond
# sombre (#0B0D12). On l'eclaircit alors jusqu'a rester lisible.
SEUIL_LUMINANCE_SOMBRE = 0.12


def recuperer(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8")


def luminance(hexa):
    canaux = []
    for i in (0, 2, 4):
        c = int(hexa[i:i + 2], 16) / 255
        canaux.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = canaux
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def eclaircir(hexa, facteur):
    """Rapproche la couleur du blanc sans changer sa teinte perçue."""
    r, g, b = (int(hexa[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (round(c + (255 - c) * facteur) for c in (r, g, b))
    return f"{r:02X}{g:02X}{b:02X}"


print(f"Recuperation du catalogue Simple Icons v{VERSION}...")
catalogue = json.loads(recuperer(f"{BASE}/_data/simple-icons.json"))["icons"]


def slugifier(titre):
    """Reproduit la regle de slug de Simple Icons pour les cas simples."""
    s = titre.lower()
    s = s.replace("+", "plus").replace(".", "dot").replace("&", "and")
    s = re.sub(r"[^a-z0-9]", "", s)
    return s


par_slug = {}
for entree in catalogue:
    par_slug[entree.get("slug") or slugifier(entree["title"])] = entree

symboles = []
regles_css = []
manquants = []

for local, slug, libelle in TECHNOS:
    entree = par_slug.get(slug)
    if entree is None:
        manquants.append((local, slug, "absent du catalogue"))
        continue

    try:
        svg = recuperer(f"{BASE}/icons/{slug}.svg")
    except Exception as e:
        manquants.append((local, slug, f"SVG injoignable : {e}"))
        continue

    trace = re.search(r'<path\s+d="([^"]+)"', svg)
    if not trace:
        manquants.append((local, slug, "aucun tracé dans le SVG"))
        continue

    hexa = entree["hex"]
    lum = luminance(hexa)
    if lum < SEUIL_LUMINANCE_SOMBRE:
        # Logos quasi noirs (Next.js, GitHub, Three.js) : invisibles sur fond
        # sombre. On les eclaircit jusqu'a repasser au-dessus du seuil.
        hexa_sombre = eclaircir(hexa, 0.75)
        note = f"  (eclairci en sombre : #{hexa} -> #{hexa_sombre})"
    else:
        hexa_sombre = hexa
        note = ""

    symboles.append(
        f'      <symbol id="t-{local}" viewBox="0 0 24 24">'
        f'<title>{libelle}</title><path d="{trace.group(1)}"/></symbol>'
    )
    regles_css.append(f"  --t-{local}: #{hexa};")
    if hexa_sombre != hexa:
        regles_css.append(f"  /* sombre: #{hexa_sombre} */")

    print(f"  {libelle:<14} #{hexa}  luminance {lum:.3f}{note}")

# --- CSS des couleurs de marque ---
lignes_clair = []
lignes_sombre = []
classes = []
for local, slug, libelle in TECHNOS:
    entree = par_slug.get(slug)
    if entree is None:
        continue
    hexa = entree["hex"]
    lignes_clair.append(f"  --t-{local}: #{hexa};")
    if luminance(hexa) < SEUIL_LUMINANCE_SOMBRE:
        lignes_sombre.append(f"  --t-{local}: #{eclaircir(hexa, 0.75)};")
    # Une classe par techno evite des styles en ligne dans le HTML.
    classes.append(f".tech--{local} {{ color: var(--t-{local}); }}")

css = f"""/* ============================================================
   tech-icons.css — couleurs de marque des logos de technologies

   GENERE PAR scripts/fetch_tech_icons.py — NE PAS EDITER A LA MAIN.
   Source : Simple Icons v{VERSION} (SVG en CC0).

   Les logos quasi noirs sont eclaircis en mode sombre : a leur couleur
   d'origine ils disparaitraient purement et simplement du fond.
   ============================================================ */

:root {{
{chr(10).join(lignes_clair)}
}}

[data-theme="dark"] {{
{chr(10).join(lignes_sombre)}
}}

/* Les logos heritent de currentColor : une classe suffit a les colorer. */
{chr(10).join(classes)}
"""

chemin_css = os.path.join(ROOT, "css", "tech-icons.css")
with open(chemin_css, "w", encoding="utf-8") as fh:
    fh.write(css)

# --- Injection des symboles dans le sprite d'index.html ---
chemin_html = os.path.join(ROOT, "index.html")
with open(chemin_html, encoding="utf-8") as fh:
    html = fh.read()

DEBUT = "      <!-- TECH-ICONS:START -->"
FIN = "      <!-- TECH-ICONS:END -->"

bloc = DEBUT + "\n" + "\n".join(symboles) + "\n" + FIN

if DEBUT in html and FIN in html:
    html = re.sub(
        re.escape(DEBUT) + r".*?" + re.escape(FIN), lambda _: bloc, html, flags=re.S
    )
else:
    print("\nECHEC : marqueurs TECH-ICONS absents d'index.html.")
    print("Ajouter ces deux lignes dans le <defs> du sprite :")
    print(DEBUT)
    print(FIN)
    sys.exit(1)

with open(chemin_html, "w", encoding="utf-8") as fh:
    fh.write(html)

print(f"\n{len(symboles)} logos injectes dans index.html")
print(f"css/tech-icons.css ecrit ({os.path.getsize(chemin_css) / 1024:.1f} Ko)")
print(f"poids des symboles : {len(bloc) / 1024:.1f} Ko")

if manquants:
    print("\nMANQUANTS :")
    for local, slug, raison in manquants:
        print(f"  - {local} (slug '{slug}') : {raison}")
    sys.exit(1)
