import { initI18n } from "./i18n.js";
import { initTheme, cycleTheme } from "./theme.js";
import { initNav } from "./nav.js";
import { initCarousel } from "./carousel.js";
import { initAnimations } from "./animations.js";

initI18n();
initTheme();
initNav();
initCarousel();

document.querySelector("#theme-toggle")?.addEventListener("click", cycleTheme);

// GSAP et Lenis sont chargés en `defer` : ils ne sont prêts qu'au DOMContentLoaded.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initAnimations);
} else {
  initAnimations();
}
