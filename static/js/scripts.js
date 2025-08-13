import { hideEl, showHiddenEl, populateCsrfTokens } from "./utils.js";

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

function setUpExpandReviewBtn(expandBtn) {
  if (!expandBtn) {
    return;
  }

  expandBtn.addEventListener("click", () => {
    const reviewParagraph = expandBtn.previousElementSibling;
    const isExpanding = expandBtn.textContent === "Expand review";

    if (isExpanding) {
      const fullText = reviewParagraph.getAttribute("data-full");
      reviewParagraph.textContent = fullText;
      expandBtn.textContent = "Collapse review";
    } else {
      const truncatedText = reviewParagraph.getAttribute("data-truncated");
      reviewParagraph.textContent = truncatedText;
      expandBtn.textContent = "Expand review";
    }
  });
}

function main() {
  populateCsrfTokens();

  const navToggleBtn = document.getElementById("nav-toggle");
  const navMenu = document.getElementById("nav-menu");

  setUpNavToggle(navToggleBtn, navMenu);

  const loaderEl = document.getElementById("global-loader");
  const navSearchFormEl = document.getElementById("nav-search-form");

  setUpNavSearchForm(navSearchFormEl, loaderEl);

  const expandBtns = document.querySelectorAll(".expand-btn");

  if (expandBtns) {
    expandBtns.forEach((btn) => {
      setUpExpandReviewBtn(btn);
    });
  }

  window.addEventListener("pageshow", () => {
    hideEl(loaderEl);
  });
}

document.addEventListener("DOMContentLoaded", main);
