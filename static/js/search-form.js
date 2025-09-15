import {
  createBookCardEl,
  updateLocalBookResultsContainer,
} from "./book-cards.js";
import { handleFormSubmission } from "./utils.js";

export function setUpSearchForm(ui) {
  ui.searchFormEl.addEventListener("submit", async function (e) {
    const response = await handleFormSubmission(
      e,
      this,
      this.action,
      ui.loaderEl,
    );

    handleResponse(response, ui);
  });
}

export function handleResponse(response, ui, localSearch = false) {
  console.log(response.data.results);
  if (response.success && Array.isArray(response.data.results)) {
    const books = response.data.results;
    console.log(books);

    // localSearch is only used by the internal search form
    // recommendation/add-book searches will always be localSearch = false
    if (localSearch) {
      updateLocalBookResultsContainer(books);
    } else {
      updateBookResultsContainer(books, ui);
    }
  } else {
    console.log(response.message);
    ui.resultsContainer.innerText = response.message || "An error occurred.";
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
