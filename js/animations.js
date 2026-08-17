/**
 * Couche d'animation : Lenis (scroll fluide) + GSAP / ScrollTrigger.
 *
 * Deux garde-fous importants :
 *
 * 1. L'opacité de départ des révélations est posée par GSAP, jamais par le
 *    CSS. Si elle vivait dans la feuille de style, la page apparaîtrait
 *    entièrement vide chez quiconque a activé le mouvement réduit, ou si le
 *    CDN GSAP tombait.
 * 2. Tout est court-circuité si l'utilisateur demande un mouvement réduit,
 *    et l'absence de GSAP est traitée sans casser la page.
 */
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Effet machine à écrire. Remplace Typed.js (~12 Ko) par une vingtaine de lignes. */
function typewriter(el) {
  const words = (el.dataset.roles || "").split("|").filter(Boolean);
  if (words.length < 2) return;

  let wordIndex = 0;
  let charCount = words[0].length;
  let deleting = true;

  const tick = () => {
    const word = words[wordIndex];
    charCount += deleting ? -1 : 1;
    el.textContent = word.slice(0, charCount);

    let delay = deleting ? 45 : 90;
    if (!deleting && charCount === word.length) {
      deleting = true;
      delay = 1800;
    } else if (deleting && charCount === 0) {
      deleting = false;
      wordIndex = (wordIndex + 1) % words.length;
      delay = 300;
    }
    setTimeout(tick, delay);
  };

  setTimeout(tick, 2200);
}

function initLenis(gsap, ScrollTrigger) {
  const lenis = new window.Lenis({ duration: 1.1, smoothWheel: true });

  lenis.on("scroll", ScrollTrigger.update);
  // On branche Lenis sur le ticker de GSAP : deux boucles rAF concurrentes
  // produiraient des saccades.
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);

  // Les ancres passent par Lenis, sinon le scroll natif et Lenis se disputent.
  const headerOffset = -72;
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    const href = a.getAttribute("href");
    if (href === "#" || href.length < 2) return;
    a.addEventListener("click", (e) => {
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      lenis.scrollTo(target, { offset: headerOffset });
    });
  });
}

export function initAnimations() {
  const role = document.querySelector(".hero__role");
  if (role && !reduced) typewriter(role);

  if (reduced) {
    // Aucune animation. Le contenu est déjà visible : rien à révéler.
    return;
  }

  const { gsap, ScrollTrigger } = window;
  if (!gsap || !ScrollTrigger) {
    console.warn("GSAP indisponible — le site reste entièrement utilisable.");
    return;
  }

  gsap.registerPlugin(ScrollTrigger);
  if (window.Lenis) initLenis(gsap, ScrollTrigger);

  // --- Barre de progression de lecture ---
  gsap.to("#scroll-progress", {
    scaleX: 1,
    ease: "none",
    scrollTrigger: {
      trigger: document.body,
      start: "top top",
      end: "bottom bottom",
      scrub: 0.3,
    },
  });

  // --- Cascade du hero au chargement ---
  gsap.from(".hero__content > *", {
    y: 28,
    opacity: 0,
    duration: 0.8,
    stagger: 0.09,
    ease: "power3.out",
    delay: 0.15,
  });
  gsap.from(".hero__visual", {
    scale: 0.94,
    opacity: 0,
    duration: 1,
    ease: "power3.out",
    delay: 0.3,
  });

  // --- Révélation des sections au scroll ---
  gsap.utils
    .toArray(".section > .container > *, .stats__grid")
    .forEach((el) => {
      gsap.from(el, {
        y: 32,
        opacity: 0,
        duration: 0.7,
        ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 88%", once: true },
      });
    });

  // --- Compteurs de statistiques ---
  gsap.utils.toArray(".stat__value").forEach((el) => {
    const target = Number(el.dataset.countTo);
    const suffix = el.dataset.suffix || "";
    const counter = { value: 0 };
    gsap.to(counter, {
      value: target,
      duration: 1.6,
      ease: "power2.out",
      scrollTrigger: { trigger: el, start: "top 92%", once: true },
      onUpdate: () => {
        el.textContent = Math.round(counter.value) + suffix;
      },
    });
  });

  // --- Ligne de timeline qui se dessine ---
  const line = document.querySelector(".timeline__line");
  if (line) {
    gsap.fromTo(
      line,
      { scaleY: 0 },
      {
        scaleY: 1,
        ease: "none",
        scrollTrigger: {
          trigger: ".timeline",
          start: "top 75%",
          end: "bottom 85%",
          scrub: 0.5,
        },
      }
    );
  }

  // --- Cartes projet en cascade ---
  gsap.from(".project-card", {
    y: 36,
    opacity: 0,
    duration: 0.6,
    stagger: 0.06,
    ease: "power3.out",
    scrollTrigger: { trigger: "#project-grid", start: "top 85%", once: true },
  });

  // --- Marquee ---
  const track = document.querySelector("#marquee-track");
  if (track) {
    // La liste est dupliquée : décaler de la moitié boucle sans couture.
    gsap.to(track, { xPercent: -50, duration: 26, ease: "none", repeat: -1 });
  }

  // --- Surbrillance de la section active ---
  // Remplace l'écouteur `scroll` manuel de l'ancien app.js, qui recalculait
  // la position de chaque section à chaque pixel défilé.
  const links = [...document.querySelectorAll(".nav__link")];
  links.forEach((link) => {
    const id = link.getAttribute("href");
    const section = document.querySelector(id);
    if (!section) return;

    const setActive = () => {
      links.forEach((l) => l.classList.remove("is-active"));
      link.classList.add("is-active");
    };

    ScrollTrigger.create({
      trigger: section,
      start: "top 45%",
      end: "bottom 45%",
      onEnter: setActive,
      onEnterBack: setActive,
    });
  });
}
