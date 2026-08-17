/**
 * Carrousel des services.
 *
 * Ne dépend ni de GSAP ni de Lenis : une translation CSS et une minuterie
 * suffisent. Le mode horizontal n'est activé qu'ici, via `.carousel--ready` ;
 * sans JavaScript les blocs restent empilés et tous lisibles.
 *
 * Contrôle du défilement automatique, en l'absence de bouton pause :
 * il s'interrompt au survol, au focus clavier et quand l'onglet passe en
 * arrière-plan, et il s'arrête **définitivement** dès que le visiteur touche
 * un chevron ou une puce. Une fois qu'on prend la main, on ne la lui reprend
 * plus au milieu d'une phrase.
 */
const INTERVALLE = 6000;

export function initCarousel() {
  const carousel = document.querySelector("#services-carousel");
  const track = document.querySelector("#services-track");
  const dotsList = document.querySelector("#services-dots");
  const status = document.querySelector("#services-status");
  const prev = document.querySelector("#services-prev");
  const next = document.querySelector("#services-next");
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
  let mainPrise = false;

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
    if (minuterie || mainPrise || reduit.matches) return;
    minuterie = setInterval(() => afficher(index + 1), INTERVALLE);
  };

  const suspendre = () => {
    clearInterval(minuterie);
    minuterie = null;
  };

  /** Le visiteur a navigué lui-même : le défilement automatique s'arrête. */
  const reprendreLaMain = (cible) => {
    mainPrise = true;
    suspendre();
    afficher(cible);
  };

  prev?.addEventListener("click", () => reprendreLaMain(index - 1));
  next?.addEventListener("click", () => reprendreLaMain(index + 1));
  dots.forEach((dot) => {
    dot.addEventListener("click", () => reprendreLaMain(Number(dot.dataset.index)));
  });

  // Suspensions temporaires : elles ne valent pas prise de main.
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

  // Si le visiteur active le mouvement réduit en cours de route.
  reduit.addEventListener("change", () => {
    if (reduit.matches) suspendre();
  });

  // Navigation au clavier quand le carrousel a le focus.
  carousel.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      reprendreLaMain(index - 1);
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      reprendreLaMain(index + 1);
    }
  });

  afficher(0);
  demarrer();
}
