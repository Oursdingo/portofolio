import { initTheme, toggleTheme } from "./theme.js";
import { initNav } from "./nav.js";
import { initFilters } from "./filters.js";

initTheme();
initNav();
initFilters();

document.querySelector("#theme-toggle")?.addEventListener("click", toggleTheme);
