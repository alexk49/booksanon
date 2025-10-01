import { hideEl, showHiddenEl, populateCsrfTokens, } from "./utils.js";

function setUpNavToggle(navToggleBtn, navMenu) {
  navToggleBtn.addEventListener("click", () => {
    const isOpen = navMenu.classList.toggle("open");
    navToggleBtn.setAttribute("aria-expanded", isOpen);
  });
}

function setUpNavSearchForm(navSearchFormEl, loaderEl) {
  if (navSearchFormEl) {
    navSearchFormEl.addEventListener("submit", () => {
      showHiddenEl(loaderEl);
    });
  }
}

function main() {
  populateCsrfTokens();

  const navToggleBtn = document.getElementById("nav-toggle");
  const navMenu = document.getElementById("nav-menu");

  setUpNavToggle(navToggleBtn, navMenu);

  const loaderEl = document.getElementById("global-loader");
  const navSearchFormEl = document.getElementById("nav-search-form");

  setUpNavSearchForm(navSearchFormEl, loaderEl);

  window.addEventListener("pageshow", () => {
    hideEl(loaderEl);
  });
}

document.addEventListener("DOMContentLoaded", main);
