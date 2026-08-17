import { initTheme, toggleTheme } from "./theme.js";
import { initNav } from "./nav.js";

initTheme();
initNav();

document.querySelector("#theme-toggle")?.addEventListener("click", toggleTheme);
