import {
  addSubmissionToLocalStorage,
  handleFormSubmission,
  writeErrorsToContainer,
} from "./utils.js";
import { createBookCardEl } from "./book-cards.js";
import { updateLocalBookResultsContainer } from "./book-cards.js";

export function setUpSearchForm(ui) {
  ui.searchFormEl.addEventListener("submit", async function (e) {
    const response = await handleFormSubmission(
      e,
      this,
      this.action,
      ui.loaderEl,
    );

    handleBookSearchResponse(response, ui);
  });
}

export function handleBookSearchResponse(response, ui, localSearch = false) {
  if (response.success && Array.isArray(response.data.results)) {
    const books = response.data.results;

    // localSearch is only used by the internal search form
    // recommendation/add-book searches will always be localSearch = false
    if (localSearch) {
      updateLocalBookResultsContainer(books);
    } else {
      updateBookResultsContainer(books, ui);
    }
  } else {
    writeErrorsToContainer(response, ui.resultsContainer);
  }
}

export function updateBookResultsContainer(books, ui) {
  if (books && books.length != 0) {
    ui.resultsContainer.innerHTML = "";
    books.forEach((book) => {
      const card = createBookCardEl(book);
      const selectBtnEl = card.querySelector(".select-book-btn");
      setUpSelectBtn(card, selectBtnEl, ui);
      ui.resultsContainer.appendChild(card);
    });
  } else {
    ui.resultsContainer.innerText = "No results found.";
  }
}

export function setUpSelectBtn(card, selectBtnEl, ui) {
  selectBtnEl.addEventListener("click", () => {
    ui.cardViewController.captureCardPosition(card);
    switchToReviewView(ui, card);
  });
}

export function setUpBackBtn(ui, backBtnEl) {
  backBtnEl.addEventListener("click", () => {
    const bookCard = ui.reviewCardContainerEl.querySelector(".book-card");
    ui.cardViewController.restoreCard(bookCard);
    switchToResultsView(ui);
  });
}

export function switchToResultsView({
  searchContainer,
  resultsContainer,
  reviewFormContainerEl,
}) {
  searchContainer.classList.remove("hidden");
  resultsContainer.classList.remove("hidden");
  reviewFormContainerEl.classList.add("hidden");
}

export function switchToReviewView(
  {
    searchContainer,
    resultsContainer,
    reviewCardContainerEl,
    reviewFormContainerEl,
    reviewHiddenIdEl,
  },
  card,
) {
  searchContainer.classList.add("hidden");
  resultsContainer.classList.add("hidden");
  reviewCardContainerEl.innerHTML = "";
  reviewCardContainerEl.appendChild(card);
  reviewFormContainerEl.classList.remove("hidden");
  reviewHiddenIdEl.value = card.querySelector(".openlib_id").innerText;
}

function createCardViewController() {
  let previousCardParent = null;
  let previousCardNextSibling = null;

  function captureCardPosition(card) {
    previousCardParent = card.parentNode;
    previousCardNextSibling = card.nextElementSibling;
  }

  function restoreCard(bookCard) {
    if (bookCard && previousCardParent) {
      if (previousCardNextSibling) {
        previousCardParent.insertBefore(bookCard, previousCardNextSibling);
      } else {
        previousCardParent.appendChild(bookCard);
      }
    }
    previousCardParent = null;
    previousCardNextSibling = null;
  }

  return {
    captureCardPosition,
    restoreCard,
  };
}

function setUpReviewForm(
  reviewFormContainerEl,
  loaderEl,
  reviewErrorsContainer,
) {
  reviewFormContainerEl.addEventListener("submit", async function (event) {
    const response = await handleFormSubmission(
      event,
      this,
      "/api/submit-book",
      loaderEl,
    );

    if (response.success) {
      const submissionID = response.data.submission_id;
      const submittedData = new FormData(this);

      const newSubmission = {
        id: submissionID,
        timestamp: Date.now(),
        review: submittedData.get("review"),
        openlib_id: submittedData.get("openlib_id_hidden"),
      };

      addSubmissionToLocalStorage(newSubmission);

      window.location.href = "/submission";
    } else {
      writeErrorsToContainer(response, reviewErrorsContainer);
    }
  });
}

function setUpReviewCounter(reviewTextEl, counterEl) {
  reviewTextEl.addEventListener("input", () => {
    const textCount = reviewTextEl.value.split(" ").length;
    counterEl.innerText = `${textCount}/1500`;
  });
}

function main() {
  const ui = {
    loaderEl: document.getElementById("global-loader"),
    searchContainer: document.getElementById("search"),
    resultsContainer: document.getElementById("results"),
    reviewFormContainerEl: document.getElementById("review-form"),
    reviewCardContainerEl: document.getElementById("review-card-container"),
    reviewHiddenIdEl: document.getElementById("openlib-id-hidden"),
    searchFormEl: document.getElementById("search-form"),
    cardViewController: createCardViewController(),
  };

  const backBtnEl = document.getElementById("back-btn");
  if (backBtnEl) {
    setUpBackBtn(ui, backBtnEl);
  }

  if (ui.searchFormEl) {
    setUpSearchForm(ui);
  }

  const providerSelect = document.getElementById("search-provider");

  if (providerSelect) {
    providerSelect.addEventListener("change", function () {
      ui.searchFormEl.action = this.value;
    });
  }

  const submitReviewForm = document.getElementById("submit-form");
  const reviewErrorsContainer = document.getElementById("review-form-errors");

  if (submitReviewForm && reviewErrorsContainer) {
    setUpReviewForm(submitReviewForm, ui.loaderEl, reviewErrorsContainer);
  }

  const reviewText = document.querySelector('textarea[name="review"]');

  if (reviewText) {
    const counterEl = document.getElementById("text-counter");
    setUpReviewCounter(reviewText, counterEl);
  }
}

document.addEventListener("DOMContentLoaded", main);
