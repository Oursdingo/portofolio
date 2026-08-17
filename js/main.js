import { initTheme, toggleTheme } from "./theme.js";
import { initNav } from "./nav.js";
import { initCarousel } from "./carousel.js";
import { initAnimations } from "./animations.js";

initTheme();
initNav();
initCarousel();

document.querySelector("#theme-toggle")?.addEventListener("click", toggleTheme);

// GSAP et Lenis sont chargés en `defer` : ils ne sont prêts qu'au DOMContentLoaded.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initAnimations);
} else {
  initAnimations();
}
