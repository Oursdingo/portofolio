/**
 * Genere les pages /fr et /en a partir de src/ et de js/translations.js.
 *
 *   node scripts/build_i18n.mjs
 *
 * Les moteurs de recherche doivent trouver chaque langue dans le HTML lui-meme :
 * une page traduite par JavaScript apres le chargement serait indexee une seule
 * fois, dans sa langue d'origine. Les textes sont donc inscrits ici, a la
 * generation, et le navigateur n'a plus rien a traduire.
 *
 * Sorties (a committer, Vercel sert le site tel quel, sans etape de build) :
 *   fr/index.html  fr/merci.html
 *   en/index.html  en/merci.html
 *
 * Dans les fichiers de src/ :
 *   data-i18n="cle"           remplace le contenu de l'element
 *   data-i18n-html="cle"      idem, la valeur contient des balises
 *   data-i18n-<attr>="cle"    remplace l'attribut <attr>
 *   {{lang}}, {{url}}...      variables definies dans LANGUES
 *   {{cle}}                   valeur brute d'une traduction (JSON-LD)
 */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { translations } from "../js/translations.js";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const SITE = "https://sharifsawadogo.dev";

const LANGUES = {
  fr: { ogLocale: "fr_FR", ogLocaleAlt: "en_US", altLang: "en" },
  en: { ogLocale: "en_US", ogLocaleAlt: "fr_FR", altLang: "fr" },
};
const PAGES = [
  { source: "index.html", chemin: "" },
  { source: "merci.html", chemin: "/merci" },
];

const echappeTexte = (s) =>
  s.replace(/&(?!\w+;)/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const echappeAttribut = (s) =>
  s.replace(/&(?!\w+;)/g, "&amp;").replace(/"/g, "&quot;");

function traduction(lang, cle) {
  const valeur = translations[lang][cle];
  if (valeur === undefined) throw new Error(`Cle absente (${lang}) : ${cle}`);
  return valeur;
}

/** Position de la balise fermante de l'element ouvert juste avant `debut`. */
function finElement(html, balise, debut) {
  const re = new RegExp(`<(/?)${balise}\\b[^>]*>`, "g");
  re.lastIndex = debut;
  let profondeur = 1;
  for (let m = re.exec(html); m; m = re.exec(html)) {
    profondeur += m[1] ? -1 : 1;
    if (profondeur === 0) return m.index;
  }
  throw new Error(`Balise <${balise}> non fermee`);
}

function appliqueContenus(html, lang) {
  const re = /<([a-z][\w-]*)\b[^<>]*?\sdata-i18n(-html)?="([^"]+)"[^<>]*>/gi;
  let sortie = "";
  let curseur = 0;
  for (let m = re.exec(html); m; m = re.exec(html)) {
    const [ouverture, balise, estHtml, cle] = m;
    const debut = m.index + ouverture.length;
    const fin = finElement(html, balise, debut);
    const valeur = traduction(lang, cle);
    sortie += html.slice(curseur, debut) + (estHtml ? valeur : echappeTexte(valeur));
    curseur = fin;
    re.lastIndex = fin;
  }
  return sortie + html.slice(curseur);
}

function appliqueAttributs(html, lang) {
  return html.replace(/<[a-z][^<>]*\sdata-i18n-[^<>]*>/gi, (balise) => {
    let resultat = balise;
    for (const [, attr, cle] of balise.matchAll(/\sdata-i18n-(?!html)([\w-]+)="([^"]+)"/g)) {
      const valeur = echappeAttribut(traduction(lang, cle));
      const existant = new RegExp(`(\\s${attr}=")[^"]*(")`);
      if (!existant.test(resultat)) throw new Error(`Attribut ${attr} absent : ${balise}`);
      resultat = resultat.replace(existant, (_, a, b) => a + valeur + b);
    }
    return resultat;
  });
}

function genere(source, lang, chemin) {
  const { ogLocale, ogLocaleAlt, altLang } = LANGUES[lang];
  const variables = {
    lang,
    altLang,
    ogLocale,
    ogLocaleAlt,
    url: `${SITE}/${lang}${chemin}`,
    altUrl: `/${altLang}`,
  };

  let html = appliqueAttributs(appliqueContenus(source, lang), lang);
  html = html.replace(/\s+data-i18n(-[\w-]+)?="[^"]*"/g, "");
  html = html.replace(/\{\{([\w.]+)\}\}/g, (_, nom) => variables[nom] ?? traduction(lang, nom));
  return html.replace(
    /(<!doctype html>)/i,
    "$1\n<!-- Page generee par scripts/build_i18n.mjs depuis src/ : ne pas editer. -->",
  );
}

for (const { source, chemin } of PAGES) {
  const gabarit = readFileSync(join(ROOT, "src", source), "utf-8");
  for (const lang of Object.keys(LANGUES)) {
    const dossier = join(ROOT, lang);
    mkdirSync(dossier, { recursive: true });
    writeFileSync(join(dossier, source), genere(gabarit, lang, chemin));
    console.log(`${lang}/${source}`);
  }
}
