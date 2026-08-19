/**
 * Gestion du thème : Auto, Clair, Sombre.
 *
 * Trois états et non deux. Avec une simple bascule clair/sombre, le premier
 * clic enferme définitivement le visiteur dans un choix manuel : plus aucun
 * moyen de revenir à « suivre mon système ». L'état Auto rend ce retour
 * possible.
 *
 * La clé de stockage est versionnée. L'ancien site écrivait `theme` à chaque
 * chargement de page, même sans action du visiteur, et y mettait « dark » par
 * défaut. Ces valeurs sont donc indiscernables d'un choix délibéré alors
 * qu'elles n'en sont pas : les lire condamnerait tout ancien visiteur au
 * thème sombre à vie. On repart d'une clé neuve, et les anciennes valeurs
 * sont ignorées.
 */
const STORAGE_KEY = "theme-mode";
const MODES = ["auto", "light", "dark"];
const root = document.documentElement;
const darkQuery = window.matchMedia("(prefers-color-scheme: dark)");

const LIBELLES = {
  auto: "Thème : automatique. Cliquer pour forcer le thème clair.",
  light: "Thème : clair. Cliquer pour forcer le thème sombre.",
  dark: "Thème : sombre. Cliquer pour suivre le système.",
};

function modeStocke() {
  try {
    const v = localStorage.getItem(STORAGE_KEY);
    return MODES.includes(v) ? v : "auto";
  } catch {
    // localStorage indisponible (navigation privée stricte).
    return "auto";
  }
}

/** Traduit un mode en thème réellement appliqué. */
function resoudre(mode) {
  if (mode === "auto") return darkQuery.matches ? "dark" : "light";
  return mode;
}

export function applyMode(mode) {
  root.setAttribute("data-theme-mode", mode);
  root.setAttribute("data-theme", resoudre(mode));

  const btn = document.querySelector("#theme-toggle");
  if (btn) {
    btn.setAttribute("aria-label", LIBELLES[mode]);
    // Trois états : `aria-pressed` ne saurait en décrire que deux.
    btn.removeAttribute("aria-pressed");
  }
}

export function initTheme() {
  applyMode(modeStocke());

  // En mode auto, le site suit les changements de thème du système en direct.
  darkQuery.addEventListener("change", () => {
    if (modeStocke() === "auto") applyMode("auto");
  });
}

export function cycleTheme() {
  const suivant = MODES[(MODES.indexOf(modeStocke()) + 1) % MODES.length];
  try {
    localStorage.setItem(STORAGE_KEY, suivant);
  } catch {
    // Le thème s'appliquera quand même, sans persistance.
  }
  applyMode(suivant);
}
