/**
 * Gestion de la langue : anglais (par défaut) ou français.
 *
 * Le HTML est écrit en anglais : sans JavaScript, ou pour un moteur de
 * recherche, la page reste complète. Ce module ne fait que remplacer les
 * textes marqués `data-i18n*` quand le visiteur choisit le français.
 *
 * L'attribut `lang` de <html> est posé dès le <head> par le script bloquant
 * (comme le thème) : le bouton EN / FR affiche le bon état dès la première
 * peinture, sans attendre ce module.
 *
 * Les autres modules qui fabriquent du texte (thème, menu, carrousel) passent
 * par `t()` et écoutent l'événement `langchange` pour se mettre à jour.
 */
import { translations } from "./translations.js";

const STORAGE_KEY = "lang";
const LANGUES = ["en", "fr"];
const DEFAUT = "en";
const ATTRIBUTS = ["alt", "aria-label", "placeholder", "data-roles"];
const root = document.documentElement;

let langue = DEFAUT;

function langueStockee() {
  try {
    const v = localStorage.getItem(STORAGE_KEY);
    return LANGUES.includes(v) ? v : DEFAUT;
  } catch {
    // localStorage indisponible (navigation privée stricte).
    return DEFAUT;
  }
}

/**
 * Texte d'une clé dans la langue courante. Les `{nom}` sont remplacés par
 * les valeurs fournies : t("carousel.status", { n: 1, total: 3, title }).
 */
export function t(cle, valeurs = {}) {
  const texte = translations[langue][cle] ?? translations[DEFAUT][cle] ?? cle;
  return texte.replace(/\{(\w+)\}/g, (_, nom) => valeurs[nom] ?? "");
}

export function applyLang(lang) {
  langue = lang;
  root.lang = lang;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    el.innerHTML = t(el.dataset.i18nHtml);
  });
  ATTRIBUTS.forEach((attr) => {
    document.querySelectorAll(`[data-i18n-${attr}]`).forEach((el) => {
      el.setAttribute(attr, t(el.getAttribute(`data-i18n-${attr}`)));
    });
  });

  document.dispatchEvent(new CustomEvent("langchange", { detail: { lang } }));
}

export function toggleLang() {
  const suivante = langue === "en" ? "fr" : "en";
  try {
    localStorage.setItem(STORAGE_KEY, suivante);
  } catch {
    // La langue s'appliquera quand même, sans persistance.
  }
  applyLang(suivante);
}

export function initI18n() {
  const lang = langueStockee();
  // Le HTML est déjà en anglais : inutile de tout réécrire au chargement.
  if (lang !== DEFAUT) applyLang(lang);

  document.querySelector("#lang-toggle")?.addEventListener("click", toggleLang);
}
