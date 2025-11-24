const sections = document.querySelectorAll("section");
const linksNav = document.querySelectorAll(".navigation a");
const header = document.querySelector(".btn-home");
const menulcon = document.querySelector("#menu-burger");
const nav = document.querySelector(".navigation");
const themeToggle = document.querySelector("#theme-toggle");

const burgerActive = () => {
  menulcon.classList.toggle("bx-x");
  nav.classList.toggle("active");
};
const scrollActive = () => {
  sections.forEach((section) => {
    let top = window.scrollY;
    let offset = section.offsetTop - 150;
    let height = section.offsetHeight;
    let id = section.getAttribute("id");
    if (top >= offset && top < offset + height) {
      linksNav.forEach((links) => {
        links.classList.remove("active");
        document
          .querySelector(`.navigation a[href*=${id}]`)
          .classList.add("active");
      });
    }
  });
};

ScrollReveal({
  reset: true,
  distance: "80px",
  duration: 2000,
  delay: 200,
});
ScrollReveal().reveal(".home-content,.section-title", { origin: "top" });
ScrollReveal().reveal(
  ".home-img,.services-content,.portfolio-box,.contact-form",
  { origin: "bottom" }
);
ScrollReveal().reveal(".home-content h1,.about-img", { origin: "left" });
ScrollReveal().reveal(".home-content p,.about-content", { origin: "right" });
ScrollReveal().reveal(".tech-category", { origin: "bottom", interval: 200 });
//Responsable de l'ecriture qui s'efface en rouge
//construit grace a ue bibliothèque typed faire des recherches sur internet
const typed = new Typed(".multiple", {
  strings: ["Développeur Web", "Développeur App", "Formateur"],
  typeSeed: 100,
  backSpeed: 100,
  backDelay: 1000,
  loop: true,
});
//console.log(typed);

// Fermer le menu mobile lors du clic sur un lien
linksNav.forEach((link) => {
  link.addEventListener("click", () => {
    if (nav.classList.contains("active")) {
      menulcon.classList.remove("bx-x");
      nav.classList.remove("active");
    }
  });
});

// Gestion du thème clair/sombre
const setTheme = (theme) => {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
};

const toggleTheme = () => {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "light" ? "dark" : "light";
  setTheme(newTheme);
};

// Initialiser le thème au chargement
const initTheme = () => {
  const savedTheme = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

  if (savedTheme) {
    setTheme(savedTheme);
  } else if (prefersDark) {
    setTheme("dark");
  } else {
    setTheme("dark"); // Thème par défaut
  }
};

// Initialiser le thème dès le chargement
initTheme();

themeToggle.addEventListener("click", toggleTheme);
menulcon.addEventListener("click", burgerActive);
window.addEventListener("scroll", scrollActive);
