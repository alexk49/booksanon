import { populateCsrfTokens } from "./utils.js";

function toggleNav(navbarEl, navItems) {
  navbarEl.classList.toggle("responsive");

  for (const item of navItems) {
    item.classList.toggle("responsive");
  }
}

function main() {
  populateCsrfTokens();

  const navbarEl = document.getElementById("nav-bar");
  const navItems = document.getElementsByClassName("nav-item");
  const navToggleBtn = document.getElementById("navbar-toggle");

  navToggleBtn.addEventListener("click", () => {
    toggleNav(navbarEl, navItems);
  });
}

document.addEventListener("DOMContentLoaded", main);
