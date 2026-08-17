# Refonte du portfolio — Sawadogo Adam Sharif

**Date :** 2026-08-17
**Statut :** validé, prêt pour le plan d'implémentation

## 1. Contexte

Le portfolio actuel (3 fichiers : `index.html`, `style.css`, `app.js`) date d'une
période où son auteur était étudiant. Il ne reflète plus ni son poste, ni ses
compétences, ni ses projets réels.

Écarts constatés entre le CV (`documents/CV_Sawadogo_Adam_Sharif.pdf`) et le site :

- le site annonce un profil web ; le CV annonce **Full Stack Web & Mobile** (Flutter)
- aucune section Expérience, alors que le CV documente deux postes en cours
- les projets affichés sont des exercices de formation (Forkify, Bankist)
- Flutter, Odoo, Metabase, GitLab n'apparaissent nulle part
- aucune section Formation & Certifications
- pas de lien GitHub

## 2. Objectifs

1. Aligner le contenu sur le CV.
2. Passer d'une esthétique « template » à un rendu éditorial professionnel.
3. Fluidifier les animations (GSAP + Lenis).
4. Faire suivre au thème la préférence système du visiteur, avec le clair en repli
   — le site s'ouvre aujourd'hui en sombre quoi qu'il arrive.
5. **Diviser le poids de la page par plus de dix** — la cible est un recruteur,
   souvent sur mobile et sur un réseau lent.

## 3. Décisions validées

| Sujet | Décision |
|---|---|
| Stack | HTML/CSS/JS vanilla, aucun build, déploiement Vercel inchangé |
| Direction visuelle | Éditorial épuré |
| Accent | Indigo profond |
| Logo | `</>` **rouge** — signature personnelle assumée face à l'indigo |
| Thème par défaut | Préférence système du visiteur, clair en repli |
| Captures des nouveaux projets | Aucune ; cartes sans image, prêtes à en accueillir |

## 4. Contenu de référence

Source unique de vérité : le CV. Aucune donnée inventée.

### 4.1 Identité

- **Nom :** Sawadogo Adam Sharif
- **Titre :** Développeur Full Stack, Web & Mobile
- **Localisation :** Nagrin, Ouagadougou, Burkina Faso
- **Email :** `sawadogosharif20@gmail.com` (normalisé en minuscules ; le
  formulaire actuel utilise une majuscule initiale)
- **Téléphone / WhatsApp :** +226 77 46 88 76 → `wa.me/22677468876`
- **GitHub :** `github.com/Oursdingo` — **à ajouter**, absent du site actuel
- **LinkedIn :** `linkedin.com/in/sharif-sawadogo-280197223/`
- **X :** `x.com/SharifSawa51023`

### 4.2 Statistiques

Chiffres vérifiés contre le CV avant publication.

| Valeur | Libellé | Justification |
|---|---|---|
| 3+ | Années d'expérience | « plus de 3 ans d'expérience académique et professionnelle » |
| 10+ | Projets réalisés | 11 projets identifiables au CV |
| 2 | Applications mobiles | KEL et LONIA, toutes deux en Flutter |
| 20+ | Technologies maîtrisées | 27 recensées dans les rubriques du CV |

### 4.3 Expérience

**Switch Maker — Développeur Full Stack — juin 2025 → présent**

- SIG (Système Intégré de Gestion) : Odoo, Metabase pour les tableaux de bord — en cours
- DAICE : plateforme de promotion des investissements pour le CEPICI (Côte d'Ivoire)
- Autres plateformes institutionnelles : gestion de dossiers et de procédures
- Conception du socle applicatif : architecture logicielle, modules métier, sécurité Keycloak
- Intégration de modèles d'IA via API (FastAPI, Python)
- LONIA : application mobile d'apprentissage en ligne (Flutter)
- KEL : application mobile de gestion de livraison (Flutter)
- Analyse des besoins, modélisation UML, comptes rendus, méthodologie Agile

**BlendBloc (agence web marketing) — Responsable des projets informatiques — en parallèle**

- Pilotage des projets techniques
- Mise en place d'un espace de gestion de projet Notion
- Développement du site vitrine de l'agence

### 4.4 Projets — ordre imposé

L'ordre ci-dessous a été dicté explicitement. Il place le travail professionnel
en tête et relègue l'académique en fin de grille.

| # | Projet | Stack | Statut | Visuel |
|---|---|---|---|---|
| 1 | SIG | Odoo, Metabase | Pro · en cours | carte sans image |
| 2 | DAICE | plateforme institutionnelle, CEPICI | Pro | carte sans image |
| 3 | Luxonera | Next.js, Three.js | **Live** | `projet7.png` |
| 4 | E‑Wari | Flutter, Spring Boot, PostgreSQL | Personnel | carte sans image |
| 5 | KEL | Flutter | Pro | carte sans image |
| 6 | LONIA | Flutter | Pro | carte sans image |
| 7 | Plateforme DAO | Angular, Spring Boot, FastAPI, Keycloak, PostgreSQL | Fin d'études | carte sans image |
| 8 | eTrack | Next.js | Personnel | `projet-2.png` |
| 9 | Plateforme hôtelière | académique | Académique | `projet_6.png` |

**Retirés :** Forkify, Bankist, et le projet de gestion de colis / transport —
tous trois des exercices de formation.

**Lien externe :** seul Luxonera en possède un (`https://luxonera-app.vercel.app/`).
Les cartes sans lien n'affichent aucun bouton mort.

Les mentions « NB : Projet non déployé », répétées cinq fois sur le site actuel,
disparaissent. Un badge de statut discret transmet la même information sans
tonalité d'excuse.

### 4.5 Compétences

- **Langages & Frameworks :** Angular, Spring Boot, Flutter (Dart), Next.js, JavaScript, TypeScript, Python, Java
- **Architecture & Méthodes :** architecture logicielle, UML, Agile, API REST, microservices
- **Intelligence artificielle :** intégration de modèles via API (FastAPI/Python), développement assisté par IA
- **Outils & Infrastructure :** Git, GitHub, GitLab, Docker, Odoo, Metabase, MySQL, PostgreSQL, Swagger, Keycloak
- **CMS :** Drupal (formation en cours)
- **Langues :** français (langue maternelle), anglais (B2)

### 4.6 Services

Cinq cartes, contre trois aujourd'hui :

1. Développement Web — Angular, Next.js, TypeScript
2. **Développement Mobile** — Flutter, Dart *(nouveau)*
3. Back‑End & API — Spring Boot, API REST, Keycloak
4. **Intégration IA** — FastAPI, Python, modèles via API *(nouveau)*
5. Formation JavaScript — conservée du site actuel

### 4.7 Formation & Certifications

- Licence Informatique
- Formation CMS Drupal (en cours)
- Certificats Python, Bases de Données et Intelligence Artificielle — Coursera
- Certificat Marketing Digital — Force N
- Formation Spring Boot et Angular — Switch Maker

## 5. Design system

### 5.1 Typographie

Polices variables servies par Google Fonts, avec `preconnect` et `display=swap`.

| Rôle | Police | Graisses |
|---|---|---|
| Titres | Sora | 600–700 (variable) |
| Corps | Inter | 400–600 (variable) |
| Labels techniques, badges | JetBrains Mono | 500 |

Poppins est abandonnée.

### 5.2 Couleurs

Le thème clair est défini sur `:root` nu ; le thème sombre ne redéfinit que les
jetons qui changent.

| Jeton | Clair (défaut) | Sombre |
|---|---|---|
| `--bg` | `#FFFFFF` | `#0B0D12` |
| `--surface` | `#F7F8FA` | `#12151C` |
| `--text` | `#0D1117` | `#E8EAF0` |
| `--text-muted` | `#5B6472` | `#9AA3B2` |
| `--accent` | `#4338CA` | `#818CF8` |
| `--accent-soft` | `rgba(67,56,202,.08)` | `rgba(129,140,248,.14)` |
| `--border` | `rgba(13,17,23,.08)` | `rgba(255,255,255,.09)` |
| `--logo-red` | `#DC2626` | `#F05252` |

L'accent change de teinte entre les deux modes : un indigo foncé sur fond noir
serait illisible. Le rouge du logo s'éclaircit également en mode sombre.

Tous les couples texte/fond doivent atteindre WCAG AA (4.5:1 pour le texte
courant, 3:1 pour le texte large).

### 5.3 Logo et favicon

Le symbole `</>` est dessiné en **tracés vectoriels** — chevrons et barre
oblique en `stroke`, avec `stroke-linecap="round"` et `stroke-linejoin="round"`.

Aucun texte SVG, aucune dépendance à une police : un `<text>` dans un favicon ne
se rend pas de façon fiable selon le navigateur et le système.

- `favicon.svg` — 32×32, carré arrondi blanc, `</>` rouge centré
- `favicon.ico` — repli 32×32 pour les navigateurs anciens
- logo d'en-tête — SVG inline `</>` rouge + mot-clé « Adam's Coding »

Le rouge est conservé sur les deux modes de thème, avec la variante `--logo-red`
éclaircie en sombre.

## 6. Architecture des fichiers

```
index.html
merci.html            confirmation d'envoi du formulaire
favicon.svg
css/
  base.css            reset, jetons, typographie, utilitaires
  layout.css          en-tête, sections, grilles, pied de page
  components.css      boutons, cartes, timeline, badges, formulaire
  responsive.css      points de rupture
js/
  theme.js            thème clair/sombre
  nav.js              menu burger, section active, en-tête au scroll
  animations.js       Lenis + GSAP + ScrollTrigger
  main.js             orchestration (module ES)
images/
  optimized/          WebP générés, avec repli PNG
docs/superpowers/specs/
```

**Le HTML reste statique.** Aucun rendu par JavaScript : le contenu doit être
indexable et rester visible si un CDN tombe ou si le JS échoue.

`style.css` atteint 951 lignes et doublerait avec les nouvelles sections. Le
découpage en quatre fichiers thématiques garde chacun sous ~400 lignes.

## 7. Structure des sections

Ordre pensé pour le parcours d'un recruteur : qui → ce que je fais → où je l'ai
fait → ce que j'ai produit → avec quoi → mon bagage → me joindre.

1. **Hero** — nom, titre rotatif, pitch, deux CTA, réseaux sociaux (GitHub inclus), photo
2. **Stats** — bandeau de quatre compteurs
3. **À propos** — profil, localisation, langues, téléchargement du CV
4. **Services** — cinq cartes
5. **Expérience** — timeline verticale, deux postes *(nouveau)*
6. **Projets** — grille filtrable : Tous · Pro · Web · Mobile · Académique
7. **Compétences** — grille par catégorie + marquees défilants retravaillés
8. **Formation & Certifications** *(nouveau)*
9. **Contact** — formulaire + coordonnées
10. **Pied de page**

Navigation (6 entrées) : Accueil · À propos · Expérience · Projets · Compétences · Contact.

### 7.1 Carte projet sans capture

Composant `.project-card--noimage` :

- fond en dégradé indigo
- monogramme du projet en grand, en JetBrains Mono
- badges de stack
- titre, description, badge de statut
- lien externe **uniquement si l'URL existe**

Déposer une image dans `images/optimized/` et renseigner l'attribut `src`
bascule la carte en version illustrée. Aucune modification de CSS ni de JS.

## 8. Couche d'animation

**Lenis** — défilement fluide global, intégré à la boucle `requestAnimationFrame`
de GSAP pour éviter deux boucles concurrentes.

**GSAP + ScrollTrigger** :

| Effet | Cible |
|---|---|
| Cascade au chargement | éléments du hero |
| Apparition au scroll | titres et contenus de section |
| Compteurs animés | bandeau de stats |
| Ligne qui se dessine | timeline d'expérience |
| Stagger + tilt léger au survol | cartes projet |
| Barre de progression | haut de page |
| Masquage/réapparition | en-tête selon le sens du scroll |
| Surbrillance de la section active | navigation |

ScrollReveal et Typed.js sont supprimés. L'effet machine à écrire est réécrit en
JavaScript natif (~15 lignes) ; importer Typed.js entier pour cela est
disproportionné.

La détection de section active passe de l'écouteur `scroll` manuel de
`app.js:12` à ScrollTrigger, qui ne recalcule pas la position de chaque section à
chaque pixel défilé.

**`prefers-reduced-motion`** : Lenis n'est pas instancié, les animations GSAP se
réduisent à des changements d'opacité instantanés, le marquee est figé.

## 9. Performance

### 9.1 Bilan

| Poste | Avant | Après |
|---|---|---|
| Icônes | Boxicons (police web) ≈ 180 Ko | sprite SVG des ~20 icônes ≈ 6 Ko |
| Animations | ScrollReveal + Typed.js ≈ 27 Ko | GSAP + ScrollTrigger + Lenis ≈ 68 Ko |
| Images | 8 633 Ko | ≈ 400 Ko |
| **Total** | **≈ 8,8 Mo** | **≈ 550 Ko** |

Le remplacement de Boxicons finance à lui seul l'arrivée de GSAP.

### 9.2 Traitement des images

Les captures sont en 3000 px de large pour un affichage à ~400 px : plus de 90 %
des pixels téléchargés sont jetés par le navigateur.

Traitement automatisé via Pillow (10.4.0, déjà installé) :

- redimensionnement à **1200 px de large maximum** — le double de la taille
  d'affichage, pour rester net sur écran haute densité
- conversion WebP qualité 82
- repli PNG optimisé, servi via `<picture>`
- portraits ramenés à 800 px

**Les originaux ne sont jamais écrasés** : les fichiers générés vont dans
`images/optimized/`.

Images conservées : `profile_1`, `profil2`, `projet-2`, `projet7`, `projet_6`.
Les autres (`projet_1`, `projet_2`, `projet_3`, `projet_4`, `projet_5`)
correspondent à des projets retirés et ne sont plus référencées ; elles restent
sur le disque mais sortent du chemin de chargement.

### 9.3 Budget

- premier chargement < 800 Ko
- LCP < 1,5 s
- Lighthouse Performance ≥ 95
- `loading="lazy"` sur toute image sous la ligne de flottaison
- `width` et `height` explicites sur chaque image (évite les décalages de mise en page)
- GSAP et Lenis en `defer`

## 10. Accessibilité

- contrastes WCAG AA vérifiés sur les deux thèmes
- `prefers-reduced-motion` respecté intégralement
- indicateurs de focus visibles
- `aria-label` sur tout bouton ou lien réduit à une icône
- lien d'évitement vers le contenu principal
- navigation au clavier complète, y compris les filtres de projets
- repères sémantiques : `<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`

## 11. SEO et partage

- `<title>` et `meta description` rédigés
- Open Graph et Twitter Card, avec image de partage dédiée
- JSON‑LD `Person` : nom, poste, employeur, liens de profil
- `lang="fr"`, URL canonique
- hiérarchie de titres cohérente, un seul `<h1>`

Objectif concret : un lien partagé sur LinkedIn ou WhatsApp affiche un aperçu
propre plutôt qu'une URL nue.

## 12. Correctifs des défauts existants

| Fichier | Défaut | Correction |
|---|---|---|
| `app.js:86` | thème sombre forcé même en préférence système claire | la préférence système est suivie ; le choix mémorisé prime |
| `app.js:47` | `typeSeed` — clé inexistante, la vitesse configurée n'a jamais été appliquée | remplacé par l'implémentation native |
| `index.html:429` | `_next` pointe vers `https://yourdomain.com/merci.html` | `merci.html` créée et référencée |
| `index.html:424` | email avec majuscule initiale | normalisé en minuscules |
| `app.js:20` | `document.querySelector` dans une boucle, à chaque événement de scroll | remplacé par ScrollTrigger |
| `index.html` | aucun lien GitHub | ajouté aux réseaux sociaux |

### Comportement du thème

1. Un choix enregistré dans `localStorage` prime toujours.
2. À défaut, la **préférence système** s'applique : appareil en clair → site
   clair, appareil en sombre → site sombre.
3. Si le système n'exprime aucune préférence, **le clair s'applique**.

Tant que le visiteur n'a pas actionné la bascule lui-même, le site suit les
changements de thème de son système en direct. Dès qu'il choisit, son choix est
mémorisé et cesse de suivre le système.

## 13. Hors périmètre

Écartés volontairement : blog, internationalisation, back-end de formulaire
maison (FormSubmit reste), CMS, animations 3D, curseur personnalisé, préchargeur.

## 14. Critères d'acceptation

1. Chaque information affichée est traçable jusqu'au CV.
2. Les neuf projets apparaissent dans l'ordre imposé en §4.4.
3. Forkify, Bankist et le projet de colis ne figurent nulle part.
4. Sur une session vierge, le thème suit la préférence système ; clair si le
   système n'en exprime aucune.
5. Le basculement de thème persiste après rechargement.
6. Poids total du premier chargement < 800 Ko, mesuré dans l'onglet réseau.
7. Lighthouse ≥ 95 en Performance et ≥ 95 en Accessibilité.
8. Avec `prefers-reduced-motion: reduce`, aucune animation de mouvement ne se déclenche.
9. Le site est utilisable et lisible de 320 px à 2560 px de large.
10. Le formulaire aboutit sur `merci.html`.
11. Le favicon `</>` est net et identifiable à 16 px.
12. Aucune erreur en console.
