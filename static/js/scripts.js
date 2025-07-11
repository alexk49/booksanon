import { populateCsrfTokens } from "./utils.js";

function main() {
  populateCsrfTokens();

  const navToggleBtn = document.getElementById("nav-toggle");
  const navMenu = document.getElementById("nav-menu");

  navToggleBtn.addEventListener("click", () => {
    const isOpen = navMenu.classList.toggle("open");
    navToggleBtn.setAttribute("aria-expanded", isOpen);
  });
}

document.addEventListener("DOMContentLoaded", main);
