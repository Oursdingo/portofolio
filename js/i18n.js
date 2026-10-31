/**
 * Langue de la page : français sur /fr, anglais sur /en.
 *
 * Les textes du HTML sont écrits dans chaque page par scripts/build_i18n.mjs.
 * Ce module ne sert qu'aux textes fabriqués par le JavaScript (thème, menu,
 * carrousel), via `t()`. La langue est celle de l'attribut `lang` de <html>.
 */
import { translations } from "./translations.js";

const DEFAUT = "fr";
const langue = translations[document.documentElement.lang]
  ? document.documentElement.lang
  : DEFAUT;

/**
 * Texte d'une clé dans la langue courante. Les `{nom}` sont remplacés par
 * les valeurs fournies : t("carousel.status", { n: 1, total: 3, title }).
 */
export function t(cle, valeurs = {}) {
  const texte = translations[langue][cle] ?? translations[DEFAUT][cle] ?? cle;
  return texte.replace(/\{(\w+)\}/g, (_, nom) => valeurs[nom] ?? "");
}

export function initI18n() {
  // Le bouton EN / FR est un lien : on garde la section en cours de lecture.
  document.querySelector("#lang-toggle")?.addEventListener("click", (e) => {
    e.currentTarget.hash = location.hash;
  });
}
