/**
 * Carrousel des services.
 *
 * Ne dépend ni de GSAP ni de Lenis : une translation CSS et une minuterie
 * suffisent. Le mode horizontal n'est activé qu'ici, via `.carousel--ready` ;
 * sans JavaScript les blocs restent empilés et tous lisibles.
 *
 * Le défilement automatique s'interrompt au survol, au focus clavier, quand
 * l'onglet passe en arrière-plan, et via un bouton explicite. Un contenu qui
 * avance seul sans moyen de l'arrêter prive le visiteur du contrôle de sa
 * lecture (WCAG 2.2.2) ; le survol seul ne couvre ni le clavier ni le tactile.
 */
const INTERVALLE = 6000;

export function initCarousel() {
  const carousel = document.querySelector("#services-carousel");
  const track = document.querySelector("#services-track");
  const toggle = document.querySelector("#services-toggle");
  const dotsList = document.querySelector("#services-dots");
  const status = document.querySelector("#services-status");
  if (!carousel || !track || !dotsList) return;

  const slides = [...track.querySelectorAll(".service")];
  if (slides.length < 2) return;

  const dots = [...dotsList.querySelectorAll("button")];
  const reduit = window.matchMedia("(prefers-reduced-motion: reduce)");

  // En mouvement réduit, on ne construit pas de carrousel du tout : les blocs
  // restent empilés et tous lisibles. Activer le mode horizontal puis le
  // neutraliser en CSS laisserait des blocs visibles marqués `aria-hidden`,
  // c'est-à-dire du contenu affiché mais invisible aux lecteurs d'écran.
  if (reduit.matches) return;

  carousel.classList.add("carousel--ready");

  let index = 0;
  let minuterie = null;
  let arretParUtilisateur = false;

  const afficher = (i) => {
    index = (i + slides.length) % slides.length;
    track.style.transform = `translateX(${-index * 100}%)`;
    slides.forEach((s, n) => {
      // Les blocs hors champ sortent de l'ordre de tabulation : sans ça, le
      // clavier se perd dans du contenu invisible.
      s.setAttribute("aria-hidden", String(n !== index));
      s.querySelectorAll("a, button").forEach((el) => {
        if (n === index) el.removeAttribute("tabindex");
        else el.setAttribute("tabindex", "-1");
      });
    });
    dots.forEach((d, n) => {
      d.classList.toggle("is-active", n === index);
      if (n === index) d.setAttribute("aria-current", "true");
      else d.removeAttribute("aria-current");
    });
    if (status) {
      status.textContent = `Service ${index + 1} sur ${slides.length} : ${
        slides[index].querySelector(".service__title").textContent
      }`;
    }
  };

  const demarrer = () => {
    if (minuterie || arretParUtilisateur || reduit.matches) return;
    minuterie = setInterval(() => afficher(index + 1), INTERVALLE);
    majBouton();
  };

  const suspendre = () => {
    clearInterval(minuterie);
    minuterie = null;
    majBouton();
  };

  function majBouton() {
    if (!toggle) return;
    const enLecture = minuterie !== null;
    toggle.classList.toggle("is-paused", !enLecture);
    toggle.setAttribute(
      "aria-label",
      enLecture
        ? "Mettre en pause le défilement automatique"
        : "Reprendre le défilement automatique"
    );
  }

  dots.forEach((dot) => {
    dot.addEventListener("click", () => {
      afficher(Number(dot.dataset.index));
      // Un clic manuel relance le compte à rebours plutôt que de couper
      // la diapositive choisie au bout d'une fraction de seconde.
      if (!arretParUtilisateur) {
        suspendre();
        demarrer();
      }
    });
  });

  toggle?.addEventListener("click", () => {
    arretParUtilisateur = minuterie !== null;
    if (arretParUtilisateur) suspendre();
    else demarrer();
  });

  // Le survol et le focus suspendent, sans annuler le choix de l'utilisateur.
  carousel.addEventListener("mouseenter", suspendre);
  carousel.addEventListener("mouseleave", demarrer);
  carousel.addEventListener("focusin", suspendre);
  carousel.addEventListener("focusout", (e) => {
    if (!carousel.contains(e.relatedTarget)) demarrer();
  });

  // Inutile de faire tourner une minuterie dans un onglet qu'on ne voit pas.
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) suspendre();
    else demarrer();
  });

  // Si le visiteur active le mouvement réduit en cours de route, on arrête
  // au moins le défilement automatique.
  reduit.addEventListener("change", () => {
    if (reduit.matches) suspendre();
  });

  afficher(0);
  demarrer();
}
