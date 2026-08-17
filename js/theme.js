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
