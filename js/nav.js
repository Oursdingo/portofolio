/**
 * Menu burger et état de l'en-tête au scroll.
 *
 * La surbrillance de la section active est gérée par ScrollTrigger dans
 * animations.js, pas ici : recalculer la position de chaque section à chaque
 * pixel défilé — ce que faisait l'ancien app.js — coûte cher pour rien.
 */
export function initNav() {
  const header = document.querySelector("#header");
  const nav = document.querySelector("#nav");
  const burger = document.querySelector("#burger");
  if (!header || !nav || !burger) return;

  const closeMenu = () => {
    nav.classList.remove("is-open");
    burger.classList.remove("is-open");
    burger.setAttribute("aria-expanded", "false");
    burger.setAttribute("aria-label", "Ouvrir le menu");
  };

  burger.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    burger.classList.toggle("is-open", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.setAttribute("aria-label", open ? "Fermer le menu" : "Ouvrir le menu");
  });

  nav.querySelectorAll(".nav__link").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && nav.classList.contains("is-open")) {
      closeMenu();
      burger.focus();
    }
  });

  let lastY = window.scrollY;
  const onScroll = () => {
    const y = window.scrollY;
    header.classList.toggle("is-stuck", y > 8);
    // Masquage au scroll descendant, uniquement menu fermé et hors du haut.
    const hide = y > 240 && y > lastY && !nav.classList.contains("is-open");
    header.classList.toggle("is-hidden", hide);
    document.querySelector("#to-top")?.classList.toggle("is-visible", y > 600);
    lastY = y;
  };

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}
