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

function setUpExpandReviewBtn(reviewSection) {
  const expandBtn = reviewSection.querySelector(".expand-btn");

  if (!expandBtn) {
    return;
  }

  expandBtn.addEventListener("click", () => {
    const reviewContent = reviewSection.querySelector(".review-content");
    reviewContent.classList.toggle("review-content-expanded");

    // Change the button text based on the expanded state
    if (reviewContent.classList.contains("review-content-expanded")) {
      expandBtn.textContent = "Hide review";
    } else {
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

  const reviewSections = document.querySelectorAll(".review-section");

  if (reviewSections) {
    reviewSections.forEach((review) => {
      setUpExpandReviewBtn(review);
    });
  }

  window.addEventListener("pageshow", () => {
    hideEl(loaderEl);
  });
}

document.addEventListener("DOMContentLoaded", main);
