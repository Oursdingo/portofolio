/**
 * Filtrage des projets par catégorie.
 *
 * Le masquage passe par l'attribut `hidden` et non par `display:none` en
 * CSS : les lecteurs d'écran ignorent alors réellement les cartes filtrées
 * au lieu de continuer à les annoncer.
 */
export function initFilters() {
  const grid = document.querySelector("#project-grid");
  const buttons = document.querySelectorAll(".filter");
  const status = document.querySelector("#filters-status");
  if (!grid || !buttons.length) return;

  const cards = [...grid.querySelectorAll(".project-card")];

  const apply = (filter) => {
    let visible = 0;
    cards.forEach((card) => {
      const categories = (card.dataset.category || "").split(/\s+/);
      const show = filter === "all" || categories.includes(filter);
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (status) {
      status.textContent =
        visible > 1 ? `${visible} projets affichés` : `${visible} projet affiché`;
    }
  };

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => {
        b.classList.remove("is-active");
        b.setAttribute("aria-pressed", "false");
      });
      btn.classList.add("is-active");
      btn.setAttribute("aria-pressed", "true");
      apply(btn.dataset.filter);
    });
  });
}
